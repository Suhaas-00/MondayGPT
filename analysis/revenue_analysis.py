import pandas as pd

class RevenueAnalysis:
    @staticmethod
    def get_total_revenue(deals_df):
        # Revenue is typically sum of 'won' deals
        won_deals = deals_df[deals_df['status'].str.lower() == 'won']
        total = won_deals['deal_value'].sum()
        count = len(won_deals)
        return {
            "total_revenue": total,
            "won_deals_count": count,
            "average_deal_value": total / count if count > 0 else 0
        }

    @staticmethod
    def get_revenue_by_sector(deals_df):
        won_deals = deals_df[deals_df['status'].str.lower() == 'won']
        sector_rev = won_deals.groupby('sector')['deal_value'].sum().sort_values(ascending=False)
        return sector_rev.to_dict()
