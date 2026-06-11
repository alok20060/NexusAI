def is_demo_case(business_name: str) -> bool:
    if not business_name:
        return False
    name_lower = business_name.lower()
    return any(x in name_lower for x in ["abc traders", "new startup", "fake corp"])

DOC_NAME_MAP = {
    "Aadhaar Card": "Government ID",
    "Aadhar Card": "Government ID",
    "PAN Card": "Tax Identification Document",
    "GST Certificate": "Tax Registration Certificate",
    "Business Registration Certificate": "Business Incorporation Certificate",
    "Business registration certificate": "Business Incorporation Certificate",
    "Utility Bill": "Proof of Address",
    "Utility bills": "Proof of Address",
    "Office address proof": "Proof of Address",
    "Bank Statements (PDF)": "Bank Statements",
    "Bank statements": "Bank Statements",
    "ITR / Tax Returns": "Income Tax Returns",
    "IT Returns": "Income Tax Returns",
    "Tax returns": "Income Tax Returns",
    "Property Documents": "Asset Ownership Documents",
    "Property documents": "Asset Ownership Documents",
    "Asset Documents": "Asset Ownership Documents",
    "Asset proofs": "Asset Ownership Documents",
    "Balance Sheet": "Financial Statements",
    "Audited financial statements": "Financial Statements",
    "Cash flow reports": "Financial Statements",
    "Profit & Loss Statement": "Income Statement",
    "Trade License": "Operating License",
    "Loan Repayment History": "Credit History Records",
    "CIBIL Report": "Credit History Records",
    "Credit score report": "Credit History Records",
    "Personal ID": "Government ID",
    "Savings account statements": "Bank Statements"
}

def map_document_name(doc_name: str) -> str:
    return DOC_NAME_MAP.get(doc_name, doc_name)
