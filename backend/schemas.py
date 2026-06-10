from pydantic import BaseModel, Field
from typing import List, Optional

class InitializeApplicationInput(BaseModel):
    business_name: str = Field(description="Name of the business requesting the loan")
    owner_name: str = Field(description="Name of the business owner or promoter")
    loan_amount: float = Field(description="Loan amount requested")
    monthly_revenue: float = Field(description="Monthly revenue of the business")
    industry: str = Field(description="Industry sector of the business")
    loan_purpose: str = Field(description="Purpose of the loan")
    years_in_business: int = Field(default=5, description="Years in business of the entity")

class InitializeApplicationResponse(BaseModel):
    application_id: str = Field(description="Generated application ID")
    applicant_type: str = Field(description="Dynamically classified applicant type")
    required_documents: List[str] = Field(description="List of required documents")

class LoanAnalysisInput(BaseModel):
    business_name: str = Field(description="Name of the business requesting the loan")
    owner_name: str = Field(description="Name of the business owner or promoter")
    loan_amount: float = Field(description="Loan amount requested")
    monthly_revenue: float = Field(description="Monthly revenue of the business")
    industry: str = Field(description="Industry sector of the business")
    loan_purpose: str = Field(description="Purpose of the loan")
    years_in_business: int = Field(default=5, description="Years in business of the entity")
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

class LoanAnalysisResponse(BaseModel):
    input: dict = Field(description="Input payload parameters")
    agent_0_output: dict = Field(default={}, description="Applicant Profiling agent output payload")
    agent_1_output: dict = Field(description="Intake agent output payload")
    agent_2_output: dict = Field(description="Document verification agent output payload")
    agent_3_output: dict = Field(description="Fraud intelligence agent output payload")
    agent_4_output: dict = Field(description="Business validation agent output payload")
    agent_5_output: dict = Field(description="Risk scoring agent output payload")
    agent_6_output: dict = Field(default={}, description="Explainability agent output payload")
    orchestrator_decision: dict = Field(description="Final aggregated orchestrator decision output")
    final_response: FinalResponseModel = Field(description="Flattened final response object for UI mapping")

