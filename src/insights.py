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
