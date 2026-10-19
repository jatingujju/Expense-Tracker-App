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
