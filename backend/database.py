"""
Centralized MongoDB Atlas connection for NexusAI-BankGuard.

All backend code must use this module — never hardcode localhost or credentials.
Set MONGO_URI in environment variables (Vercel: Project → Settings → Environment Variables).
"""
import os
import logging
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("NexusAI-BankGuardDB")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "BankGuard")

_CLIENT_KWARGS = {
    "serverSelectionTimeoutMS": 10000,
    "connectTimeoutMS": 10000,
    "socketTimeoutMS": 30000,
    "tls": True,
    "tlsAllowInvalidCertificates": False,
}

REQUIRED_COLLECTIONS = [
    "applications",
    "businesses",
    "fraud_cases",
    "loan_history",
    "applicant_profiles",
    "documents",
    "document_analysis",
    "asset_records",
    "credit_scores",
    "identity_records",
    "audit_logs",
    "decision_history",
]


def get_sync_client() -> MongoClient:
    """Return a synchronous MongoClient connected to Atlas."""
    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI environment variable is not set. "
            "Set it to your MongoDB Atlas connection string."
        )
    return MongoClient(MONGO_URI, **_CLIENT_KWARGS)


def get_sync_db():
    """Return the bankguard database via a synchronous client."""
    client = get_sync_client()
    return client[DB_NAME]


def create_async_client() -> AsyncIOMotorClient:
    """Return an async Motor client connected to Atlas."""
    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI environment variable is not set. "
            "Set it to your MongoDB Atlas connection string."
        )
    return AsyncIOMotorClient(MONGO_URI, **_CLIENT_KWARGS)


async def verify_atlas_connection(db_client: AsyncIOMotorClient) -> dict:
    """Ping Atlas, log startup status, and return a status dict."""
    try:
        await db_client.admin.command("ping")
        db = db_client[DB_NAME]
        collections = await db.list_collection_names()
        logger.info("Atlas connection established")
        logger.info(f"Database selected: {DB_NAME}")
        logger.info(f"Collections loaded successfully ({len(collections)} found)")
        missing = [c for c in REQUIRED_COLLECTIONS if c not in collections]
        if missing:
            logger.warning(
                "Some required collections not yet present (created on first use): %s",
                missing,
            )
        return {
            "connected": True,
            "db_name": DB_NAME,
            "collection_count": len(collections),
            "missing_required": missing,
        }
    except Exception as e:
        logger.error(f"MongoDB error: {e}")
        return {"connected": False, "error": str(e)}
