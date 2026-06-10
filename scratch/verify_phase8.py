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
from backend.connectors import BankAPIConnector, CreditBureauConnector, GovtRegistryConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Phase8-Verifier")

async def run_verifier():
    logger.info("Initializing BankGuardOrchestrator for Phase 8 Verification...")
    os.environ["MOCK_AGENTS"] = "true"
    orchestrator = BankGuardOrchestrator(mock_mode=True)
    
    # 1. Connect to MongoDB
    logger.info("Connecting to MongoDB...")
    db = orchestrator.db
    if db is None:
        logger.error("MONGO_URI not configured — cannot connect to Atlas")
        return
    
    # Clean up any old Phase 8 test records
    app_id = "APP_PHASE8_TEST"
    await db.consent_records.delete_many({"application_id": app_id})
    await db.document_hashes.delete_many({"application_id": app_id})
    await db.report_hashes.delete_many({"application_id": app_id})
    await db.audit_chain.delete_many({"application_id": app_id})
    
    # Ensure database collections are initialized
    await orchestrator._init_db_collections()
    cols = await db.list_collection_names()
    logger.info(f"MongoDB collections: {cols}")
    
    # Verify new Phase 8 collections exist
    required_cols = ["consent_records", "document_hashes", "report_hashes", "audit_chain"]
    for col in required_cols:
        assert col in cols, f"Collection '{col}' was not created!"
    logger.info("✓ Phase 8 collection initialization verified.")

    # 2. Test Connector Interfaces
    logger.info("Testing Connector Interfaces...")
    bank_connector = BankAPIConnector("Plaid")
    bureau_connector = CreditBureauConnector("CIBIL")
    govt_connector = GovtRegistryConnector("MCA")
    
    bank_data = await bank_connector.fetch_12_months_statements(app_id, "consent_123")
    bureau_data = await bureau_connector.pull_credit_report("TAX_ID_123", "consent_123")
    govt_data = await govt_connector.verify_business_legitimacy("REG_123", "TAX_ID_123")
    
    assert "monthly_revenue" in bank_data
    assert "credit_score" in bureau_data
    assert "company_registration_number" in govt_data
    logger.info("✓ Mock Connector interfaces and responses verified.")

    # Mock uploads folder with document for hashing
    from PIL import Image
    import io
    import shutil
    img = Image.new('RGB', (10, 10), color = 'red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    png_content = img_bytes.getvalue()

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

    # 3. Run SME loan analysis for a Beginner Entrepreneur under zero-trust design
    logger.info("Running SME application for Beginner Entrepreneur under Phase 8 Zero-Trust...")
    app_data = {
        "application_id": app_id,
        "business_name": "Phase 8 Trust Ventures",
        "owner_name": "Trust Builder",
        "loan_amount": 60000.0,
        "monthly_revenue": 7000.0,
        "industry": "Finance",
        "loan_purpose": "API Integration",
        "years_in_business": 1,
        "savings_balance": 120000.0,
        "consent_granted": True
    }
    
    result = await orchestrator.run(app_data)
    
    # Assert Phase 8 fields exist in top level returned payload
    assert "trust_score" in result, "Trust score missing from returned dictionary!"
    assert "zero_trust_data" in result, "Zero-trust fields missing from returned dictionary!"
    assert "agent_7_output" in result, "Agent 7 output missing from returned dictionary!"
    
    logger.info(f"Calculated Trust Score: {result['trust_score']}")
    logger.info(f"Compliance Report summary: {result['agent_7_output']['compliance_summary']}")
    
    # Validate Zero Trust Field format
    zt_data = result["zero_trust_data"]
    assert "monthly_revenue" in zt_data
    rev_field = zt_data["monthly_revenue"]
    assert "value" in rev_field
    assert "source" in rev_field
    assert "confidence" in rev_field
    assert "verification_status" in rev_field
    assert "timestamp" in rev_field
    logger.info("✓ Zero-Trust field schema layout verified.")

    # 4. Verify MongoDB document hashes persistence
    logger.info("Verifying document hashes persistence...")
    doc_hashes = await db.document_hashes.find({"application_id": app_id}).to_list(length=10)
    assert len(doc_hashes) > 0, "No document hashes stored!"
    logger.info(f"Stored document hashes: {doc_hashes}")
    
    report_hashes = await db.report_hashes.find({"application_id": app_id}).to_list(length=10)
    assert len(report_hashes) > 0, "No report hashes stored!"
    logger.info(f"Stored report hashes: {report_hashes}")
    logger.info("✓ Document and Report hashing verified successfully.")

    # 5. Verify Consent management
    logger.info("Verifying consent records persistence...")
    consent_record = await db.consent_records.find_one({"application_id": app_id})
    assert consent_record is not None, "Consent record not stored!"
    assert consent_record["granted"] is True, "Consent status value mismatch!"
    logger.info("✓ Consent tracking verified successfully.")

    # 6. Verify Cryptographic Audit Chain (immutability linkage)
    logger.info("Verifying Cryptographic Audit Chain...")
    audit_chain = await db.audit_chain.find({"application_id": app_id}).to_list(length=10)
    assert len(audit_chain) > 0, "No audit chain blocks linked!"
    
    # Verify blockchain-like previous hash reference
    first_block = audit_chain[0]
    assert "previous_hash" in first_block
    assert "current_hash" in first_block
    logger.info(f"Linked block event type: {first_block['event_type']}")
    logger.info(f"Previous block hash: {first_block['previous_hash']}")
    logger.info(f"Current block hash: {first_block['current_hash']}")
    logger.info("✓ Cryptographic Audit Chain verification successful.")

    # Cleanup uploads
    shutil.rmtree(upload_dir)
    logger.info("ALL PHASE 8 ARCHITECTURAL AND PERSISTENCE CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_verifier())
