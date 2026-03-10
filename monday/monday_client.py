import requests
import config

class MondayClient:
    def __init__(self):
        self.api_url = config.MONDAY_API_URL
        self.headers = {
            "Authorization": config.MONDAY_API_TOKEN,
            "Content-Type": "application/json",
            "API-Version": "2023-10"
        }

    def execute_query(self, query):
        try:
            response = requests.post(
                self.api_url, 
                json={'query': query}, 
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"errors": [str(e)]}

    def fetch_board_data(self, board_id):
        if not board_id:
            return None
            
        # Increase limit to 500 to ensure we get enough data for lookups and analysis
        query = f"""
        {{
          boards(ids: {board_id}) {{
            name
            items_page (limit: 500) {{
              items {{
                name
                column_values {{
                  column {{
                    title
                  }}
                  text
                }}
              }}
            }}
          }}
        }}
        """
        return self.execute_query(query)
