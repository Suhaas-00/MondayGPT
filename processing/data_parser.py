import pandas as pd
import numpy as np

class DataParser:
    @staticmethod
    def parse_monday_response(response):
        """
        Converts Monday.com GraphQL response into a clean Pandas DataFrame.
        """
        try:
            data = response.get('data')
            if not data:
                return pd.DataFrame()
                
            boards = data.get('boards', [])
            if not boards:
                return pd.DataFrame()

            items_page = boards[0].get('items_page', {})
            items = items_page.get('items', [])
            
            rows = []
            for item in items:
                row = {'name': item.get('name')}
                for cv in item.get('column_values', []):
                    title = cv.get('column', {}).get('title', '').strip().lower().replace(" ", "_")
                    if not title:
                        continue
                    text = cv.get('text', '')
                    row[title] = text
                rows.append(row)

            df = pd.DataFrame(rows)
            return DataParser.clean_dataframe(df)
        except Exception as e:
            print(f"[*] Parsing error: {str(e)}")
            return pd.DataFrame()

    @staticmethod
    def clean_dataframe(df):
        if df.empty:
            return df

        # Strip all string values
        df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

        # Basic cleaning: Convert numeric columns
        for col in df.columns:
            if col == 'name' or '_id' in col:
                continue
                
            # Try to convert to numeric safely
            try:
                # Remove common currency and formatting characters
                cleaned_col = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
                # Only convert if at least some values become valid numbers and not just empty strings
                numeric_series = pd.to_numeric(cleaned_col, errors='coerce')
                
                # Check if we have at least 50% non-NaN numeric values
                if numeric_series.notna().sum() > (len(df) * 0.5):
                    df[col] = numeric_series
            except:
                pass
            
            # Convert date columns
            if 'date' in col or 'due' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')

        # Fill NaNs with empty string for display stability
        df = df.replace({np.nan: None}) # Use None for cleaner LLM output than 'NaN'
        return df
