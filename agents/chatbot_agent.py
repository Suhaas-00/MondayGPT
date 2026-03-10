from llm.groq_client import GroqClient
from monday.monday_client import MondayClient
from processing.data_parser import DataParser
from processing.insight_generator import InsightGenerator
import config
import pandas as pd

class ChatbotAgent:
    def __init__(self):
        self.llm = GroqClient()
        self.monday = MondayClient()
        self.parser = DataParser()
        self.insight_gen = InsightGenerator()

    def handle_question(self, question):
        # 1. Interpret what the user wants
        interpretation = self.llm.interpret_query(question)
        intent = interpretation.get('intent', 'GENERAL')
        target = interpretation.get('target_board', 'deals')
        
        # Check if this is a specific lookup (contains ID-like patterns)
        is_specific_lookup = any(char.isdigit() for char in question) and len(question.split()) < 10
        
        # 2. Fetch data
        all_dfs = {}
        
        if is_specific_lookup:
            # For specific lookups, we search BOTH boards to be sure
            print(f"[*] Searching for specific item across all boards...")
            for board_name, board_id in config.BOARD_MAP.items():
                raw_data = self.monday.fetch_board_data(board_id)
                if "errors" not in raw_data:
                    df = self.parser.parse_monday_response(raw_data)
                    if not df.empty:
                        all_dfs[board_name] = df
        else:
            # For general analysis, fetch the targeted board
            board_id = config.BOARD_MAP.get(target)
            if not board_id:
                return f"Error: No Board ID configured for '{target}'."
            
            print(f"[*] Fetching data from Monday.com board ({target})...")
            raw_data = self.monday.fetch_board_data(board_id)
            if "errors" in raw_data:
                return f"Error from Monday.com API: {raw_data['errors'][0]}"
            
            df = self.parser.parse_monday_response(raw_data)
            if df.empty:
                return f"The {target} board appears to be empty or unreadable."
            all_dfs[target] = df

        # 3. Combine data if multiple boards were searched
        if len(all_dfs) > 1:
            # We pass a combined context or let the generator handle it
            # For now, let's just merge or pass the most relevant one
            # The InsightGenerator is better at searching within a DF
            # So we pass a combined DF for lookup purposes
            combined_df = pd.concat(all_dfs.values(), ignore_index=True, sort=False)
        elif len(all_dfs) == 1:
            combined_df = list(all_dfs.values())[0]
        else:
            return "Could not retrieve data from any configured Monday.com boards."

        # 4. Generate conversational insight
        print(f"[*] Generating insights for intent: {intent}...")
        answer = self.insight_gen.generate_answer(question, combined_df, intent)
        
        return answer
