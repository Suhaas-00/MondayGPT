import sys
import os
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv(override=True)

# Import after loading env variables
from agents.chatbot_agent import ChatbotAgent


def check_environment():
    """Validate required environment variables before starting."""

    required_vars = [
        "MONDAY_API_TOKEN",
        "GROQ_API_KEY",
        "DEALS_BOARD_ID",
        "WORK_ORDERS_BOARD_ID"
    ]

    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print("\nCRITICAL CONFIGURATION ERROR")
        print("Missing environment variables in .env file:\n")

        for var in missing:
            print(f" - {var}")

        print("\nPlease update your .env file and restart the program.")
        sys.exit(1)


def main():

    # Validate configuration
    check_environment()

    print("=" * 60)
    print("Monday.com Business Intelligence Chatbot")
    print("=" * 60)
    print("Ask business questions about Deals or Work Orders.")
    print("Type 'exit' to quit.\n")

    try:
        agent = ChatbotAgent()
    except Exception as e:
        print("\nFailed to initialize chatbot agent.")
        print("Error:", str(e))
        sys.exit(1)

    while True:
        try:
            user_input = input("\n[You]: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nSession ended. Goodbye!")
                break

            if not user_input:
                continue

            print("\n[Assistant]: Thinking...\n")

            # Process user question
            response = agent.handle_question(user_input)

            print(response)
            print("-" * 40)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting...")
            break

        except Exception as e:
            print("\n[Error] Unexpected issue occurred:")
            print(str(e))


if __name__ == "__main__":
    main()