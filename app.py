from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
import os
import sys
import yaml
import plotly
import plotly.graph_objs as go
import json
from collections import defaultdict
import csv
from Database.llm_train import analyze_transactions, llm_chain
from functools import wraps
import time

current_dir = os.path.dirname(os.path.abspath(__file__))

# Add the directory containing setu_fetch_data.py to the Python path
sys.path.append(os.path.join(current_dir))

from setu_fetch_data import generate_token, generate_consent  # Import your functions

app = Flask(__name__)

# Path to the config.yaml file
CONFIG_PATH = r"./config.yaml"

# Check if config.yaml exists
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

# Load credentials from config.yaml
with open(CONFIG_PATH, "r") as config_file:
    config = yaml.safe_load(config_file)

# Extract credentials from config.yaml
CLIENT_ID = config.get("CLIENT_ID")
CLIENT_SECRET = config.get("CLIENT_SECRET")
PRODUCT_INSTANCE_ID = config.get("PRODUCT_INSTANCE_ID")

if not CLIENT_ID or not CLIENT_SECRET or not PRODUCT_INSTANCE_ID:
    raise ValueError("Missing required credentials in config.yaml")

# Path to store user data
USER_DATA_FILE = "user_data.txt"

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        # Get the name and mobile number from the form
        name = request.form.get("name")
        mobile_number = request.form.get("mobile")
        vua = f"{mobile_number}@onemoney"

        # Save name and mobile number to a text file
        with open(USER_DATA_FILE, "a") as file:
            file.write(f"Name: {name}, Mobile: {mobile_number}\n")

        # Generate token using setu_fetch_data.py
        auth_token = generate_token(CLIENT_ID, CLIENT_SECRET)
        if auth_token:
            # Generate consent URL
            consent_url = generate_consent(auth_token, PRODUCT_INSTANCE_ID, vua)
            if consent_url:
                # Redirect to the consent URL
                return redirect(consent_url)

    # Render the form
    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", activeTab="dashboard")

@app.route("/dashboard/brands")
def brands():
    # Loyalty brands
    with open("database\\updated_brand_loyalty_rewards.csv", "r") as csvFile:
        csv_reader = csv.DictReader(csvFile)
        lb_data = [row for row in csv_reader]
    
    # Recommended Brands
    recommended_brands_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'discount.json')
    with open(recommended_brands_json_file_path, 'r') as jsonFile:
        rb_data = json.load(jsonFile)

    return render_template("dashboard.html", activeTab="brands", loyalty_brands_data = lb_data, recommended_brands_data = rb_data)

# Route to serve files from the "database" folder
@app.route("/database/<filename>")
def database(filename):
    return send_from_directory("database", filename)

@app.route("/dashboard/finpilot")
def finpilot():
    return render_template("finpilot.html")

@app.route("/dashboard/finpilot/ask", methods=['POST'])
def ask():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({'error': 'No question provided'}), 400
        
        user_question = data['question']
        
        # Get the answer
        answer = analyze_transactions(user_question)
        
        # Debug print to see what's being returned
        print("Answer from analyze_transactions:", answer)
        
        if not answer:
            answer = llm_chain.run(question=user_question)
            print("Answer from llm_chain:", answer)
        
        # If the answer is already a list, return it directly
        if isinstance(answer, list):
            return jsonify({'answer': answer})
            
        # If it's a string but contains multiple questions (separated by newlines)
        elif isinstance(answer, str) and '\n' in answer:
            questions = [q.strip() for q in answer.split('\n') if q.strip()]
            return jsonify({'answer': questions})
            
        # If it's a single response
        return jsonify({'answer': answer})
        
    except Exception as e:
        print(f"Error in /ask endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route("/dashboard/profile")
def profile():
    return render_template("dashboard.html", activeTab="profile")

@app.route("/accounts-and-cards")
def accounts_cards():
    return render_template("dashboard-content.html", activeTab="accounts-and-cards")

@app.route("/reminders")
def reminders():
    # Path to the JSON file
    reminders_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'reminderDetails.json')

    # Load JSON data from the file
    with open(reminders_json_file_path, 'r') as file7:
        remindersData = json.load(file7)
    return render_template("dashboard-content.html", activeTab="reminders", remindersData=remindersData)

@app.route("/transactions-and-trends")
def transactions_and_trends():
    # ============ MONTH WISE ============
    # Path to the JSON file
    monthwise_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'monthWiseEI.json')

    # Load JSON data from the file
    with open(monthwise_json_file_path, 'r') as file:
        monthWiseEIdata = json.load(file)

    # Extract data for the chart
    months = [entry["Month"] for entry in monthWiseEIdata]
    total_expenses = [entry["Total_Expense"] for entry in monthWiseEIdata]
    total_incomes = [entry["Total_Income"] for entry in monthWiseEIdata]

    # Create bar traces for Total_Expense and Total_Income
    trace_expense = go.Bar(
        x=months,
        y=total_expenses,
        name='Total Expense',
        marker=dict(color='#f03433')
    )
    trace_income = go.Bar(
        x=months,
        y=total_incomes,
        name='Total Income',
        marker=dict(color='#2fd06e')
    )

    # Define the layout
    layout = go.Layout(
        title='Monthly Income and Expense',
        xaxis=dict(title='Month'),
        yaxis=dict(title='Amount'),
        barmode='group'  # Grouped bars
    )

    # Create the figure
    fig = go.Figure(data=[trace_expense, trace_income], layout=layout)

    # Convert the figure to JSON
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # ============ CATEOGRY WISE ============
    categorywise_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'categoryWiseTransactions.json')
    
    with open(categorywise_json_file_path, 'r') as file2:
        cateogryWisedata = json.load(file2)

    # Calculate total spending per category
    category_spending = defaultdict(float)
    for entry in cateogryWisedata:
        category = entry["category"]
        amount = entry["amount"]
        category_spending[category] += amount

    # Prepare data for the pie chart
    labels = list(category_spending.keys())  # Categories
    values = list(category_spending.values())  # Total spending per category
    values.sort(reverse=True)  # sorting in descending order
    values = values[:10]  # taking top 10 values
     # Create the pie chart trace
    trace2 = go.Pie(
        labels=labels,
        values=values,
        textinfo='percent',  # Show label and percentage
        insidetextorientation='radial',  # Orient text inside slices
        hole=0.3  # Create a donut chart (optional)
    )

    # Define the layout
    layout2 = go.Layout(
        title='Category-wise Spending (Top 10)',
        showlegend=True
    )

    # Create the figure
    fig2 = go.Figure(data=[trace2], layout=layout2)

    # Convert the figure to JSON
    graphJSON2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    # ============ BRAND WISE ============
    brandwise_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'brandWise.json')
    
    with open(brandwise_json_file_path, 'r') as file3:
        brandWisedata = json.load(file3)

    # Aggregate data by brand
    brand_spending = {entry["brand"]: entry["amount"] for entry in brandWisedata}

    # Prepare data for the pie chart
    labels2 = list(brand_spending.keys())  # Brands
    values2 = list(brand_spending.values())  # Amounts
    values2.sort(reverse=True)
    values2 = values2[:10]

    # Create the pie chart trace
    trace3 = go.Pie(
        labels=labels2,
        values=values2,
        textinfo='percent',  # Show label and percentage
        insidetextorientation='radial',  # Orient text inside slices
        hole=0.3  # Create a donut chart (optional)
    )

    # Define the layout
    layout3 = go.Layout(
        title='Brand-wise Spending (Top 10)',
        showlegend=True
    )

    # Create the figure
    fig3 = go.Figure(data=[trace3], layout=layout3)

    # Convert the figure to JSON
    graphJSON3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    # ============ MONTH WISE TRANSACTIONS ============
    monthwisetrnx_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'monthWiseTransactions.json')
    
    with open(monthwisetrnx_json_file_path, 'r') as file4:
        monthWiseTrnxdata = json.load(file4)
    
    # ============ CATEGORY MONTH WISE TRANSACTIONS ============
    categorymonthwise_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'categoryMonthWise.json')
    
    with open(categorymonthwise_json_file_path, 'r') as file5:
        categoryMonthWisedata = json.load(file5)
    
    # ============ BRANDS MONTH WISE TRANSACTIONS ============
    brandmonthwise_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'brandWiseMonth.json')
    
    with open(brandmonthwise_json_file_path, 'r') as file6:
        brandMonthWisedata = json.load(file6)

    return render_template("dashboard-content.html", activeTab="transactions-and-trends", graphJSON=[graphJSON,graphJSON2,graphJSON3], df=[monthWiseEIdata, cateogryWisedata, brandWisedata, monthWiseTrnxdata, categoryMonthWisedata, brandMonthWisedata])

@app.route("/investments")
def investments():
    # ============ FD Data ============
    fdDetails_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'fdDetails.json')
    with open(fdDetails_json_file_path, 'r') as file8:
        fdData = json.load(file8)
    # ============ RD Data ============
    rdDetails_json_file_path = os.path.join(os.path.dirname(__file__), 'database', 'rdDetails.json')
    with open(rdDetails_json_file_path, 'r') as file9:
        rdData = json.load(file9)

    return render_template("dashboard-content.html", activeTab="investments", fdData=fdData, rdData=rdData)

@app.route("/insurance-and-mortgage")
def insurance_and_mortgage():
    return render_template("dashboard-content.html", activeTab="insurance-and-mortgage")

@app.route("/redirecting")
def start_heavy_process():
    """Shows a loading animation before redirecting to the heavy page."""
    return render_template("loading.html")

if __name__ == '__main__':
    app.run(debug=True)