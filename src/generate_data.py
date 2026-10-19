"""Create a realistic SYNTHETIC expense dataset (no real financial data needed).

The generator deliberately builds in patterns so the analysis has something to find:
  * fixed monthly costs (rent, internet, mobile, AI-tool subscriptions)
  * higher food / entertainment spend on weekends
  * festive shopping spike in Oct-Nov, travel spike in May-Jun and Dec
  * higher electricity bills in summer
  * a few one-off large purchases (anomalies)
  * monthly stipend/salary plus irregular freelance AI-project income
Then it optionally "dirties" the file (duplicates, blanks, odd casing, Rs symbols)
so the cleaning step has real work to do.
"""
import numpy as np
import pandas as pd

from src.config import END_DATE, RAW_FILE, SEED, START_DATE

# name: (transactions/day, mean Rs, std Rs, descriptions, payment-method weights)
VARIABLE = {
    "Food": (0.85, 230, 95,
             ["Lunch", "Dinner", "Groceries", "Cafe", "Zomato order", "Swiggy order", "Snacks"],
             {"UPI": 0.6, "Card": 0.2, "Cash": 0.2}),
    "Transport": (0.35, 140, 70,
                  ["Auto fare", "Uber ride", "Metro recharge", "Petrol", "Bus ticket"],
                  {"UPI": 0.6, "Cash": 0.3, "Card": 0.1}),
    "Shopping": (0.12, 900, 450,
                 ["Clothes", "Accessories", "Amazon order", "Household items", "Gadget accessory"],
                 {"Card": 0.5, "UPI": 0.4, "Net Banking": 0.1}),
    "Entertainment": (0.10, 450, 220,
                      ["Movie ticket", "Gaming", "Outing with friends", "Concert pass", "OTT add-on"],
                      {"UPI": 0.7, "Card": 0.3}),
    "Health": (0.04, 600, 300,
               ["Pharmacy", "Doctor consultation", "Gym day pass", "Vitamins"],
               {"UPI": 0.7, "Cash": 0.2, "Card": 0.1}),
}

# month -> multiplier for seasonal patterns
SEASON = {
    "Shopping": {10: 1.8, 11: 1.9, 1: 1.3},
    "Entertainment": {12: 1.5, 5: 1.3},
}
TRAVEL_MONTHS = (5, 6, 12)   # months with trips


def _pick(rng, weights):
    return str(rng.choice(list(weights.keys()), p=list(weights.values())))


def generate(seed: int = SEED, start: str = START_DATE, end: str = END_DATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    days = pd.date_range(start, end, freq="D")
    rows = []

    for day in days:
        weekend = day.dayofweek >= 5
        # ---- variable spending ----
        for cat, (rate, mean, std, descs, methods) in VARIABLE.items():
            mult = SEASON.get(cat, {}).get(day.month, 1.0)
            if cat in ("Food", "Entertainment") and weekend:
                mult *= 1.5
            for _ in range(rng.poisson(rate * mult)):
                amt = max(20, rng.normal(mean, std))
                rows.append((day, cat, str(rng.choice(descs)), round(amt), "Expense", _pick(rng, methods)))

        # ---- fixed monthly items ----
        if day.day == 2:
            rows.append((day, "Rent", "Room rent", 12000, "Expense", "UPI"))
        if day.day == 5:
            summer = day.month in (4, 5, 6)
            bill = rng.integers(1500, 2100) if summer else rng.integers(700, 1300)
            rows.append((day, "Bills", "Electricity bill", int(bill), "Expense", "UPI"))
        if day.day == 7:
            rows.append((day, "Bills", "Internet bill", 799, "Expense", "UPI"))
            rows.append((day, "Bills", "Mobile recharge", 299, "Expense", "UPI"))
        if day.day == 10:
            rows.append((day, "Subscriptions", "AI tools subscription", 1650, "Expense", "Card"))
            rows.append((day, "Subscriptions", "Cloud / domain hosting", 450, "Expense", "Card"))

        # ---- trips (travel) ----
        if day.month in TRAVEL_MONTHS and day.day in (12, 13, 14):
            rows.append((day, "Travel", str(rng.choice(["Train tickets", "Hotel stay", "Local sightseeing"])),
                         int(rng.normal(1100, 300)), "Expense", _pick(rng, {"UPI": 0.6, "Card": 0.4})))

        # ---- education (courses, exam fees) ----
        if day.day == 20 and day.month in (10, 1, 4, 7):
            rows.append((day, "Education", str(rng.choice(["Online course", "Certification exam fee", "Books"])),
                         int(rng.normal(1800, 500)), "Expense", "Card"))

        # ---- income ----
        if day.day == 1:
            rows.append((day, "Salary", "Monthly stipend / salary", 35000, "Income", "Bank Transfer"))
        if day.day in (12, 26) and rng.random() < 0.55:
            rows.append((day, "Freelance",
                         str(rng.choice(["AI automation project", "Data dashboard gig", "n8n workflow client"])),
                         int(rng.integers(4000, 14000)), "Income", "Bank Transfer"))

    # ---- hand-placed one-off anomalies (big purchases) ----
    rows += [
        (pd.Timestamp("2026-02-14"), "Shopping", "Laptop repair + new SSD", 18500, "Expense", "Card"),
        (pd.Timestamp("2025-12-22"), "Travel", "Flight tickets (home trip)", 14500, "Expense", "Card"),
        (pd.Timestamp("2026-06-18"), "Health", "Dental treatment", 9000, "Expense", "UPI"),
    ]

    df = pd.DataFrame(rows, columns=["Date", "Category", "Description", "Amount", "Type", "Payment_Method"])
    df["Amount"] = df["Amount"].astype(float).abs().round(0)
    return df.sort_values("Date").reset_index(drop=True)


def make_messy(df: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    """Add realistic data-quality problems so the cleaning step is meaningful."""
    rng = np.random.default_rng(seed + 1)
    out = df.copy()
    out["Date"] = out["Date"].dt.strftime("%Y-%m-%d")
    out["Category"] = out["Category"].astype(object)
    out["Amount"] = out["Amount"].astype(object)
    n = len(out)

    # inconsistent category casing / spaces
    for i in rng.choice(n, size=int(0.04 * n), replace=False):
        out.iat[i, out.columns.get_loc("Category")] = f" {str(out.iat[i, out.columns.get_loc('Category')]).lower()} "
    # rupee symbol and thousands separators in amounts
    for i in rng.choice(n, size=int(0.03 * n), replace=False):
        out.iat[i, out.columns.get_loc("Amount")] = f"\u20b9{int(float(out.iat[i, out.columns.get_loc('Amount')])):,}"
    # missing amounts and categories
    for i in rng.choice(n, size=int(0.01 * n), replace=False):
        out.iat[i, out.columns.get_loc("Amount")] = np.nan
    for i in rng.choice(n, size=int(0.01 * n), replace=False):
        out.iat[i, out.columns.get_loc("Category")] = np.nan
    # duplicated rows
    dupes = out.sample(int(0.015 * n), random_state=seed)
    out = pd.concat([out, dupes], ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)
    return out


def create_raw_file(messy: bool = True) -> pd.DataFrame:
    RAW_FILE.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    if messy:
        df = make_messy(df)
    df.to_csv(RAW_FILE, index=False)
    return df


if __name__ == "__main__":
    d = create_raw_file()
    print(f"Created {RAW_FILE} with {len(d)} rows")
