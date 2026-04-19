# =========================================
# Expense Tracker Dashboard (Streamlit)
# =========================================

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 1. App Config
# -----------------------------
st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("💰 Expense Tracker Dashboard")

# -----------------------------
# 2. Load Data
# -----------------------------
df = pd.read_csv("data/expenses.csv")
df["Date"] = pd.to_datetime(df["Date"])

# Feature Engineering
df["Month"] = df["Date"].dt.month_name()
df["Year"] = df["Date"].dt.year

# -----------------------------
# 3. Sidebar Filters
# -----------------------------
st.sidebar.header("🔍 Filters")

categories = st.sidebar.multiselect(
    "Select Category",
    options=df["Category"].unique(),
    default=df["Category"].unique()
)

payment_mode = st.sidebar.multiselect(
    "Select Payment Mode",
    options=df["Payment_Mode"].unique(),
    default=df["Payment_Mode"].unique()
)

# Filter Data
filtered_df = df[
    (df["Category"].isin(categories)) &
    (df["Payment_Mode"].isin(payment_mode))
]

# -----------------------------
# 4. Key Metrics
# -----------------------------
total_expense = filtered_df["Amount"].sum()
avg_expense = filtered_df["Amount"].mean()
max_category = filtered_df.groupby("Category")["Amount"].sum().idxmax()

col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Expense", f"₹{total_expense}")
col2.metric("📊 Avg Expense", f"₹{int(avg_expense)}")
col3.metric("🔥 Top Category", max_category)

# -----------------------------
# 5. Category-wise Chart
# -----------------------------
st.subheader("📊 Category-wise Expense")

category_expense = filtered_df.groupby("Category")["Amount"].sum()

fig1, ax1 = plt.subplots()
sns.barplot(x=category_expense.index, y=category_expense.values, ax=ax1)
plt.xticks(rotation=45)
st.pyplot(fig1)

# -----------------------------
# 6. Pie Chart
# -----------------------------
st.subheader("🥧 Expense Distribution")

fig2, ax2 = plt.subplots()
ax2.pie(category_expense, labels=category_expense.index, autopct='%1.1f%%')
ax2.axis('equal')
st.pyplot(fig2)

# -----------------------------
# 7. Monthly Trend
# -----------------------------
st.subheader("📈 Monthly Trend")

monthly_expense = filtered_df.groupby("Month")["Amount"].sum()

fig3, ax3 = plt.subplots()
monthly_expense.plot(marker='o', ax=ax3)
plt.ylabel("Amount")
st.pyplot(fig3)

# -----------------------------
# 8. Payment Mode Analysis
# -----------------------------
st.subheader("💳 Payment Mode Usage")

payment_counts = filtered_df["Payment_Mode"].value_counts()

fig4, ax4 = plt.subplots()
sns.barplot(x=payment_counts.index, y=payment_counts.values, ax=ax4)
st.pyplot(fig4)

# -----------------------------
# 9. Raw Data (Optional)
# -----------------------------
if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

# -----------------------------
# 10. Insights Section
# -----------------------------
st.subheader("🧠 Insights")

top_category = category_expense.idxmax()
st.write(f"🔥 Highest spending category: **{top_category}**")

if total_expense > 500000:
    st.error("⚠️ Overspending Alert!")
else:
    st.success("✅ Spending is under control")