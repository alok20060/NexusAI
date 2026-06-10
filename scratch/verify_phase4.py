import asyncio
import os
import json
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Setup paths
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.orchestrator import BankGuardOrchestrator
from backend.schemas import LoanAnalysisInput

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase4-Verifier")

async def run_verifier():
    logger.info("Initializing BankGuardOrchestrator...")
    # Set MOCK_AGENTS = True so we use mock agent runs if no real keys, but we still test the orchestrator logic
    os.environ["MOCK_AGENTS"] = "true"
    orchestrator = BankGuardOrchestrator(mock_mode=True)
    
    # Ensure MongoDB is online
    logger.info("Connecting to MongoDB...")
    db = orchestrator.db
    if db is None:
        logger.error("MONGO_URI not configured — cannot connect to Atlas")
        return
    
    # 1. Verify collections are initialized on start
    await orchestrator._init_db_collections()
    cols = await db.list_collection_names()
    logger.info(f"Existing MongoDB collections: {cols}")
    assert "underwriting_intelligence" in cols, "Collection 'underwriting_intelligence' was not created!"
    assert "manual_review_cases" in cols, "Collection 'manual_review_cases' was not created!"
    logger.info("✓ MongoDB collections successfully verified.")
    
    # Write mock documents for Beginner Entrepreneur as valid PNGs
    from PIL import Image
    import io
    import shutil
    img = Image.new('RGB', (10, 10), color = 'green')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    png_content = img_bytes.getvalue()

    beg_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "APP_BEG_TEST")
    if os.path.exists(beg_dir):
        shutil.rmtree(beg_dir)
    os.makedirs(beg_dir, exist_ok=True)
    required_docs_beg = ["Personal ID", "Asset proofs", "Property documents", "Savings account statements", "Education_professional background", "Guarantor information"]
    for doc in required_docs_beg:
        sanitized = doc.lower().replace(" ", "_").replace("/", "_")
        with open(os.path.join(beg_dir, f"{sanitized}.png"), "wb") as f:
            f.write(png_content)
            
    # Write mock documents for Fake Corp
    fake_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "APP_FAKE_TEST")
    if os.path.exists(fake_dir):
        shutil.rmtree(fake_dir)
    os.makedirs(fake_dir, exist_ok=True)
    for doc in required_docs_beg:
        sanitized = doc.lower().replace(" ", "_").replace("/", "_")
        with open(os.path.join(fake_dir, f"{sanitized}.png"), "wb") as f:
            f.write(png_content)

    # 2. Test Experienced Business Owner (ABC Traders)
    logger.info("Testing Experienced Business Owner (ABC Traders) consistency...")
    app_data_abc = {
        "application_id": "APP_ABC_TEST",
        "business_name": "ABC Traders Pvt Ltd",
        "owner_name": "Rajesh Kumar",
        "loan_amount": 500000.0,
        "monthly_revenue": 10000.0,
        "industry": "Retail",
        "loan_purpose": "Inventory expansion",
        "years_in_business": 5,
        "country": "India"
    }
    
    result_abc = await orchestrator.run(app_data_abc)
    logger.info(f"ABC Traders Decision: {result_abc['final_recommendation']}")
    logger.info(f"ABC Traders Risk Score: {result_abc['risk_score']}")
    
    # Verify DB writing for ABC Traders
    intel_abc = await db.underwriting_intelligence.find_one({"application_id": "APP_ABC_TEST"})
    assert intel_abc is not None, "ABC Traders underwriting intelligence record not found!"
    logger.info(f"Extracted entities for ABC: {intel_abc['extracted_entities']}")
    logger.info(f"AI Assessments for ABC: {intel_abc['revenue_assessment']}")
    
    # 3. Test Beginner Entrepreneur (Alternative Credit Scoring)
    logger.info("Testing Beginner Entrepreneur (Alternative Credit Scoring)...")
    app_data_beg = {
        "application_id": "APP_BEG_TEST",
        "business_name": "New Ventures Ltd",
        "owner_name": "Fresh Graduate",
        "loan_amount": 20000.0,
        "monthly_revenue": 2000.0,
        "industry": "Tech",
        "loan_purpose": "Working capital",
        "years_in_business": 1,
        "country": "India"
    }
    
    result_beg = await orchestrator.run(app_data_beg)
    logger.info(f"Beginner Entrepreneur Decision: {result_beg['final_recommendation']}")
    logger.info(f"Beginner Entrepreneur Risk Score: {result_beg['risk_score']}")
    # Risk score should be low/moderate because of Alternative Credit Scoring
    assert result_beg['risk_score'] <= 50, "Beginner Entrepreneur risk score was not correctly adjusted by Alternative Credit Scoring!"
    
    # Check manual review cases
    mr_beg = await db.manual_review_cases.find_one({"application_id": "APP_BEG_TEST"})
    if mr_beg:
        logger.info(f"Beginner Manual Review reasons: {mr_beg['reason']}")
        
    # 4. Test High Mismatch / Fraud Case (Fake Corp)
    logger.info("Testing Critical Mismatch routing (Fake Corp)...")
    app_data_fake = {
        "application_id": "APP_FAKE_TEST",
        "business_name": "Fake Corp Ltd",
        "owner_name": "Fraud User",
        "loan_amount": 100000.0,
        "monthly_revenue": 1000.0,
        "industry": "Shell",
        "loan_purpose": "Suspicious transfer",
        "years_in_business": 1,
        "country": "India"
    }
    
    result_fake = await orchestrator.run(app_data_fake)
    logger.info(f"Fake Corp Decision: {result_fake['final_recommendation']}")
    assert result_fake['final_recommendation'] == "Reject" or result_fake['final_recommendation'] == "Manual Review"
    
    # Fake Corp should have triggered manual review because of mismatch severity
    mr_fake = await db.manual_review_cases.find_one({"application_id": "APP_FAKE_TEST"})
    assert mr_fake is not None, "Fake Corp should have been routed to manual review queue!"
    logger.info(f"Fake Corp manual review trigger reasons: {mr_fake['reason']}")
    logger.info("✓ Manual review queue routing verified.")
    
    # Cleanup test dirs
    import shutil
    for d in [beg_dir, fake_dir]:
        if os.path.exists(d):
            shutil.rmtree(d)

    logger.info("Testing fallback sequence execution...")
    # Simulate a file extraction
    # Create a dummy pdf file on disk
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", "APP_TEMP_TEST")
    os.makedirs(upload_dir, exist_ok=True)
    filepath = os.path.join(upload_dir, "utility_bill.pdf")
    with open(filepath, "w") as f:
        f.write("Business Name: Temp Corp\nOwner Name: Tester\nMonthly Revenue: 5000")
        
    extracted = orchestrator._extract_text_from_file(filepath)
    logger.info(f"Fallback extraction method used: {extracted['method']}")
    assert extracted['text'] != "", "Text extraction returned empty content!"
    logger.info("✓ Fallback sequence successfully verified.")
    
    # Cleanup
    try:
        os.remove(filepath)
        os.rmdir(upload_dir)
    except Exception:
        pass
        
    logger.info("ALL INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_verifier())
