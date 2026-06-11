import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

print("Waiting 10 seconds for Uvicorn server to start...")
time.sleep(10)

def test_endpoint(name, method, path, data=None, files=None):
    url = f"{BASE_URL}{path}"
    print(f"\n--- Testing {name} ({method} {path}) ---")
    try:
        if method == "GET":
            resp = requests.get(url, timeout=40)
        elif method == "POST":
            if files:
                resp = requests.post(url, data=data, files=files, timeout=40)
            elif data:
                resp = requests.post(url, json=data, timeout=40)
            else:
                resp = requests.post(url, timeout=40)
        
        print(f"Status Code: {resp.status_code}")
        try:
            print("Response:", json.dumps(resp.json(), indent=2))
        except Exception:
            print("Response text:", resp.text[:200])
    except Exception as e:
        print(f"Request failed: {e}")

# 1. GET /health
test_endpoint("GET /health", "GET", "/health")

# 2. POST /initialize-application
init_data = {
    "business_name": "ABC Traders Pvt Ltd",
    "owner_name": "Rajesh Kumar",
    "loan_amount": 1000000,
    "monthly_revenue": 200000,
    "industry": "Trading",
    "loan_purpose": "Expansion",
    "years_in_business": 5
}
test_endpoint("POST /initialize-application", "POST", "/initialize-application", data=init_data)

# 3. POST /upload-document
# We need to simulate a file upload.
files = {
    "file": ("test.pdf", b"%PDF-1.4 ... test file content", "application/pdf")
}
data = {
    "application_id": "APP123",
    "document_type": "PAN Card"
}
test_endpoint("POST /upload-document", "POST", "/upload-document", data=data, files=files)

# 4. POST /analyze-loan
analysis_data = {
    "business_name": "ABC Traders Pvt Ltd",
    "owner_name": "Rajesh Kumar",
    "loan_amount": 1000000,
    "monthly_revenue": 200000,
    "industry": "Trading",
    "loan_purpose": "Expansion",
    "years_in_business": 5,
    "application_id": "APP123"
}
test_endpoint("POST /analyze-loan", "POST", "/analyze-loan", data=analysis_data)

# 5. GET /manual-review/queue
test_endpoint("GET /manual-review/queue", "GET", "/manual-review/queue")
