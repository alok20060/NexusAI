from pydantic import BaseModel, Field
from typing import List

class LoanAnalysisInput(BaseModel):
    business_name: str = Field(description="Name of the business requesting the loan")
    owner_name: str = Field(description="Name of the business owner or promoter")
    loan_amount: float = Field(description="Loan amount requested")
    monthly_revenue: float = Field(description="Monthly revenue of the business")
    industry: str = Field(description="Industry sector of the business")
    loan_purpose: str = Field(description="Purpose of the loan")

class AgentTraceItem(BaseModel):
    agent: str = Field(description="Short identifier of the agent")
    text: str = Field(description="Summary of the agent's findings or trace")

class AuditLogItem(BaseModel):
    timestamp: str = Field(description="Time of the log event (HH:MM:SS)")
    message: str = Field(description="Description of the log event")

class FinalDecisionOutput(BaseModel):
    final_recommendation: str = Field(description="Final decision: 'Approve', 'Manual Review', 'Reject', or 'Additional Verification'")
    fraud_risk: str = Field(description="Aggregated fraud risk level ('Low', 'Medium', 'High')")
    business_status: str = Field(description="Business validation status ('Verified', 'Partially Verified', 'Unable to Verify')")
    repayment_risk: str = Field(description="Repayment risk level ('Low', 'Medium', 'High')")
    key_reasons: List[str] = Field(description="Aggregated key findings and reasons from all agents")
    next_action: str = Field(description="Actionable next step recommended by the orchestrator")
    confidence: float = Field(description="Confidence score for the overall decision, between 0.0 and 1.0")
    decision_explanation: str = Field(description="Human-readable decision explanation and summary")

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

class LoanAnalysisResponse(BaseModel):
    input: dict = Field(description="Input payload parameters")
    agent_1_output: dict = Field(description="Intake agent output payload")
    agent_2_output: dict = Field(description="Document verification agent output payload")
    agent_3_output: dict = Field(description="Fraud intelligence agent output payload")
    agent_4_output: dict = Field(description="Business validation agent output payload")
    agent_5_output: dict = Field(description="Risk scoring agent output payload")
    orchestrator_decision: dict = Field(description="Final aggregated orchestrator decision output")
    final_response: FinalResponseModel = Field(description="Flattened final response object for UI mapping")

