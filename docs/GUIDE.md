# Expense Tracker App using Data Science - Complete Project Guide

Prepared for Jatin (student + AIpreneur). Everything here has been run and tested: the pipeline, the 5 unit tests and the Streamlit dashboard all work, and results are identical on pandas 2.x and 3.x.

**Contents**
1. Project explanation · 2. Tech stack options · 3. Architecture · 4. Phase-wise plan · 5. Folder structure · 6. Installation · 7. Full code · 8. Virtual simulation · 9. How to run · 10. GitHub upload · 11. README · 12. Proof-building plan · 13. Screenshots · 14. Interview prep · 15. Future improvements · 16. Troubleshooting

---

## 1️⃣ Project Explanation

### What is an Expense Tracker App?
**Simple explanation:** a tool that records every rupee you earn and spend, groups it into categories (food, rent, travel...) and shows you where your money goes, so you can spend smarter.

**Technical explanation:** a data pipeline that ingests transaction records (`Date, Category, Description, Amount, Type, Payment_Method`), cleans and validates them, engineers time-based features, aggregates by category/month/weekday, compares actuals with budgets, flags anomalies, forecasts future spend and presents everything as charts, a report and an interactive dashboard.

### Why it matters
- Raw bank/UPI data is noisy and unreadable; analytics turns it into decisions.
- People who track spending typically find 10-20% of "leaks" (unused subscriptions, impulse buying).
- Finance, banking and FinTech teams build exactly this kind of analytics (Google Pay spend insights, CRED, PhonePe, RazorpayX).

### Real-world use cases
| Use case | How the project maps to it |
|---|---|
| Personal finance tracking | Monthly income vs expense, savings rate, weekday habits |
| Business expense monitoring | Category totals, payment-method mix, anomaly flags for unusual bills |
| Budgeting and cost control | Per-category budgets, overspending alerts, budget-vs-actual |
| Financial planning | Next-month forecast, category risk table, "what to cut" insights |

### Workflow
```
data input -> storage -> analysis -> visualization -> insights -> decision-making
 (CSV /       (CSV in     (pandas)    (charts +        (plain-English   (cut food spend,
  form)        data/)                  dashboard)       report + AI)     raise budget...)
```

> **AIpreneur angle:** this is a ready-made seed for a product. The same pipeline can power a micro-SaaS for freelancers or small shops ("upload your UPI statement, get a spend report and WhatsApp alerts"). Section 15 covers how.

---

## 2️⃣ Tech Stack Options

| | Option A (Easy) | Option B (Intermediate) | Option C (Advanced) |
|---|---|---|---|
| Tools | Python, pandas, NumPy | + Matplotlib, Seaborn, Streamlit, Plotly | + SQLite/PostgreSQL, scikit-learn/Prophet, FastAPI, Docker |
| Visualization | Matplotlib | Seaborn + Plotly | Plotly Dash / Power BI |
| App / dashboard | None (notebook) | Streamlit dashboard | Web app with login + API + database |
| Difficulty | Beginner, 1-2 days | Beginner-plus, 4-5 days | Advanced, 2-3 weeks |
| Recruiter impact | Basic | **Strong** | Very strong but easy to leave unfinished |

**Best choice for students: Option B.** It shows cleaning, analysis, visualization *and* a deployable app, finishes in about 5 days, and runs on any laptop. This project is Option B plus a light "AI layer" (anomaly detection, forecast, optional local LLM) borrowed from Option C.

---

## 3️⃣ Project Architecture

**Input:** expense data (date, category, amount, payment method) from the synthetic generator, a CSV, or the dashboard form.
**Processing:** cleaning → categorisation → aggregation → trend analysis → budget check → anomaly detection → forecast.
**Output:** CSV reports, PNG charts, `insights_report.md`, Streamlit dashboard.

```
+-----------------------+     +--------------------------+
| SOURCES               |     | data/raw_expenses.csv    |
| - generate_data.py    +---->| (messy, synthetic)       |
| - your own CSV        |     +------------+-------------+
| - dashboard form      |                  |
+-----------------------+                  v
                              +--------------------------+
                              | clean_data.py            |
                              | dupes, types, text fix,  |
                              | features (Month, Weekday)|
                              +------------+-------------+
                                           v
                              +--------------------------+
                              | data/cleaned_expenses.csv|
                              +------------+-------------+
                                           v
                              +--------------------------+
                              | analysis.py              |
                              | KPIs - category - monthly|
                              | budget - anomalies -     |
                              | forecast                 |
                              +------+------------+------+
                                     |            |
                  +------------------+            +------------------+
                  v                                                  v
        +--------------------+                             +--------------------+
        | visualize.py       |                             | insights.py        |
        | 10 PNG charts      |                             | rule-based report  |
        | -> images/         |                             | + optional Ollama  |
        +---------+----------+                             +---------+----------+
                  |                                                  |
                  +-------------------+------------------------------+
                                      v
                       outputs/*.csv, insights_report.md
                                      v
                          app.py (Streamlit dashboard)
```

**Data flow in words:** `main.py` calls the generator (if no data exists), cleans the file, runs analysis functions that return DataFrames, saves tables to `outputs/`, draws charts into `images/`, and writes the insights report. `app.py` reuses the same analysis functions, so the dashboard and the report can never disagree.

---

## 4️⃣ Implementation Plan (Phase-wise)

| Phase | What to do | Why | Expected output | Mistakes to avoid |
|---|---|---|---|---|
| 1. Setup | Install Python, create venv, install libraries, create folders | Reproducible environment | `pip list` shows libraries; folders exist | Installing globally; wrong Python version |
| 2. Data creation | Run `generate_data.py` | No real data available; synthetic data with built-in patterns gives something to discover | `data/raw_expenses.csv` (732 rows) | Purely random data with no patterns; forgetting a fixed seed |
| 3. Cleaning | Run `clean_data.py` | Bad data gives misleading charts | cleaned CSV and a cleaning report | Silently dropping rows without counting them |
| 4. EDA | Explore with `info()`, summaries, group-bys | Understand before modelling | Category, monthly, weekday tables | Plotting before checking types |
| 5. Feature engineering | Month, Weekday, Is_Weekend, savings rate | Enables time-based analysis | New columns | Text month names (they sort alphabetically); use `YYYY-MM` |
| 6. Analysis | Budgets, overspending, anomalies, forecast | This is the "data science" part | Alerts, anomaly table, forecast | Mixing income and expenses in one total |
| 7. Visualization | 10 charts + dashboard | Visuals sell the project | PNGs in `images/` | Unlabelled axes; unreadable pie charts with 12 slices |
| 8. Insights | Write plain-English findings | Analysts are paid for conclusions, not charts | `insights_report.md` | Describing charts instead of giving advice |
| 9. GitHub upload | README, screenshots, commits, push | Public proof for recruiters | Live repo | One giant "final commit"; committing `.venv` or personal data |

---

## 5️⃣ Folder Structure

```
Expense-Tracker-App/
├── data/            raw_expenses.csv (synthetic, messy) and cleaned_expenses.csv
├── notebooks/       expense_tracker_walkthrough.ipynb - same pipeline step by step
├── src/             reusable modules (config, generate_data, clean_data, analysis, visualize, insights)
├── outputs/         category_summary.csv, monthly_summary.csv, overspending_alerts.csv,
│                    anomalies.csv, category_forecast.csv, insights_report.md
├── images/          10 generated charts (README uses them)
├── tests/           pytest unit tests
├── docs/            this guide
├── hardware/        optional ESP32 button expense logger
├── app.py           Streamlit dashboard
├── main.py          one command to run everything
├── requirements.txt dependency list
├── .gitignore       keeps venv and personal entries out of GitHub
├── LICENSE          MIT
└── README.md        the recruiter-facing front page
```

---

## 6️⃣ Installation Guide

1. **Install Python 3.10+** from python.org. On Windows tick **"Add Python to PATH"**. Check: `python --version` (Mac/Linux may need `python3`).
2. **Create a virtual environment** (an isolated folder of libraries for this project):

| | Windows (PowerShell / CMD) | Mac / Linux |
|---|---|---|
| Create | `python -m venv .venv` | `python3 -m venv .venv` |
| Activate | `.venv\Scripts\activate` | `source .venv/bin/activate` |

   If PowerShell blocks activation: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
3. **Install libraries:** `pip install -r requirements.txt`
4. **Verify:** `python -c "import pandas, streamlit, plotly; print('OK')"`
5. **No local setup?** Use Google Colab: upload the folder, run `!pip install -r requirements.txt`, then `!python main.py`.

---

## 7️⃣ Full Project Code

All files below are complete and copy-paste ready. They are also included in the zip.

### `requirements.txt`
```text
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
plotly>=5.18
streamlit>=1.50
openpyxl>=3.1
pytest>=7.0
jupyter>=1.0
```

### `src/config.py` - paths, budgets, constants
```python
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
```

### `src/generate_data.py` - synthetic dataset
```python
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
```

### `src/clean_data.py` - cleaning and feature engineering
```python
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
```

### `src/analysis.py` - KPIs, budgets, anomalies, forecast
```python
"""Analysis functions: KPIs, category/monthly summaries, budget checks,
anomaly detection and a simple spending forecast.  All functions take the
cleaned DataFrame and return DataFrames/dicts, so they are easy to test and
reuse from both main.py and the Streamlit dashboard."""
import numpy as np
import pandas as pd

from src.config import BUDGETS


def _expenses(df):
    return df[df["Type"] == "Expense"]


def _income(df):
    return df[df["Type"] == "Income"]


def kpis(df: pd.DataFrame) -> dict:
    """Headline numbers shown at the top of the report / dashboard."""
    income = _income(df)["Amount"].sum()
    expense = _expenses(df)["Amount"].sum()
    savings = income - expense
    n_months = max(df["Month"].nunique(), 1)
    return {
        "total_income": float(income),
        "total_expense": float(expense),
        "net_savings": float(savings),
        "savings_rate_pct": float(savings / income * 100) if income else 0.0,
        "avg_monthly_expense": float(expense / n_months),
        "avg_monthly_income": float(income / n_months),
        "n_transactions": int(len(df)),
        "n_months": int(n_months),
    }


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Total, share, count and average per expense category."""
    exp = _expenses(df)
    out = (exp.groupby("Category")["Amount"]
           .agg(Total="sum", Transactions="count", Average="mean")
           .sort_values("Total", ascending=False))
    out["Share_%"] = (out["Total"] / out["Total"].sum() * 100).round(1)
    return out.round(1).reset_index()


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Income, expense, savings and savings-rate per month (+ month-on-month change)."""
    inc = _income(df).groupby("Month")["Amount"].sum().rename("Income")
    exp = _expenses(df).groupby("Month")["Amount"].sum().rename("Expense")
    out = pd.concat([inc, exp], axis=1).fillna(0.0).sort_index()
    out["Savings"] = out["Income"] - out["Expense"]
    out["Savings_Rate_%"] = np.where(out["Income"] > 0, out["Savings"] / out["Income"] * 100, 0.0)
    out["Expense_MoM_%"] = out["Expense"].pct_change() * 100
    return out.round(1).reset_index()


def category_month_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Rows = category, columns = month, values = spend (used for the heatmap)."""
    return (_expenses(df).pivot_table(index="Category", columns="Month", values="Amount",
                                      aggfunc="sum", fill_value=0))


def weekday_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Average DAILY discretionary spend per weekday (fixed bills excluded, so habits show up)."""
    from src.config import FIXED_CATEGORIES, WEEKDAY_ORDER
    exp = _expenses(df)
    exp = exp[~exp["Category"].isin(FIXED_CATEGORIES)]
    n_days = (df.groupby("Weekday")["Date"].nunique()).reindex(WEEKDAY_ORDER)   # how many Mondays etc.
    tot = exp.groupby("Weekday")["Amount"].sum().reindex(WEEKDAY_ORDER)
    cnt = exp.groupby("Weekday")["Amount"].count().reindex(WEEKDAY_ORDER)
    out = pd.DataFrame({"Total": tot, "Transactions": cnt, "Avg_Per_Day": tot / n_days})
    return out.round(1).reset_index().rename(columns={"index": "Weekday"})


def payment_summary(df: pd.DataFrame) -> pd.DataFrame:
    out = (_expenses(df).groupby("Payment_Method")["Amount"]
           .agg(Total="sum", Transactions="count").sort_values("Total", ascending=False))
    out["Share_%"] = (out["Total"] / out["Total"].sum() * 100).round(1)
    return out.round(1).reset_index()


def budget_check(df: pd.DataFrame, budgets: dict = None) -> pd.DataFrame:
    """Compare each month's category spend with its monthly budget.
    Returns ONLY the breaches (overspending alerts), worst first."""
    budgets = budgets or BUDGETS
    m = (_expenses(df).groupby(["Month", "Category"])["Amount"].sum().reset_index(name="Spent"))
    m["Budget"] = m["Category"].map(budgets)
    m = m.dropna(subset=["Budget"])
    m["Over_By"] = m["Spent"] - m["Budget"]
    m["Over_%"] = m["Over_By"] / m["Budget"] * 100
    alerts = m[m["Over_By"] > 0].sort_values("Over_%", ascending=False)
    return alerts.round(1).reset_index(drop=True)


def budget_vs_actual(df: pd.DataFrame, budgets: dict = None) -> pd.DataFrame:
    """Average monthly spend per category vs budget."""
    budgets = budgets or BUDGETS
    n_months = max(df["Month"].nunique(), 1)
    spent = _expenses(df).groupby("Category")["Amount"].sum() / n_months
    out = pd.DataFrame({"Avg_Monthly_Spend": spent})
    out["Budget"] = pd.Series(budgets)
    out = out.dropna(subset=["Budget"])
    out["Used_%"] = out["Avg_Monthly_Spend"] / out["Budget"] * 100
    return out.sort_values("Used_%", ascending=False).round(1).reset_index().rename(columns={"index": "Category"})


def detect_anomalies(df: pd.DataFrame, k: float = 3.0, min_count: int = 8) -> pd.DataFrame:
    """Flag unusually large single expenses inside each category.
    Rule: amount > Q3 + k * IQR of that category (k=3 -> 'extreme' outliers)."""
    exp = _expenses(df)
    flagged = []
    for cat, g in exp.groupby("Category"):
        if len(g) < min_count:
            continue
        q1, q3 = g["Amount"].quantile([0.25, 0.75])
        limit = q3 + k * (q3 - q1)
        hit = g[g["Amount"] > limit]
        if len(hit) and (q3 - q1) > 0:
            flagged.append(hit.assign(Threshold=round(limit, 0)))
    if not flagged:
        return pd.DataFrame(columns=["Date", "Category", "Description", "Amount", "Threshold"])
    out = pd.concat(flagged).sort_values("Amount", ascending=False)
    return out[["Date", "Category", "Description", "Amount", "Threshold"]].reset_index(drop=True)


def forecast_next_month(df: pd.DataFrame) -> dict:
    """Very simple, explainable forecast of next month's total expense.
    Two methods: linear trend (np.polyfit) and 3-month moving average.
    Returns a dict with the monthly history and both predictions."""
    monthly = (_expenses(df).groupby("Month")["Amount"].sum().sort_index())
    y = monthly.values.astype(float)
    x = np.arange(len(y))
    if len(y) < 3:
        return {"history": monthly, "trend": float(y.mean()), "moving_avg": float(y.mean()),
                "next_month": None, "slope": 0.0}
    slope, intercept = np.polyfit(x, y, 1)
    trend_pred = float(slope * len(y) + intercept)
    ma_pred = float(y[-3:].mean())
    next_month = (pd.Period(monthly.index[-1], "M") + 1).strftime("%Y-%m")
    return {"history": monthly, "trend": max(trend_pred, 0.0), "moving_avg": ma_pred,
            "next_month": next_month, "slope": float(slope)}


def category_forecast(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """Per-category forecast = average of the last `window` months (simple & explainable)."""
    pv = category_month_matrix(df)
    last = pv.iloc[:, -window:]
    out = pd.DataFrame({"Forecast_Next_Month": last.mean(axis=1)})
    out["Budget"] = pd.Series(BUDGETS)
    out["Risk"] = np.where(out["Forecast_Next_Month"] > out["Budget"], "Over budget", "OK")
    return out.sort_values("Forecast_Next_Month", ascending=False).round(0).reset_index()
```

### `src/visualize.py` - charts
```python
"""Static charts (matplotlib + seaborn) saved to the images/ folder."""
import matplotlib

matplotlib.use("Agg")  # works without a display (servers, CI); charts are saved as PNG
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from src import analysis as an
from src.config import BUDGETS, IMAGE_DIR

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = sns.color_palette("Set2")
INR = "\u20b9"


def _save(fig, name):
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGE_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def category_bar(df):
    cs = an.category_summary(df).sort_values("Total")
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.barh(cs["Category"], cs["Total"], color=PALETTE[0])
    for y, v in enumerate(cs["Total"]):
        ax.text(v, y, f"  {INR}{v:,.0f}", va="center", fontsize=9)
    ax.set_title("Total Expense by Category")
    ax.set_xlabel(f"Total spent ({INR})")
    ax.set_xlim(0, cs["Total"].max() * 1.18)
    return _save(fig, "01_category_spending.png")


def expense_pie(df, min_share=3.0):
    cs = an.category_summary(df)
    big = cs[cs["Share_%"] >= min_share]
    other = cs[cs["Share_%"] < min_share]["Total"].sum()
    labels = list(big["Category"]) + (["Other"] if other > 0 else [])
    values = list(big["Total"]) + ([other] if other > 0 else [])
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=140, colors=sns.color_palette("Set3"),
           wedgeprops={"edgecolor": "white"})
    ax.set_title("Expense Distribution by Category")
    return _save(fig, "02_expense_pie.png")


def monthly_income_vs_expense(df):
    ms = an.monthly_summary(df)
    x = np.arange(len(ms))
    w = 0.38
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(x - w / 2, ms["Income"], w, label="Income", color="#4CAF50")
    ax.bar(x + w / 2, ms["Expense"], w, label="Expense", color="#E57373")
    ax.plot(x, ms["Savings"], marker="o", color="#1565C0", label="Savings")
    ax.set_xticks(x)
    ax.set_xticklabels(ms["Month"], rotation=45)
    ax.set_ylabel(f"Amount ({INR})")
    ax.set_title("Monthly Income vs Expense vs Savings")
    ax.legend()
    return _save(fig, "03_monthly_income_vs_expense.png")


def savings_rate(df):
    ms = an.monthly_summary(df)
    fig, ax = plt.subplots(figsize=(10, 4))
    colors = ["#4CAF50" if v >= 20 else "#FFB74D" if v >= 0 else "#E57373" for v in ms["Savings_Rate_%"]]
    ax.bar(ms["Month"], ms["Savings_Rate_%"], color=colors)
    ax.axhline(20, ls="--", color="grey", label="20% target")
    ax.set_ylabel("Savings rate (%)")
    ax.set_title("Monthly Savings Rate")
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45)
    return _save(fig, "04_savings_rate.png")


def weekday_spending(df):
    ws = an.weekday_summary(df)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(ws["Weekday"], ws["Avg_Per_Day"], color=sns.color_palette("coolwarm", 7))
    ax.set_title("Average Daily Spending by Weekday (excl. rent, bills, subscriptions)")
    ax.set_ylabel(f"Avg spend per day ({INR})")
    plt.setp(ax.get_xticklabels(), rotation=30)
    return _save(fig, "05_weekday_spending.png")


def category_month_heatmap(df):
    pv = an.category_month_matrix(df)
    fig, ax = plt.subplots(figsize=(12, 5.5))
    sns.heatmap(pv, cmap="YlOrRd", annot=True, fmt=".0f", annot_kws={"size": 7}, linewidths=0.4, ax=ax,
                cbar_kws={"label": f"Spend ({INR})"})
    ax.set_title("Spending Heatmap: Category x Month")
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=45)
    return _save(fig, "06_category_month_heatmap.png")


def budget_vs_actual_chart(df):
    b = an.budget_vs_actual(df).sort_values("Used_%")
    y = np.arange(len(b))
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(y + 0.2, b["Budget"], 0.4, label="Budget", color="#B0BEC5")
    colors = ["#E57373" if u > 100 else "#4CAF50" for u in b["Used_%"]]
    ax.barh(y - 0.2, b["Avg_Monthly_Spend"], 0.4, label="Avg monthly spend", color=colors)
    ax.set_yticks(y)
    ax.set_yticklabels(b["Category"])
    ax.set_xlabel(f"{INR} per month")
    ax.set_title("Budget vs Actual (red = over budget)")
    ax.legend()
    return _save(fig, "07_budget_vs_actual.png")


def forecast_chart(df):
    f = an.forecast_next_month(df)
    hist = f["history"]
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(hist.index, hist.values, marker="o", color="#1565C0", label="Actual expense")
    if f["next_month"]:
        ax.plot([hist.index[-1], f["next_month"]], [hist.values[-1], f["trend"]],
                ls="--", marker="s", color="#E65100", label=f"Trend forecast ({INR}{f['trend']:,.0f})")
        ax.plot([hist.index[-1], f["next_month"]], [hist.values[-1], f["moving_avg"]],
                ls=":", marker="^", color="#2E7D32", label=f"3-mo average ({INR}{f['moving_avg']:,.0f})")
    ax.set_title("Monthly Expense and Next-Month Forecast")
    ax.set_ylabel(f"Expense ({INR})")
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45)
    return _save(fig, "08_forecast.png")


def payment_methods(df):
    ps = an.payment_summary(df)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(ps["Payment_Method"], ps["Total"], color=PALETTE[2])
    ax.set_title("Spending by Payment Method")
    ax.set_ylabel(f"Total ({INR})")
    return _save(fig, "09_payment_methods.png")


def summary_dashboard(df):
    """One-page 2x2 summary image: good hero picture for the README."""
    cs = an.category_summary(df).sort_values("Total")
    ms = an.monthly_summary(df)
    ws = an.weekday_summary(df)
    k = an.kpis(df)
    fig, axs = plt.subplots(2, 2, figsize=(15, 9))
    fig.suptitle(
        f"Expense Tracker Summary  |  Income {INR}{k['total_income']:,.0f}  |  Expense {INR}{k['total_expense']:,.0f}  "
        f"|  Savings rate {k['savings_rate_pct']:.1f}%", fontsize=14, fontweight="bold")
    axs[0, 0].barh(cs["Category"], cs["Total"], color=PALETTE[0])
    axs[0, 0].set_title("Spend by category")
    axs[0, 1].plot(ms["Month"], ms["Income"], marker="o", color="#4CAF50", label="Income")
    axs[0, 1].plot(ms["Month"], ms["Expense"], marker="o", color="#E57373", label="Expense")
    axs[0, 1].set_title("Monthly income vs expense")
    axs[0, 1].legend()
    plt.setp(axs[0, 1].get_xticklabels(), rotation=45)
    top = cs.tail(6)
    axs[1, 0].pie(top["Total"], labels=top["Category"], autopct="%1.0f%%", colors=sns.color_palette("Set3"))
    axs[1, 0].set_title("Top 6 categories")
    axs[1, 1].bar(ws["Weekday"], ws["Avg_Per_Day"], color=sns.color_palette("coolwarm", 7))
    axs[1, 1].set_title("Avg daily spend by weekday")
    plt.setp(axs[1, 1].get_xticklabels(), rotation=30)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return _save(fig, "10_summary_dashboard.png")


def make_all(df):
    fns = [category_bar, expense_pie, monthly_income_vs_expense, savings_rate, weekday_spending,
           category_month_heatmap, budget_vs_actual_chart, forecast_chart, payment_methods, summary_dashboard]
    return [fn(df) for fn in fns]
```

### `src/insights.py` - insights and optional local AI
```python
"""Turn numbers into plain-English insights (rule-based), plus an OPTIONAL local-LLM
summary using Ollama (free, runs on your laptop, no API key)."""
import json
import urllib.request

from src import analysis as an

INR = "\u20b9"


def build_insights(df) -> list:
    k = an.kpis(df)
    cs = an.category_summary(df)
    ms = an.monthly_summary(df)
    ws = an.weekday_summary(df)
    alerts = an.budget_check(df)
    anomalies = an.detect_anomalies(df)
    fc = an.forecast_next_month(df)
    out = []

    # 1. overall health
    rate = k["savings_rate_pct"]
    verdict = "healthy (above the 20% rule of thumb)" if rate >= 20 else "below the recommended 20%"
    out.append(f"Overall savings rate is {rate:.1f}% - {verdict}. "
               f"Income {INR}{k['total_income']:,.0f} vs expense {INR}{k['total_expense']:,.0f}.")

    # 2. biggest category (and biggest *discretionary* one)
    top = cs.iloc[0]
    out.append(f"{top['Category']} is the largest expense: {INR}{top['Total']:,.0f} ({top['Share_%']}% of all spending).")
    fixed = {"Rent", "Bills", "Subscriptions"}
    disc = cs[~cs["Category"].isin(fixed)].iloc[0]
    out.append(f"Biggest flexible (discretionary) category is {disc['Category']} at {INR}{disc['Total']:,.0f} "
               f"- the best place to look for savings.")

    # 3. months
    worst = ms.loc[ms["Expense"].idxmax()]
    best = ms.loc[ms["Savings"].idxmax()]
    out.append(f"Highest-spend month: {worst['Month']} ({INR}{worst['Expense']:,.0f}). "
               f"Best savings month: {best['Month']} ({INR}{best['Savings']:,.0f}).")
    neg = ms[ms["Savings"] < 0]
    if len(neg):
        out.append(f"Warning: expenses exceeded income in {len(neg)} month(s): {', '.join(neg['Month'])}.")

    # 4. weekday pattern
    wk = ws.set_index("Weekday")["Avg_Per_Day"]
    out.append(f"Day-to-day spending peaks on {wk.idxmax()} (avg {INR}{wk.max():,.0f}/day) and is lowest on "
               f"{wk.idxmin()} (avg {INR}{wk.min():,.0f}/day).")

    # 5. budget alerts
    if len(alerts):
        counts = alerts["Category"].value_counts()
        cat = counts.index[0]
        out.append(f"Budget breached {len(alerts)} times in total; {cat} is the repeat offender ({counts.iloc[0]} months).")
        w = alerts.iloc[0]
        out.append(f"Worst single breach: {w['Category']} in {w['Month']} - {INR}{w['Spent']:,.0f} against a "
                   f"budget of {INR}{w['Budget']:,.0f} ({w['Over_%']:.0f}% over).")
    else:
        out.append("No category exceeded its monthly budget.")

    # 6. anomalies
    if len(anomalies):
        a = anomalies.iloc[0]
        out.append(f"{len(anomalies)} unusually large expense(s) detected; biggest: {a['Description']} "
                   f"({INR}{a['Amount']:,.0f}, {a['Category']}).")

    # 7. forecast
    if fc["next_month"]:
        out.append(f"Forecast for {fc['next_month']}: about {INR}{fc['moving_avg']:,.0f} (3-month average) to "
                   f"{INR}{fc['trend']:,.0f} (linear trend). Keep a buffer for seasonal spikes.")
    return out


def write_report(df, path, ai_text=None) -> str:
    k = an.kpis(df)
    lines = ["# Expense Insights Report", "",
             f"- Period: {df['Date'].min().date()} to {df['Date'].max().date()} ({k['n_months']} months)",
             f"- Transactions: {k['n_transactions']}",
             f"- Total income: {INR}{k['total_income']:,.0f}",
             f"- Total expense: {INR}{k['total_expense']:,.0f}",
             f"- Net savings: {INR}{k['net_savings']:,.0f} ({k['savings_rate_pct']:.1f}%)", "",
             "## Key insights", ""]
    lines += [f"{i}. {t}" for i, t in enumerate(build_insights(df), 1)]
    if ai_text:
        lines += ["", "## AI-generated advice (local LLM)", "", ai_text]
    text = "\n".join(lines) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text


def ai_summary(df, model="llama3.2", host="http://localhost:11434"):
    """OPTIONAL: ask a local Ollama model for budgeting advice. Returns None if Ollama isn't running."""
    facts = "\n".join(f"- {t}" for t in build_insights(df))
    prompt = ("You are a friendly personal-finance coach. Based ONLY on these facts, give 4 short, "
              "practical tips to improve savings. Do not invent numbers.\n\nFACTS:\n" + facts)
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(f"{host}/api/generate", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["response"].strip()
    except Exception as e:  # Ollama not installed / not running / model missing
        print(f"[AI summary skipped: {e}]")
        return None
```

### `main.py` - run everything
```python
"""Run the full Expense Tracker pipeline:

    python main.py              # generate data (if missing) -> clean -> analyse -> charts -> report
    python main.py --regenerate # force a fresh synthetic dataset
    python main.py --ai         # also add AI advice from a local Ollama model (optional)
"""
import argparse

import pandas as pd

from src import analysis as an
from src import insights, visualize
from src.clean_data import clean, save_clean
from src.config import OUTPUT_DIR, RAW_FILE, USER_FILE
from src.generate_data import create_raw_file


def load_raw() -> pd.DataFrame:
    """Raw file + any rows the user added through the dashboard form."""
    df = pd.read_csv(RAW_FILE)
    if USER_FILE.exists():
        df = pd.concat([df, pd.read_csv(USER_FILE)], ignore_index=True)
    return df


def main():
    p = argparse.ArgumentParser(description="Expense Tracker using Data Science")
    p.add_argument("--regenerate", action="store_true", help="create a fresh synthetic dataset")
    p.add_argument("--ai", action="store_true", help="add local-LLM (Ollama) advice to the report")
    p.add_argument("--model", default="llama3.2", help="Ollama model name (default: llama3.2)")
    args = p.parse_args()

    print("=" * 60)
    print(" EXPENSE TRACKER APP USING DATA SCIENCE")
    print("=" * 60)

    # Phase 1-2: data
    if args.regenerate or not RAW_FILE.exists():
        raw = create_raw_file()
        print(f"[1/6] Synthetic dataset created: {RAW_FILE.name} ({len(raw)} rows)")
    else:
        print(f"[1/6] Using existing dataset: {RAW_FILE.name}")

    # Phase 3: cleaning
    df, report = clean(load_raw())
    save_clean(df)
    print(f"[2/6] Cleaning done: {report}")

    # Phase 4-6: analysis
    OUTPUT_DIR.mkdir(exist_ok=True)
    an.category_summary(df).to_csv(OUTPUT_DIR / "category_summary.csv", index=False)
    an.monthly_summary(df).to_csv(OUTPUT_DIR / "monthly_summary.csv", index=False)
    an.budget_check(df).to_csv(OUTPUT_DIR / "overspending_alerts.csv", index=False)
    an.detect_anomalies(df).to_csv(OUTPUT_DIR / "anomalies.csv", index=False)
    an.category_forecast(df).to_csv(OUTPUT_DIR / "category_forecast.csv", index=False)
    print("[3/6] Analysis tables saved to outputs/")

    k = an.kpis(df)
    print(f"      Income  : Rs {k['total_income']:>10,.0f}")
    print(f"      Expense : Rs {k['total_expense']:>10,.0f}")
    print(f"      Savings : Rs {k['net_savings']:>10,.0f}  ({k['savings_rate_pct']:.1f}%)")
    print("\n      Top categories:")
    print(an.category_summary(df).head(5).to_string(index=False))
    print("\n      Worst budget breaches:")
    print(an.budget_check(df).head(5).to_string(index=False))

    # Phase 7: charts
    paths = visualize.make_all(df)
    print(f"\n[4/6] {len(paths)} charts saved to images/")

    # Phase 8: insights
    ai_text = insights.ai_summary(df, model=args.model) if args.ai else None
    text = insights.write_report(df, OUTPUT_DIR / "insights_report.md", ai_text)
    print("[5/6] Insights report saved to outputs/insights_report.md\n")
    print(text)
    print("[6/6] Done. Launch the dashboard with:  streamlit run app.py")


if __name__ == "__main__":
    main()
```

### `app.py` - Streamlit dashboard
```python
"""Streamlit dashboard for the Expense Tracker.   Run:  streamlit run app.py"""
import datetime as dt

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import analysis as an
from src import insights
from src.clean_data import clean
from src.config import BUDGETS, RAW_FILE, USER_FILE
from src.generate_data import create_raw_file

INR = "\u20b9"
INDIGO, GREEN, ROSE, AMBER, SKY, VIOLET, TEAL, PINK = (
    "#6366F1", "#10B981", "#F43F5E", "#F59E0B", "#0EA5E9", "#8B5CF6", "#14B8A6", "#EC4899")
COLORWAY = [INDIGO, TEAL, AMBER, ROSE, SKY, VIOLET, GREEN, PINK, "#64748B", "#A3E635", "#FB923C"]

st.set_page_config(page_title="Expense Tracker", page_icon="\U0001F4B8", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 3.8rem; padding-bottom: 3rem; max-width: 1400px;}
html, body, [class*="css"] {font-family: 'Inter', 'Segoe UI', sans-serif;}

.hero {background: linear-gradient(120deg, #4F46E5 0%, #7C3AED 55%, #EC4899 120%);
       border-radius: 20px; padding: 28px 34px; color: white; margin-bottom: 22px;
       box-shadow: 0 10px 30px rgba(99,102,241,.35);}
.hero h1 {margin: 0; font-size: 2rem; font-weight: 800; color: white; padding: 0;}
.hero p {margin: 6px 0 0 0; opacity: .9; font-size: 1rem;}
.chip {display:inline-block; background: rgba(255,255,255,.18); border-radius: 999px;
       padding: 4px 14px; font-size: .8rem; margin: 12px 8px 0 0; backdrop-filter: blur(4px);}

.kpi {background: white; border-radius: 16px; padding: 18px 20px; border: 1px solid #E8EAF3;
      box-shadow: 0 2px 10px rgba(30,41,59,.05); border-left: 6px solid var(--c); height: 100%;}
.kpi .lbl {font-size: .78rem; text-transform: uppercase; letter-spacing: .06em; color: #64748B; font-weight: 600;}
.kpi .val {font-size: 1.85rem; font-weight: 800; color: #0F172A; margin: 4px 0 2px 0;}
.kpi .sub {font-size: .82rem; font-weight: 600;}
.up {color: #10B981;} .down {color: #F43F5E;} .flat {color: #64748B;}

.section {font-size: 1.15rem; font-weight: 700; color: #0F172A; margin: 6px 0 2px 0;}
.insight {background: white; border: 1px solid #E8EAF3; border-left: 5px solid #6366F1;
          border-radius: 12px; padding: 12px 16px; margin-bottom: 10px; color: #1E293B;
          box-shadow: 0 1px 6px rgba(30,41,59,.04); font-size: .95rem;}
.bud {background: white; border: 1px solid #E8EAF3; border-radius: 14px; padding: 14px 16px; margin-bottom: 12px;}
.bud .top {display:flex; justify-content: space-between; font-size: .9rem; font-weight: 600; color: #1E293B;}
.bud .track {background: #EEF0F7; border-radius: 999px; height: 10px; margin-top: 8px; overflow: hidden;}
.bud .fill {height: 10px; border-radius: 999px;}
.bud .meta {font-size: .76rem; color: #64748B; margin-top: 6px;}

div[data-testid="stVerticalBlockBorderWrapper"] {border-radius: 16px;}
.stTabs [data-baseweb="tab-list"] {gap: 8px; background: transparent;}
.stTabs [data-baseweb="tab"] {background: white; border-radius: 10px; padding: 10px 20px; height: auto;
      border: 1px solid #E8EAF3; font-weight: 600;}
.stTabs [aria-selected="true"] {background: #6366F1 !important; color: white !important; border-color: #6366F1;}
.stTabs [aria-selected="true"] p {color: white !important;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {display: none;}
section[data-testid="stSidebar"] {border-right: 1px solid #E8EAF3;}
.stButton > button, .stFormSubmitButton > button {border-radius: 10px; font-weight: 600;}
</style>
""", unsafe_allow_html=True)


def money(v):
    return f"{INR}{v:,.0f}"


def style(fig, height=380, legend=True):
    """Apply one consistent, modern look to every Plotly chart."""
    fig.update_layout(
        template="plotly_white", colorway=COLORWAY, height=height,
        margin=dict(l=10, r=10, t=50, b=10), font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        title=dict(font=dict(size=16, color="#0F172A"), x=0.01),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", hoverlabel=dict(font_size=13),
        showlegend=legend, legend=dict(orientation="h", y=-0.18, x=0))
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0")
    fig.update_yaxes(gridcolor="#EEF0F7", zeroline=False)
    return fig


def kpi(label, value, sub, color, cls="flat"):
    return (f'<div class="kpi" style="--c:{color}"><div class="lbl">{label}</div>'
            f'<div class="val">{value}</div><div class="sub {cls}">{sub}</div></div>')


def delta_text(cur, prev, good_when_up=True):
    if prev in (0, None) or pd.isna(prev):
        return "no previous month", "flat"
    pct = (cur - prev) / prev * 100
    up = pct >= 0
    good = up if good_when_up else not up
    return f"{'▲' if up else '▼'} {abs(pct):.1f}% vs previous month", ("up" if good else "down")


# ------------------------------------------------------------------ data
@st.cache_data(show_spinner=False)
def load_data(_version: float) -> pd.DataFrame:
    """Raw file (+ rows added via the form) -> cleaned DataFrame."""
    if not RAW_FILE.exists():
        create_raw_file()
    raw = pd.read_csv(RAW_FILE)
    if USER_FILE.exists():
        raw = pd.concat([raw, pd.read_csv(USER_FILE)], ignore_index=True)
    df, _ = clean(raw)
    return df


if "version" not in st.session_state:
    st.session_state.version = 0.0
df_all = load_data(st.session_state.version)

# ------------------------------------------------------------------ sidebar
st.sidebar.markdown("## \U0001F4B8 Expense Tracker")
st.sidebar.caption("Filter your data or add a new transaction")

with st.sidebar.expander("\u2795 Add a transaction", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        d = st.date_input("Date", dt.date.today())
        t = st.selectbox("Type", ["Expense", "Income"])
        c = st.selectbox("Category", sorted(df_all["Category"].unique()))
        desc = st.text_input("Description")
        amt = st.number_input("Amount (Rs)", min_value=1.0, step=50.0)
        pm = st.selectbox("Payment method", ["UPI", "Card", "Cash", "Net Banking", "Bank Transfer"])
        if st.form_submit_button("Save transaction", width="stretch"):
            row = pd.DataFrame([{"Date": d, "Category": c, "Description": desc, "Amount": amt,
                                 "Type": t, "Payment_Method": pm}])
            row.to_csv(USER_FILE, mode="a", header=not USER_FILE.exists(), index=False)
            st.session_state.version += 1
            st.rerun()

st.sidebar.markdown("### \U0001F50D Filters")
min_d, max_d = df_all["Date"].min().date(), df_all["Date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_d, max_d), min_value=min_d, max_value=max_d)
start, end = (date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_d, max_d))
sel_cats = st.sidebar.multiselect("Categories", sorted(df_all["Category"].unique()),
                                  default=sorted(df_all["Category"].unique()))
sel_pm = st.sidebar.multiselect("Payment method", sorted(df_all["Payment_Method"].unique()),
                                default=sorted(df_all["Payment_Method"].unique()))

df = df_all[(df_all["Date"].dt.date >= start) & (df_all["Date"].dt.date <= end)
            & df_all["Category"].isin(sel_cats) & df_all["Payment_Method"].isin(sel_pm)]

# ------------------------------------------------------------------ hero
st.markdown(f"""
<div class="hero">
  <h1>\U0001F4B8 Expense Tracker Dashboard</h1>
  <p>See where your money goes, catch overspending early and plan the next month.</p>
  <span class="chip">\U0001F4C5 {start:%d %b %Y} - {end:%d %b %Y}</span>
  <span class="chip">\U0001F9FE {len(df):,} transactions</span>
  <span class="chip">\U0001F916 Anomaly detection + forecast</span>
</div>
""", unsafe_allow_html=True)

if df.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# ------------------------------------------------------------------ KPI cards
k = an.kpis(df)
ms = an.monthly_summary(df)
last = ms.iloc[-1]
prev = ms.iloc[-2] if len(ms) > 1 else None
inc_t, inc_c = delta_text(last["Income"], prev["Income"] if prev is not None else None, True)
exp_t, exp_c = delta_text(last["Expense"], prev["Expense"] if prev is not None else None, False)
rate = k["savings_rate_pct"]
rate_c, rate_t = (GREEN, "Healthy: above the 20% target") if rate >= 20 else (AMBER, "Below the 20% target")

cols = st.columns(4)
cols[0].markdown(kpi("Total income", money(k["total_income"]), inc_t, GREEN, inc_c), unsafe_allow_html=True)
cols[1].markdown(kpi("Total expense", money(k["total_expense"]), exp_t, ROSE, exp_c), unsafe_allow_html=True)
cols[2].markdown(kpi("Net savings", money(k["net_savings"]),
                     f"Avg {money(k['net_savings'] / k['n_months'])} per month", INDIGO), unsafe_allow_html=True)
cols[3].markdown(kpi("Savings rate", f"{rate:.1f}%", rate_t, rate_c, "up" if rate >= 20 else "flat"),
                 unsafe_allow_html=True)
st.write("")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["\U0001F4CA Overview", "\U0001F4C8 Trends", "\U0001F3AF Budget",
                                        "\U0001F916 AI Insights", "\U0001F5C3\uFE0F Data"])

# ------------------------------------------------------------------ Overview
with tab1:
    cs = an.category_summary(df)
    l, r = st.columns([1.15, 1])
    with l.container(border=True):
        fig = px.bar(cs.sort_values("Total"), x="Total", y="Category", orientation="h",
                     color="Total", color_continuous_scale=["#C7D2FE", "#6366F1", "#4338CA"],
                     title="Where the money goes", text_auto=",.0f")
        fig.update_coloraxes(showscale=False)
        fig.update_traces(textposition="outside", cliponaxis=False)
        st.plotly_chart(style(fig, 430, False), width="stretch")
    with r.container(border=True):
        fig = px.pie(cs, names="Category", values="Total", hole=0.62, title="Expense distribution")
        fig.update_traces(textposition="outside", textinfo="percent+label", marker=dict(line=dict(color="white", width=2)))
        fig.add_annotation(text=f"<b>{money(cs['Total'].sum())}</b><br>total spend", showarrow=False, font=dict(size=15))
        st.plotly_chart(style(fig, 430, False), width="stretch")

    l2, r2 = st.columns(2)
    with l2.container(border=True):
        ws = an.weekday_summary(df)
        fig = px.bar(ws, x="Weekday", y="Avg_Per_Day", color="Avg_Per_Day",
                     color_continuous_scale=["#99F6E4", "#14B8A6", "#F43F5E"],
                     title="Average daily spend by weekday (excl. rent, bills, subscriptions)")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style(fig, 360, False), width="stretch")
    with r2.container(border=True):
        ps = an.payment_summary(df)
        fig = px.pie(ps, names="Payment_Method", values="Total", hole=0.55, title="Payment methods")
        fig.update_traces(marker=dict(line=dict(color="white", width=2)))
        st.plotly_chart(style(fig, 360), width="stretch")

# ------------------------------------------------------------------ Trends
with tab2:
    with st.container(border=True):
        fig = go.Figure()
        fig.add_bar(x=ms["Month"], y=ms["Income"], name="Income", marker_color=GREEN, opacity=.85)
        fig.add_bar(x=ms["Month"], y=ms["Expense"], name="Expense", marker_color=ROSE, opacity=.85)
        fig.add_scatter(x=ms["Month"], y=ms["Savings"], name="Savings", mode="lines+markers",
                        line=dict(color=INDIGO, width=3), marker=dict(size=8))
        fig.update_layout(barmode="group", title="Monthly income, expense and savings")
        st.plotly_chart(style(fig, 400), width="stretch")
    a, b = st.columns([1, 1.3])
    with a.container(border=True):
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=rate, number=dict(suffix="%", font=dict(size=40)),
            title=dict(text="Overall savings rate"),
            gauge=dict(axis=dict(range=[min(-10, rate - 5), 60]), bar=dict(color=INDIGO, thickness=0.28),
                       steps=[dict(range=[-100, 0], color="#FECDD3"), dict(range=[0, 20], color="#FDE68A"),
                              dict(range=[20, 100], color="#A7F3D0")],
                       threshold=dict(line=dict(color="#0F172A", width=3), value=20))))
        st.plotly_chart(style(fig, 340, False), width="stretch")
        st.caption("Black line = 20% rule-of-thumb target.")
    with b.container(border=True):
        pv = an.category_month_matrix(df)
        fig = px.imshow(pv, aspect="auto", color_continuous_scale="YlOrRd", title="Category x month heatmap")
        fig.update_coloraxes(colorbar=dict(title=INR))
        st.plotly_chart(style(fig, 340, False), width="stretch")

# ------------------------------------------------------------------ Budget
with tab3:
    latest = df["Month"].max()
    st.markdown(f'<div class="section">Budget status for {latest} (latest month)</div>', unsafe_allow_html=True)
    spent = (df[(df["Type"] == "Expense") & (df["Month"] == latest)].groupby("Category")["Amount"].sum())
    cards = st.columns(2)
    for i, (cat, bud) in enumerate(BUDGETS.items()):
        s = float(spent.get(cat, 0))
        pct = s / bud * 100
        color = GREEN if pct < 80 else AMBER if pct <= 100 else ROSE
        tag = "On track" if pct < 80 else "Close to limit" if pct <= 100 else f"Over by {money(s - bud)}"
        cards[i % 2].markdown(
            f'<div class="bud"><div class="top"><span>{cat}</span><span>{money(s)} / {money(bud)}</span></div>'
            f'<div class="track"><div class="fill" style="width:{min(pct, 100):.0f}%;background:{color}"></div></div>'
            f'<div class="meta" style="color:{color}">{pct:.0f}% used - {tag}</div></div>', unsafe_allow_html=True)

    with st.container(border=True):
        bva = an.budget_vs_actual(df)
        fig = go.Figure()
        fig.add_bar(x=bva["Category"], y=bva["Budget"], name="Budget", marker_color="#CBD5E1")
        fig.add_bar(x=bva["Category"], y=bva["Avg_Monthly_Spend"], name="Avg monthly spend",
                    marker_color=[ROSE if u > 100 else TEAL for u in bva["Used_%"]])
        fig.update_layout(barmode="group", title="Budget vs average monthly spend (red = over budget)")
        st.plotly_chart(style(fig, 380), width="stretch")
    st.markdown('<div class="section">\u26A0\uFE0F Overspending alerts</div>', unsafe_allow_html=True)
    st.dataframe(an.budget_check(df), width="stretch", hide_index=True)

# ------------------------------------------------------------------ AI insights
with tab4:
    f = an.forecast_next_month(df)
    if f["next_month"]:
        m1, m2, m3 = st.columns(3)
        m1.markdown(kpi(f"Forecast {f['next_month']}", money(f["moving_avg"]), "3-month average", TEAL),
                    unsafe_allow_html=True)
        m2.markdown(kpi(f"Forecast {f['next_month']}", money(f["trend"]), "Linear trend", VIOLET),
                    unsafe_allow_html=True)
        m3.markdown(kpi("Anomalies found", str(len(an.detect_anomalies(df))), "Unusually large expenses", AMBER),
                    unsafe_allow_html=True)
        st.write("")
        with st.container(border=True):
            hist = f["history"]
            fig = go.Figure()
            fig.add_scatter(x=hist.index, y=hist.values, mode="lines+markers", name="Actual",
                            line=dict(color=INDIGO, width=3))
            fig.add_scatter(x=[hist.index[-1], f["next_month"]], y=[hist.values[-1], f["trend"]],
                            mode="lines+markers", name="Trend forecast", line=dict(color=VIOLET, dash="dash"))
            fig.add_scatter(x=[hist.index[-1], f["next_month"]], y=[hist.values[-1], f["moving_avg"]],
                            mode="lines+markers", name="3-month average", line=dict(color=TEAL, dash="dot"))
            fig.update_layout(title="Monthly expense and next-month forecast")
            st.plotly_chart(style(fig, 360), width="stretch")

    left, right = st.columns(2)
    with left:
        st.markdown('<div class="section">\U0001F4A1 Key insights</div>', unsafe_allow_html=True)
        for tip in insights.build_insights(df):
            st.markdown(f'<div class="insight">{tip}</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="section">\U0001F6A8 Unusually large expenses</div>', unsafe_allow_html=True)
        st.dataframe(an.detect_anomalies(df), width="stretch", hide_index=True)
        st.markdown('<div class="section">\U0001F52E Category forecast (next month)</div>', unsafe_allow_html=True)
        st.dataframe(an.category_forecast(df), width="stretch", hide_index=True)

    st.markdown('<div class="section">\U0001F9E0 Local AI coach</div>', unsafe_allow_html=True)
    if st.button("Ask the AI coach (needs Ollama running)", type="primary"):
        with st.spinner("Thinking..."):
            txt = insights.ai_summary(df)
        if txt:
            st.success(txt)
        else:
            st.info("Ollama not reachable. Start it with `ollama serve` and run `ollama pull llama3.2`.")

# ------------------------------------------------------------------ Data
with tab5:
    st.dataframe(df.sort_values("Date", ascending=False), width="stretch", hide_index=True)
    st.download_button("\u2B07\uFE0F Download filtered data (CSV)", df.to_csv(index=False), "filtered_expenses.csv",
                       type="primary")
```

### `tests/test_pipeline.py`
```python
"""Run with:  pytest -q"""
import pandas as pd

from src import analysis as an
from src.clean_data import clean
from src.generate_data import generate, make_messy


def _clean_df():
    df, _ = clean(make_messy(generate()))
    return df


def test_cleaning_removes_problems():
    df = _clean_df()
    assert df["Amount"].notna().all() and (df["Amount"] > 0).all()
    assert set(df["Type"]) <= {"Income", "Expense"}
    assert df["Category"].str.strip().eq(df["Category"]).all()
    assert not df.duplicated().any()


def test_kpis_consistent():
    k = an.kpis(_clean_df())
    assert abs(k["net_savings"] - (k["total_income"] - k["total_expense"])) < 1e-6


def test_budget_alerts_only_breaches():
    alerts = an.budget_check(_clean_df())
    assert (alerts["Over_By"] > 0).all()


def test_forecast_positive():
    f = an.forecast_next_month(_clean_df())
    assert f["moving_avg"] > 0 and f["next_month"] == "2026-10"


def test_clean_handles_rupee_symbol():
    raw = pd.DataFrame({"Date": ["2026-01-01"], "Category": [" food "], "Description": ["x"],
                        "Amount": ["\u20b91,200"], "Type": ["expense"], "Payment_Method": ["upi"]})
    df, _ = clean(raw)
    assert df.loc[0, "Amount"] == 1200 and df.loc[0, "Category"] == "Food" and df.loc[0, "Payment_Method"] == "UPI"
```

### `.gitignore`
```text
__pycache__/
*.pyc
.venv/
venv/
.ipynb_checkpoints/
.DS_Store
# rows typed into the dashboard are personal data - keep them out of GitHub
data/user_entries.csv
```

(`src/__init__.py` is an empty file. The notebook, README, LICENSE and the optional ESP32 sketch are in the project folder.)

---

## 8️⃣ Virtual Simulation

**How expenses are generated** (`generate_data.py`): for every day in 12 months the program draws random transactions per category. The count follows a Poisson distribution (typical for "events per day") and the amount a normal distribution around a category-specific average.

| Category | Pattern built in |
|---|---|
| Food | ~0.85 transactions/day, ₹230 average, **×1.5 on weekends** |
| Transport | Frequent, small amounts |
| Shopping | **×1.8-1.9 in Oct-Nov (festive season)**, ×1.3 in Jan |
| Entertainment | ×1.5 in December, ×1.3 in May |
| Rent / Bills / Subscriptions | Fixed dates every month; electricity higher in Apr-Jun |
| Travel | Trips in May, Jun, Dec |
| Education | Courses/exam fees in Oct, Jan, Apr, Jul |
| Income | ₹35,000 stipend on the 1st + irregular freelance AI projects (₹4k-14k) |
| One-offs | Laptop repair ₹18,500 (Feb), flights ₹14,500 (Dec), dental ₹9,000 (Jun) |

**How trends appear:** festive and travel multipliers create spikes in Oct-Nov, Dec and Jun; weekend multipliers create the Saturday peak; the one-offs become anomalies.

**How overspending is detected:** `budget_check()` sums each category per month and compares it with `BUDGETS` in `config.py`. Any month above budget becomes an alert with `Over_By` and `Over_%`. Month-level overspending is detected when Expense > Income (savings below zero). Anomalies use the IQR rule: a single expense above Q3 + 3×IQR of its category is flagged.

**Step-by-step run:**
1. `generate_data.py` creates 732 rows with realistic patterns
2. `make_messy()` adds duplicates, blank amounts/categories, ₹ symbols and odd casing
3. `clean()` removes 10 duplicates and 7 invalid rows → 715 clean rows
4. Feature engineering adds `Month`, `Weekday`, `Is_Weekend`
5. `analysis.py` builds KPIs, category/monthly/weekday tables
6. Budget check finds 24 breaches; anomaly detector flags 4 expenses
7. Forecast predicts October 2026 at roughly ₹31.7k-₹33.3k
8. `visualize.py` saves 10 charts; `insights.py` writes the report
9. `streamlit run app.py` shows it all interactively

**Proof to save:** terminal output of `python main.py`, the 10 charts, `insights_report.md`, dashboard screenshots, green `pytest` result, GitHub commit history.

---

## 9️⃣ How to Run the Project

```bash
python main.py                 # full pipeline
python main.py --regenerate    # brand-new synthetic data
python main.py --ai            # + local LLM advice (needs Ollama)
streamlit run app.py           # dashboard at http://localhost:8501
pytest -q                      # 5 tests should pass
```

**Expected terminal output (abridged):**
```
[1/6] Synthetic dataset created: raw_expenses.csv (732 rows)
[2/6] Cleaning done: {'rows_in': 732, 'duplicates_removed': 10, 'invalid_rows_removed': 7, ... 'rows_out': 715}
      Income  : Rs    555,835
      Expense : Rs    425,621
      Savings : Rs    130,214  (23.4%)
[4/6] 10 charts saved to images/
[5/6] Insights report saved to outputs/insights_report.md
```

**Expected files:** 6 files in `outputs/`, 10 PNGs in `images/`, `cleaned_expenses.csv` in `data/`.

**Using your own data:** replace `data/raw_expenses.csv` with a CSV that has columns `Date, Category, Description, Amount, Type, Payment_Method` (Type = Income/Expense), then run `python main.py` (without `--regenerate`).

**Optional local AI coach:** install Ollama, run `ollama pull llama3.2`, then `python main.py --ai` or click the button in the dashboard's AI Insights tab. It is free, offline and your data never leaves your laptop.

---

## 🔟 GitHub Upload Steps

1. Create an account at github.com → **New repository**.
2. **Repo name:** `Expense-Tracker-App-Data-Science`
3. **Description:** `End-to-end expense analytics in Python: synthetic data, cleaning, budget alerts, anomaly detection, forecasting and a Streamlit dashboard.`
4. **Topics/tags:** `data-science` `python` `pandas` `streamlit` `data-analysis` `data-visualization` `expense-tracker` `personal-finance` `fintech` `portfolio-project` `forecasting` `ollama`
5. Keep it **Public**; do not tick "Add README" (you already have one).
6. In the project folder:

```bash
git init
git add .gitignore requirements.txt
git commit -m "chore: project setup and dependencies"
git add src/generate_data.py src/config.py data/
git commit -m "feat: add synthetic expense data generator"
git add src/clean_data.py
git commit -m "feat: add data cleaning and feature engineering"
git add src/analysis.py
git commit -m "feat: add category, monthly, budget, anomaly and forecast analysis"
git add src/visualize.py images/
git commit -m "feat: add visualizations"
git add src/insights.py main.py outputs/
git commit -m "feat: add insights report and pipeline entry point"
git add app.py
git commit -m "feat: add Streamlit dashboard"
git add tests/ notebooks/ hardware/ LICENSE
git commit -m "test: add unit tests and walkthrough notebook"
git add README.md docs/
git commit -m "docs: add README and project guide"

git branch -M main
git remote add origin https://github.com/<your-username>/Expense-Tracker-App-Data-Science.git
git push -u origin main
```

7. **Deploy free (optional):** share.streamlit.io → connect the repo → main file `app.py` → Deploy. Paste the live link at the top of your README and in your resume.

**Commit message style:** `feat:` new feature, `fix:` bug fix, `docs:` documentation, `test:` tests, `chore:` setup. Small, meaningful commits spread over several days look far better than one big upload.

---

## 1️⃣1️⃣ README.md

The complete, ready-to-use README is in the project root (`README.md`). It contains the overview, problem, solution, features, tech stack, structure, how to run, results from this synthetic dataset, screenshots, future improvements and license. Before pushing, replace `<your-username>` and add your Streamlit link and dashboard screenshots.

---

## 1️⃣2️⃣ Proof-Building Strategy (5 days)

| Day | Goal | Tasks | Commits | Proof screenshots |
|---|---|---|---|---|
| 1 | Setup | Install Python, venv, libraries, folders, repo | `chore: project setup` | Terminal with `pip list`, empty repo page |
| 2 | Dataset | Run generator; inspect raw vs clean | `feat: synthetic data generator`, `feat: data cleaning` | `raw_expenses.csv` preview (messy), cleaning report, cleaned preview |
| 3 | Analysis | Category/monthly/weekday, budgets, anomalies, forecast | `feat: analysis` | Tables from `outputs/`, notebook outputs |
| 4 | Visualization | Charts and dashboard | `feat: visualizations`, `feat: dashboard` | All charts, dashboard tabs |
| 5 | Final upload | README, tests, deploy, LinkedIn post | `test:`, `docs:` | Green tests, live app link, final repo page |

**Extra credit (AIpreneur move):** post a short LinkedIn/X write-up: "I built an expense analytics app with anomaly detection and a local-LLM finance coach, here is what I learned", with the dashboard GIF and repo link.

---

## 1️⃣3️⃣ Screenshots / Outputs to Capture

| # | What | Where it comes from | Save as |
|---|---|---|---|
| 1 | Dataset preview (messy raw) | Open `data/raw_expenses.csv` or `raw.head(10)` in the notebook | `images/shot_01_raw_data.png` |
| 2 | Cleaning report in terminal | `python main.py` output | `images/shot_02_cleaning.png` |
| 3 | Cleaned data preview | Notebook `df.head()` | `images/shot_03_clean_data.png` |
| 4 | Category-wise spending | `images/01_category_spending.png` (auto-generated) | already saved |
| 5 | Pie chart | `images/02_expense_pie.png` | already saved |
| 6 | Monthly trends | `images/03_monthly_income_vs_expense.png` | already saved |
| 7 | Heatmap, budget vs actual, forecast | `06`, `07`, `08` PNGs | already saved |
| 8 | Bar/weekday chart | `05_weekday_spending.png` | already saved |
| 9 | Final dashboard (Overview, Trends, Budget, AI Insights) | Browser at localhost:8501, one screenshot per tab | `images/dashboard_overview.png` etc. |
| 10 | Passing tests | Terminal after `pytest -q` | `images/shot_tests.png` |
| 11 | GitHub repo with commit history | Browser | for LinkedIn/resume |

---

## 1️⃣4️⃣ Interview Preparation

**1. Explain your project in one minute (HR version).**
"I built an expense tracker that takes messy transaction data, cleans it, and tells you where the money goes. It shows monthly trends, warns when a category goes over budget, flags unusual expenses and forecasts next month's spending. It has a dashboard anyone can use. Since I had no real financial data, I created a realistic synthetic dataset with seasonal patterns."

**2. Why synthetic data? Is that a weakness?**
Real financial data is private and hard to get. A seeded generator makes the project reproducible and lets me embed known patterns, so I can *verify* that my analysis finds them (for example the Saturday peak and the festive-season shopping spike). The pipeline accepts any real CSV with the same columns.

**3. What cleaning did you do?**
Removed duplicates, converted amounts like "₹1,200" to numbers, parsed dates, trimmed and title-cased categories, labelled blank categories "Uncategorized", dropped rows with missing amount, and reported counts at each step (10 duplicates and 7 invalid rows removed).

**4. How do you detect overspending?**
I group expenses by month and category, compare each total with its budget, and flag any breach with the excess amount and percentage. At month level, expense greater than income signals a deficit.

**5. How does anomaly detection work and why IQR?**
For each category I compute Q1, Q3 and IQR and flag single expenses above Q3 + 3×IQR. It is simple, explainable, needs no model training and is robust to skewed spending data. Limitation: categories with very few transactions are skipped.

**6. How does the forecast work? Is it accurate?**
Two baselines: a linear trend fitted with `np.polyfit` and a 3-month moving average. It is deliberately simple and explainable. With only 12 months it cannot learn seasonality, so I present a range. Next steps would be Prophet or SARIMA with more history.

**7. Why did you exclude rent and bills from the weekday analysis?**
They are fixed, scheduled payments that hide behavioural patterns. Excluding them reveals real habits (Saturday is highest), and I used average per day rather than totals so weekday counts do not bias the result.

**8. Why use `YYYY-MM` for months instead of "January"?**
Month names sort alphabetically and mix years. `YYYY-MM` sorts correctly and works across years.

**9. How would you scale this to real users?**
Move storage from CSV to a database (SQLite → PostgreSQL), add an API (FastAPI) and authentication, ingest bank/UPI statements with parsers, auto-categorise with a text classifier or an LLM, and deploy with Docker. I already separated logic into `src/` modules so the dashboard and API can reuse it.

**10. What business insights did you find, and what would you recommend?**
Savings rate 23.4% (above the 20% guideline); rent is 34% of spend; Food is the largest flexible category and breaches budget in 9 of 12 months, so I would either raise the food budget realistically or cut delivery orders; June went into deficit because of a trip plus a one-off health cost with no freelance income, which argues for an emergency buffer of 2-3 months of expenses.

**Bonus technical questions:** What is the difference between `groupby` and `pivot_table`? Why `errors="coerce"` in `to_numeric`? What is a Poisson distribution and why use it for transactions per day? How would you evaluate a forecast (MAE, MAPE, train/test split by time)? Why seed the random generator?

**How to speak about the AI layer (AIpreneur pitch):** "I added a local LLM through Ollama that only receives aggregated facts, never raw transactions, so it is private and free. The numbers come from deterministic code and the LLM only phrases the advice, which avoids hallucinated figures."

---

## 1️⃣5️⃣ Future Improvements

| Idea | How to build it |
|---|---|
| Mobile app | Wrap the logic in FastAPI, build the UI in Flutter / React Native, or ship a Streamlit PWA first |
| Real-time tracking | Parse UPI/bank SMS or email alerts; ESP32 button logger (`hardware/` sketch); n8n workflow to append rows |
| AI spending prediction | Prophet/SARIMA, or gradient boosting on lag features; evaluate with a time-based split |
| Smart categorisation | Classify transaction descriptions (TF-IDF + logistic regression, or an LLM) |
| Budgeting alerts | n8n or a Python scheduler sends Telegram/WhatsApp messages when a category reaches 80% of its budget |
| Financial goal tracking | Goal table (target, deadline) and a progress bar based on monthly savings |
| Multi-user product | Auth, per-user database, subscription tiers: a micro-SaaS for freelancers and small shops |

---

## 1️⃣6️⃣ Troubleshooting

| Error / symptom | Cause | Fix |
|---|---|---|
| `'python' is not recognized` | Python not on PATH | Reinstall and tick "Add Python to PATH", or use `py` on Windows |
| `ModuleNotFoundError: No module named 'src'` | Running from the wrong folder | `cd` into the project root and run `python main.py` |
| `ModuleNotFoundError: pandas` (or streamlit/plotly) | venv not activated or libraries not installed | Activate `.venv`, then `pip install -r requirements.txt` |
| PowerShell: "running scripts is disabled" | Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Charts do not pop up | The project saves charts to `images/` (headless mode) | Open the PNG files; in a notebook, use `plt.show()` cells |
| `FileNotFoundError: raw_expenses.csv` | Data not generated yet | `python main.py --regenerate` |
| `KeyError: 'Amount'` / wrong columns | Your CSV has different headers | Rename columns to `Date, Category, Description, Amount, Type, Payment_Method` |
| `ValueError: could not convert string to float` | Amounts contain ₹ or commas | The cleaner already handles it; make sure you load through `clean()` |
| Dates become `NaT` | Unusual date format | Use `pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")` for DD-MM-YYYY |
| Streamlit shows old data | Cache | Press `C` then "Clear cache" in the app menu, or restart Streamlit |
| `streamlit: command not found` | Not installed in the active environment | `pip install streamlit`, or `python -m streamlit run app.py` |
| Port 8501 already in use | Another Streamlit is running | `streamlit run app.py --server.port 8502` |
| `use_container_width` deprecation warning | Old code with new Streamlit | This project already uses `width="stretch"` (needs Streamlit 1.50+) |
| `--ai` prints "AI summary skipped" | Ollama not running or model missing | Install Ollama, run `ollama serve` and `ollama pull llama3.2` |
| `git push` rejected / "remote origin already exists" | Remote mismatch | `git remote set-url origin <url>` then `git push -u origin main` |
| `git` asks for a password and fails | GitHub no longer accepts passwords | Use a Personal Access Token or GitHub Desktop / `gh auth login` |
| Large or personal files pushed by mistake | Missing `.gitignore` | Add it, then `git rm -r --cached .venv` and commit |
