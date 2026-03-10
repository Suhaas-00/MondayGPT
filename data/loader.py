import pandas as pd
import os
import config

class DataLoader:
    @staticmethod
    def load_csv(file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Dataset not found at {file_path}")
        
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            raise Exception(f"Failed to load CSV: {str(e)}")

    def load_all_data(self):
        deals_df = self.load_csv(config.DEALS_CSV)
        orders_df = self.load_csv(config.WORK_ORDERS_CSV)
        return deals_df, orders_df
