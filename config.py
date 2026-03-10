import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# -------------------------------------------------
# Groq Configuration
# -------------------------------------------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# -------------------------------------------------
# Monday.com Configuration
# -------------------------------------------------
MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_API_URL = "https://api.monday.com/v2"

# -------------------------------------------------
# Board IDs
# -------------------------------------------------
try:
    DEALS_BOARD_ID = int(os.getenv("DEALS_BOARD_ID"))
    WORK_ORDERS_BOARD_ID = int(os.getenv("WORK_ORDERS_BOARD_ID"))
except (TypeError, ValueError):
    raise ValueError(
        "Board IDs must be valid integers. Check your .env file."
    )

# Map boards for easier lookup
BOARD_MAP = {
    "deals": DEALS_BOARD_ID,
    "work_orders": WORK_ORDERS_BOARD_ID
}

# -------------------------------------------------
# Validate required environment variables
# -------------------------------------------------
REQUIRED_VARS = {
    "GROQ_API_KEY": GROQ_API_KEY,
    "MONDAY_API_TOKEN": MONDAY_API_TOKEN,
    "DEALS_BOARD_ID": DEALS_BOARD_ID,
    "WORK_ORDERS_BOARD_ID": WORK_ORDERS_BOARD_ID
}

missing = [key for key, value in REQUIRED_VARS.items() if value is None]

if missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing)}"
    )