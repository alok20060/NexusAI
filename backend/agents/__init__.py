from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field
from backend.database import get_sync_db, DB_NAME
from backend.mcp_client import get_business_history, get_historical_loan_data

class BusinessValidationOutput(BaseModel):
    business_status: str = Field(description="Verification status of the business: 'Verified', 'Partially Verified', or 'Unable to Verify'")
    historical_records_found: bool = Field(description="Flag indicating if any historical records were found in the database")
    previous_loan_count: int = Field(description="The number of previous loans the business had")
    positive_signals: list[str] = Field(description="List of positive indicators found during validation")
    concerns: list[str] = Field(description="List of concerns or red flags identified")
    confidence: float = Field(description="Confidence score for the validation result, between 0.0 and 1.0")

class RiskScoringOutput(BaseModel):
    repayment_risk: str = Field(description="Repayment risk level: 'Low', 'Medium', or 'High'")
    repayment_risk_level: str = Field(description="Repayment risk level: 'Low', 'Medium', or 'High'")
    risk_score: int = Field(description="Numerical risk score from 0 to 100, where higher is higher risk")
    key_risk_factors: list[str] = Field(description="List of key risk factors identified")
    positive_factors: list[str] = Field(description="List of key positive factors identified")
    loan_suitability: str = Field(description="Evaluation of loan suitability")
    recommendation: str = Field(description="Lending recommendation: 'Approve', 'Manual Review', or 'Reject'")
    confidence: float = Field(description="Confidence score for the risk assessment, between 0.0 and 1.0")
    loan_to_revenue_ratio: float = Field(description="The calculated loan-to-revenue ratio")
    alternative_credit_score: list[int] = Field(default=[], description="Alternative credit score (0-100) wrapped in a list or None")
    collateral_quality: list[str] = Field(default=[], description="Collateral quality assessment wrapped in a list or None")
    cash_flow_health: list[str] = Field(default=[], description="Cash flow health assessment wrapped in a list or None")
    business_sustainability: list[int] = Field(default=[], description="Sustainability score wrapped in a list or None")

class ApplicantProfilingOutput(BaseModel):
    applicant_type: str = Field(description="Classified applicant type: 'Beginner Entrepreneur', 'Experienced Business Owner', or 'High-Value Loan Applicant'")
    required_documents: list[str] = Field(description="Dynamic checklist of required documents based on profile")
    profile_confidence: float = Field(description="Confidence of profiling, between 0.0 and 1.0")

class DocumentVerificationOutput(BaseModel):
    document_completeness: float = Field(description="Completeness of documents uploaded (0.0 to 1.0)")
    verified_documents: list[str] = Field(description="List of verified documents")
    missing_documents: list[str] = Field(description="List of missing documents")
    unsupported_documents: list[str] = Field(description="List of unsupported or corrupted documents")
    extracted_fields: dict = Field(default={}, description="Extracted key-value pairs from documents")
    extraction_confidence: float = Field(default=1.0, description="Average confidence score of extraction (0.0 to 1.0)")
    inconsistencies: list[str] = Field(default=[], description="Consistency check warnings and mismatch messages")
    verification_status: str = Field(default="Verified", description="Final verification status (Verified, Partial Extraction, Mismatch Detected)")
    consistency_score: float = Field(default=100.0, description="Computed consistency score (0 to 100)")
    document_health_score: float = Field(default=100.0, description="Computed document health score (0 to 100)")
    mismatch_severity: str = Field(default="LOW", description="Overall severity of mismatches (LOW, MEDIUM, HIGH, CRITICAL)")
    normalized_business_name: str = Field(default="", description="Normalized business name from extracted document")
    normalized_owner_name: str = Field(default="", description="Normalized owner name from extracted document")

class ExplainabilityOutput(BaseModel):
    explainability_report: str = Field(description="Human-readable decision explanation with ✓ and ✗ markers")

class TrustComplianceOutput(BaseModel):
    trust_score: int = Field(description="Computed trust score (0-100)")
    source_integrity_status: str = Field(description="Integrity status of data sources (e.g. 'Passed', 'Failed')")
    hash_verification_status: str = Field(description="Verification status of document/report hashes (e.g. 'Verified', 'Mismatch')")
    audit_chain_verification_status: str = Field(description="Verification status of immutable audit ledger (e.g. 'Valid', 'Broken')")
    compliance_summary: str = Field(description="Detailed compliance review summary and findings")
    confidence: float = Field(description="Confidence of compliance assessment (0.0 to 1.0)")

bankguard_applicant_profiling_agent = LlmAgent(
  name='bankguard_applicant_profiling_agent',
  model='gemini-2.5-flash',
  description='Applicant Profiling Agent classifies the applicant into a specific tier and dynamically decides required documents.',
  instruction='You are Applicant Profiling Agent. Based on the loan amount, years in operation, and credit history, classify the applicant into Beginner Entrepreneur, Experienced Business Owner, or High-Value Loan Applicant and determine the required documents checklist.',
  tools=[]
)

bankguard_intake__risk_coordinator = LlmAgent(
  name='bankguard_intake__risk_coordinator',
  model='gemini-2.5-flash',
  description=(
      'NexusAI-NexusAI-BankGuard Intake & Risk Coordinator is the first specialist agent in the loan assessment workflow. It collects SME loan application data, normalizes the input, checks for missing fields, identifies obvious inconsistencies, and prepares a clean structured case for downstream verification, fraud, business validation, and risk scoring agents.'
  ),
  sub_agents=[],
  instruction='You are NexusAI-NexusAI-BankGuard Intake & Risk Coordinator.\n\nYour job is to collect and structure the SME loan application before it is analyzed by other agents.\n\nResponsibilities:\n1. Receive the loan application data and any basic supporting details.\n2. Clean and organize the input into a structured business profile.\n3. Identify missing, incomplete, or unclear fields.\n4. Detect obvious inconsistencies in the submitted information.\n5. Summarize the application for downstream agents.\n6. Do not perform final fraud detection.\n7. Do not perform document verification.\n8. Do not perform business validation.\n9. Do not assign the final repayment risk score.\n10. Do not make the final loan decision.\n\nExtract and standardize:\n- Business name\n- Owner name\n- Country\n- Industry\n- Business type\n- Years in operation\n- Loan amount requested\n- Revenue\n- Existing debt\n- Business address\n- Website\n- Contact details\n\nOutput format:\n\nAPPLICATION SUMMARY\n- Structured profile of the business and loan request\n\nDATA QUALITY CHECK\n- Missing fields\n- Unclear fields\n- Inconsistencies\n- Confidence level\n\nPRELIMINARY OBSERVATIONS\n- Obvious strengths\n- Obvious concerns\n\nNEXT STEP\n- Forward to Document Verification Agent\n- Forward to Fraud Intelligence Agent\n- Forward to Business Validation Agent\n- Forward to Risk Scoring Agent\n- Request more information',
  tools=[],
)

def query_mcp_fraud_cases(
  case_id: str | None = None,
  phone: str | None = None,
  address: str | None = None,
  limit: int = 10,
) -> dict:
  """
  Query the MongoDB Atlas `fraud_cases` collection and return matching records.
  Uses MONGO_URI environment variable for Atlas connection.
  """
  try:
    db = get_sync_db()
    query: dict[str, str] = {}
    if case_id:
      query['case_id'] = case_id
    if phone:
      query['phone'] = phone
    if address:
      query['address'] = address
    results = list(db.fraud_cases.find(query, {'_id': 0}).limit(limit))
    return {'query': query, 'results': results, 'database': DB_NAME}
  except Exception as e:
    print(f"MongoDB error: {e}")
    return {'query': {}, 'results': [], 'error': f'MongoDB error: {e}'}

bankguard_document_verification_agent = LlmAgent(
  name='bankguard_document_verification_agent',
  model='gemini-2.5-flash',
  description=(
      'NexusAI-BankGuard AI Document Intelligence Agent extracts structured credit metrics from uploaded documents and evaluates consistency.'
  ),
  sub_agents=[],
  instruction='You are NexusAI-BankGuard AI Document Intelligence Agent. Your responsibility is to analyze the extracted document texts, populate the document intelligence parameters, and report consistency results. You consume the filesystem verification checks and raw text fields.',
  tools=[],
  output_schema=DocumentVerificationOutput,
)

bankguard_fraud_intelligence_agent = LlmAgent(
  name='bankguard_fraud_intelligence_agent',
  model='gemini-2.5-flash',
  description=(
      'NexusAI-NexusAI-BankGuard Fraud Intelligence Agent analyzes loan applications and document verification results to identify potential fraud indicators, anomalies, inconsistencies, and suspicious patterns. It provides evidence-based fraud risk assessments and highlights applications that require additional review.'
  ),
  sub_agents=[],
  tools=[query_mcp_fraud_cases],
  instruction='You are NexusAI-NexusAI-BankGuard Fraud Intelligence Agent.\n\nYour responsibility is to identify potential fraud risks in SME loan applications.\n\nYou may use the MCP fraud_cases query tool to inspect known fraud reports and compare suspicious case data.\n\nAnalyze:\n- Loan application details\n- Intake & Risk Coordinator output\n- Document Verification Agent output\n\nLook for the following fraud indicators:\n\nIDENTITY RISKS\n- Mismatched names\n- Inconsistent personal information\n- Suspicious contact information\n- Duplicate identities\n\nBUSINESS RISKS\n- Unusual business details\n- Contradictory information\n- Unrealistic business claims\n- Newly established business requesting unusually large loans\n\nFINANCIAL RISKS\n- Revenue inconsistent with loan amount\n- Sudden or unrealistic growth claims\n- Suspicious financial patterns\n- Inconsistent financial information\n\nAPPLICATION RISKS\n- Missing critical information\n- Repeated modifications to application details\n- Multiple suspicious inconsistencies\n\nDOCUMENT RISKS\n- Conflicting information between documents\n- Suspicious formatting anomalies\n- Missing supporting evidence\n\nRules:\n1. Do not declare fraud with certainty.\n2. Report evidence-based concerns only.\n3. Explain every fraud signal detected.\n4. Highlight both positive and negative indicators.\n5. Do not make the final approval decision.\n6. Do not calculate repayment risk.\n\nOutput format:\n\nFRAUD INTELLIGENCE SUMMARY\n\nFRAUD RISK LEVEL\n- Low\n- Medium\n- High\n\nFRAUD SIGNALS DETECTED\n- Signal\n- Evidence\n- Severity\n\nANOMALIES FOUND\n- List of suspicious findings\n\nPOSITIVE LEGITIMACY SIGNALS\n- Evidence supporting authenticity\n\nINVESTIGATION PRIORITY\n- Low\n- Medium\n- High\n\nRECOMMENDED ACTION\n- Continue Processing\n- Additional Verification Required\n- Manual Review Required\n\nCONFIDENCE LEVEL\n- Percentage',
)

bankguard_business_validation_agent = LlmAgent(
  name='bankguard_business_validation_agent',
  model='gemini-2.5-flash',
  description=(
      'NexusAI-NexusAI-BankGuard Business Validation Agent checks whether the applicant\'s business appears real, active, and consistent with the submitted loan information. It reviews business identity signals, public presence, and operational consistency to identify whether the business looks legitimate or requires further verification.'
  ),
  sub_agents=[],
  instruction='You are NexusAI-NexusAI-BankGuard Business Validation Agent.\n\n'
              'Your responsibility is to validate whether the business appears legitimate, active, and consistent with the application.\n\n'
              'Before generating the response, you MUST query MongoDB through MCP by calling `get_business_history` with the business_name.\n\n'
              'Analyze:\n'
              '- Business name\n'
              '- Business address\n'
              '- Industry type\n'
              '- Website\n'
              '- Public business information\n'
              '- Registration details\n'
              '- Business activity signals\n'
              '- Historical consistency from previous agent outputs\n'
              '- Historical records returned by get_business_history tool\n\n'
              'Perform the following checks:\n'
              '- Check whether the business was previously verified using the retrieved history.\n'
              '- Check whether previous loans existed and count them.\n'
              '- Evaluate business existence, operational consistency, and red flags.\n\n'
              'Rules:\n'
              '1. Do not make the final loan decision.\n'
              '2. Do not calculate repayment risk.\n'
              '3. Do not declare fraud with certainty.\n'
              '4. Report only evidence-based observations.\n'
              '5. Formulate a structured response matching the output schema.',
  tools=[get_business_history],
  output_schema=BusinessValidationOutput,
)

bankguard_risk_scoring_agent = LlmAgent(
  name='bankguard_risk_scoring_agent',
  model='gemini-2.5-flash',
  description=(
      'NexusAI-NexusAI-BankGuard Risk Scoring Agent evaluates the likelihood that an SME can successfully repay a loan. It analyzes business stability, financial health, operational maturity, and findings from previous agents to generate a repayment risk assessment and lending recommendation.'
  ),
  sub_agents=[],
  instruction='You are NexusAI-NexusAI-BankGuard Risk Scoring Agent.\n\n'
              'Your responsibility is to assess repayment risk and loan suitability by combining:\n'
              '1. Fraud risk level from Agent 3\n'
              '2. Document Consistency score from Agent 2\n'
              '3. Document health score from Agent 2\n'
              '4. AI confidence score from Agent 2\n'
              '5. Alternative credit score (for Beginner Entrepreneurs)\n'
              '6. Collateral quality/adequacy\n'
              '7. Cash flow health (based on bank statements / transaction logs)\n'
              '8. Business sustainability (maturity & growth trends)\n'
              '9. Historical repayment behavior (using get_historical_loan_data)\n\n'
              'Before generating the response, you MUST read the outputs from the following agents:\n'
              '- Intake & Risk Coordinator\n'
              '- Document Verification Agent (including Document Health, Consistency Score, AI Confidence, Extracted Fields)\n'
              '- Fraud Intelligence Agent\n'
              '- Business Validation Agent\n\n'
              'And you MUST query MongoDB through MCP by calling `get_historical_loan_data` with the business_name.\n\n'
              'ALTERNATIVE CREDIT SCORING FOR BEGINNER ENTREPRENEURS:\n'
              'If years_in_business < 2 or the applicant is classified as a Beginner Entrepreneur:\n'
              '- Do NOT reject or penalize the applicant for having thin/no traditional credit history.\n'
              '- Evaluate alternative data inputs: Savings bank balances, Asset proofs, Promoter education/professional background, Guarantor quality, Collateral details, and Account balances.\n'
              '- If alternative parameters are strong, assign a lower risk score and recommend Approve or Manual Review (instead of Reject).\n\n'
              'You MUST calculate: ratio = loan_amount / monthly_revenue\n\n'
              'Apply the following risk rules:\n'
              '- If ratio > 100:\n'
              '  repayment_risk = "High", repayment_risk_level = "High", risk_score = 95, recommendation = "Reject"\n'
              '- If ratio > 20:\n'
              '  repayment_risk = "Medium", repayment_risk_level = "Medium", risk_score = 70, recommendation = "Manual Review"\n'
              '- If ratio > 5:\n'
              '  repayment_risk = "Medium", repayment_risk_level = "Medium", risk_score = 50, recommendation = "Manual Review"\n'
              '- Else:\n'
              '  repayment_risk = "Low", repayment_risk_level = "Low", risk_score = 20, recommendation = "Approve"\n\n'
              'Apply additional rules:\n'
              '- If fraud_risk == "High" -> recommendation = "Reject"\n'
              '- If business_status != "Verified" -> recommendation = "Manual Review"\n'
              '- If Document Health Score < 50 or Consistency Score < 50 -> increase risk score by +20 points and recommend Manual Review.\n\n'
              'Generate a structured response according to the output schema with:\n'
              '- repayment_risk\n'
              '- repayment_risk_level\n'
              '- risk_score\n'
              '- key_risk_factors\n'
              '- positive_factors\n'
              '- loan_suitability\n'
              '- recommendation\n'
              '- confidence: 0.0 to 1.0\n'
              '- loan_to_revenue_ratio\n'
              '- alternative_credit_score\n'
              '- collateral_quality\n'
              '- cash_flow_health\n'
              '- business_sustainability\n\n'
              'Rules:\n'
              '1. Focus on repayment risk only.\n'
              '2. Do not perform fraud investigations.\n'
              '3. Do not verify documents.\n'
              '4. Do not make the final approval decision.\n'
              '5. Explain every risk factor identified.',
  tools=[get_historical_loan_data],
  output_schema=RiskScoringOutput,
)
 
bankguard_explainability_agent = LlmAgent(
  name='bankguard_explainability_agent',
  model='gemini-2.5-flash',
  description='NexusAI-BankGuard Explainability Agent converts technical credit decision details into reader-friendly justifications.',
  instruction='You are Explainability Agent. Your responsibility is to take the final recommendation, risk factors, document intelligence, and verification results, and produce a structured explainability report containing: Decision, Confidence, Strengths, Weaknesses, Key risks, Supporting evidence, Reason codes, and Manual review recommendation.\n\nEnsure you structure the output report with the following headers:\n\nDECISION: [Approve/Manual Review/Reject]\nCONFIDENCE: [Score 0-100%]\nSTRENGTHS:\n[List business strengths, prefixed with ✓]\nWEAKNESSES:\n[List weaknesses, prefixed with ✗]\nKEY RISKS:\n[List key risk scoring concerns, prefixed with ✗]\nSUPPORTING EVIDENCE:\n[List verified fields or data metrics confirming details, prefixed with ✓]\nREASON CODES:\n[List reason codes like REV_MISMATCH, LOW_SCORE, FRAUD_ALERT, alt]\nMANUAL REVIEW RECOMMENDATION:\n[Specify if manual review is recommended or not, and state the primary reason prefixing with ✓ or ✗]',
  tools=[],
  output_schema=ExplainabilityOutput,
)

bankguard_trust_compliance_agent = LlmAgent(
  name='bankguard_trust_compliance_agent',
  model='gemini-2.5-flash',
  description='NexusAI-BankGuard Trust & Compliance Agent validates source integrity, hashes, audit chains, and computes overall trust scores.',
  instruction='You are Trust & Compliance Agent (Agent 7). Your responsibility is to validate source integrity, verify document and report hashes, check the cryptographic audit chain, calculate the trust score (0-100), and generate compliance summaries.',
  tools=[],
  output_schema=TrustComplianceOutput,
)

root_agent = LlmAgent(
  name='BankGuard_Orchestrator',
  model='gemini-3.5-flash',
  description=(
      'NexusAI-NexusAI-BankGuard Orchestrator coordinates the full SME loan intelligence workflow. It receives the loan application, routes data to specialist agents, collects their outputs, combines findings, applies final decision rules, and generates a transparent risk report with evidence and next actions.'
  ),
  sub_agents=[bankguard_intake__risk_coordinator, bankguard_document_verification_agent, bankguard_fraud_intelligence_agent, bankguard_business_validation_agent, bankguard_risk_scoring_agent, bankguard_explainability_agent, bankguard_trust_compliance_agent],
  instruction='You are NexusAI-NexusAI-BankGuard Orchestrator.\n\nYour role is to coordinate the entire loan assessment workflow. You do not perform deep fraud analysis, document verification, business validation, or repayment scoring yourself. Instead, you manage the specialist agents and produce the final decision report.',
  tools=[],
)
