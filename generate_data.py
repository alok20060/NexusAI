"""
generate_data.py — NexusAI-BankGuard Document-Driven Architecture
Seed Script v2.0

Generates and upserts 100 complete applicant records across all 18
MongoDB collections required by the NexusAI-BankGuard platform.

Safe to run multiple times (idempotent via upsert).
Database : mcp_demo
Connection: mongodb://localhost:27017 (override via MONGO_URI env var)
"""

import hashlib
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

# ──────────────────────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME   = "mcp_demo"
SEED      = 42
NUM_APPS  = 100
DIST      = {"Approved": 60, "Manual Review": 20, "Rejected": 20}

random.seed(SEED)

# ──────────────────────────────────────────────────────────────
# Data pools
# ──────────────────────────────────────────────────────────────
INDIAN_OWNERS = [
    "Rajesh Kumar",      "Amit Patel",        "Priya Sharma",
    "Vikram Singh",      "Sneha Reddy",       "Arjun Mehta",
    "Sanjay Gupta",      "Deepa Nair",        "Anil Verma",
    "Rohan Kapoor",      "Meera Iyer",        "Suresh Pillai",
    "Kavitha Menon",     "Ravi Shankar",      "Pooja Joshi",
    "Manish Tiwari",     "Lalitha Devi",      "Kiran Desai",
    "Harish Malhotra",   "Anita Rao",
]

CITIES = [
    "Mumbai", "Bangalore", "Delhi", "Chennai", "Hyderabad",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Surat",
    "Lucknow", "Nagpur", "Indore", "Coimbatore", "Kochi",
]

STREETS = [
    "MG Road", "Link Road", "Station Road", "Jubilee Hills",
    "Whitefield", "Koramangala", "Banjara Hills", "Connaught Place",
    "Anna Salai", "Brigade Road", "Residency Road", "Nehru Nagar",
]

BIZ_PREFIXES = [
    "Bharath", "Indus", "Ganga", "Kalyan", "Shree",
    "Sri", "Royal", "Prime", "Excel", "Alpha",
    "Pioneer", "Apex", "Zenith", "Summit", "Horizon",
    "Sunrise", "Fortune", "Heritage", "Global", "National",
    "Metro", "Crown", "Diamond", "Platinum", "Golden",
]

BIZ_SECTORS = {
    "Retail & FMCG":    ["Traders",    "Retailers",  "Mart",        "Stores",      "Commerce"],
    "Manufacturing":    ["Industries", "Manufacturing","Factory",    "Productions", "Works"],
    "Services & IT":    ["Solutions",  "Technologies","Systems",     "Digital",     "Infosys"],
    "Agriculture":      ["Agro",       "Farms",       "Agriculture", "Seeds",       "Harvest"],
    "Healthcare":       ["Medicals",   "Healthcare",  "Pharma",      "Clinics",     "LifeCare"],
    "Logistics":        ["Logistics",  "Cargo",       "Transport",   "Express",     "Carriers"],
    "Education":        ["Academy",    "Institute",   "Learning",    "Education",   "Scholars"],
    "Food & Beverage":  ["Foods",      "Beverages",   "Catering",    "Kitchen",     "Spices"],
}

LEGAL_SUFFIXES = ["Pvt Ltd", "Ltd", "LLP", "& Sons", "Enterprises", "Group"]

INDUSTRIES = list(BIZ_SECTORS.keys())

PROFILE_TYPES = ["Beginner Entrepreneur", "Experienced Business Owner", "High Value Applicant"]

DOC_TYPES_REQUIRED = [
    "Aadhaar Card", "PAN Card", "GST Certificate",
    "Bank Statement", "Business Registration Certificate",
    "Utility Bill", "CIBIL Report",
]
DOC_TYPES_OPTIONAL = [
    "Asset Documents", "Property Documents", "Vehicle RC",
    "Investment Statements", "ITR / Tax Returns",
]
ALL_DOC_TYPES = DOC_TYPES_REQUIRED + DOC_TYPES_OPTIONAL

BUREAUS = ["CIBIL", "Experian", "CRIF High Mark", "TransUnion"]

FRAUD_ENTITIES = [
    {"name": "Fake Corp Ltd",         "owner": "Fraud User",        "pan": "FRAUD0001F", "aadhaar": "0000-0000-0001", "gst": "00FRAUD001F1Z5"},
    {"name": "Ghost Enterprises",     "owner": "Ghost Owner",       "pan": "GHOST0002G", "aadhaar": "0000-0000-0002", "gst": "00GHOST002G1Z5"},
    {"name": "Shadow Traders Pvt Ltd","owner": "Shadow Agent",      "pan": "SHADW0003S", "aadhaar": "0000-0000-0003", "gst": "00SHADW003S1Z5"},
    {"name": "Phantom Industries",    "owner": "Phantom Director",  "pan": "PHNTM0004P", "aadhaar": "0000-0000-0004", "gst": "00PHNTM004P1Z5"},
    {"name": "Mirage Solutions",      "owner": "Mirage CEO",        "pan": "MIRAG0005M", "aadhaar": "0000-0000-0005", "gst": "00MIRAG005M1Z5"},
    {"name": "Illusion Finance Ltd",  "owner": "Illusion Owner",    "pan": "ILLUS0006I", "aadhaar": "0000-0000-0006", "gst": "00ILLUS006I1Z5"},
    {"name": "Duplicate Identity Co", "owner": "Clone User",        "pan": "DUPLI0007D", "aadhaar": "0000-0000-0007", "gst": "00DUPLI007D1Z5"},
    {"name": "Blacklisted Ventures",  "owner": "Blacklist Owner",   "pan": "BLACK0008B", "aadhaar": "0000-0000-0008", "gst": "00BLACK008B1Z5"},
    {"name": "Straw Corp Ltd",        "owner": "Straw Director",    "pan": "STRAW0009S", "aadhaar": "0000-0000-0009", "gst": "00STRAW009S1Z5"},
    {"name": "Shell Company PLC",     "owner": "Shell Nominee",     "pan": "SHELL0010S", "aadhaar": "0000-0000-0010", "gst": "00SHELL010S1Z5"},
]

FRAUD_REASONS = [
    "Identity theft / Stolen credentials",
    "Forged bank statements & financial history",
    "Defaulted on multiple identity-theft loans",
    "Straw company setup / Shell corporation",
    "Suspicious business registration mismatch",
    "Multiple simultaneous applications under different names",
    "Duplicate PAN with different identities",
    "Blacklisted address used across multiple applications",
    "Phantom business with no physical presence",
    "Synthetic identity fraud — composite credentials",
]

# ──────────────────────────────────────────────────────────────
# Utility helpers
# ──────────────────────────────────────────────────────────────
def now_iso():
    return datetime.now(timezone.utc).isoformat()

def past_iso(days_ago=0):
    return (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()

def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()

def make_aadhaar():
    return f"{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"

def make_pan(owner: str, idx: int) -> str:
    initials = "".join(w[0].upper() for w in owner.split()[:2]).ljust(2, "A")
    return f"{initials}{''.join([str(random.randint(0,9)) for _ in range(3)])}{chr(65+idx%26)}{random.randint(1000,9999)}{chr(65+(idx*3)%26)}"

def make_gst(pan: str, state_code: int = None) -> str:
    sc = state_code or random.randint(10, 35)
    return f"{sc:02d}{pan[:10]}1Z5"

def make_reg(idx: int, city: str) -> str:
    city_code = city[:3].upper()
    return f"REG-{city_code}-{idx+1000:05d}-IN"

def make_phone():
    return f"+91 {random.randint(70000,99999)} {random.randint(10000,99999)}"

def make_address(city: str):
    n = random.randint(10, 999)
    st = random.choice(STREETS)
    return f"{n}, {st}, {city}, India"

_used_biz_names = set()
def make_biz_name(idx: int) -> tuple:
    sector = INDUSTRIES[idx % len(INDUSTRIES)]
    while True:
        prefix = random.choice(BIZ_PREFIXES)
        suffix = random.choice(BIZ_SECTORS[sector])
        legal  = random.choice(LEGAL_SUFFIXES)
        name   = f"{prefix} {suffix} {legal}"
        if name not in _used_biz_names:
            _used_biz_names.add(name)
            return name, sector

def weighted_decision(idx: int) -> str:
    """Deterministic distribution: 60 Approved, 20 Manual Review, 20 Rejected"""
    if idx < 60:
        return "Approved"
    elif idx < 80:
        return "Manual Review"
    else:
        return "Rejected"

def credit_score_for(decision: str) -> int:
    if decision == "Approved":
        return random.randint(700, 850)
    elif decision == "Manual Review":
        return random.randint(600, 700)
    else:
        return random.randint(300, 600)

def risk_score_for(decision: str) -> int:
    if decision == "Approved":
        return random.randint(0, 30)
    elif decision == "Manual Review":
        return random.randint(31, 60)
    else:
        return random.randint(61, 100)

def trust_score_for(decision: str) -> int:
    if decision == "Approved":
        return random.randint(72, 100)
    elif decision == "Manual Review":
        return random.randint(45, 72)
    else:
        return random.randint(10, 45)

def doc_status_for(doc_type: str, decision: str, is_fraud: bool) -> str:
    if is_fraud:
        return random.choice(["Rejected", "Missing", "Pending"])
    if decision == "Approved":
        if doc_type in DOC_TYPES_REQUIRED:
            return random.choice(["Verified", "Verified", "Verified", "Uploaded"])
        return random.choice(["Verified", "Uploaded", "Missing"])
    elif decision == "Manual Review":
        if doc_type in DOC_TYPES_REQUIRED:
            return random.choice(["Verified", "Uploaded", "Missing"])
        return random.choice(["Uploaded", "Missing", "Pending"])
    else:
        return random.choice(["Missing", "Rejected", "Pending"])

def make_audit_chain_block(event_type: str, app_id: str, block_num: int, prev_hash: str) -> dict:
    content = f"{app_id}:{event_type}:{block_num}:{now_iso()}:{random.random()}"
    current_hash = sha256(content)
    return {
        "event_id":      f"{app_id}-BLK-{block_num:03d}",
        "application_id": app_id,
        "previous_hash": prev_hash,
        "current_hash":  current_hash,
        "event_type":    event_type,
        "timestamp":     now_iso(),
        "block_number":  block_num,
    }

# ──────────────────────────────────────────────────────────────
# Build a shuffle of 100 decision labels (60/20/20)
# ──────────────────────────────────────────────────────────────
decision_pool = (
    ["Approved"]      * DIST["Approved"]     +
    ["Manual Review"] * DIST["Manual Review"] +
    ["Rejected"]      * DIST["Rejected"]
)
random.shuffle(decision_pool)

# ──────────────────────────────────────────────────────────────
# Build all applicants
# ──────────────────────────────────────────────────────────────
applicants = []   # will drive all collections

for idx in range(NUM_APPS):
    app_id   = f"APP{idx+1:03d}"
    owner    = random.choice(INDIAN_OWNERS)
    city     = random.choice(CITIES)
    address  = make_address(city)
    phone    = make_phone()
    decision = decision_pool[idx]
    biz_name, sector = make_biz_name(idx)
    years    = random.randint(1, 18)

    # Profile type
    if years <= 2:
        profile_type = "Beginner Entrepreneur"
    elif years <= 7:
        profile_type = "Experienced Business Owner"
    else:
        profile_type = "High Value Applicant"

    aadhaar  = make_aadhaar()
    pan      = make_pan(owner, idx)
    gst      = make_gst(pan)
    reg_no   = make_reg(idx, city)

    credit_score = credit_score_for(decision)
    risk_sc      = risk_score_for(decision)
    trust_sc     = trust_score_for(decision)
    bureau       = random.choice(BUREAUS)

    loan_amount   = random.randint(100, 5000) * 10000
    monthly_rev   = int(loan_amount * random.uniform(0.3, 4.0) / 12)
    annual_rev    = monthly_rev * 12
    existing_debt = int(loan_amount * random.uniform(0.0, 0.5))

    # Asset generation — stronger for approved
    if decision == "Approved":
        prop_val  = random.randint(2000000, 20000000)
        veh_val   = random.randint(200000, 2000000)
        invest    = random.randint(100000, 5000000)
        fd_val    = random.randint(50000, 2000000)
    elif decision == "Manual Review":
        prop_val  = random.randint(500000, 5000000)
        veh_val   = random.randint(50000, 500000)
        invest    = random.randint(10000, 500000)
        fd_val    = random.randint(10000, 200000)
    else:
        prop_val  = random.randint(0, 1000000)
        veh_val   = random.randint(0, 100000)
        invest    = random.randint(0, 50000)
        fd_val    = random.randint(0, 50000)

    total_assets = prop_val + veh_val + invest + fd_val

    applicants.append({
        "app_id":        app_id,
        "owner":         owner,
        "city":          city,
        "address":       address,
        "phone":         phone,
        "decision":      decision,
        "biz_name":      biz_name,
        "sector":        sector,
        "years":         years,
        "profile_type":  profile_type,
        "aadhaar":       aadhaar,
        "pan":           pan,
        "gst":           gst,
        "reg_no":        reg_no,
        "credit_score":  credit_score,
        "risk_score":    risk_sc,
        "trust_score":   trust_sc,
        "bureau":        bureau,
        "loan_amount":   loan_amount,
        "monthly_rev":   monthly_rev,
        "annual_rev":    annual_rev,
        "existing_debt": existing_debt,
        "prop_val":      prop_val,
        "veh_val":       veh_val,
        "invest":        invest,
        "fd_val":        fd_val,
        "total_assets":  total_assets,
        "is_fraud":      False,
    })

# ──────────────────────────────────────────────────────────────
# Connect & seed
# ──────────────────────────────────────────────────────────────
print("=" * 60)
print("NexusAI-BankGuard — MongoDB Seed Script v2.0")
print("=" * 60)
print(f"Connecting to {MONGO_URI} / database: {DB_NAME}")

client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
try:
    client.admin.command("ping")
    print("[OK] MongoDB connection successful")
except Exception as e:
    print(f"[FAIL] Cannot connect to MongoDB: {e}")
    sys.exit(1)

db = client[DB_NAME]

# Ensure all required collections exist
REQUIRED_COLLECTIONS = [
    "applications", "documents", "document_analysis", "applicant_profiles",
    "asset_records", "fraud_cases", "business_registry", "aadhaar_registry",
    "pan_registry", "credit_history", "decision_history", "audit_chain",
    "blacklist", "previous_rejections", "previous_loans", "application_timeline",
    "manual_review_cases", "underwriting_intelligence", "consent_records",
    "document_hashes", "report_hashes", "alternative_credit_profiles",
    "collateral_analysis", "cash_flow_analysis", "sustainability_analysis",
]
existing_cols = db.list_collection_names()
created_cols  = []
for col in REQUIRED_COLLECTIONS:
    if col not in existing_cols:
        db.create_collection(col)
        created_cols.append(col)
print(f"[OK] Collections ensured ({len(created_cols)} newly created)")

# ──────────────────────────────────────────────────────────────
# 1. fraud_cases  (10 fraud entities + existing FC*** records)
# ──────────────────────────────────────────────────────────────
print("\n[1/18] Seeding fraud_cases ...")
fraud_ops = []
for i, fe in enumerate(FRAUD_ENTITIES):
    doc = {
        "case_id":     f"FC{i+1:03d}",
        "business_name": fe["name"],
        "owner_name":  fe["owner"],
        "pan":         fe["pan"],
        "aadhaar":     fe["aadhaar"],
        "reason":      FRAUD_REASONS[i],
        "fraud_risk":  "High",
        "status":      "Active",
        "reported_at": past_iso(random.randint(1, 365)),
        "phone":       f"+91 {random.randint(90000,99999)} {random.randint(10000,99999)}",
        "address":     f"{random.randint(1,999)}, Fraud Lane, Mumbai, India",
    }
    fraud_ops.append(UpdateOne({"case_id": doc["case_id"]}, {"$set": doc}, upsert=True))
if fraud_ops:
    db.fraud_cases.bulk_write(fraud_ops)
print(f"    Upserted {len(FRAUD_ENTITIES)} fraud entities")

# ──────────────────────────────────────────────────────────────
# 2. blacklist
# ──────────────────────────────────────────────────────────────
print("[2/18] Seeding blacklist ...")
bl_records = []
for fe in FRAUD_ENTITIES:
    bl_records += [
        {"type": "pan",    "value": fe["pan"],    "reason": "Fraudulent PAN"},
        {"type": "aadhaar","value": fe["aadhaar"], "reason": "Forged Aadhaar"},
        {"type": "business_name", "value": fe["name"], "reason": "Blacklisted entity"},
    ]
bl_ops = [UpdateOne({"type": r["type"], "value": r["value"]}, {"$set": r}, upsert=True) for r in bl_records]
if bl_ops:
    db.blacklist.bulk_write(bl_ops)
print(f"    Upserted {len(bl_records)} blacklist entries")

# ──────────────────────────────────────────────────────────────
# 3. aadhaar_registry
# ──────────────────────────────────────────────────────────────
print("[3/18] Seeding aadhaar_registry ...")
aadhaar_ops = []
for a in applicants:
    doc = {
        "aadhaar_number": a["aadhaar"],
        "name":           a["owner"],
        "address":        a["address"],
        "dob":            f"{random.randint(1965,2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "status":         "Active",
        "verified_at":    past_iso(random.randint(30, 730)),
    }
    aadhaar_ops.append(UpdateOne({"aadhaar_number": doc["aadhaar_number"]}, {"$set": doc}, upsert=True))
if aadhaar_ops:
    db.aadhaar_registry.bulk_write(aadhaar_ops)
print(f"    Upserted {len(aadhaar_ops)} Aadhaar records")

# ──────────────────────────────────────────────────────────────
# 4. pan_registry
# ──────────────────────────────────────────────────────────────
print("[4/18] Seeding pan_registry ...")
pan_ops = []
for a in applicants:
    doc = {
        "pan_number":  a["pan"],
        "name":        a["owner"],
        "aadhaar_linked": a["aadhaar"],
        "status":      "Active",
        "verified_at": past_iso(random.randint(30, 730)),
    }
    pan_ops.append(UpdateOne({"pan_number": doc["pan_number"]}, {"$set": doc}, upsert=True))
if pan_ops:
    db.pan_registry.bulk_write(pan_ops)
print(f"    Upserted {len(pan_ops)} PAN records")

# ──────────────────────────────────────────────────────────────
# 5. business_registry
# ──────────────────────────────────────────────────────────────
print("[5/18] Seeding business_registry ...")
biz_ops = []
for a in applicants:
    doc = {
        "registration_number": a["reg_no"],
        "business_name":       a["biz_name"],
        "owner_name":          a["owner"],
        "address":             a["address"],
        "gst_number":          a["gst"],
        "pan_number":          a["pan"],
        "industry":            a["sector"],
        "years_in_business":   a["years"],
        "city":                a["city"],
        "status": (
            "Active" if a["decision"] == "Approved"
            else "Under Review" if a["decision"] == "Manual Review"
            else "Inactive"
        ),
        "registered_at": past_iso(a["years"] * 365),
    }
    biz_ops.append(UpdateOne({"registration_number": doc["registration_number"]}, {"$set": doc}, upsert=True))
if biz_ops:
    db.business_registry.bulk_write(biz_ops)
print(f"    Upserted {len(biz_ops)} business registry records")

# ──────────────────────────────────────────────────────────────
# 6. credit_history
# ──────────────────────────────────────────────────────────────
print("[6/18] Seeding credit_history ...")
ch_ops = []
for a in applicants:
    score = a["credit_score"]
    rating = "Excellent" if score >= 800 else "Good" if score >= 700 else "Fair" if score >= 600 else "Poor"
    doc = {
        "pan_number":      a["pan"],
        "business_name":   a["biz_name"],
        "bureau_name":     a["bureau"],
        "credit_score":    score,
        "cibil_rating":    rating,
        "loan_count":      random.randint(0, 5),
        "default_history": a["decision"] == "Rejected",
        "default_count":   random.randint(0, 3) if a["decision"] == "Rejected" else 0,
        "active_loans":    random.randint(0, 3),
        "credit_utilization": round(random.uniform(0.1, 0.9), 2),
        "oldest_account_years": random.randint(1, a["years"] + 1),
        "last_updated":    past_iso(random.randint(1, 90)),
        "consent_status":  "granted",
        "pull_timestamp":  past_iso(random.randint(1, 30)),
    }
    ch_ops.append(UpdateOne({"pan_number": doc["pan_number"]}, {"$set": doc}, upsert=True))
if ch_ops:
    db.credit_history.bulk_write(ch_ops)
print(f"    Upserted {len(ch_ops)} credit history records")

# ──────────────────────────────────────────────────────────────
# 7. applications
# ──────────────────────────────────────────────────────────────
print("[7/18] Seeding applications ...")
app_ops = []
for a in applicants:
    doc = {
        "application_id":   a["app_id"],
        "business_name":    a["biz_name"],
        "owner_name":       a["owner"],
        "industry":         a["sector"],
        "city":             a["city"],
        "address":          a["address"],
        "phone":            a["phone"],
        "email":            f"info@{a['biz_name'].lower().replace(' ','').replace('.','')[:20]}.in",
        "loan_amount":      a["loan_amount"],
        "monthly_revenue":  a["monthly_rev"],
        "annual_revenue":   a["annual_rev"],
        "existing_debt":    a["existing_debt"],
        "years_in_business":a["years"],
        "loan_purpose":     random.choice([
            "Working capital expansion", "Equipment purchase",
            "Business expansion", "Inventory financing",
            "Debt refinancing", "Technology upgrade",
        ]),
        "pan_number":       a["pan"],
        "aadhaar_number":   a["aadhaar"],
        "gst_number":       a["gst"],
        "registration_number": a["reg_no"],
        "decision":         a["decision"],
        "risk_score":       a["risk_score"],
        "trust_score":      a["trust_score"],
        "credit_score":     a["credit_score"],
        "profile_type":     a["profile_type"],
        "submitted_at":     past_iso(random.randint(1, 180)),
        "status":           "Completed",
    }
    app_ops.append(UpdateOne({"application_id": doc["application_id"]}, {"$set": doc}, upsert=True))
if app_ops:
    db.applications.bulk_write(app_ops)
print(f"    Upserted {len(app_ops)} application records")

# ──────────────────────────────────────────────────────────────
# 8. documents
# ──────────────────────────────────────────────────────────────
print("[8/18] Seeding documents ...")
doc_ops = []
for a in applicants:
    for doc_type in ALL_DOC_TYPES:
        status = doc_status_for(doc_type, a["decision"], a["is_fraud"])
        required = doc_type in DOC_TYPES_REQUIRED
        file_hash = sha256(f"{a['app_id']}:{doc_type}:{random.random()}") if status in ("Uploaded", "Verified") else None
        rec = {
            "document_id":    f"{a['app_id']}-{doc_type[:4].upper().replace(' ','')}",
            "application_id": a["app_id"],
            "document_type":  doc_type,
            "upload_status":  status,
            "required":       required,
            "sha256_hash":    file_hash,
            "uploaded_at":    past_iso(random.randint(1, 60)) if status != "Missing" else None,
            "verified_at":    past_iso(random.randint(1, 30)) if status == "Verified" else None,
        }
        doc_ops.append(UpdateOne(
            {"application_id": a["app_id"], "document_type": doc_type},
            {"$set": rec}, upsert=True
        ))
if doc_ops:
    db.documents.bulk_write(doc_ops)
print(f"    Upserted {len(doc_ops)} document records")

# ──────────────────────────────────────────────────────────────
# 9. document_analysis
# ──────────────────────────────────────────────────────────────
print("[9/18] Seeding document_analysis ...")
da_ops = []
for a in applicants:
    if a["decision"] == "Approved":
        completeness = round(random.uniform(0.75, 1.0), 3)
        consistency  = round(random.uniform(0.80, 1.0), 3)
        ocr_conf     = round(random.uniform(0.85, 0.99), 3)
        mismatches   = random.randint(0, 1)
    elif a["decision"] == "Manual Review":
        completeness = round(random.uniform(0.50, 0.80), 3)
        consistency  = round(random.uniform(0.55, 0.80), 3)
        ocr_conf     = round(random.uniform(0.65, 0.85), 3)
        mismatches   = random.randint(1, 3)
    else:
        completeness = round(random.uniform(0.10, 0.55), 3)
        consistency  = round(random.uniform(0.10, 0.55), 3)
        ocr_conf     = round(random.uniform(0.30, 0.70), 3)
        mismatches   = random.randint(3, 8)

    rec = {
        "application_id":    a["app_id"],
        "completeness_score": completeness,
        "consistency_score":  consistency,
        "ocr_confidence":     ocr_conf,
        "mismatch_count":     mismatches,
        "verified_fields": [
            "business_name", "owner_name", "pan_number", "aadhaar_number",
        ] if a["decision"] in ("Approved", "Manual Review") else ["business_name"],
        "mismatch_fields": [
            "address", "revenue"
        ] if mismatches > 1 else [],
        "mismatch_severity": (
            "LOW" if mismatches == 0 else
            "MEDIUM" if mismatches <= 2 else "HIGH"
        ),
        "analyzed_at": past_iso(random.randint(1, 30)),
    }
    da_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": rec}, upsert=True))
if da_ops:
    db.document_analysis.bulk_write(da_ops)
print(f"    Upserted {len(da_ops)} document_analysis records")

# ──────────────────────────────────────────────────────────────
# 10. applicant_profiles
# ──────────────────────────────────────────────────────────────
print("[10/18] Seeding applicant_profiles ...")
ap_ops = []
for a in applicants:
    doc = {
        "application_id":  a["app_id"],
        "owner_name":      a["owner"],
        "business_name":   a["biz_name"],
        "profile_type":    a["profile_type"],
        "industry":        a["sector"],
        "years_in_business": a["years"],
        "city":            a["city"],
        "risk_tier":       (
            "Low" if a["decision"] == "Approved" else
            "Medium" if a["decision"] == "Manual Review" else "High"
        ),
        "fraud_risk":      (
            "Low" if a["decision"] == "Approved" else
            "Medium" if a["decision"] == "Manual Review" else "High"
        ),
        "repayment_risk":  (
            "Low" if a["decision"] == "Approved" else
            "Medium" if a["decision"] == "Manual Review" else "High"
        ),
        "profiled_at":     past_iso(random.randint(1, 60)),
    }
    ap_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if ap_ops:
    db.applicant_profiles.bulk_write(ap_ops)
print(f"    Upserted {len(ap_ops)} applicant_profile records")

# ──────────────────────────────────────────────────────────────
# 11. asset_records
# ──────────────────────────────────────────────────────────────
print("[11/18] Seeding asset_records ...")
ar_ops = []
for a in applicants:
    doc = {
        "application_id": a["app_id"],
        "owner_name":     a["owner"],
        "property_value": a["prop_val"],
        "vehicle_value":  a["veh_val"],
        "investments":    a["invest"],
        "fixed_deposits": a["fd_val"],
        "total_assets":   a["total_assets"],
        "collateral_type": (
            "Property" if a["prop_val"] > 2000000 else
            "Vehicle"  if a["veh_val"] > 500000  else
            "Fixed Deposit"
        ),
        "collateral_strength": (
            "Strong"   if a["total_assets"] > 5000000 else
            "Moderate" if a["total_assets"] > 1000000 else "Weak"
        ),
        "verified_at": past_iso(random.randint(1, 60)),
    }
    ar_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if ar_ops:
    db.asset_records.bulk_write(ar_ops)
print(f"    Upserted {len(ar_ops)} asset_record records")

# ──────────────────────────────────────────────────────────────
# 12. decision_history
# ──────────────────────────────────────────────────────────────
print("[12/18] Seeding decision_history ...")
dh_ops = []
for a in applicants:
    ref_id   = f"NBG-{sha256(a['app_id'])[:6].upper()}"
    conf     = (
        round(random.uniform(0.80, 0.99), 3) if a["decision"] == "Approved"  else
        round(random.uniform(0.55, 0.80), 3) if a["decision"] == "Manual Review" else
        round(random.uniform(0.70, 0.95), 3)
    )
    reason_codes = []
    if a["decision"] == "Approved":
        reason_codes = random.sample(["LOW_RISK", "STRONG_FINANCIALS", "VERIFIED_DOCS", "CLEAN_CREDIT", "ASSET_BACKED"], k=random.randint(2,4))
    elif a["decision"] == "Manual Review":
        reason_codes = random.sample(["BORDERLINE_SCORE", "PARTIAL_DOCS", "MEDIUM_RISK", "MANUAL_REQUIRED"], k=random.randint(1,3))
    else:
        reason_codes = random.sample(["HIGH_RISK", "POOR_CREDIT", "MISSING_DOCS", "FRAUD_SIGNAL", "EXCESS_DEBT"], k=random.randint(2,4))

    doc = {
        "application_id":     a["app_id"],
        "reference_id":       ref_id,
        "final_recommendation": a["decision"],
        "confidence":         conf,
        "risk_score":         a["risk_score"],
        "trust_score":        a["trust_score"],
        "credit_score":       a["credit_score"],
        "reason_codes":       reason_codes,
        "loan_amount":        a["loan_amount"],
        "decided_at":         past_iso(random.randint(0, 30)),
    }
    dh_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if dh_ops:
    db.decision_history.bulk_write(dh_ops)
print(f"    Upserted {len(dh_ops)} decision_history records")

# ──────────────────────────────────────────────────────────────
# 13. audit_chain
# ──────────────────────────────────────────────────────────────
print("[13/18] Seeding audit_chain ...")
ac_ops = []
EVENTS = [
    "ApplicationSubmitted", "DocumentsReceived", "OCRCompleted",
    "RegistryVerified", "FraudCheck", "CreditBureauPull",
    "RiskScoringComplete", "UnderwritingDecision",
]
for a in applicants:
    prev_hash = "0" * 64
    for block_num, event in enumerate(EVENTS):
        block = make_audit_chain_block(event, a["app_id"], block_num, prev_hash)
        prev_hash = block["current_hash"]
        ac_ops.append(UpdateOne(
            {"event_id": block["event_id"]},
            {"$set": block}, upsert=True
        ))
if ac_ops:
    db.audit_chain.bulk_write(ac_ops)
print(f"    Upserted {len(ac_ops)} audit_chain blocks ({len(EVENTS)} per applicant)")

# ──────────────────────────────────────────────────────────────
# 14. alternative_credit_profiles (Beginner Entrepreneurs)
# ──────────────────────────────────────────────────────────────
print("[14/18] Seeding alternative_credit_profiles ...")
acp_ops = []
for a in applicants:
    if a["profile_type"] != "Beginner Entrepreneur":
        continue
    asset_strength = min(100, int(a["total_assets"] / 100000))
    guarantor_q    = random.randint(40, 90) if a["decision"] != "Rejected" else random.randint(10, 50)
    edu_score      = random.randint(50, 100)
    digital_score  = random.randint(30, 100)
    alt_score      = int((asset_strength * 0.3 + guarantor_q * 0.3 + edu_score * 0.2 + digital_score * 0.2))
    doc = {
        "application_id":          a["app_id"],
        "owner_name":              a["owner"],
        "savings_balance":         random.randint(10000, 500000),
        "asset_strength":          asset_strength,
        "guarantor_quality":       guarantor_q,
        "education_score":         edu_score,
        "digital_transaction_score": digital_score,
        "bank_account_age_years":  random.randint(1, 10),
        "business_plan_score":     random.randint(40, 100),
        "alternative_credit_score": min(100, alt_score),
        "computed_at":             past_iso(random.randint(1, 30)),
    }
    acp_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if acp_ops:
    db.alternative_credit_profiles.bulk_write(acp_ops)
print(f"    Upserted {len(acp_ops)} alternative_credit_profile records")

# ──────────────────────────────────────────────────────────────
# 15. collateral_analysis
# ──────────────────────────────────────────────────────────────
print("[15/18] Seeding collateral_analysis ...")
ca_ops = []
for a in applicants:
    strength = (
        "Strong"   if a["total_assets"] > 5000000 else
        "Moderate" if a["total_assets"] > 1000000 else "Weak"
    )
    doc = {
        "application_id":  a["app_id"],
        "property_value":  a["prop_val"],
        "vehicle_value":   a["veh_val"],
        "investments":     a["invest"],
        "fixed_deposits":  a["fd_val"],
        "collateral_value":  a["total_assets"],
        "collateral_strength": strength,
        "ltv_ratio": round(a["loan_amount"] / max(a["total_assets"], 1), 3),
        "analyzed_at": past_iso(random.randint(1, 30)),
    }
    ca_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if ca_ops:
    db.collateral_analysis.bulk_write(ca_ops)
print(f"    Upserted {len(ca_ops)} collateral_analysis records")

# ──────────────────────────────────────────────────────────────
# 16. cash_flow_analysis
# ──────────────────────────────────────────────────────────────
print("[16/18] Seeding cash_flow_analysis ...")
cf_ops = []
for a in applicants:
    if a["decision"] == "Approved":
        rev_stability = round(random.uniform(0.70, 1.0), 3)
        exp_ratio     = round(random.uniform(0.30, 0.60), 3)
        debt_ratio    = round(random.uniform(0.10, 0.35), 3)
        health        = "Healthy"
    elif a["decision"] == "Manual Review":
        rev_stability = round(random.uniform(0.45, 0.75), 3)
        exp_ratio     = round(random.uniform(0.55, 0.75), 3)
        debt_ratio    = round(random.uniform(0.30, 0.55), 3)
        health        = "Moderate"
    else:
        rev_stability = round(random.uniform(0.10, 0.50), 3)
        exp_ratio     = round(random.uniform(0.70, 0.95), 3)
        debt_ratio    = round(random.uniform(0.55, 0.90), 3)
        health        = "Stressed"

    doc = {
        "application_id":    a["app_id"],
        "monthly_revenue":   a["monthly_rev"],
        "annual_revenue":    a["annual_rev"],
        "existing_debt":     a["existing_debt"],
        "revenue_stability": rev_stability,
        "expense_ratio":     exp_ratio,
        "debt_ratio":        debt_ratio,
        "cash_flow_health":  health,
        "avg_monthly_balance": int(a["monthly_rev"] * random.uniform(0.5, 3.0)),
        "analyzed_at": past_iso(random.randint(1, 30)),
    }
    cf_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if cf_ops:
    db.cash_flow_analysis.bulk_write(cf_ops)
print(f"    Upserted {len(cf_ops)} cash_flow_analysis records")

# ──────────────────────────────────────────────────────────────
# 17. sustainability_analysis
# ──────────────────────────────────────────────────────────────
print("[17/18] Seeding sustainability_analysis ...")
sa_ops = []
INDUSTRY_RISKS = {
    "Retail & FMCG": "Low", "Manufacturing": "Medium", "Services & IT": "Low",
    "Agriculture": "High", "Healthcare": "Low", "Logistics": "Medium",
    "Education": "Low", "Food & Beverage": "Medium",
}
for a in applicants:
    if a["decision"] == "Approved":
        growth_score  = random.randint(60, 100)
        cust_stability= round(random.uniform(0.65, 1.0), 3)
        sustain_score = random.randint(60, 100)
    elif a["decision"] == "Manual Review":
        growth_score  = random.randint(35, 70)
        cust_stability= round(random.uniform(0.40, 0.70), 3)
        sustain_score = random.randint(35, 65)
    else:
        growth_score  = random.randint(5, 40)
        cust_stability= round(random.uniform(0.10, 0.45), 3)
        sustain_score = random.randint(5, 40)

    doc = {
        "application_id":    a["app_id"],
        "industry":          a["sector"],
        "years_in_business": a["years"],
        "growth_score":      growth_score,
        "industry_risk":     INDUSTRY_RISKS.get(a["sector"], "Medium"),
        "customer_stability": cust_stability,
        "sustainability_score": sustain_score,
        "analyzed_at": past_iso(random.randint(1, 30)),
    }
    sa_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if sa_ops:
    db.sustainability_analysis.bulk_write(sa_ops)
print(f"    Upserted {len(sa_ops)} sustainability_analysis records")

# ──────────────────────────────────────────────────────────────
# 18. manual_review_cases
# ──────────────────────────────────────────────────────────────
print("[18/18] Seeding manual_review_cases ...")
mr_ops = []
for a in applicants:
    if a["decision"] not in ("Manual Review", "Rejected"):
        continue
    priority = "HIGH" if a["risk_score"] > 70 else "MEDIUM" if a["risk_score"] > 40 else "LOW"
    reason_codes = []
    if a["risk_score"] > 60:
        reason_codes.append("HIGH_RISK_SCORE")
    if a["credit_score"] < 650:
        reason_codes.append("LOW_CREDIT_SCORE")
    if a["decision"] == "Rejected":
        reason_codes.append("AUTO_REJECT_TRIGGER")
    if not reason_codes:
        reason_codes = ["BORDERLINE_METRICS"]

    doc = {
        "application_id": a["app_id"],
        "business_name":  a["biz_name"],
        "owner_name":     a["owner"],
        "loan_amount":    a["loan_amount"],
        "risk_score":     a["risk_score"],
        "trust_score":    a["trust_score"],
        "credit_score":   a["credit_score"],
        "priority":       priority,
        "reason_codes":   reason_codes,
        "review_status":  "Pending",
        "assigned_to":    None,
        "reviewer_notes": None,
        "created_at":     past_iso(random.randint(0, 30)),
    }
    mr_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": doc}, upsert=True))
if mr_ops:
    db.manual_review_cases.bulk_write(mr_ops)
print(f"    Upserted {len(mr_ops)} manual_review_cases records")

# ──────────────────────────────────────────────────────────────
# Also seed: previous_loans, previous_rejections, consent_records
# ──────────────────────────────────────────────────────────────
prev_loan_ops = []
prev_rej_ops  = []
consent_ops   = []

for a in applicants:
    if a["decision"] == "Approved" and a["years"] > 3:
        pl = {
            "application_id": a["app_id"],
            "business_name":  a["biz_name"],
            "loan_id":        f"L-{a['app_id']}",
            "amount":         int(a["loan_amount"] * 0.6),
            "repayment_status": random.choice(["Completed", "Active"]),
            "decision":       "Approved",
        }
        prev_loan_ops.append(UpdateOne({"loan_id": pl["loan_id"]}, {"$set": pl}, upsert=True))

    if a["decision"] == "Rejected":
        pr = {
            "application_id": a["app_id"],
            "business_name":  a["biz_name"],
            "owner_name":     a["owner"],
            "rejected_at":    past_iso(random.randint(30, 360)),
            "reason":         random.choice([
                "Excessive existing liabilities", "Poor credit history",
                "Insufficient documentation", "Fraud signal detected",
                "Revenue insufficient for loan amount",
            ]),
        }
        prev_rej_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": pr}, upsert=True))

    # Consent record for every applicant
    cr = {
        "application_id":   a["app_id"],
        "owner_name":       a["owner"],
        "consent_type":     "full_credit_bureau_pull",
        "granted":          True,
        "granted_at":       past_iso(random.randint(1, 60)),
        "expires_at":       past_iso(-365),   # future
        "consent_version":  "v2.1",
        "ip_address":       f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
    }
    consent_ops.append(UpdateOne({"application_id": a["app_id"]}, {"$set": cr}, upsert=True))

if prev_loan_ops:
    db.previous_loans.bulk_write(prev_loan_ops)
if prev_rej_ops:
    db.previous_rejections.bulk_write(prev_rej_ops)
if consent_ops:
    db.consent_records.bulk_write(consent_ops)

print(f"\n    Extra collections:")
print(f"      previous_loans       : {len(prev_loan_ops)} records")
print(f"      previous_rejections  : {len(prev_rej_ops)} records")
print(f"      consent_records      : {len(consent_ops)} records")

# ──────────────────────────────────────────────────────────────
# Summary Report
# ──────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SEED SUMMARY REPORT")
print("=" * 60)

decisions = [a["decision"] for a in applicants]
print(f"\n[Dataset Statistics]")
print(f"  Total applicants    : {NUM_APPS}")
print(f"  Approved            : {decisions.count('Approved')}")
print(f"  Manual Review       : {decisions.count('Manual Review')}")
print(f"  Rejected            : {decisions.count('Rejected')}")

profiles = [a["profile_type"] for a in applicants]
print(f"\n[Profile Types]")
for pt in PROFILE_TYPES:
    print(f"  {pt:<30}: {profiles.count(pt)}")

print(f"\n[Fraud Entities Seeded]")
for fe in FRAUD_ENTITIES:
    print(f"  {fe['name']:<35} | PAN: {fe['pan']}")

risk_scores   = [a["risk_score"]   for a in applicants]
trust_scores  = [a["trust_score"]  for a in applicants]
credit_scores = [a["credit_score"] for a in applicants]
print(f"\n[Score Distributions]")
print(f"  Risk Score   — min: {min(risk_scores):3d}  max: {max(risk_scores):3d}  avg: {sum(risk_scores)//len(risk_scores):3d}")
print(f"  Trust Score  — min: {min(trust_scores):3d}  max: {max(trust_scores):3d}  avg: {sum(trust_scores)//len(trust_scores):3d}")
print(f"  Credit Score — min: {min(credit_scores):3d}  max: {max(credit_scores):3d}  avg: {sum(credit_scores)//len(credit_scores):3d}")

print(f"\n[Collections Created/Updated]")
for col in REQUIRED_COLLECTIONS:
    count = db[col].count_documents({})
    print(f"  {col:<35}: {count:>5} documents")

print(f"\n[Sample Records]")
sample = applicants[0]
print(f"  APP001 — {sample['biz_name']}")
print(f"    Owner    : {sample['owner']}")
print(f"    Decision : {sample['decision']}")
print(f"    Risk     : {sample['risk_score']}  |  Trust: {sample['trust_score']}  |  Credit: {sample['credit_score']}")
print(f"    Loan     : INR {sample['loan_amount']:,}")
print(f"    PAN      : {sample['pan']}  |  Aadhaar: {sample['aadhaar']}")

fraud_sample = FRAUD_ENTITIES[0]
print(f"\n  Fraud001 — {fraud_sample['name']}")
print(f"    Owner    : {fraud_sample['owner']}")
print(f"    Reason   : {FRAUD_REASONS[0]}")
print(f"    fraud_risk: High")

print(f"\n{'='*60}")
print("Seeding complete. All collections are ready.")
print(f"{'='*60}\n")

client.close()
