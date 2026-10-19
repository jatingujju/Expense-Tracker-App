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
