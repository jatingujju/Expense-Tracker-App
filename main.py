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
