from llm.groq_client import GroqClient
import pandas as pd

class InsightGenerator:
    def __init__(self):
        self.llm = GroqClient()

    def generate_answer(self, user_question, df, intent):
        if df.empty:
            return "I couldn't find any relevant data on your Monday.com board to answer that."

        # Search for specific identifiers in the question (IDs, codes, etc.)
        clean_question = "".join([c if c.isalnum() or c in [' ', '-', '_'] else " " for c in user_question])
        words = clean_question.split()
        
        # Identifier detection: words that are long or have digits
        potential_ids = [w for w in words if len(w) > 3 or any(char.isdigit() for char in w)]
        
        relevant_df = pd.DataFrame()
        if potential_ids:
            search_pattern = '|'.join(potential_ids)
            for col in df.columns:
                try:
                    matches = df[df[col].astype(str).str.contains(search_pattern, case=False, na=False)]
                    if not matches.empty:
                        relevant_df = pd.concat([relevant_df, matches])
                except:
                    continue
        
        if not relevant_df.empty:
            relevant_df = relevant_df.drop_duplicates().head(20) # Limit to 20 records to save tokens
            data_context = "SPECIFIC RECORDS FOUND IN DATABASE (Top 20 matches):\n"
            for idx, row in relevant_df.iterrows():
                # Compact record representation: "Col: Val | Col: Val"
                fields = [f"{col}: {row[col]}" for col in df.columns if col != 'name' and row[col] is not None]
                data_context += f"- {row.get('name', 'Unknown')}: {' | '.join(fields)}\n"
            intent = "SPECIFIC_ITEM_LOOKUP"
        else:
            # For general context, limit to 5 rows and exclude rows with all None
            data_context = f"GENERAL CONTEXT (Sample data):\n{df.head(5).to_string(index=False)}\n"

        summary_stats = self._get_summary_stats(df, intent)
        
        prompt = f"""
        User Question: {user_question}
        Intent: {intent}
        
        {data_context}
        
        Overall Statistics:
        {summary_stats}
        
        Task: 
        1. If specific records are listed in 'SPECIFIC RECORDS FOUND', describe their details (status, values, dates) precisely.
        2. If no specific record matches but general data is available, summarize the trends.
        3. Keep the answer professional and conversational.
        """
        
        system_prompt = """
        You are a Business Intelligence Assistant. 
        Your primary goal is to provide specific details from the 'SPECIFIC RECORDS FOUND' block.
        Always list every available field (column) and its value for the records found.
        If multiple records are found, describe them individually.
        Never hide data behind general summaries if specific records are available.
        """
        return self.llm.get_completion(prompt, system_prompt)

    def _get_summary_stats(self, df, intent):
        summary = {}
        try:
            val_cols = [c for c in df.columns if any(k in c for k in ['value', 'amount', 'revenue', 'cost'])]
            if val_cols:
                summary['total_value'] = df[val_cols[0]].sum()
                summary['average_value'] = df[val_cols[0]].mean()
            
            sector_cols = [c for c in df.columns if any(k in c for k in ['sector', 'industry', 'category'])]
            if sector_cols and val_cols:
                summary['top_sectors'] = df.groupby(sector_cols[0])[val_cols[0]].sum().sort_values(ascending=False).head(3).to_dict()

            status_cols = [c for c in df.columns if 'status' in c]
            if status_cols:
                summary['status_counts'] = df[status_cols[0]].value_counts().to_dict()
        except:
            pass
            
        return summary if summary else "No specific aggregations performed, see raw data samples."
