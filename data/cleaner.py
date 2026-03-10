import pandas as pd
import config

class DataCleaner:
    @staticmethod
    def clean_dataframe(df):
        # Normalize column names (lowercase, replace spaces with underscores)
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        
        # Fill missing numeric values with 0
        numeric_cols = df.select_dtypes(include=['number']).columns
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Fill missing string values with 'Unknown'
        string_cols = df.select_dtypes(include=['object']).columns
        df[string_cols] = df[string_cols].fillna('Unknown')
        
        # Convert date columns
        for col in df.columns:
            if 'date' in col:
                df[col] = pd.to_datetime(df[col], errors='coerce', format='mixed')
        
        return df

    def clean_all(self, deals_df, orders_df):
        clean_deals = self.clean_dataframe(deals_df)
        clean_orders = self.clean_dataframe(orders_df)
        return clean_deals, clean_orders
