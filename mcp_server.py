import os
import logging
from mcp.server.fastmcp import FastMCP
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MongoDB_MCP_Server")

# Initialize FastMCP server
mcp = FastMCP("MongoDB_MCP_Server")

# MongoDB connection settings
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "mcp_demo"

@mcp.tool()
def get_business_history_from_db(business_name: str) -> list:
    """
    Retrieve the business profile and history from the businesses collection in MongoDB.

    Args:
        business_name (str): The name of the business to search for.

    Returns:
        list: A list of matching business documents (without _id).
    """
    logger.info(f"Searching businesses collection for: {business_name}")
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db["businesses"]
            # Case-insensitive exact match
            query = {"business_name": {"$regex": f"^{business_name}$", "$options": "i"}}
            records = list(collection.find(query, {"_id": 0}))
            logger.info(f"Found {len(records)} matching records in businesses collection.")
            return records
    except Exception as e:
        logger.error(f"Error querying businesses collection: {e}", exc_info=True)
        raise e

@mcp.tool()
def get_historical_loan_data_from_db(business_name: str) -> list:
    """
    Retrieve historical loan records for the specified business from the loan_history collection in MongoDB.

    Args:
        business_name (str): The name of the business to search for.

    Returns:
        list: A list of matching loan history documents (without _id).
    """
    logger.info(f"Searching loan_history collection for: {business_name}")
    try:
        with MongoClient(MONGO_URI) as client:
            db = client[DB_NAME]
            collection = db["loan_history"]
            # Case-insensitive exact match
            query = {"business_name": {"$regex": f"^{business_name}$", "$options": "i"}}
            records = list(collection.find(query, {"_id": 0}))
            logger.info(f"Found {len(records)} matching records in loan_history collection.")
            return records
    except Exception as e:
        logger.error(f"Error querying loan_history collection: {e}", exc_info=True)
        raise e

if __name__ == "__main__":
    mcp.run()
