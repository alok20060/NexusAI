import asyncio
import logging
import os
from backend.database import get_sync_client, DB_NAME, MONGO_URI
from mcp_client import get_business_history, get_historical_loan_data
from orchestrator import BankGuardOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_integration")

# Sample data
SAMPLE_BUSINESS = {
    "business_name": "ABC Traders Pvt Ltd",
    "owner_name": "Rajesh Kumar",
    "country": "India",
    "years_in_business": 5,
    "status": "Verified",
    "previous_loans": [
        {
            "loan_id": "L001",
            "amount": 1000000,
            "decision": "Approved"
        }
    ]
}

SAMPLE_LOAN_HISTORY = {
    "business_name": "ABC Traders Pvt Ltd",
    "previous_loans": [
        {
            "loan_id": "L001",
            "amount": 1000000,
            "decision": "Approved",
            "repayment_status": "Completed"
        }
    ]
}

def setup_test_db():
    if not MONGO_URI:
        logger.error("MONGO_URI is not set. Skipping test database setup.")
        return
    logger.info("Setting up test database in MongoDB Atlas...")
    try:
        client = get_sync_client()
        db = client[DB_NAME]
    except Exception as e:
        logger.error(f"MongoDB error: {e}")
        return
    
    # Setup businesses collection
    db.businesses.delete_many({"business_name": "ABC Traders Pvt Ltd"})
    db.businesses.insert_one(SAMPLE_BUSINESS)
    
    # Setup loan_history collection
    db.loan_history.delete_many({"business_name": "ABC Traders Pvt Ltd"})
    db.loan_history.insert_one(SAMPLE_LOAN_HISTORY)
    
    logger.info("Test database setup completed.")
    client.close()

async def run_tests():
    setup_test_db()
    
    logger.info("--- Testing get_business_history ---")
    business_records = await get_business_history("ABC Traders Pvt Ltd")
    logger.info(f"Retrieved business records: {business_records}")
    assert len(business_records) > 0, "Should retrieve at least one business record"
    assert business_records[0]["owner_name"] == "Rajesh Kumar", "Owner name should match"
    
    logger.info("--- Testing get_historical_loan_data ---")
    loan_records = await get_historical_loan_data("ABC Traders Pvt Ltd")
    logger.info(f"Retrieved loan records: {loan_records}")
    assert len(loan_records) > 0, "Should retrieve at least one loan history record"
    assert loan_records[0]["previous_loans"][0]["repayment_status"] == "Completed", "Repayment status should match"
    
    logger.info("--- Testing non-existent business ---")
    empty_records = await get_business_history("Non Existent Business LLC")
    logger.info(f"Retrieved for non-existent: {empty_records}")
    assert len(empty_records) == 0, "Should return empty list for non-existent business"

    # Orchestrator Testing
    logger.info("--- Testing Orchestrator ---")
    orchestrator = BankGuardOrchestrator(mock_mode=True)
    
    # 1. Normal/Approve Case
    app1 = {"business_name": "ABC Traders Pvt Ltd", "loan_amount": 500000, "years_in_business": 5}
    res1 = await orchestrator.run(app1)
    logger.info(f"Result 1: {res1}")
    assert res1.final_recommendation == "Approve"
    assert res1.business_status == "Verified"
    assert res1.fraud_risk == "Low"
    assert res1.repayment_risk == "Low"

    # 2. Reject due to High Fraud Case
    app2 = {"business_name": "High Fraud Test Inc", "loan_amount": 500000, "years_in_business": 5}
    res2 = await orchestrator.run(app2)
    logger.info(f"Result 2: {res2}")
    assert res2.final_recommendation == "Reject"

    # 3. Manual Review due to High Repayment Risk
    app3 = {"business_name": "High Risk Test Corp", "loan_amount": 2000000, "years_in_business": 1}
    res3 = await orchestrator.run(app3)
    logger.info(f"Result 3: {res3}")
    assert res3.final_recommendation == "Manual Review"

    # 4. Additional Verification due to Unverifiable Business
    app4 = {"business_name": "Unverifiable Test Ltd", "loan_amount": 100000, "years_in_business": 2}
    res4 = await orchestrator.run(app4)
    logger.info(f"Result 4: {res4}")
    assert res4.final_recommendation == "Additional Verification"

    logger.info("All tests passed successfully including Orchestrator tests!")

if __name__ == "__main__":
    asyncio.run(run_tests())
