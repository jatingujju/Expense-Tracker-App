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
