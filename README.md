# Monday.com BI Chatbot

A Python CLI chatbot that answers business questions by querying Monday.com boards using GraphQL and generating insights via Groq (Llama3).

## Features
- **Natural Language Understanding**: Uses Llama3 to interpret user intent.
- **Dynamic Board Querying**: Fetches real-time data from Monday.com boards.
- **Automated Data Processing**: Converts Monday.com nested structures into flat DataFrames for analysis.
- **AI Insights**: Summarizes raw metrics into conversational business intelligence.

## Setup Instructions

1.  **Clone the project** and navigate to the directory.
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment Variables**:
    Create a `.env` file in the root directory (use `.env.example` as a template):
    ```env
    MONDAY_API_TOKEN=your_monday_token
    GROQ_API_KEY=your_groq_key
    DEALS_BOARD_ID=123456789
    WORK_ORDERS_BOARD_ID=987654321
    ```
4.  **How to get Board IDs**:
    - Open your board on Monday.com.
    - The Board ID is the numeric string at the end of the URL (e.g., `https://yourspace.monday.com/boards/123456789`).

## Usage
Run the chatbot:
```bash
python main.py
```

## Example Questions
- "How much revenue is pending collection?"
- "Which sector has the highest deal value?"
- "Are there any work orders currently delayed?"
- "Show me a summary of our pipeline health."

## Architecture Flow
1. **User Input** → Terminal
2. **Intent Engine** → Llama3 (Groq) identifies board and metric.
3. **Data Fetcher** → GraphQL queries Monday.com API.
4. **Parser** → Pandas cleans and flattens the response.
5. **Summarizer** → Llama3 generates the final conversational insight.
