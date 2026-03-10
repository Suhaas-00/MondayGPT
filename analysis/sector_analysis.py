import pandas as pd

class SectorAnalysis:
    @staticmethod
    def get_sector_performance(deals_df):
        # Calculate win rate and total value per sector
        performance = deals_df.groupby('sector').agg(
            total_deals=('deal_id', 'count'),
            total_value=('deal_value', 'sum'),
            won_deals=('status', lambda x: (x.str.lower() == 'won').sum())
        )
        performance['win_rate'] = (performance['won_deals'] / performance['total_deals']) * 100
        return performance.sort_values(by='total_value', ascending=False).to_dict('index')
