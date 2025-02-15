import json
import pandas as pd
import joblib
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
import sys
import yaml

# current_dir = os.path.dirname(os.path.abspath(__file__))

# # Add the directory containing setu_fetch_data.py to the Python path
# sys.path.append(os.path.join(current_dir))
# # ==========================
# LOAD TRANSACTION DATA FILE
# ==========================
CONFIG_PATH = r"./config.yaml"

# Check if config.yaml exists
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

# Load credentials from config.yaml
with open(CONFIG_PATH, "r") as config_file:
    config = yaml.safe_load(config_file)

GROQ_API_KEY = config.get("GROQ_API_KEY")


file_path = "Database/customer_data.json"

with open(file_path, "r") as f:
    data = json.load(f)

transactions = data["fiData"]
df = pd.DataFrame(transactions)

# Convert valueDate to datetime & ensure numeric amounts
df["valueDate"] = pd.to_datetime(df["valueDate"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
df["type"] = df["type"].str.lower().str.strip()  # Normalize 'type' column

# ==========================
# LOAD OTHER FINANCIAL DATA
# ==========================
fav_brands_file = "Database/favBrands.json"
reminder_file_path = "Database/reminderDetails.json"
fd_file_path = "Database/fdDetails.json"
rd_file_path = "Database/rdDetails.json"
file_path = "Database/customer_data.json"

with open(file_path, "r") as f:
    data = json.load(f)

transactions = data["fiData"]
# Load JSON Data
with open(fav_brands_file, "r") as f:
    fav_brands_data = json.load(f)

with open(reminder_file_path, "r") as f:
    reminder_data = json.load(f)

with open(fd_file_path, "r") as f:
    fd_data = json.load(f)

with open(rd_file_path, "r") as f:
    rd_data = json.load(f)

# Convert data into DataFrames
fav_brands_df = pd.DataFrame(fav_brands_data)
reminder_df = pd.DataFrame(reminder_data)
fd_df = pd.DataFrame(fd_data)
rd_df = pd.DataFrame(rd_data)
shreya_df = pd.DataFrame(transactions)

# Convert valueDate to datetime & ensure numeric amounts
shreya_df["valueDate"] = pd.to_datetime(shreya_df["valueDate"], errors="coerce")
shreya_df["amount"] = pd.to_numeric(shreya_df["amount"], errors="coerce")
shreya_df["type"] = shreya_df["type"].str.lower().str.strip()
def gen_narrations(shreya_df):
    nan = shreya_df["narration"].isna().sum()
    if nan!=0:
        return ("The narration is empty for nan no. of transactions!")
    n = shreya_df.shape[0]
    narrations = []
    for i in range(0,n):
        li = [shreya_df["txnId"][i]]
        li += (shreya_df["narration"][i].split('/'))
        narrations.append(li)
    return pd.DataFrame(narrations, columns =['txnId','f1','f2','f3','f4','f5','f6'], dtype = str)

narration_df = gen_narrations(shreya_df)
shreya_df = shreya_df.merge(narration_df, on='txnId', how='left')

# Convert financial values to numeric
fd_df["principalAmount"] = pd.to_numeric(fd_df["principalAmount"], errors="coerce")
fd_df["maturityAmount"] = pd.to_numeric(fd_df["maturityAmount"], errors="coerce")
rd_df["principalAmount"] = pd.to_numeric(rd_df["principalAmount"], errors="coerce")
rd_df["maturityAmount"] = pd.to_numeric(rd_df["maturityAmount"], errors="coerce")
rd_df["currentValue"] = pd.to_numeric(rd_df["currentValue"], errors="coerce")

# Convert reminder dates
reminder_df["next_date"] = pd.to_datetime(reminder_df["next_date"], format="%d-%m-%y", errors="coerce")

# ==========================
# LOAD TRAINED LOAN MODEL
# ==========================
model_path = "Database/loan_model/loan_model/loan_model.pkl"
scaler_path = "Database/loan_model/loan_model/loan_scaler.pkl"
encoder_path = "Database/loan_model/loan_model/loan_encoder_classes.pkl"
feature_path = "Database/loan_model/loan_model/loan_features.pkl"

# Load the model, scaler, and encoder
model = joblib.load(model_path)
scaler = joblib.load(scaler_path)
encoder_classes = joblib.load(encoder_path)
feature_names = joblib.load(feature_path)

# ==========================
# FUNCTION TO HANDLE LOAN APPLICATION
# ==========================
def handle_loan_application():
    """Gathers loan details from user and predicts approval using the trained model."""

    questions = {
        "Gender": "What is your gender? (Male/Female)",
        "Married": "Are you married? (Yes/No)",
        "Dependents": "How many dependents do you have? (0, 1, 2, 3+)",
        "Education": "Are you a Graduate? (Yes/No)",
        "Self_Employed": "Are you self-employed? (Yes/No)",
        "ApplicantIncome": "What is your monthly income?",
        "CoapplicantIncome": "What is your co-applicant's monthly income? (Enter 0 if none)",
        "LoanAmount": "How much loan amount are you applying for?",
        "Loan_Amount_Term": "What is the loan tenure in months? (e.g., 360 for 30 years)",
        "Credit_History": "Do you have a credit history? (1 for Yes, 0 for No)",
        "Property_Area": "What is your property location? (Urban/Semiurban/Rural)",
    }

    user_inputs = {}
    for feature, question in questions.items():
        user_inputs[feature] = input(question + " ")

    # Convert to numeric types
    for col in ["ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term", "Credit_History"]:
        user_inputs[col] = float(user_inputs[col])

    # Encode categorical values
    for col in ["Gender", "Married", "Education", "Self_Employed", "Property_Area", "Dependents"]:
        user_inputs[col] = encoder_classes[col].index(user_inputs[col]) if user_inputs[col] in encoder_classes[col] else -1

    # Convert to DataFrame
    user_df = pd.DataFrame([user_inputs])
    user_df = user_df.reindex(columns=feature_names)
    user_df_scaled = scaler.transform(user_df)

    # Predict Loan Approval
    prediction = model.predict(user_df_scaled)
    print(prediction)
    return "✅ Loan Approved" if prediction[0] == 1 else "❌ Loan Rejected"

# ==========================
# FUNCTION TO FETCH REMINDERS
# ==========================
# ==========================
# FUNCTION TO HANDLE CREATOR QUERY
# ==========================
def get_creator_info(query):
    """Returns the creator information if the query is about who built the system."""
    query_lower = query.lower()
    creator_keywords = ["who built you", "who created you", "who made you", "creator", "developer"]

    if any(keyword in query_lower for keyword in creator_keywords):
        return "I was built by **Dhiraj Solanki** and **Ratan Sharma**, 3rd-year FinTech enthusiasts. 🚀"
    
    return None  # If the query is not related to the creators

def analyze_shreya_fidata():
    """Analyzes transaction history and investments from shreya_fidata."""
    total_income = df[df["type"] == "credit"]["amount"].sum()
    total_expense = df[df["type"] == "debit"]["amount"].sum()
    balance = total_income - total_expense
    
    # Extract investment details
    investments = df[df["narration"].str.contains("FD|RD|investment", case=False, na=False)]
    investment_summary = investments.groupby("narration")["amount"].sum().reset_index()
    investment_details = "\n".join([f"{row['narration']}: ₹{row['amount']}" for _, row in investment_summary.iterrows()])
    
    return (f"Total Income: ₹{total_income}\nTotal Expenses: ₹{total_expense}\nBalance: ₹{balance}\n\n"
            f"Investments:\n{investment_details if not investments.empty else 'No recorded investments.'}")

def find_reminders_from_data():
    """Fetches upcoming reminders from the structured reminder dataset."""
    today = pd.to_datetime("today").normalize()
    upcoming_reminders = reminder_df[reminder_df["next_date"] >= today]

    if upcoming_reminders.empty:
        return "You currently have no upcoming payment reminders."

    reminder_details = []
    for _, row in upcoming_reminders.iterrows():
        brand = row.get("brand", "Unknown")
        category = row.get("category", "Unknown")
        amount = row["amount"] if row["amount"] != "--" else "Unknown Amount"
        due_date = row["next_date"].strftime("%d-%m-%Y") if pd.notna(row["next_date"]) else "Unknown Date"

        reminder_details.append(f"{brand} ({category}): ₹{amount} due on {due_date}")

    return "\n".join(reminder_details)
def find_favorite_brands():
    """Fetches the user's favorite brands from structured data."""
    if fav_brands_df.empty:
        return "You have not listed any favorite brands."

    favorite_brands = fav_brands_df["brand"].tolist()
    return f"Your favorite brands are: {', '.join(favorite_brands)}."
def find_investment_details():
    """Fetches Fixed Deposit (FD) and Recurring Deposit (RD) details."""
    investment_details = []

    # Fixed Deposits
    if not fd_df.empty:
        for _, row in fd_df.iterrows():
            investment_details.append(
                f"FD at {row['bankName']} - ₹{row['principalAmount']} principal, "
                f"₹{row['maturityAmount']} at maturity, interest: {row['interestRate']}%"
            )

    # Recurring Deposits
    if not rd_df.empty:
        for _, row in rd_df.iterrows():
            investment_details.append(
                f"RD at {row['bankName']} - ₹{row['principalAmount']} principal, "
                f"₹{row['currentValue']} current value, ₹{row['maturityAmount']} at maturity, "
                f"interest: {row['interestRate']}%"
            )

    if not investment_details:
        return "You have no recorded investments or deposits."

    return "\n".join(investment_details)
# ==========================
# FUNCTION TO PROCESS USER QUERIES
# ==========================
def analyze_transactions(query):
    """Processes user queries and fetches relevant financial information"""
    query_lower = query.lower()

    # Last month's income and expenses
    if "last month" in query_lower:
        last_month = (pd.to_datetime("today") - pd.DateOffset(months=1)).month
        last_month_df = df[df["valueDate"].dt.month == last_month]
        income = last_month_df[last_month_df["type"] == "credit"]["amount"].sum()
        expense = last_month_df[last_month_df["type"] == "debit"]["amount"].sum()
        return f"Your last month's income was ₹{income} and expenses were ₹{expense}."

    # Specific month income and expenses
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    for month, month_index in months.items():
        if month in query_lower:
            month_df = df[df["valueDate"].dt.month == month_index]
            income = month_df[month_df["type"] == "credit"]["amount"].sum()
            expense = month_df[month_df["type"] == "debit"]["amount"].sum()
            return f"Your {month.capitalize()} income was ₹{income} and expenses were ₹{expense}."

    # FD and Investments
    if "fd" in query_lower or "fixed deposit" in query_lower or "investment" in query_lower:
        return find_investment_details()

    # Payment Reminders
    if "reminder" in query_lower or "bills" in query_lower or "emi" in query_lower:
        return find_reminders_from_data()

    # Favorite Brands
    if "favorite brand" in query_lower or "favourite brand" in query_lower:
        return find_favorite_brands()
    
    if "transaction" in query_lower or "my transaction " in query_lower or "analysis" in query_lower or "advice" in query_lower:
        return analyze_shreya_fidata()
    if "loan" in query_lower or "apply" in query_lower:
        return handle_loan_application()
    if "who built you" in query_lower or "who created you" in query_lower or "who made you" in query_lower or "developer" in query_lower or "creator" in query_lower:
        return get_creator_info(query_lower)
    

    return None  # If no direct answer is found

# ==========================
# AI MODEL SETUP
# ==========================
GROQ_API_KEY = config.get("GROQ_API_KEY")
llama3 = ChatGroq(api_key=GROQ_API_KEY, model="llama3-8b-8192")

template = PromptTemplate.from_template(
    "You are a personal financial assistant. "
    "User asks: {question}\n"
    "Provide an accurate response using transaction history."
)

llm_chain = LLMChain(llm=llama3, prompt=template)

# ==========================
# USER INTERACTION
# ==========================
# user_question = input("Ask me anything about your finances: ")
# answer = analyze_transactions(user_question)

# if not answer:
#     answer = llm_chain.run(question=user_question)

# print("Assistant:", answer)
