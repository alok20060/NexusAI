from pydantic import BaseModel, Field
from typing import Any, List, Optional

class InitializeApplicationInput(BaseModel):
    business_name: str = Field(description="Name of the business requesting the loan")
    owner_name: Optional[str] = Field(default="", description="Name of the business owner or promoter")
    loan_amount: float = Field(description="Loan amount requested")
    monthly_revenue: Optional[float] = Field(default=0.0, description="Monthly revenue of the business")
    industry: Optional[str] = Field(default="General Trade", description="Industry sector of the business")
    loan_purpose: Optional[str] = Field(default="Working capital", description="Purpose of the loan")
    years_in_business: Optional[int] = Field(default=5, description="Years in business of the entity")

class InitializeApplicationResponse(BaseModel):
    application_id: str = Field(description="Generated application ID")
    applicant_type: str = Field(description="Dynamically classified applicant type")
    required_documents: List[str] = Field(description="List of required documents")

class LoanAnalysisInput(BaseModel):
    business_name: str = Field(description="Name of the business requesting the loan")
    owner_name: Optional[str] = Field(default="", description="Name of the business owner or promoter")
    loan_amount: float = Field(description="Loan amount requested")
    monthly_revenue: Optional[float] = Field(default=0.0, description="Monthly revenue of the business")
    industry: Optional[str] = Field(default="General Trade", description="Industry sector of the business")
    loan_purpose: Optional[str] = Field(default="Working capital", description="Purpose of the loan")
    years_in_business: Optional[int] = Field(default=5, description="Years in business of the entity")
    application_id: Optional[str] = Field(default=None, description="Pre-initialized application ID if available")

class AgentTraceItem(BaseModel):
    agent: str = Field(description="Short identifier of the agent")
    text: str = Field(description="Summary of the agent's findings or trace")

class AuditLogItem(BaseModel):
    timestamp: str = Field(description="Time of the log event (HH:MM:SS)")
    message: str = Field(description="Description of the log event")

class TimelineEvent(BaseModel):
    stage: str = Field(description="Name of the underwriting stage")
    status: str = Field(description="Status of the stage: 'Pending', 'In Progress', or 'Completed'")
    timestamp: str = Field(description="Timestamp of the status update")

class DocumentIntelligencePanel(BaseModel):
    verified_fields: List[str] = Field(default=[], description="List of verified fields")
    mismatch_warnings: List[str] = Field(default=[], description="List of warnings/mismatch alerts")
    extraction_confidence: float = Field(default=1.0, description="Average confidence of extraction (0.0 to 1.0)")
    consistency_score: float = Field(default=100.0, description="Consistency score of details (0 to 100)")
    document_health: float = Field(default=100.0, description="Document integrity health percentage (0 to 100)")
    document_health_score: float = Field(default=100.0, description="Document health score (0 to 100)")
    color_coding: str = Field(default="Green", description="Color tier representing overall document health (Green, Yellow, Red)")
    normalized_business_name: str = Field(default="", description="Normalized business name from documents")
    normalized_owner_name: str = Field(default="", description="Normalized owner name from documents")
    mismatch_severity: str = Field(default="LOW", description="Overall severity of mismatches (LOW, MEDIUM, HIGH, CRITICAL)")
    extraction_errors: List[str] = Field(default=[], description="Errors encountered during extraction")
    ocr_fallback_used: bool = Field(default=False, description="True if OCR fallback was triggered")
    extracted_fields: dict = Field(default={}, description="Key-value extracted pairs")
    verification_status: str = Field(default="Verified", description="Overall status (Verified, Partial Extraction, Mismatch Detected)")

class UnderwritingIntelligenceModel(BaseModel):
    application_id: str = Field(description="Linked application ID")
    ai_summary: str = Field(description="AI executive summary of the underwriting case")
    extracted_entities: dict = Field(default={}, description="The 15 semantic entities extracted from documents")
    revenue_assessment: str = Field(default="N/A", description="Revenue trends & cash flow quality assessment")
    debt_assessment: str = Field(default="N/A", description="Debt burden & liabilities assessment")
    sustainability_assessment: str = Field(default="N/A", description="Business maturity & durability assessment")
    affordability_assessment: str = Field(default="N/A", description="Loan affordability assessment")
    collateral_assessment: str = Field(default="N/A", description="Collateral adequacy assessment")
    overall_document_quality: float = Field(default=100.0, description="Document quality index percentage (0 to 100)")
    ai_confidence: float = Field(default=1.0, description="AI underwriting confidence score (0.0 to 1.0)")
    timestamp: str = Field(description="Timestamp of intelligence extraction")

class ManualReviewCaseModel(BaseModel):
    application_id: str = Field(description="Linked application ID")
    case_id: str = Field(description="Generated manual review case ID")
    status: str = Field(default="Pending", description="Review status: Pending, Under Review, Completed")
    reason: List[str] = Field(default=[], description="List of reasons triggering human manual review")
    created_at: str = Field(description="Timestamp when review task was created")
    details: dict = Field(default={}, description="Metadata containing discrepancy/scoring flags")
    reason_codes: List[str] = Field(default=[], description="Reason codes representing decision anomalies")
    priority: str = Field(default="Medium", description="Priority level: Low, Medium, High, Critical")
    assigned_reviewer: str = Field(default="Unassigned", description="Assigned reviewer email or name")
    timestamp: str = Field(description="Time of creation / update")

class AIUnderwritingInsightsPanel(BaseModel):
    revenue_quality: str = Field(default="N/A", description="Assessment of business revenue trends and sustainability")
    debt_burden: str = Field(default="N/A", description="Assessment of current leverage and liabilities")
    collateral_strength: str = Field(default="N/A", description="Evaluation of assets and security offered")
    business_sustainability: str = Field(default="N/A", description="Evaluation of business age, industry segment, survival outlook")
    cash_flow_health: str = Field(default="N/A", description="Cash flow quality score/level based on bank transactions")
    ai_confidence: float = Field(default=1.0, description="AI confidence score (0.0 to 1.0)")
    document_health_score: float = Field(default=100.0, description="Underlying document health score (0 to 100)")
    consistency_score: float = Field(default=100.0, description="Overall consistency score (0 to 100)")
    alternative_credit_score: Optional[int] = Field(default=None, description="Alternative credit score (0-100) for Beginner Entrepreneurs")
    collateral_value: Optional[float] = Field(default=None, description="Estimated collateral value")
    sustainability_score: Optional[int] = Field(default=None, description="Business sustainability score (0-100)")
class ZeroTrustField(BaseModel):
    value: Optional[Any] = None
    source: str = Field(default="unknown")
    confidence: float = Field(default=1.0)
    verification_status: str = Field(default="unverified")
    timestamp: str = Field(default="")

class ZeroTrustPayload(BaseModel):
    business_name: Optional[ZeroTrustField] = None
    owner_name: Optional[ZeroTrustField] = None
    loan_amount: Optional[ZeroTrustField] = None
    monthly_revenue: Optional[ZeroTrustField] = None
    industry: Optional[ZeroTrustField] = None
    years_in_business: Optional[ZeroTrustField] = None
    credit_score: Optional[ZeroTrustField] = None
    collateral_value: Optional[ZeroTrustField] = None
    savings_balance: Optional[ZeroTrustField] = None

class ConsentRecordModel(BaseModel):
    application_id: str
    consent_type: str
    granted: bool
    revoked: bool
    timestamp: str

class HashRecordModel(BaseModel):
    application_id: str
    file_type: str
    file_name: str
    sha256_hash: str
    timestamp: str

class AuditChainModel(BaseModel):
    event_id: str
    application_id: str
    previous_hash: str
    current_hash: str
    event_type: str
    timestamp: str
    details: Optional[dict] = None

class TrustScoreModel(BaseModel):
    trust_score: int
    document_health: float
    consistency_score: float
    ai_confidence: float
    fraud_history: str
    source_reliability: float
    consent_completeness: float

class FinalDecisionOutput(BaseModel):
    final_recommendation: str = Field(description="Final decision: 'Approve', 'Manual Review', 'Reject', or 'Additional Verification'")
    fraud_risk: str = Field(description="Aggregated fraud risk level ('Low', 'Medium', 'High')")
    business_status: str = Field(description="Business validation status ('Verified', 'Partially Verified', 'Unable to Verify')")
    repayment_risk: str = Field(description="Repayment risk level ('Low', 'Medium', 'High')")
    key_reasons: List[str] = Field(description="Aggregated key findings and reasons from all agents")
    next_action: str = Field(description="Actionable next step recommended by the orchestrator")
    confidence: float = Field(description="Confidence score for the overall decision, between 0.0 and 1.0")
    decision_explanation: str = Field(description="Human-readable decision explanation and summary")
    applicant_type: str = Field(default="Beginner Entrepreneur", description="Dynamically classified applicant type")
    required_documents: List[str] = Field(default=[], description="List of required documents")
    missing_documents: List[str] = Field(default=[], description="List of missing documents")
    verified_documents: List[str] = Field(default=[], description="List of verified documents")
    document_completeness: float = Field(default=0.0, description="Completeness of documents uploaded (0.0 to 1.0)")
    upload_progress: float = Field(default=0.0, description="Upload progress (0.0 to 1.0)")
    explainability_report: str = Field(default="", description="Explainability report from Agent 6")
    timeline: List[TimelineEvent] = Field(default=[], description="Timeline events for the application")
    document_intelligence: Optional[DocumentIntelligencePanel] = Field(default=None, description="Document intelligence check results")
    risk_score: Optional[int] = Field(default=None, description="Adjusted risk score")
    ai_underwriting_insights: Optional[AIUnderwritingInsightsPanel] = Field(default=None, description="UI Underwriting insights panel data")
    underwriting_intelligence: Optional[UnderwritingIntelligenceModel] = Field(default=None, description="Detailed AI reasoning assessments")
    alternative_credit_score: Optional[int] = Field(default=None, description="Alternative credit score")
    collateral_strength: Optional[str] = Field(default=None, description="Collateral strength classification")
    collateral_value: Optional[float] = Field(default=None, description="Estimated collateral value")
    cash_flow_health: Optional[str] = Field(default=None, description="Cash flow health status")
    sustainability_score: Optional[int] = Field(default=None, description="Business sustainability score")
    trust_score: Optional[int] = Field(default=None, description="Computed trust score (0-100)")
    zero_trust_data: Optional[ZeroTrustPayload] = Field(default=None, description="Zero-trust fields payload")

class FinalResponseModel(BaseModel):
    final_recommendation: str = Field(description="Final decision: 'Approve', 'Manual Review', 'Reject', or 'Additional Verification'")
    fraud_risk: str = Field(description="Aggregated fraud risk level ('Low', 'Medium', 'High')")
    business_status: str = Field(description="Business validation status ('Verified', 'Partially Verified', 'Unable to Verify')")
    repayment_risk: str = Field(description="Repayment risk level ('Low', 'Medium', 'High')")
    key_reasons: List[str] = Field(description="Aggregated key findings and reasons from all agents")
    confidence: float = Field(description="Confidence score for the overall decision, between 0.0 and 1.0")
    next_action: str = Field(description="Actionable next step recommended by the orchestrator")
    reference_id: str = Field(description="Reference ID of the application")
    risk_score: int = Field(description="Calculated risk score")
    fraud_score: int = Field(description="Calculated fraud score")
    loan_to_revenue_ratio: float = Field(description="Calculated loan-to-revenue ratio")
    reasoning_trace: List[AgentTraceItem] = Field(description="Sequential list of agent findings")
    audit_log: List[AuditLogItem] = Field(description="Compliance audit log entries")
    decision_explanation: str = Field(description="Human-readable decision explanation and summary")
    applicant_type: str = Field(default="Beginner Entrepreneur", description="Dynamically classified applicant type")
    required_documents: List[str] = Field(default=[], description="List of required documents")
    missing_documents: List[str] = Field(default=[], description="List of missing documents")
    verified_documents: List[str] = Field(default=[], description="List of verified documents")
    document_completeness: float = Field(default=0.0, description="Completeness of documents uploaded (0.0 to 1.0)")
    upload_progress: float = Field(default=0.0, description="Upload progress (0.0 to 1.0)")
    explainability_report: str = Field(default="", description="Explainability report from Agent 6")
    timeline: List[TimelineEvent] = Field(default=[], description="Timeline events for the application")
    document_intelligence: Optional[DocumentIntelligencePanel] = Field(default=None, description="Document intelligence check results")
    ai_underwriting_insights: Optional[AIUnderwritingInsightsPanel] = Field(default=None, description="UI Underwriting insights panel data")
    underwriting_intelligence: Optional[UnderwritingIntelligenceModel] = Field(default=None, description="Detailed AI reasoning assessments")
    alternative_credit_score: Optional[int] = Field(default=None, description="Alternative credit score")
    collateral_strength: Optional[str] = Field(default=None, description="Collateral strength classification")
    collateral_value: Optional[float] = Field(default=None, description="Estimated collateral value")
    cash_flow_health: Optional[str] = Field(default=None, description="Cash flow health status")
    sustainability_score: Optional[int] = Field(default=None, description="Business sustainability score")
    trust_score: Optional[int] = Field(default=None, description="Computed trust score (0-100)")
    zero_trust_data: Optional[ZeroTrustPayload] = Field(default=None, description="Zero-trust fields payload")
    document_hashes: Optional[List[dict]] = Field(default=[], description="SHA-256 hashes of uploaded files")
    report_hashes: Optional[List[dict]] = Field(default=[], description="SHA-256 hashes of generated reports")
    audit_chain: Optional[List[dict]] = Field(default=[], description="Lightweight blockchain ledger audit entries")
    checklist: Optional[List[dict]] = Field(default=[], description="Checklist with document statuses")

class LoanAnalysisResponse(BaseModel):
    input: dict = Field(description="Input payload parameters")
    agent_0_output: dict = Field(default={}, description="Applicant Profiling agent output payload")
    agent_1_output: dict = Field(description="Intake agent output payload")
    agent_2_output: dict = Field(description="Document verification agent output payload")
    agent_3_output: dict = Field(description="Fraud intelligence agent output payload")
    agent_4_output: dict = Field(description="Business validation agent output payload")
    agent_5_output: dict = Field(description="Risk scoring agent output payload")
    agent_6_output: dict = Field(default={}, description="Explainability agent output payload")
    agent_7_output: dict = Field(default={}, description="Trust & Compliance agent output payload")
    orchestrator_decision: dict = Field(description="Final aggregated orchestrator decision output")
    final_response: FinalResponseModel = Field(description="Flattened final response object for UI mapping")

