import asyncio
import httpx
import os
import sys

# Load env variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BACKEND = "http://localhost:8000"

DEMO_CASES = [
    {
        "biz": "ABC Traders Pvt Ltd",
        "owner": "Rajesh Kumar",
        "amount": 500000,
        "revenue": 200000,
        "years": 5,
        "industry": "Retail & FMCG",
        "purpose": "Working capital expansion",
        "expected_decision": "Approve"
    },
    {
        "biz": "New Startup Ltd",
        "owner": "Test User",
        "amount": 1000000,
        "revenue": 100000,
        "years": 1,
        "industry": "Services & IT",
        "purpose": "Expansion",
        "expected_decision": "Manual Review"
    },
    {
        "biz": "Fake Corp Ltd",
        "owner": "Fraud User",
        "amount": 1000000,
        "revenue": 100000,
        "years": 3,
        "industry": "General Trade",
        "purpose": "Equipment purchase",
        "expected_decision": "Reject"
    }
]

GLOBAL_NAMES = [
    "Government ID",
    "Tax Identification Document",
    "Tax Registration Certificate",
    "Business Incorporation Certificate",
    "Proof of Address",
    "Bank Statements",
    "Income Tax Returns",
    "Asset Ownership Documents",
    "Financial Statements",
    "Income Statement",
    "Operating License",
    "Credit History Records"
]

INDIA_NAMES = [
    "Aadhaar Card",
    "PAN Card",
    "GST Certificate",
    "Business Registration Certificate",
    "Utility Bill",
    "Bank Statements (PDF)",
    "ITR / Tax Returns",
    "CIBIL Report",
    "Property Documents"
]

async def run_verification():
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Check health
        try:
            health = await client.get(f"{BACKEND}/health")
            print(f"[HEALTH] Status: {health.status_code}, Response: {health.json()}")
        except Exception as e:
            print(f"[ERROR] Health check failed: {e}")
            sys.exit(1)

        for i, case in enumerate(DEMO_CASES, 1):
            print(f"\n--- Testing Demo Case {i}: {case['biz']} ---")
            
            # Step 1: Initialize
            init_payload = {
                "business_name": case["biz"],
                "owner_name": case["owner"],
                "loan_amount": case["amount"],
                "monthly_revenue": case["revenue"],
                "years_in_business": case["years"],
                "industry": case["industry"],
                "loan_purpose": case["purpose"]
            }
            
            init_resp = await client.post(f"{BACKEND}/initialize-application", json=init_payload)
            assert init_resp.status_code == 200, f"Failed to initialize: {init_resp.text}"
            init_data = init_resp.json()
            app_id = init_data["application_id"]
            req_docs = init_data["required_documents"]
            print(f"  Initialized Application ID: {app_id}")
            print(f"  Required Documents: {req_docs}")
            
            # Verify no India-specific names in required docs
            for doc in req_docs:
                for ind_name in INDIA_NAMES:
                    assert ind_name not in doc, f"Found India-specific name '{ind_name}' in required document list '{doc}'"

            # Step 2: Fetch application documents (checklist)
            docs_resp = await client.get(f"{BACKEND}/application-documents/{app_id}")
            assert docs_resp.status_code == 200, f"Failed to fetch checklist: {docs_resp.text}"
            checklist = docs_resp.json()
            print(f"  Checklist entries count: {len(checklist)}")
            
            # Verify all required documents are marked as Verified (not Pending)
            verified_count = 0
            required_count = 0
            for doc in checklist:
                name = doc["document_type"]
                is_req = doc["required"]
                status = doc["upload_status"]
                
                # Check for global renaming
                for ind_name in INDIA_NAMES:
                    assert ind_name not in name, f"Found India-specific name '{ind_name}' in checklist '{name}'"
                
                if is_req:
                    required_count += 1
                    assert status == "Verified", f"Required document '{name}' is not Verified: status is '{status}'"
                if status == "Verified":
                    verified_count += 1
                    
            print(f"  Verified docs in checklist: {verified_count} of {required_count} required ones")
            assert required_count > 0, "No required documents found in checklist"

            # Step 3: Run /analyze-loan
            analyze_payload = {
                "business_name": case["biz"],
                "owner_name": case["owner"],
                "loan_amount": case["amount"],
                "monthly_revenue": case["revenue"],
                "years_in_business": case["years"],
                "industry": case["industry"],
                "loan_purpose": case["purpose"],
                "application_id": app_id
            }
            
            analyze_resp = await client.post(f"{BACKEND}/analyze-loan", json=analyze_payload)
            assert analyze_resp.status_code == 200, f"Analysis failed: {analyze_resp.text}"
            analyze_data = analyze_resp.json()
            fr = analyze_data["final_response"]
            decision = fr["final_recommendation"]
            print(f"  Final Decision: {decision}")
            print(f"  Document Completeness: {fr.get('document_completeness')}")
            print(f"  Upload Progress: {fr.get('upload_progress')}")
            
            assert fr["document_completeness"] == 1.0, f"Expected document completeness 1.0, got {fr.get('document_completeness')}"
            assert fr["upload_progress"] == 1.0, f"Expected upload progress 1.0, got {fr.get('upload_progress')}"
            assert decision == case["expected_decision"], f"Expected decision '{case['expected_decision']}', got '{decision}'"
            print(f"  [PASS] Demo Case {i} verified successfully.")

        print("\nAll Demo Cases verified successfully!")

if __name__ == "__main__":
    asyncio.run(run_verification())
