import pandas as pd

class OrderAnalysis:
    @staticmethod
    def get_delayed_orders(orders_df):
        now = pd.Timestamp.now()
        # Delayed if status is not completed and due_date is in the past
        delayed = orders_df[
            (orders_df['status'].str.lower() != 'completed') & 
            (orders_df['due_date'] < now)
        ]
        
        return {
            "delayed_count": len(delayed),
            "delayed_orders": delayed[['work_order_id', 'description', 'due_date']].to_dict('records')
        }
