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
.stTabs [data-baseweb="tab-list"] {gap: 10px; background: transparent; padding: 4px 0;}
.stTabs button[role="tab"] {padding: 10px 22px !important; height: auto !important; border-radius: 10px !important;}
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
    fig.update_xaxes(showgrid=False, linecolor="#E2E8F0", title=None)
    fig.update_yaxes(gridcolor="#EEF0F7", zeroline=False, title=None)
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
        fig.update_xaxes(range=[0, cs["Total"].max() * 1.18])
        st.plotly_chart(style(fig, 430, False), width="stretch")
    with r.container(border=True):
        big = cs[cs["Share_%"] >= 3.0]
        small = cs["Total"].sum() - big["Total"].sum()
        pie = pd.concat([big[["Category", "Total"]],
                         pd.DataFrame({"Category": ["Other"], "Total": [small]})]) if small > 0 else big
        fig = px.pie(pie, names="Category", values="Total", hole=0.62, title="Expense distribution")
        fig.update_traces(textposition="outside", textinfo="percent+label", texttemplate="%{label}<br>%{percent:.0%}",
                          marker=dict(line=dict(color="white", width=2)))
        fig.add_annotation(text=f"<b>{money(cs['Total'].sum())}</b><br>total spend", showarrow=False, font=dict(size=15))
        st.plotly_chart(style(fig, 430, False), width="stretch")

    l2, r2 = st.columns(2)
    with l2.container(border=True):
        ws = an.weekday_summary(df)
        peak = ws["Avg_Per_Day"].idxmax()
        fig = px.bar(ws, x="Weekday", y="Avg_Per_Day",
                     title="Average daily spend by weekday (excl. rent, bills, subscriptions)")
        fig.update_traces(marker_color=[ROSE if i == peak else TEAL for i in ws.index],
                          hovertemplate="%{x}: " + INR + "%{y:,.0f}<extra></extra>")
        st.plotly_chart(style(fig, 360, False), width="stretch")
    with r2.container(border=True):
        ps = an.payment_summary(df)
        fig = px.pie(ps, names="Payment_Method", values="Total", hole=0.55, title="Payment methods")
        fig.update_traces(texttemplate="%{percent:.0%}", textposition="auto",
                          insidetextfont=dict(color="white", size=14), outsidetextfont=dict(color="#334155", size=13),
                          marker=dict(line=dict(color="white", width=2)))
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
        anom = an.detect_anomalies(df).copy()
        anom["Date"] = pd.to_datetime(anom["Date"]).dt.strftime("%d %b %Y")
        st.dataframe(anom, width="stretch", hide_index=True)
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
