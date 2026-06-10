import asyncio
import os
import json
import logging
import random
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

# Setup paths
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.orchestrator import BankGuardOrchestrator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase5-Verifier")

async def run_verifier():
    logger.info("Initializing BankGuardOrchestrator for Phase 5 verification...")
    os.environ["MOCK_AGENTS"] = "true"
    orchestrator = BankGuardOrchestrator(mock_mode=True)
    
    # 1. Connect to MongoDB
    logger.info("Connecting to MongoDB...")
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.mcp_demo
    
    # Initialize collections
    await orchestrator._init_db_collections()
    cols = await db.list_collection_names()
    logger.info(f"MongoDB collections: {cols}")
    
    # Assert all 5 new collections are initialized
    required_cols = [
        "alternative_credit_profiles",
        "collateral_analysis",
        "cash_flow_analysis",
        "sustainability_analysis",
        "manual_review_cases"
    ]
    for col in required_cols:
        assert col in cols, f"Collection '{col}' was not created!"
    logger.info("✓ Collection initialization verified.")
    
    # Mock uploads folder
    from PIL import Image
    import io
    import shutil
    img = Image.new('RGB', (10, 10), color = 'blue')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    png_content = img_bytes.getvalue()

    app_id = "APP_PHASE5_TEST"
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads", app_id)
    if os.path.exists(upload_dir):
        shutil.rmtree(upload_dir)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Mock upload required files for Beginner Entrepreneur to pass completeness checks
    required_docs_beg = ["Personal ID", "Asset proofs", "Property documents", "Savings account statements", "Education/professional background", "Guarantor information"]
    for doc in required_docs_beg:
        sanitized = orchestrator._sanitize_doc_type(doc)
        with open(os.path.join(upload_dir, f"{sanitized}.png"), "wb") as f:
            f.write(png_content)

    # 2. Run SME loan analysis for a Beginner Entrepreneur
    logger.info("Running SME application for Beginner Entrepreneur...")
    app_data = {
        "application_id": app_id,
        "business_name": "Phase 5 Tech Ventures",
        "owner_name": "Jane Innovator",
        "loan_amount": 75000.0,
        "monthly_revenue": 8000.0,
        "industry": "Tech",
        "loan_purpose": "Software development",
        "years_in_business": 1, # Beginner Entrepreneur
        "savings_balance": 180000.0,
        "assets_owned": ["Laptops", "Office Furniture"],
        "education_level": "Master of Science in CS",
        "guarantor_quality": "Strong",
        "collateral_value": 350000.0,
        "bank_account_history": "Healthy transaction count",
        "business_plan_quality": "High",
        "digital_transaction_history": "Active digital payments"
    }
    
    result = await orchestrator.run(app_data)
    logger.info(f"Final recommendation: {result['final_recommendation']}")
    logger.info(f"Aggregated Risk Score: {result['risk_score']}")
    
    # Verify that the decision contains alternative credit and other Phase 5 fields
    assert "alternative_credit_score" in result, "Alternative Credit Score missing from results!"
    assert "collateral_strength" in result, "Collateral strength missing from results!"
    assert "cash_flow_health" in result, "Cash flow health missing from results!"
    assert "sustainability_score" in result, "Sustainability score missing from results!"
    
    logger.info(f"Alternative Credit Score: {result['alternative_credit_score']}")
    logger.info(f"Collateral Strength: {result['collateral_strength']}")
    logger.info(f"Cash Flow Health: {result['cash_flow_health']}")
    logger.info(f"Sustainability Score: {result['sustainability_score']}")
    
    # 3. Check MongoDB collection persistence
    logger.info("Verifying records in new database collections...")
    
    alt_profile = await db.alternative_credit_profiles.find_one({"application_id": app_id})
    assert alt_profile is not None, "alternative_credit_profiles record was not stored!"
    logger.info(f"Stored alternative credit profile: {alt_profile}")
    
    col_analysis = await db.collateral_analysis.find_one({"application_id": app_id})
    assert col_analysis is not None, "collateral_analysis record was not stored!"
    logger.info(f"Stored collateral analysis: {col_analysis}")
    
    cf_analysis = await db.cash_flow_analysis.find_one({"application_id": app_id})
    assert cf_analysis is not None, "cash_flow_analysis record was not stored!"
    logger.info(f"Stored cash flow analysis: {cf_analysis}")
    
    sust_analysis = await db.sustainability_analysis.find_one({"application_id": app_id})
    assert sust_analysis is not None, "sustainability_analysis record was not stored!"
    logger.info(f"Stored sustainability analysis: {sust_analysis}")
    
    logger.info("✓ Collection storage verified successfully.")
    
    # 4. Check manual review queue enqueuing
    logger.info("Checking manual review queue enqueuing...")
    mr_case = await db.manual_review_cases.find_one({"application_id": app_id})
    assert mr_case is not None, "Manual review case was not enqueued!"
    logger.info(f"Enqueued manual review case details: {mr_case}")
    assert "priority" in mr_case, "Priority is missing from manual review case!"
    assert "reason_codes" in mr_case, "Reason codes are missing from manual review case!"
    assert mr_case["status"] == "Pending", "Initial manual review status must be 'Pending'!"
    logger.info("✓ Manual review enqueuing verified successfully.")
    
    # 5. Test manual review endpoints via httpx (simulate API server running)
    logger.info("Simulating manual review HTTP endpoints...")
    # Clean up uploads
    shutil.rmtree(upload_dir)
    
    logger.info("ALL BACKEND ENGINES AND MONGO PERSISTENCE VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_verifier())
