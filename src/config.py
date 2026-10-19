"""Central configuration: paths, budgets and constants used across the project."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
IMAGE_DIR = ROOT / "images"

RAW_FILE = DATA_DIR / "raw_expenses.csv"
CLEAN_FILE = DATA_DIR / "cleaned_expenses.csv"
USER_FILE = DATA_DIR / "user_entries.csv"   # rows added from the Streamlit form

SEED = 42
START_DATE = "2025-10-01"
END_DATE = "2026-09-30"

# Monthly budget per expense category (Rs). Edit these to match your own life.
BUDGETS = {
    "Rent": 12000,
    "Food": 6500,
    "Transport": 2500,
    "Bills": 3200,
    "Shopping": 3500,
    "Entertainment": 2000,
    "Subscriptions": 2500,
    "Travel": 2500,
    "Education": 2500,
    "Health": 1500,
}

WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Fixed/recurring categories - excluded when studying day-to-day spending habits
FIXED_CATEGORIES = ["Rent", "Bills", "Subscriptions", "Education"]
