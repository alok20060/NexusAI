"""
create_collections.py — NexusAI-BankGuard Atlas Collection Setup

Creates all required MongoDB collections on Atlas.
Removes all dependency on local MongoDB Compass.

Usage:
    python create_collections.py
    (Requires MONGO_URI env var or .env file)
"""

import os
import sys

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_sync_client, DB_NAME, MONGO_URI

# ── Atlas connection ──────────────────────────────────────────────────────────
if not MONGO_URI:
    print("[FAIL] MONGO_URI environment variable is not set.")
    print("       Set it to your MongoDB Atlas connection string.")
    sys.exit(1)

print("=" * 60)
print("NexusAI-BankGuard — Atlas Collection Setup")
print("=" * 60)

try:
    client = get_sync_client()
    client.admin.command("ping")
    print("Connected to MongoDB Atlas")
except Exception as e:
    print(f"MongoDB Atlas connection failed: {e}")
    sys.exit(1)

db = client[DB_NAME]
print(f"Database selected: {DB_NAME}")

# All collections required by the NexusAI-BankGuard platform
COLLECTIONS = [
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
    "audit_chain",
    "blacklist",
    "previous_rejections",
    "previous_loans",
    "application_timeline",
    "manual_review_cases",
    "underwriting_intelligence",
    "consent_records",
    "document_hashes",
    "report_hashes",
    "alternative_credit_profiles",
    "collateral_analysis",
    "cash_flow_analysis",
    "sustainability_analysis",
    "aadhaar_registry",
    "pan_registry",
    "business_registry",
    "credit_history",
]

existing = db.list_collection_names()
created = []
skipped = []

for col in COLLECTIONS:
    if col not in existing:
        db.create_collection(col)
        created.append(col)
    else:
        skipped.append(col)

print(f"\nAtlas connection established")
print(f"Database selected: {DB_NAME}")
print(f"Collections loaded successfully ({len(existing) + len(created)} total)")

if created:
    print(f"\n  Newly created ({len(created)}):")
    for c in created:
        print(f"    + {c}")
if skipped:
    print(f"\n  Already existed ({len(skipped)}):")
    for c in skipped:
        print(f"    . {c}")

# Final verification
print("\n" + "-" * 60)
print("Collection list:")
print(db.list_collection_names())

client.close()
print("\n[OK] Atlas setup complete. Zero localhost dependencies.")