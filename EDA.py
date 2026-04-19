# =========================================
# EDA - Expense Tracker App
# =========================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 1. Load Dataset
# -----------------------------
df = pd.read_csv("data/expenses.csv")

print("📌 Data Preview:")
print(df.head())

print("\n📊 Dataset Info:")
print(df.info())

print("\n📈 Summary Statistics:")
print(df.describe())

# -----------------------------
# 2. Data Preparation
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"])

df["Month"] = df["Date"].dt.month_name()
df["Weekday"] = df["Date"].dt.day_name()

# -----------------------------
# 3. Category-wise Analysis
# -----------------------------
category_expense = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

print("\n💰 Category-wise Expense:\n", category_expense)

# -----------------------------
# 4. Monthly Trend Analysis
# -----------------------------
monthly_expense = df.groupby("Month")["Amount"].sum()

print("\n📅 Monthly Expense:\n", monthly_expense)

# -----------------------------
# 5. Payment Mode Analysis
# -----------------------------
payment_analysis = df["Payment_Mode"].value_counts()

print("\n💳 Payment Mode Usage:\n", payment_analysis)

# -----------------------------
# 6. Visualization
# -----------------------------
sns.set(style="whitegrid")

# --- Bar Chart (Category) ---
plt.figure(figsize=(8,5))
sns.barplot(x=category_expense.index, y=category_expense.values)
plt.title("Category-wise Expense")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --- Pie Chart ---
plt.figure(figsize=(6,6))
category_expense.plot(kind='pie', autopct='%1.1f%%')
plt.title("Expense Distribution")
plt.ylabel("")
plt.show()

# --- Monthly Trend ---
plt.figure(figsize=(8,5))
monthly_expense.plot(marker='o')
plt.title("Monthly Expense Trend")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.grid(True)
plt.show()

# --- Payment Mode ---
plt.figure(figsize=(6,4))
sns.countplot(x="Payment_Mode", data=df)
plt.title("Payment Mode Distribution")
plt.show()

# -----------------------------
# 7. Advanced Insights
# -----------------------------

# Highest expense day
daily_expense = df.groupby("Weekday")["Amount"].sum()
print("\n📆 Expense by Weekday:\n", daily_expense)

# Top 3 categories
top3 = category_expense.head(3)
print("\n🏆 Top 3 Categories:\n", top3)

# Average expense
avg_expense = df["Amount"].mean()
print("\n📊 Average Transaction Amount:", avg_expense)

# -----------------------------
# 8. Business Insights
# -----------------------------
print("\n🧠 Insights:")

top_category = category_expense.idxmax()
print(f"- Highest spending category: {top_category}")

if avg_expense > 2000:
    print("- High average spending detected")
else:
    print("- Spending is moderate")

print("- Focus on reducing top expense categories for better savings")