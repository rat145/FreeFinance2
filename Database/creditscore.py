import pandas as pd
import json

# File Paths
fd_file_path = r"Database\fdDetails.json"
rd_file_path = r"Database\rdDetails.json"
shreya_file_path = r"Database\customer_alldata.json"

# Load FD details
with open(fd_file_path, "r") as f:
    fd_data = json.load(f)

# Load RD details
with open(rd_file_path, "r") as f:
    rd_data = json.load(f)

# Load Bank Account & Transactions
with open(shreya_file_path, "r") as f:
    shreya_data = json.load(f)

# Function to safely extract numerical values
def safe_float(value):
    """Convert value to float safely, return 0 if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0  # Ignore non-numeric values

# Extract Financial Assets (FDs and RDs)
fd_principal = sum(safe_float(fd.get("principalAmount", 0)) for fd in fd_data)
fd_maturity = sum(safe_float(fd.get("maturityAmount", 0)) for fd in fd_data)

rd_principal = sum(safe_float(rd.get("principalAmount", 0)) for rd in rd_data)
rd_maturity = sum(safe_float(rd.get("maturityAmount", 0)) for rd in rd_data)
rd_current_value = sum(safe_float(rd.get("currentValue", 0)) for rd in rd_data)

# Handle missing "accounts" key safely
accounts_data = shreya_data.get("accounts", [])

if accounts_data and isinstance(accounts_data, list):  # Ensure it's a list
    account_summary = accounts_data[0].get("Summary", {})
    transactions_list = accounts_data[0].get("Transactions", [])
else:
    account_summary = {}
    transactions_list = []

# Extract Savings Balance
savings_balance = safe_float(account_summary.get("currentBalance", 0))

# Convert transaction list to DataFrame
transactions = pd.DataFrame(transactions_list)

if transactions.empty:
    print("No transaction data found.")
    transactions["amount"] = 0  # Create an empty column
else:
    transactions["amount"] = transactions["amount"].apply(safe_float)  # Convert safely

# Drop unnecessary columns
new_df = transactions.drop(["transactionTimestamp", "balance", "reference"], axis=1, errors="ignore")

# Function to generate narration split DataFrame
def gen_narrations(df):
    """Splits the narration field into multiple components."""
    if "narration" not in df.columns:
        return pd.DataFrame(columns=['txnId', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6'])

    narrations = []
    for i in range(len(df)):
        split_values = df["narration"].iloc[i].split('/') if pd.notna(df["narration"].iloc[i]) else []
        split_values = split_values[:6]  # Limit to 6 parts
        while len(split_values) < 6:  # Fill missing parts
            split_values.append("")
        narrations.append([df["txnId"].iloc[i]] + split_values)

    return pd.DataFrame(narrations, columns=['txnId', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6'])

# Generate narration DataFrame
narrations_df = gen_narrations(new_df)

# Merge narrations with original transaction data
merged_df = new_df.merge(narrations_df, on="txnId", how="left")

# Compute Total Credits & Debits
total_credits = merged_df[merged_df["type"] == "CREDIT"]["amount"].sum()
total_debits = merged_df[merged_df["type"] == "DEBIT"]["amount"].sum()

# Compute Debt Utilization Ratio (DUR)
debt_utilization_ratio = (total_debits / total_credits) * 100 if total_credits > 0 else 100

# Compute Account Age (Years)
try:
    account_open_date = pd.to_datetime(account_summary.get("openingDate", "2000-01-01"))
    current_date = pd.to_datetime("2025-02-15")  # Assuming today's date
    account_age_years = (current_date - account_open_date).days / 365
except Exception:
    account_age_years = 0

# Compute Credit Score Components
financial_assets_score = min(30, ((fd_maturity + rd_maturity + savings_balance) / 1000000) * 30)
debt_utilization_score = max(0, 25 - (debt_utilization_ratio / 4))
transaction_consistency_score = min(20, (total_credits / 500000) * 20)
loan_repayment_score = max(0, 15 - (total_debits / total_credits) * 15) if total_credits > 0 else 0
account_age_score = min(10, account_age_years)

# Final Credit Score Calculation (out of 100)
credit_score = (
    financial_assets_score +
    debt_utilization_score +
    transaction_consistency_score +
    loan_repayment_score +
    account_age_score
)

# Scale credit score to 300-900 range
scaled_credit_score = 300 + (credit_score / 100) * 600

# Print Final Credit Score
print(f"\nFinal Credit Score: {scaled_credit_score:.2f} (Scale: 300-900)")

# Breakdown of Score Components
print("\n🔹 **Score Breakdown:**")
print(f"- Financial Assets Score: {financial_assets_score:.2f}/30")
print(f"- Debt Utilization Score: {debt_utilization_score:.2f}/25")
print(f"- Transaction Consistency Score: {transaction_consistency_score:.2f}/20")
print(f"- Loan Repayment Score: {loan_repayment_score:.2f}/15")
print(f"- Account Age Score: {account_age_score:.2f}/10")

# Provide Actionable Insights
print("\n💡 **Suggestions to Improve Credit Score:**")
if debt_utilization_ratio > 50:
    print("- 📉 Reduce debt utilization by increasing savings or reducing large withdrawals.")
if total_credits < 50000:
    print("- 💰 Increase regular credited income to improve financial stability.")
if account_age_years < 2:
    print("- ⏳ Keep the bank account active for a longer period to build credibility.")
if financial_assets_score < 15:
    print("- 🏦 Consider increasing FDs, RDs, and bank balance for better financial security.")

print("\n🚀 Aiming for a score above **700** will make loan approvals much easier!\n")
