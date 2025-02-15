import requests
import webbrowser

def generate_token(client_id, client_secret):
    """Generate an access token."""
    url = "https://orgservice-prod.setu.co/v1/users/login"
    payload = {
        "clientID": client_id,
        "grant_type": "client_credentials",
        "secret": client_secret
    }
    headers = {"client": "bridge"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Error generating token: {response.status_code} - {response.text}")
        return None
def generate_consent(auth_token, product_instance_id, vua):
    """Generate a consent ID and return the URL."""
    url = "https://fiu-sandbox.setu.co/v2/consents"
    payload = {
        "consentDuration": {
            "unit": "MONTH",
            "value": "24"
        },
        "vua": vua,
        "dataRange": {
            "from": "2023-01-01T00:00:00Z",
            "to": "2025-01-24T00:00:00Z"
        },
        "consentTypes": ["PROFILE", "SUMMARY", "TRANSACTIONS"],
        "context": [],
        "redirectUrl": "http://localhost:5000/dashboard"
    }
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "x-product-instance-id": product_instance_id
    }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:  # Treat 201 as success
        consent_data = response.json()
        return consent_data.get("url")  # URL to access the consent webview
    else:
        print(f"Error generating consent: {response.status_code} - {response.text}")
        return None


def open_consent_url(consent_url):
    """Open the consent URL in the default web browser."""
    print(f"Opening consent URL: {consent_url}")
    webbrowser.open(consent_url)
