from groq import Groq
import config
import json

class GroqClient:
    def __init__(self):
        # Sanitize key in case of hidden whitespace/newlines from .env
        api_key = config.GROQ_API_KEY.strip() if config.GROQ_API_KEY else None
        self.client = Groq(api_key=api_key)
        self.model = config.GROQ_MODEL

    def get_completion(self, prompt: str, system_prompt: str):
        # Safety truncation: Limit prompt to ~10k characters to avoid Groq 400 errors
        if len(prompt) > 10000:
            prompt = prompt[:10000] + "... [TRUNCATED DUE TO LENGTH]"
            
        try:
            completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                model=self.model,
                temperature=0.1,
            )
            return completion.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
                return "Error: Invalid Groq API Key. Please verify the GROQ_API_KEY in your .env file."
            return f"Groq API Error: {error_msg}"

    def interpret_query(self, user_question):
        system_prompt = """
        You are a query interpreter for a Monday.com BI tool.
        Categorize the user's question and extract the intent.
        
        Boards Available:
        - deals: Contains sales opportunities, revenue, sectors, and client codes.
        - work_orders: Contains project execution tasks, statuses, due dates, and technical details.
        
        Intent Categories:
        - REVENUE_SUMMARY: Financial metrics like collection, total value, or billing.
        - PIPELINE_HEALTH: Sales stage, probability, and upcoming deal closures.
        - SECTOR_PERFORMANCE: Comparisons across different industries or sectors.
        - DELAYED_TASKS: Specifically for work orders or tasks that are behind schedule.
        - GENERAL: Any other lookup or broad question.
        
        Respond ONLY with a JSON object:
        {
            "intent": "CATEGORY_NAME",
            "target_board": "deals" or "work_orders"
        }
        """
        response = self.get_completion(user_question, system_prompt)
        try:
            # Clean possible markdown code blocks from LLM response
            clean_response = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_response)
        except:
            return {"intent": "GENERAL", "target_board": "deals"}
