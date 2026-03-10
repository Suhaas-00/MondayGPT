import pandas as pd
from datetime import datetime

class PipelineAnalysis:
    @staticmethod
    def get_pipeline_health(deals_df):
        pipeline_deals = deals_df[deals_df['status'].str.lower() == 'pipeline']
        total_value = pipeline_deals['deal_value'].sum()
        count = len(pipeline_deals)
        
        # Check for deals nearing close date (within 30 days)
        now = pd.Timestamp.now()
        upcoming_closures = pipeline_deals[
            (pipeline_deals['close_date'] > now) & 
            (pipeline_deals['close_date'] <= now + pd.Timedelta(days=30))
        ]
        
        return {
            "total_pipeline_value": total_value,
            "pipeline_deals_count": count,
            "upcoming_closures_count": len(upcoming_closures),
            "upcoming_deals": upcoming_closures[['deal_name', 'deal_value', 'close_date']].to_dict('records')
        }
