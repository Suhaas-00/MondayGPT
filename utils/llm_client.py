from groq import Groq
import config

class LLMClient:
    def __init__(self):
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL

    def get_completion(self, prompt: str, system_prompt: str = "You are a helpful Business Intelligence assistant."):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.2,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error connecting to Groq API: {str(e)}"

    def interpret_query(self, query: str):
        """
        Interprets the user's business question and maps it to a specific analysis task.
        """
        system_prompt = """
        You are a query interpreter for a BI Agent. 
        Categorize the user's question into one of the following tasks: 
        1. REVENUE_ANALYSIS (Totals, averages, sector-wise revenue)
        2. PIPELINE_ANALYSIS (Deal health, deal status, upcoming closures)
        3. SECTOR_ANALYSIS (Performance by industry/sector)
        4. DELAYED_ORDERS (Work orders behind schedule)
        5. GENERAL_INSIGHTS (Overall business health)

        Respond ONLY with the task name.
        """
        return self.get_completion(query, system_prompt).strip()
