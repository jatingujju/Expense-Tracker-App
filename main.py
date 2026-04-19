# =========================================
# Expense Tracker App using Data Science
# =========================================
import os

# Always create required folders first
def create_folders():
    folders = ["data", "images", "outputs"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

create_folders()
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -----------------------------
# 0. Create Required Folders
# -----------------------------
def create_folders():
    folders = ["data", "images", "outputs"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

create_folders()

# -----------------------------
# 1. Generate Synthetic Data
# -----------------------------
np.random.seed(42)

dates = pd.date_range(start="2024-01-01", end="2024-03-31")
categories = ["Food", "Travel", "Rent", "Shopping", "Bills"]
payment_modes = ["Cash", "UPI", "Card"]

data = {
    "Date": np.random.choice(dates, 200),
    "Category": np.random.choice(categories, 200),
    "Amount": np.random.randint(100, 5000, 200),
    "Payment_Mode": np.random.choice(payment_modes, 200)
}

df = pd.DataFrame(data)

# Save dataset
df.to_csv("data/expenses.csv", index=False)
print("✅ Dataset saved in data/expenses.csv")

# -----------------------------
# 2. Data Cleaning
# -----------------------------
df["Date"] = pd.to_datetime(df["Date"])
df.dropna(inplace=True)

# -----------------------------
# 3. Feature Engineering
# -----------------------------
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day_name()

# -----------------------------
# 4. Analysis
# -----------------------------
total_expense = df["Amount"].sum()
category_expense = df.groupby("Category")["Amount"].sum()
monthly_expense = df.groupby("Month")["Amount"].sum()

print("\n💰 Total Expense:", total_expense)
print("\n📊 Category-wise Expense:\n", category_expense)

# -----------------------------
# 5. Visualization
# -----------------------------

# Pie Chart
plt.figure(figsize=(6,6))
category_expense.plot(kind='pie', autopct='%1.1f%%')
plt.title("Category Distribution")
plt.ylabel("")
plt.savefig("images/pie_chart.png")
plt.close()

# Bar Chart
plt.figure(figsize=(8,5))
sns.barplot(x=category_expense.index, y=category_expense.values)
plt.title("Category-wise Expense")
plt.xlabel("Category")
plt.ylabel("Amount")
plt.savefig("images/bar_chart.png")
plt.close()

# Line Chart
plt.figure(figsize=(8,5))
monthly_expense.plot(marker='o')
plt.title("Monthly Expense Trend")
plt.xlabel("Month")
plt.ylabel("Amount")
plt.savefig("images/line_chart.png")
plt.close()

print("\n📸 Charts saved in images/ folder")

# -----------------------------
# 6. Insights
# -----------------------------
percentage = (category_expense / total_expense) * 100
top_category = category_expense.idxmax()

print("\n📈 Percentage Contribution:\n", percentage.round(2))
print(f"\n🔥 Highest spending category: {top_category}")

# -----------------------------
# 7. Business Insights
# -----------------------------
print("\n🧠 Business Insights:")

for category, value in percentage.items():
    print(f"- {category}: {value:.2f}% of total expenses")

# Overspending Detection
if total_expense > 500000:
    print("\n⚠️ Overspending Alert! Consider reducing expenses.")
else:
    print("\n✅ Spending is under control.")

# -----------------------------
# 8. Save Summary Report
# -----------------------------
report = pd.DataFrame({
    "Category": category_expense.index,
    "Total Amount": category_expense.values,
    "Percentage": percentage.values
})

report.to_csv("outputs/expense_summary.csv", index=False)
print("\n📁 Summary report saved in outputs/expense_summary.csv")

# =========================================
# END OF PROJECT
# =========================================