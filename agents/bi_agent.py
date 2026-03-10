import pandas as pd
from utils.llm_client import LLMClient
from data.loader import DataLoader
from data.cleaner import DataCleaner
from data.schema_mapper import SchemaMapper
from analysis.revenue_analysis import RevenueAnalysis
from analysis.pipeline_analysis import PipelineAnalysis
from analysis.sector_analysis import SectorAnalysis
from analysis.order_analysis import OrderAnalysis

class BIAgent:
    def __init__(self):
        self.llm = LLMClient()
        self.loader = DataLoader()
        self.cleaner = DataCleaner()
        self.mapper = SchemaMapper()
        
        self.deals_df = None
        self.orders_df = None
        self.is_initialized = False

    def initialize_data(self):
        try:
            # Load
            raw_deals, raw_orders = self.loader.load_all_data()
            
            # Clean
            clean_deals, clean_orders = self.cleaner.clean_all(raw_deals, raw_orders)
            
            # Validate
            self.mapper.validate_all(clean_deals, clean_orders)
            
            self.deals_df = clean_deals
            self.orders_df = clean_orders
            self.is_initialized = True
            return True, "Data loaded and cleaned successfully."
        except Exception as e:
            return False, f"Initialization failed: {str(e)}"

    def chat(self, user_query):
        if not self.is_initialized:
            success, msg = self.initialize_data()
            if not success:
                return msg

        # 1. Interpret query
        task = self.llm.interpret_query(user_query)
        
        # 2. Perform Analysis based on task
        analysis_data = {}
        if "REVENUE" in task:
            analysis_data = RevenueAnalysis.get_total_revenue(self.deals_df)
            analysis_data['sector_revenue'] = RevenueAnalysis.get_revenue_by_sector(self.deals_df)
        elif "PIPELINE" in task:
            analysis_data = PipelineAnalysis.get_pipeline_health(self.deals_df)
        elif "SECTOR" in task:
            analysis_data = SectorAnalysis.get_sector_performance(self.deals_df)
        elif "DELAYED" in task:
            analysis_data = OrderAnalysis.get_delayed_orders(self.orders_df)
        else:
            # General combined stats
            analysis_data = {
                "total_revenue": RevenueAnalysis.get_total_revenue(self.deals_df)['total_revenue'],
                "pipeline_value": PipelineAnalysis.get_pipeline_health(self.deals_df)['total_pipeline_value'],
                "delayed_orders_count": OrderAnalysis.get_delayed_orders(self.orders_df)['delayed_count']
            }

        # 3. Generate Insight using LLM
        prompt = f"""
        User Question: {user_query}
        Raw Analysis Data: {analysis_data}
        
        Provide a professional business insight based on this data. 
        Focus on trends, health, and actionable points. 
        Keep it concise but informative.
        """
        
        insight = self.llm.get_completion(prompt, "You are a Business Intelligence Analyst. Transform data into qualitative insights.")
        return insight
