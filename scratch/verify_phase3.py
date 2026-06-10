import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import shutil
import asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

# Ensure project root is in sys.path
sys.path.insert(0, "c:\\Users\\smgal\\Documents\\hw")

from backend.main import app

async def run_tests():
    print("==========================================================")
    print("--- Starting Phase 3 Integration & Consistency Tests ---")
    print("==========================================================")
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        
        # TEST 1: Normal Approved Flow with Normalized Suffixes
        # Suffixes should normalize ABC Traders Pvt Ltd -> abc traders, matching extracted abc traders
        print("\n[TEST 1] Testing Normal Flow with Name Normalization Suffixes...")
        init_payload_1 = {
            "business_name": "ABC Traders Pvt Ltd",
            "owner_name": "Rajesh Kumar",
            "loan_amount": 50000.0,
            "monthly_revenue": 10000.0,
            "industry": "Trading",
            "loan_purpose": "Inventory expansion",
            "years_in_business": 5  # Experienced Business Owner
        }
        res = await client.post("/initialize-application", json=init_payload_1)
        assert res.status_code == 200, f"Failed init: {res.text}"
        data_1 = res.json()
        app_id_1 = data_1["application_id"]
        required_docs_1 = data_1["required_documents"]
        
        print(f"Initialized application {app_id_1}. Required docs: {required_docs_1}")
        
        # Uploading one dummy file so it's not totally empty (the demo code will mock full extraction anyway)
        from PIL import Image
        import io
        img = Image.new('RGB', (10, 10), color = 'green')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        png_content = img_bytes.getvalue()
        
        # Upload a required document (e.g. Bank Statement)
        first_doc = required_docs_1[0]
        res = await client.post(
            "/upload-document",
            data={"application_id": app_id_1, "document_type": first_doc},
            files={"file": ("doc.png", png_content, "image/png")}
        )
        assert res.status_code == 200
        
        # Analyze
        analyze_payload_1 = {
            **init_payload_1,
            "application_id": app_id_1
        }
        res = await client.post("/analyze-loan", json=analyze_payload_1)
        assert res.status_code == 200, f"Analysis failed: {res.text}"
        result_1 = res.json()
        
        fr_1 = result_1["final_response"]
        doc_intel_1 = fr_1.get("document_intelligence")
        
        print(f"Final Recommendation: {fr_1['final_recommendation']}")
        print(f"Document Intelligence Panel: {doc_intel_1}")
        
        # Assertions
        assert doc_intel_1 is not None, "Document intelligence is missing in response"
        assert doc_intel_1["normalized_business_name"] == "abc traders"
        assert doc_intel_1["normalized_owner_name"] == "rajesh kumar"
        assert doc_intel_1["mismatch_severity"] == "LOW"
        assert doc_intel_1["consistency_score"] == 100.0
        assert doc_intel_1["document_health_score"] > 0.0
        
        # Verify MongoDB database update
        print("Checking MongoDB document_analysis collection...")
        db = orchestrator.db
        if db is None:
            print("SKIP: MONGO_URI not configured — Atlas connection unavailable")
            return
        analysis_doc = await db.document_analysis.find_one({"application_id": app_id_1})
        print(f"Database Record: {analysis_doc}")
        
        assert analysis_doc is not None
        assert analysis_doc["normalized_business_name"] == "abc traders"
        assert analysis_doc["normalized_owner_name"] == "rajesh kumar"
        assert analysis_doc["consistency_score"] == 100.0
        assert analysis_doc["mismatch_severity"] == "LOW"
        assert "ocr_fallback_used" in analysis_doc
        assert "extraction_errors" in analysis_doc

        # TEST 2: Conditional Credit Score Check for Beginners
        # Beginner Entrepreneurs should skip credit checks. Missing credit score should not penalize.
        print("\n[TEST 2] Testing Beginner Entrepreneur - Credit Score Skip...")
        init_payload_2 = {
            "business_name": "Test Phase 3 Corp",
            "owner_name": "Verification Tester",
            "loan_amount": 50000.0,
            "monthly_revenue": 10000.0,
            "industry": "IT Services",
            "loan_purpose": "Equipment",
            "years_in_business": 1  # Beginner Entrepreneur (< 2 years)
        }
        res = await client.post("/initialize-application", json=init_payload_2)
        data_2 = res.json()
        app_id_2 = data_2["application_id"]
        
        # Upload a doc
        await client.post(
            "/upload-document",
            data={"application_id": app_id_2, "document_type": "Personal ID"},
            files={"file": ("personal_id.png", png_content, "image/png")}
        )
        
        analyze_payload_2 = {
            **init_payload_2,
            "application_id": app_id_2
        }
        res = await client.post("/analyze-loan", json=analyze_payload_2)
        assert res.status_code == 200
        result_2 = res.json()
        fr_2 = result_2["final_response"]
        doc_intel_2 = fr_2["document_intelligence"]
        print(f"Beginner final recommendation: {fr_2['final_recommendation']}")
        print(f"Beginner consistency warnings: {doc_intel_2['mismatch_warnings']}")
        
        # No credit score warning or penalty should exist since beginner credit check is skipped
        credit_warnings = [w for w in doc_intel_2["mismatch_warnings"] if "credit" in w.lower()]
        assert len(credit_warnings) == 0, f"Found credit warnings for beginner: {credit_warnings}"
        
        # TEST 3: Mismatch Severity - CRITICAL Revenue Mismatch
        # Declared Monthly Revenue = 50,000, Extracted Monthly Revenue (from Test Phase 3 Corp defaults) = 10,000.
        # This is a discrepancy of > 50% (actual extracted is 20% of declared).
        # This should trigger CRITICAL severity and result in REJECT.
        print("\n[TEST 3] Testing CRITICAL Revenue Mismatch (>50%)...")
        init_payload_3 = {
            "business_name": "Test Phase 3 Corp",
            "owner_name": "Verification Tester",
            "loan_amount": 50000.0,
            "monthly_revenue": 50000.0,  # 50,000 declared, 10,000 extracted
            "industry": "IT Services",
            "loan_purpose": "Equipment",
            "years_in_business": 5  # Experienced
        }
        res = await client.post("/initialize-application", json=init_payload_3)
        data_3 = res.json()
        app_id_3 = data_3["application_id"]
        
        # Upload credit report
        await client.post(
            "/upload-document",
            data={"application_id": app_id_3, "document_type": "Credit Score Report"},
            files={"file": ("credit.png", png_content, "image/png")}
        )
        
        analyze_payload_3 = {
            **init_payload_3,
            "application_id": app_id_3
        }
        res = await client.post("/analyze-loan", json=analyze_payload_3)
        assert res.status_code == 200
        result_3 = res.json()
        fr_3 = result_3["final_response"]
        doc_intel_3 = fr_3["document_intelligence"]
        
        print(f"Revenue mismatch recommendation: {fr_3['final_recommendation']}")
        print(f"Revenue mismatch severity: {doc_intel_3['mismatch_severity']}")
        print(f"Revenue mismatch warnings: {doc_intel_3['mismatch_warnings']}")
        print(f"Explainability Report:\n{fr_3['explainability_report']}")
        
        assert doc_intel_3["mismatch_severity"] == "CRITICAL"
        assert fr_3["final_recommendation"] == "Reject"
        assert "✗ Revenue mismatch detected" in fr_3["explainability_report"]

        # TEST 4: Mismatch Severity - HIGH Owner Mismatch with Risk Score adjustment (+30)
        # Declared Owner = "Wrong Owner", Extracted Owner = "Verification Tester"
        # This should trigger HIGH severity mismatch, increase risk score by +30 points, and Manual Review.
        print("\n[TEST 4] Testing HIGH Owner Mismatch (Elevated Risk Score)...")
        init_payload_4 = {
            "business_name": "Test Phase 3 Corp",
            "owner_name": "Wrong Owner",  # mismatched owner
            "loan_amount": 50000.0,
            "monthly_revenue": 10000.0,
            "industry": "IT Services",
            "loan_purpose": "Equipment",
            "years_in_business": 5
        }
        res = await client.post("/initialize-application", json=init_payload_4)
        data_4 = res.json()
        app_id_4 = data_4["application_id"]
        
        # Upload credit report
        await client.post(
            "/upload-document",
            data={"application_id": app_id_4, "document_type": "Credit Score Report"},
            files={"file": ("credit.png", png_content, "image/png")}
        )
        
        analyze_payload_4 = {
            **init_payload_4,
            "application_id": app_id_4
        }
        
        # We need to query risk scoring output before adjustment.
        # For ratio <= 5, risk score should be 20. With owner mismatch, it elevates to 50.
        res = await client.post("/analyze-loan", json=analyze_payload_4)
        assert res.status_code == 200
        result_4 = res.json()
        fr_4 = result_4["final_response"]
        doc_intel_4 = fr_4["document_intelligence"]
        
        print(f"Owner mismatch recommendation: {fr_4['final_recommendation']}")
        print(f"Owner mismatch severity: {doc_intel_4['mismatch_severity']}")
        print(f"Owner mismatch warnings: {doc_intel_4['mismatch_warnings']}")
        print(f"Risk Score: {fr_4['risk_score']}")
        
        assert doc_intel_4["mismatch_severity"] == "HIGH"
        # Original risk score = 20 (ratio <= 5). With +30 elevation, it must be 50.
        assert fr_4["risk_score"] == 50, f"Expected risk score 50, got {fr_4['risk_score']}"
        assert fr_4["final_recommendation"] == "Manual Review"
        assert "✗ Owner identity mismatch" in fr_4["explainability_report"]
        
        # Clean up uploads directories
        for app_id in [app_id_1, app_id_2, app_id_3, app_id_4]:
            upload_dir = os.path.join("c:\\Users\\smgal\\Documents\\hw", "uploads", app_id)
            if os.path.exists(upload_dir):
                shutil.rmtree(upload_dir)
        
        print("\n==========================================================")
        print("--- All Phase 3 Integration & Consistency Tests Passed! ---")
        print("==========================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
