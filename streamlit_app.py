import streamlit as st
import os
import json
import requests
import pandas as pd
import numpy as np
from groq import Groq
from dotenv import load_dotenv

# =============================================================================
# CONFIGURATION & SECRETS
# =============================================================================

# Load environment variables if they exist locally
load_dotenv(override=True)

def get_config(key, default=None):
    """Helper to get config from Streamlit Secrets or Environment Variables"""
    if key in st.secrets:
        return st.secrets[key]
    return os.getenv(key, default)

try:
    GROQ_API_KEY = get_config("GROQ_API_KEY")
    GROQ_MODEL = get_config("GROQ_MODEL", "llama-3.3-70b-versatile")
    MONDAY_API_TOKEN = get_config("MONDAY_API_TOKEN")
    MONDAY_API_URL = "https://api.monday.com/v2"
    DEALS_BOARD_ID = int(get_config("DEALS_BOARD_ID", 0))
    WORK_ORDERS_BOARD_ID = int(get_config("WORK_ORDERS_BOARD_ID", 0))
    
    BOARD_MAP = {
        "deals": DEALS_BOARD_ID,
        "work_orders": WORK_ORDERS_BOARD_ID
    }
except (TypeError, ValueError):
    st.error("⚠️ Configuration Error: Please check your Streamlit Secrets or .env file for valid Board IDs.")
    st.stop()

# =============================================================================
# MONDAY CLIENT
# =============================================================================

class MondayClient:
    def __init__(self):
        self.api_url = MONDAY_API_URL
        self.headers = {
            "Authorization": MONDAY_API_TOKEN,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }

    def execute_query(self, query):
        try:
            response = requests.post(self.api_url, json={'query': query}, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"errors": [str(e)]}

    def fetch_board_data(self, board_id):
        if not board_id: return None
        query = f"{{ boards(ids: {board_id}) {{ name items_page (limit: 500) {{ items {{ name column_values {{ column {{ title }} text }} }} }} }} }}"
        return self.execute_query(query)

# =============================================================================
# DATA PARSER
# =============================================================================

class DataParser:
    @staticmethod
    def parse_monday_response(response):
        try:
            data = response.get('data')
            if not data or not data.get('boards'): return pd.DataFrame()
            items = data['boards'][0].get('items_page', {}).get('items', [])
            
            rows = []
            for item in items:
                row = {'name': item.get('name')}
                for cv in item.get('column_values', []):
                    title = cv.get('column', {}).get('title', '').strip().lower().replace(" ", "_")
                    if title: row[title] = cv.get('text', '')
                rows.append(row)
            return DataParser.clean_dataframe(pd.DataFrame(rows))
        except:
            return pd.DataFrame()

    @staticmethod
    def clean_dataframe(df):
        if df.empty: return df
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
        for col in df.columns:
            if col == 'name' or '_id' in col: continue
            try:
                cleaned_col = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                numeric_series = pd.to_numeric(cleaned_col, errors='coerce')
                if numeric_series.notna().sum() > (len(df) * 0.5): df[col] = numeric_series
            except: pass
            if 'date' in col or 'due' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')
        return df.replace({np.nan: None})

# =============================================================================
# GROQ CLIENT
# =============================================================================

class GroqClient:
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = GROQ_MODEL

    def get_completion(self, prompt: str, system_prompt: str):
        if len(prompt) > 10000: prompt = prompt[:10000] + "... [TRUNCATED]"
        try:
            completion = self.client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                model=self.model, temperature=0.1
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Groq API Error: {str(e)}"

    def interpret_query(self, user_question):
        system_prompt = "You are a query interpreter for a Monday.com BI tool. Categorize intent: REVENUE_SUMMARY, PIPELINE_HEALTH, SECTOR_PERFORMANCE, DELAYED_TASKS, GENERAL. Respond ONLY with JSON: {\"intent\": \"CATEGORY\", \"target_board\": \"deals\" or \"work_orders\"}"
        response = self.get_completion(user_question, system_prompt)
        try:
            clean_res = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_res)
        except:
            return {"intent": "GENERAL", "target_board": "deals"}

# =============================================================================
# INSIGHT GENERATOR
# =============================================================================

class InsightGenerator:
    def __init__(self, groq_client):
        self.llm = groq_client

    def generate_answer(self, user_question, df, intent):
        if df.empty: return "I couldn't find any relevant data to answer that."
        
        # Simple ID lookup
        potential_ids = [w for w in user_question.split() if len(w) > 3 or any(char.isdigit() for char in w)]
        relevant_df = pd.DataFrame()
        if potential_ids:
            pattern = '|'.join(potential_ids)
            for col in df.columns:
                try:
                    matches = df[df[col].astype(str).str.contains(pattern, case=False, na=False)]
                    if not matches.empty: relevant_df = pd.concat([relevant_df, matches])
                except: continue

        if not relevant_df.empty:
            relevant_df = relevant_df.drop_duplicates().head(20)
            data_context = "SPECIFIC RECORDS FOUND:\n"
            for _, row in relevant_df.iterrows():
                fields = [f"{c}: {row[c]}" for c in df.columns if c != 'name' and row[c] is not None]
                data_context += f"- {row.get('name', 'Unknown')}: {' | '.join(fields)}\n"
            intent = "SPECIFIC_ITEM_LOOKUP"
        else:
            data_context = f"GENERAL CONTEXT Sample:\n{df.head(5).to_string(index=False)}\n"

        stats = self._get_stats(df)
        prompt = f"Question: {user_question}\nIntent: {intent}\n\n{data_context}\nStats: {stats}"
        sys_prompt = "You are a Business Intelligence Assistant. Provide specific details from records found. Be professional and list column values clearly."
        return self.llm.get_completion(prompt, sys_prompt)

    def _get_stats(self, df):
        summary = {}
        try:
            val_cols = [c for c in df.columns if any(k in c for k in ['revenue', 'amount', 'value'])]
            if val_cols:
                summary['total'] = df[val_cols[0]].sum()
            status_cols = [c for c in df.columns if 'status' in c]
            if status_cols:
                summary['status'] = df[status_cols[0]].value_counts().head(3).to_dict()
        except: pass
        return summary if summary else "No summary stats."

# =============================================================================
# CHATBOT AGENT
# =============================================================================

class ChatbotAgent:
    def __init__(self):
        self.llm = GroqClient()
        self.monday = MondayClient()
        self.parser = DataParser()
        self.insight_gen = InsightGenerator(self.llm)

    def handle_question(self, question):
        interpretation = self.llm.interpret_query(question)
        intent = interpretation.get('intent', 'GENERAL')
        target = interpretation.get('target_board', 'deals')
        is_specific = any(char.isdigit() for char in question) and len(question.split()) < 10
        
        all_dfs = {}
        target_ids = list(BOARD_MAP.values()) if is_specific else [BOARD_MAP.get(target)]
        
        for b_id in target_ids:
            if not b_id: continue
            raw = self.monday.fetch_board_data(b_id)
            if raw and "errors" not in raw:
                df = self.parser.parse_monday_response(raw)
                if not df.empty: all_dfs[b_id] = df

        if not all_dfs: return "Could not retrieve data from Monday.com."
        combined_df = pd.concat(all_dfs.values(), ignore_index=True, sort=False)
        return self.insight_gen.generate_answer(question, combined_df, intent)

# =============================================================================
# STREAMLIT UI
# =============================================================================

st.set_page_config(page_title="Monday.com BI Assistant", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #000000; }
    div, p, span, h1, h2, h3, h4, h5, h6, li { color: #ffffff !important; }
    header { visibility: hidden; }
    [data-testid="stChatMessage"] {
        background-color: #8B0000 !important;
        border-radius: 0px !important;
        padding: 15px !important;
        margin-bottom: 20px !important;
    }
    .chat-title { text-align: center; font-size: 24px; font-weight: 600; margin-bottom: 2rem; }
</style>
<div class="chat-title">Monday.com BI Assistant</div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm your Monday.com BI Assistant. Ask me anything about your Deals or Work Orders!"}]

if "agent" not in st.session_state:
    st.session_state.agent = ChatbotAgent()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"]=="user" else "🤖"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.agent.handle_question(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")
