"""Data cleaning and feature engineering for the expense data."""
import pandas as pd

from src.config import CLEAN_FILE

PAYMENT_FIX = {"Upi": "UPI", "Netbanking": "Net Banking"}


def clean(df: pd.DataFrame):
    """Return (clean_df, report). Never mutates the input."""
    df = df.copy()
    report = {"rows_in": len(df)}

    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    if "Payment_Method" not in df.columns:
        df["Payment_Method"] = "Unknown"
    if "Description" not in df.columns:
        df["Description"] = ""

    # 1. duplicates
    before = len(df)
    df = df.drop_duplicates()
    report["duplicates_removed"] = before - len(df)

    # 2. types: amounts like "Rs 1,200" -> 1200.0 ; bad dates -> NaT
    df["Amount"] = pd.to_numeric(
        df["Amount"].astype(str).str.replace(r"[^0-9.\-]", "", regex=True), errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # 3. text standardisation (missing category -> "Uncategorized")
    df["Category"] = df["Category"].fillna("Uncategorized").astype(str).str.strip().str.title()
    df["Category"] = df["Category"].replace({"": "Uncategorized", "Nan": "Uncategorized"})
    df["Type"] = df["Type"].astype(str).str.strip().str.title()
    df["Payment_Method"] = df["Payment_Method"].astype(str).str.strip().str.title().replace(PAYMENT_FIX)
    df["Description"] = df["Description"].fillna("").astype(str).str.strip()

    # 4. drop unusable rows (missing amount/date, non-positive amount, unknown type)
    before = len(df)
    df = df.dropna(subset=["Date", "Amount"])
    df = df[(df["Amount"] > 0) & (df["Type"].isin(["Income", "Expense"]))]
    report["invalid_rows_removed"] = before - len(df)
    report["uncategorized_rows"] = int((df["Category"] == "Uncategorized").sum())

    # 5. feature engineering
    df["Year"] = df["Date"].dt.year
    df["Month_Num"] = df["Date"].dt.month
    df["Month"] = df["Date"].dt.to_period("M").astype(str)       # e.g. 2026-03 (sortable)
    df["Month_Name"] = df["Date"].dt.month_name()
    df["Day"] = df["Date"].dt.day
    df["Weekday"] = df["Date"].dt.day_name()
    df["Is_Weekend"] = df["Date"].dt.dayofweek >= 5

    df = df.sort_values("Date").reset_index(drop=True)
    report["rows_out"] = len(df)
    return df, report


def save_clean(df: pd.DataFrame) -> None:
    CLEAN_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False)
