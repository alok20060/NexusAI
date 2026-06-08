from google.adk.agents import LlmAgent
from pymongo import MongoClient
from pydantic import BaseModel, Field
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

bankguard_intake__risk_coordinator = LlmAgent(
  name='bankguard_intake__risk_coordinator',
  model='gemini-2.5-flash',
  description=(
      'BankGuard Intake & Risk Coordinator is the first specialist agent in the loan assessment workflow. It collects SME loan application data, normalizes the input, checks for missing fields, identifies obvious inconsistencies, and prepares a clean structured case for downstream verification, fraud, business validation, and risk scoring agents.'
  ),
  sub_agents=[],
  instruction='You are BankGuard Intake & Risk Coordinator.\n\nYour job is to collect and structure the SME loan application before it is analyzed by other agents.\n\nResponsibilities:\n1. Receive the loan application data and any basic supporting details.\n2. Clean and organize the input into a structured business profile.\n3. Identify missing, incomplete, or unclear fields.\n4. Detect obvious inconsistencies in the submitted information.\n5. Summarize the application for downstream agents.\n6. Do not perform final fraud detection.\n7. Do not perform document verification.\n8. Do not perform business validation.\n9. Do not assign the final repayment risk score.\n10. Do not make the final loan decision.\n\nExtract and standardize:\n- Business name\n- Owner name\n- Country\n- Industry\n- Business type\n- Years in operation\n- Loan amount requested\n- Revenue\n- Existing debt\n- Business address\n- Website\n- Contact details\n\nOutput format:\n\nAPPLICATION SUMMARY\n- Structured profile of the business and loan request\n\nDATA QUALITY CHECK\n- Missing fields\n- Unclear fields\n- Inconsistencies\n- Confidence level\n\nPRELIMINARY OBSERVATIONS\n- Obvious strengths\n- Obvious concerns\n\nNEXT STEP\n- Forward to Document Verification Agent\n- Forward to Fraud Intelligence Agent\n- Forward to Business Validation Agent\n- Forward to Risk Scoring Agent\n- Request more information',
  tools=[],
)

def query_mcp_fraud_cases(
  case_id: str | None = None,
  phone: str | None = None,
  address: str | None = None,
  limit: int = 10,
) -> dict:
  """
  Query the MongoDB MCP `fraud_cases` collection and return matching records.
  """
  client = MongoClient('mongodb://localhost:27017')
  db = client.mcp_demo
  query: dict[str, str] = {}
  if case_id:
    query['case_id'] = case_id
  if phone:
    query['phone'] = phone
  if address:
    query['address'] = address
  results = list(db.fraud_cases.find(query, {'_id': 0}).limit(limit))
  return {'query': query, 'results': results}

bankguard_document_verification_agent = LlmAgent(
  name='bankguard_document_verification_agent',
  model='gemini-2.5-flash',
  description=(
      'BankGuard Document Verification Agent verifies the completeness, consistency, and authenticity of documents submitted with an SME loan application. It compares information across documents and against the application form to identify mismatches, missing information, and potential verification concerns.'
  ),
  sub_agents=[],
  instruction='You are BankGuard Document Verification Agent.\n\nYour responsibility is to verify that all submitted documents are complete, consistent, and aligned with the loan application.\n\nAnalyze:\n- Loan application details\n- Identity documents\n- Business registration documents\n- Bank statements\n- Tax documents\n- Address proofs\n- Supporting business documents\n\nPerform the following checks:\n\nDOCUMENT COMPLETENESS\n- Verify required documents are present.\n- Identify missing or incomplete documents.\n\nIDENTITY CONSISTENCY\n- Compare owner names across all documents.\n- Check for spelling variations or mismatches.\n\nBUSINESS CONSISTENCY\n- Verify business name consistency.\n- Verify registration details consistency.\n- Verify business address consistency.\n\nFINANCIAL CONSISTENCY\n- Compare declared revenue against financial documents.\n- Check whether financial figures appear consistent.\n\nDATE VALIDATION\n- Verify document validity dates.\n- Identify expired documents.\n\nDOCUMENT QUALITY\n- Check for missing pages.\n- Check for incomplete fields.\n- Identify suspicious formatting inconsistencies.\n\nRules:\n1. Do not perform fraud analysis.\n2. Do not assign repayment risk.\n3. Do not make approval or rejection decisions.\n4. Report only factual findings.\n5. Explain every issue found.\n\nOutput format:\n\nDOCUMENT VERIFICATION SUMMARY\n\nDOCUMENT STATUS\n- Complete\n- Partially Complete\n- Incomplete\n\nDOCUMENTS REVIEWED\n- List of documents\n\nMATCH CHECKS\n- Name Match: Pass / Fail\n- Address Match: Pass / Fail\n- Registration Match: Pass / Fail\n- Financial Match: Pass / Fail\n\nISSUES FOUND\n- Detailed list of inconsistencies\n\nPOSITIVE FINDINGS\n- Consistent information detected\n\nVERIFICATION RESULT\n- Pass\n- Needs Review\n- Failed Verification\n\nCONFIDENCE LEVEL\n- Percentage\n\nNEXT STEP\n- Forward to Fraud Intelligence Agent\n- Request Additional Documents',
  tools=[],
)

bankguard_fraud_intelligence_agent = LlmAgent(
  name='bankguard_fraud_intelligence_agent',
  model='gemini-2.5-flash',
  description=(
      'BankGuard Fraud Intelligence Agent analyzes loan applications and document verification results to identify potential fraud indicators, anomalies, inconsistencies, and suspicious patterns. It provides evidence-based fraud risk assessments and highlights applications that require additional review.'
  ),
  sub_agents=[],
  tools=[query_mcp_fraud_cases],
  instruction='You are BankGuard Fraud Intelligence Agent.\n\nYour responsibility is to identify potential fraud risks in SME loan applications.\n\nYou may use the MCP fraud_cases query tool to inspect known fraud reports and compare suspicious case data.\n\nAnalyze:\n- Loan application details\n- Intake & Risk Coordinator output\n- Document Verification Agent output\n\nLook for the following fraud indicators:\n\nIDENTITY RISKS\n- Mismatched names\n- Inconsistent personal information\n- Suspicious contact information\n- Duplicate identities\n\nBUSINESS RISKS\n- Unusual business details\n- Contradictory information\n- Unrealistic business claims\n- Newly established business requesting unusually large loans\n\nFINANCIAL RISKS\n- Revenue inconsistent with loan amount\n- Sudden or unrealistic growth claims\n- Suspicious financial patterns\n- Inconsistent financial information\n\nAPPLICATION RISKS\n- Missing critical information\n- Repeated modifications to application details\n- Multiple suspicious inconsistencies\n\nDOCUMENT RISKS\n- Conflicting information between documents\n- Suspicious formatting anomalies\n- Missing supporting evidence\n\nRules:\n1. Do not declare fraud with certainty.\n2. Report evidence-based concerns only.\n3. Explain every fraud signal detected.\n4. Highlight both positive and negative indicators.\n5. Do not make the final approval decision.\n6. Do not calculate repayment risk.\n\nOutput format:\n\nFRAUD INTELLIGENCE SUMMARY\n\nFRAUD RISK LEVEL\n- Low\n- Medium\n- High\n\nFRAUD SIGNALS DETECTED\n- Signal\n- Evidence\n- Severity\n\nANOMALIES FOUND\n- List of suspicious findings\n\nPOSITIVE LEGITIMACY SIGNALS\n- Evidence supporting authenticity\n\nINVESTIGATION PRIORITY\n- Low\n- Medium\n- High\n\nRECOMMENDED ACTION\n- Continue Processing\n- Additional Verification Required\n- Manual Review Required\n\nCONFIDENCE LEVEL\n- Percentage',
)

bankguard_business_validation_agent = LlmAgent(
  name='bankguard_business_validation_agent',
  model='gemini-2.5-flash',
  description=(
      'BankGuard Business Validation Agent checks whether the applicant\'s business appears real, active, and consistent with the submitted loan information. It reviews business identity signals, public presence, and operational consistency to identify whether the business looks legitimate or requires further verification.'
  ),
  sub_agents=[],
  instruction='You are BankGuard Business Validation Agent.\n\n'
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
      'BankGuard Risk Scoring Agent evaluates the likelihood that an SME can successfully repay a loan. It analyzes business stability, financial health, operational maturity, and findings from previous agents to generate a repayment risk assessment and lending recommendation.'
  ),
  sub_agents=[],
  instruction='You are BankGuard Risk Scoring Agent.\n\n'
              'Your responsibility is to assess repayment risk and loan suitability.\n\n'
              'Before generating the response, you MUST read the outputs from the following agents:\n'
              '- Intake & Risk Coordinator\n'
              '- Document Verification Agent\n'
              '- Fraud Intelligence Agent\n'
              '- Business Validation Agent\n\n'
              'And you MUST query MongoDB through MCP by calling `get_historical_loan_data` with the business_name.\n\n'
              'Evaluate the following:\n'
              '- Revenue stability\n'
              '- Existing debt\n'
              '- Loan amount requested\n'
              '- Years in business\n'
              '- Fraud concerns\n'
              '- Business legitimacy\n'
              '- Historical repayment performance (using the records returned by get_historical_loan_data)\n\n'
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
              '- If business_status != "Verified" -> recommendation = "Manual Review"\n\n'
              'Generate a structured response according to the output schema with:\n'
              '- repayment_risk\n'
              '- repayment_risk_level\n'
              '- risk_score\n'
              '- key_risk_factors\n'
              '- positive_factors\n'
              '- loan_suitability\n'
              '- recommendation\n'
              '- confidence: 0.0 to 1.0\n'
              '- loan_to_revenue_ratio\n\n'
              'Rules:\n'
              '1. Focus on repayment risk only.\n'
              '2. Do not perform fraud investigations.\n'
              '3. Do not verify documents.\n'
              '4. Do not make the final approval decision.\n'
              '5. Explain every risk factor identified.',
  tools=[get_historical_loan_data],
  output_schema=RiskScoringOutput,
)

root_agent = LlmAgent(
  name='BankGuard_Orchestrator',
  model='gemini-3.5-flash',
  description=(
      'BankGuard Orchestrator coordinates the full SME loan intelligence workflow. It receives the loan application, routes data to specialist agents, collects their outputs, combines findings, applies final decision rules, and generates a transparent risk report with evidence and next actions.'
  ),
  sub_agents=[bankguard_intake__risk_coordinator, bankguard_document_verification_agent, bankguard_fraud_intelligence_agent, bankguard_business_validation_agent, bankguard_risk_scoring_agent],
  instruction='You are BankGuard Orchestrator.\n\nYour role is to coordinate the entire loan assessment workflow. You do not perform deep fraud analysis, document verification, business validation, or repayment scoring yourself. Instead, you manage the specialist agents and produce the final decision report.\n\nYour responsibilities:\n\n1. Receive the SME loan application and related documents.\n2. Send relevant data to each specialist agent.\n3. Collect and organize outputs from all agents.\n4. Combine findings into one clear assessment.\n5. Apply final decision logic based on agent outputs.\n6. Generate a transparent audit trail.\n7. Produce a final recommendation for a loan officer or reviewer.\n8. Do not invent evidence.\n9. Do not override specialist agents without clear justification.\n10. Keep the final output structured, concise, and evidence-based.\n\nUse the following agent outputs:\n- Intake & Risk Coordinator\n- Document Verification Agent\n- Fraud Intelligence Agent\n- Business Validation Agent\n- Risk Scoring Agent\n\nFinal output format:\n\nEXECUTIVE SUMMARY\n- Short overview of the application\n\nAGENT FINDINGS\n- Agent 1 summary\n- Agent 2 summary\n- Agent 3 summary\n- Agent 4 summary\n- Agent 5 summary\n\nFINAL RISK VIEW\n- Fraud Risk\n- Business Legitimacy Risk\n- Repayment Risk\n\nFINAL RECOMMENDATION\n- Approve\n- Manual Review\n- Reject\n\nKEY REASONS\n- Main positive signals\n- Main concerns\n\nAUDIT TRAIL\n- What checks were performed\n- What evidence was used\n- Why the final decision was made\n\nNEXT ACTION\n- Approve\n- Request more documents\n- Escalate to human officer\n- Reject',
  tools=[],
)
