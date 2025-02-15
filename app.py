from flask import Flask, render_template, request, redirect
import os
import sys
import yaml

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

if __name__ == '__main__':
    app.run(debug=True)