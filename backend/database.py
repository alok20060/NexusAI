"""
Centralized MongoDB Atlas connection for NexusAI-BankGuard.

All backend code must use this module — never hardcode localhost or credentials.
Set MONGO_URI in environment variables (Vercel: Project → Settings → Environment Variables).
"""
import os
import logging
import certifi
from pymongo import MongoClient
from pymongo.errors import (
    ServerSelectionTimeoutError,
    ConfigurationError,
    OperationFailure,
    ConnectionFailure,
)
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger("NexusAI-BankGuardDB")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "BankGuard")

# ── MongoDB Client Creation — certifi CA bundle for Vercel SSL compatibility ──

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


def _log_connection_error(error: Exception, context: str = ""):
    """Log detailed diagnostic info for common Atlas connection failures."""
    err_str = str(error).lower()
    prefix = f"[{context}] " if context else ""

    if "ssl" in err_str or "tls" in err_str or "handshake" in err_str:
        logger.error(
            f"{prefix}SSL/TLS handshake failed. "
            "Ensure certifi is installed and tlsCAFile=certifi.where() is set. "
            f"Detail: {error}"
        )
    elif "authentication" in err_str or "auth" in err_str:
        logger.error(
            f"{prefix}Authentication failed. "
            "Check MONGO_URI username/password and Atlas user permissions. "
            f"Detail: {error}"
        )
    elif "dns" in err_str or "nodename" in err_str or "getaddrinfo" in err_str:
        logger.error(
            f"{prefix}DNS resolution failed. "
            "Check cluster hostname in MONGO_URI and network connectivity. "
            f"Detail: {error}"
        )
    elif "timeout" in err_str or "timed out" in err_str:
        logger.error(
            f"{prefix}Connection timed out. "
            "Check Atlas Network Access IP whitelist (allow 0.0.0.0/0 for Vercel). "
            f"Detail: {error}"
        )
    elif isinstance(error, OperationFailure) or "authorized" in err_str or "collection" in err_str or "permission" in err_str:
        logger.error(
            f"{prefix}Collection access or operation failed. "
            "Verify that the database user has correct readWrite permissions for this collection. "
            f"Detail: {error}"
        )
    else:
        logger.error(f"{prefix}MongoDB error: {error}")


def get_sync_client() -> MongoClient:
    """Return a synchronous MongoClient connected to Atlas."""
    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI environment variable is not set. "
            "Set it to your MongoDB Atlas connection string."
        )
    try:
        client = MongoClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            socketTimeoutMS=60000,
            retryWrites=True
        )
        try:
            client.admin.command("ping")
            print("Atlas connection successful")
        except Exception as e:
            print("Atlas connection failed:", e)
        return client
    except Exception as e:
        _log_connection_error(e, "get_sync_client")
        raise


def get_sync_db():
    """Return the BankGuard database via a synchronous client."""
    client = get_sync_client()
    return client[DB_NAME]


def create_async_client() -> AsyncIOMotorClient:
    """Return an async Motor client connected to Atlas."""
    if not MONGO_URI:
        raise RuntimeError(
            "MONGO_URI environment variable is not set. "
            "Set it to your MongoDB Atlas connection string."
        )
    try:
        client = AsyncIOMotorClient(
            MONGO_URI,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=60000,
            connectTimeoutMS=60000,
            socketTimeoutMS=60000,
            retryWrites=True
        )
        return client
    except Exception as e:
        _log_connection_error(e, "create_async_client")
        raise


async def verify_atlas_connection(db_client: AsyncIOMotorClient) -> dict:
    """Ping Atlas, log startup status, and return a status dict."""
    try:
        await db_client.admin.command("ping")
        db = db_client[DB_NAME]
        collections = await db.list_collection_names()
        
        # Console output as requested
        print("Atlas connection successful")
        print(f"Database name: {DB_NAME}")
        print(f"Number of collections loaded: {len(collections)}")
        
        logger.info("Atlas connection successful")
        logger.info(f"Database name: {DB_NAME}")
        logger.info(f"Number of collections loaded: {len(collections)}")
        
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
        _log_connection_error(e, "verify_atlas_connection")
        return {"connected": False, "error": str(e)}
