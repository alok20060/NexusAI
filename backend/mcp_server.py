import os
import logging
from mcp.server.fastmcp import FastMCP
from backend.database import get_sync_client, DB_NAME, MONGO_URI

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("MongoDB_MCP_Server")

# Initialize FastMCP server
mcp = FastMCP("MongoDB_MCP_Server")

# ── MongoDB / Atlas connection ────────────────────────────────────────────────
if not MONGO_URI:
    logger.error(
        "MONGO_URI environment variable is not set. "
        "MCP MongoDB tools will return empty results. "
        "Set MONGO_URI to your MongoDB Atlas connection string."
    )


def _get_db():
    """Create a new MongoClient connected to Atlas and return (client, db)."""
    if not MONGO_URI:
        raise RuntimeError("MONGO_URI is not configured. Set the environment variable to your Atlas connection string.")
    try:
        client = get_sync_client()
        return client, client[DB_NAME]
    except Exception as e:
        logger.error(f"MongoDB error: {e}")
        raise


@mcp.tool()
def get_business_history_from_db(business_name: str) -> list:
    """
    Retrieve the business profile and history from the businesses collection in MongoDB Atlas.

    Args:
        business_name (str): The name of the business to search for.

    Returns:
        list: A list of matching business documents (without _id).
    """
    logger.info(f"[Atlas] Searching businesses collection for: {business_name}")
    try:
        client, db = _get_db()
        collection = db["businesses"]
        query = {"business_name": {"$regex": f"^{business_name}$", "$options": "i"}}
        records = list(collection.find(query, {"_id": 0}))
        client.close()
        logger.info(f"[Atlas] Found {len(records)} matching records in businesses collection.")
        return records
    except Exception as e:
        logger.error(f"MongoDB error querying businesses collection: {e}", exc_info=True)
        return []


@mcp.tool()
def get_fraud_cases_from_db(
    business_name: str | None = None,
    owner_name: str | None = None,
    phone: str | None = None,
    address: str | None = None,
    limit: int = 20,
) -> list:
    """
    Query the fraud_cases collection by business_name, owner_name, phone, or address.
    Returns all matching fraud records (without _id).

    Args:
        business_name (str, optional): Business name to match (case-insensitive).
        owner_name (str, optional): Owner name to match (case-insensitive).
        phone (str, optional): Phone number to match exactly.
        address (str, optional): Address to match (case-insensitive).
        limit (int): Maximum number of records to return (default 20).

    Returns:
        list: Matching fraud case documents.
    """
    logger.info(
        f"[Atlas] get_fraud_cases_from_db called with business_name={business_name!r}, "
        f"owner_name={owner_name!r}, phone={phone!r}, address={address!r}"
    )
    try:
        client, db = _get_db()
        collection = db["fraud_cases"]

        conditions = []
        if business_name:
            conditions.append({"business_name": {"$regex": f"^{business_name}$", "$options": "i"}})
        if owner_name:
            conditions.append({"owner_name": {"$regex": f"^{owner_name}$", "$options": "i"}})
        if phone:
            conditions.append({"phone": phone})
        if address:
            conditions.append({"address": {"$regex": address, "$options": "i"}})

        if not conditions:
            logger.warning("get_fraud_cases_from_db called with no filter parameters.")
            client.close()
            return []

        query = {"$or": conditions}
        logger.info(f"[Atlas] MongoDB fraud_cases query: {query}")
        records = list(collection.find(query, {"_id": 0}).limit(limit))
        client.close()
        logger.info(f"[Atlas] Found {len(records)} matching fraud record(s).")
        return records
    except Exception as e:
        logger.error(f"MongoDB error querying fraud_cases collection: {e}", exc_info=True)
        return []


@mcp.tool()
def get_historical_loan_data_from_db(business_name: str) -> list:
    """
    Retrieve historical loan records for the specified business from the loan_history collection in MongoDB Atlas.

    Args:
        business_name (str): The name of the business to search for.

    Returns:
        list: A list of matching loan history documents (without _id).
    """
    logger.info(f"[Atlas] Searching loan_history collection for: {business_name}")
    try:
        client, db = _get_db()
        collection = db["loan_history"]
        query = {"business_name": {"$regex": f"^{business_name}$", "$options": "i"}}
        records = list(collection.find(query, {"_id": 0}))
        client.close()
        logger.info(f"[Atlas] Found {len(records)} matching records in loan_history collection.")
        return records
    except Exception as e:
        logger.error(f"MongoDB error querying loan_history collection: {e}", exc_info=True)
        return []


if __name__ == "__main__":
    mcp.run()
