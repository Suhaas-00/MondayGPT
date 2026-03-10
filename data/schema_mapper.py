class SchemaMapper:
    """
    Ensures that the DataFrames have the expected columns for our business logic.
    """
    REQUIRED_DEAL_COLS = ['deal_id', 'deal_value', 'sector', 'status', 'close_date']
    REQUIRED_ORDER_COLS = ['work_order_id', 'deal_id', 'status', 'due_date']

    @staticmethod
    def validate_schema(df, required_cols):
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        return True

    def validate_all(self, deals_df, orders_df):
        self.validate_schema(deals_df, self.REQUIRED_DEAL_COLS)
        self.validate_schema(orders_df, self.REQUIRED_ORDER_COLS)
        return True
