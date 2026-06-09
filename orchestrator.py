import asyncio
import os
import json
import logging
from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

# Import the agents defined in agent.py
from agent import (
    bankguard_intake__risk_coordinator,
    bankguard_document_verification_agent,
    bankguard_fraud_intelligence_agent,
    bankguard_business_validation_agent,
    bankguard_risk_scoring_agent
)

# Import ADK components for running the agents
try:
    from google.adk import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("BankGuardOrchestrator")

class FinalDecisionOutput(BaseModel):
    final_recommendation: str = Field(description="Final decision: 'Approve', 'Manual Review', 'Reject', or 'Additional Verification'")
    fraud_risk: str = Field(description="Aggregated fraud risk level ('Low', 'Medium', 'High')")
    business_status: str = Field(description="Business validation status ('Verified', 'Partially Verified', 'Unable to Verify')")
    repayment_risk: str = Field(description="Repayment risk level ('Low', 'Medium', 'High')")
    key_reasons: list[str] = Field(description="Aggregated key findings and reasons from all agents")
    next_action: str = Field(description="Actionable next step recommended by the orchestrator")
    confidence: float = Field(description="Confidence score for the overall decision, between 0.0 and 1.0")
    decision_explanation: str = Field(description="Human-readable decision explanation and summary")

class BankGuardOrchestrator:
    """
    Coordinates the loan assessment workflow by executing the specialist agents in sequence:
    Intake & Risk Coordinator -> Document Verification -> Fraud Intelligence -> Business Validation -> Risk Scoring
    And aggregates findings to produce a final recommendation.
    """
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode or (os.getenv("MOCK_AGENTS", "false").lower() == "true")
        self.logger = logging.getLogger("BankGuardOrchestrator")

    async def run(self, application: dict) -> FinalDecisionOutput:
        """
        Runs the orchestration pipeline for the given SME loan application.
        
        Args:
            application (dict): The raw SME loan application data.
            
        Returns:
            FinalDecisionOutput: The aggregated structured decision report.
        """
        business_name = application.get("business_name", "Unknown Business")
        self.logger.info(f"Starting orchestration pipeline for: {business_name}")
        
        try:
            # 1. Invoke Intake & Risk Coordinator
            self.logger.info("Executing Step 1: Intake & Risk Coordinator...")
            intake_output = await self._run_agent_step(
                bankguard_intake__risk_coordinator,
                application
            )
            self.logger.info(f"Intake Agent complete. Output: {intake_output}")

            # 2. Invoke Document Verification Agent
            self.logger.info("Executing Step 2: Document Verification Agent...")
            doc_input = {
                "application": application,
                "intake_summary": intake_output
            }
            doc_output = await self._run_agent_step(
                bankguard_document_verification_agent,
                doc_input
            )
            self.logger.info(f"Document Verification Agent complete. Output: {doc_output}")

            # 3. Invoke Fraud Intelligence Agent
            self.logger.info("Executing Step 3: Fraud Intelligence Agent...")
            fraud_input = {
                "application": application,
                "intake_summary": intake_output,
                "doc_verification": doc_output
            }
            fraud_output = await self._run_agent_step(
                bankguard_fraud_intelligence_agent,
                fraud_input
            )
            self.logger.info(f"Fraud Intelligence Agent complete. Output: {fraud_output}")

            # 4. Invoke Business Validation Agent
            self.logger.info("Executing Step 4: Business Validation Agent...")
            business_input = {
                "application": application,
                "intake_summary": intake_output,
                "doc_verification": doc_output
            }
            business_output = await self._run_agent_step(
                bankguard_business_validation_agent,
                business_input
            )
            self.logger.info(f"Business Validation Agent complete. Output: {business_output}")

            # 5. Invoke Risk Scoring Agent
            self.logger.info("Executing Step 5: Risk Scoring Agent...")
            risk_input = {
                "application": application,
                "intake_summary": intake_output,
                "doc_verification": doc_output,
                "fraud_intelligence": fraud_output,
                "business_validation": business_output
            }
            risk_output = await self._run_agent_step(
                bankguard_risk_scoring_agent,
                risk_input
            )
            repayment_risk = risk_output.get("repayment_risk") or risk_output.get("repayment_risk_level", "Low")
            risk_score = risk_output.get("risk_score", 15)
            recommendation = risk_output.get("recommendation", "Approve")
            loan_amount = float(application.get("loan_amount", 0))
            monthly_revenue = float(application.get("monthly_revenue", 0))
            loan_to_revenue_ratio = risk_output.get("loan_to_revenue_ratio", 0.0)

            # Logging as requested
            self.logger.info(f"Risk Scoring Agent - loan_amount: {loan_amount}")
            self.logger.info(f"Risk Scoring Agent - monthly_revenue: {monthly_revenue}")
            self.logger.info(f"Risk Scoring Agent - loan_to_revenue_ratio: {loan_to_revenue_ratio}")
            self.logger.info(f"Risk Scoring Agent - risk_score: {risk_score}")
            self.logger.info(f"Risk Scoring Agent - repayment_risk: {repayment_risk}")
            self.logger.info(f"Risk Scoring Agent - recommendation: {recommendation}")

            self.logger.info(f"Risk Scoring Agent complete. Output: {risk_output}")

            # 6. Apply Decision Rules & Aggregate
            decision = self._evaluate_decision(
                application,
                intake_output,
                doc_output,
                fraud_output,
                business_output,
                risk_output
            )
            
            return decision

        except Exception as e:
            self.logger.error(f"Error in orchestrator pipeline: {e}", exc_info=True)
            raise e

    async def _run_agent_step(self, agent: Any, input_data: Union[dict, str]) -> Any:
        """
        Helper method to run an agent. If mock_mode is enabled or ADK is not configured with credentials,
        it uses mock outputs for deterministic results.
        """
        input_str = json.dumps(input_data) if isinstance(input_data, dict) else input_data

        if self.mock_mode or not ADK_AVAILABLE:
            return self._get_mock_response(agent.name, input_str)

        try:
            session_service = InMemorySessionService()
            runner = Runner(agent=agent, session_service=session_service, auto_create_session=True)
            
            message = types.Content(parts=[types.Part.from_text(text=input_str)])
            output = None
            
            async for event in runner.run_async(
                user_id="orchestrator",
                session_id=f"session_{agent.name}",
                new_message=message
            ):
                if hasattr(event, "output") and event.output is not None:
                    output = event.output
            
            if output is None:
                raise ValueError(f"Agent {agent.name} did not return any output.")
            
            # If the output is a Pydantic model, convert to dict
            if isinstance(output, BaseModel):
                return output.model_dump()
            return output

        except Exception as e:
            self.logger.warning(f"ADK invocation for {agent.name} failed. Falling back to mock. Error: {e}")
            return self._get_mock_response(agent.name, input_str)

    def _get_mock_response(self, agent_name: str, input_str: str) -> Any:
        """
        Generates mock responses for testing the orchestrator logic without requiring LLM calls.
        """
        try:
            data = json.loads(input_str)
        except Exception:
            data = {}

        # Basic parsing to extract details if they exist in nested inputs
        app_data = data.get("application", data) if "application" in data else data
        biz_name = app_data.get("business_name", "Unknown Business")

        # Simulate outputs
        if agent_name == "bankguard_intake__risk_coordinator":
            return {
                "summary": f"SME loan application for {biz_name}. Stated years in business: {app_data.get('years_in_business', 'N/A')}.",
                "data_quality": "High",
                "missing_fields": []
            }
        
        elif agent_name == "bankguard_document_verification_agent":
            return {
                "verification_status": "Pass",
                "verified_documents": ["Bank Statements", "Business Registration"],
                "mismatches": []
            }
        
        elif agent_name == "bankguard_fraud_intelligence_agent":
            owner_val = str(app_data.get("owner_name", ""))
            # For testing decision rules, we can check for specific mock inputs
            fraud_risk = "Low"
            if "high fraud" in biz_name.lower() or biz_name.lower() == "fake corp ltd" or owner_val.lower() == "fraud user":
                fraud_risk = "High"
            return {
                "fraud_risk_level": fraud_risk,
                "fraud_signals": ["None"] if fraud_risk == "Low" else ["Matches known fraud case address"],
                "confidence": 0.95
            }
        
        elif agent_name == "bankguard_business_validation_agent":
            status = "Verified"
            if "unverifiable" in biz_name.lower():
                status = "Unable to Verify"
            return {
                "business_status": status,
                "historical_records_found": True if status == "Verified" else False,
                "previous_loan_count": 1 if status == "Verified" else 0,
                "positive_signals": ["Valid registration"] if status == "Verified" else [],
                "concerns": [] if status == "Verified" else ["No public presence found"],
                "confidence": 0.90
            }
        
        elif agent_name == "bankguard_risk_scoring_agent":
            application = data.get("application", {})
            fraud_intel = data.get("fraud_intelligence", {})
            biz_val = data.get("business_validation", {})
            
            loan_amount = float(application.get("loan_amount", 0))
            monthly_revenue = float(application.get("monthly_revenue", 0))
            ratio = loan_amount / monthly_revenue if monthly_revenue > 0 else 0.0
            
            # Risk Scoring Agent Rules
            if ratio > 100:
                repayment_risk = "High"
                risk_score = 95
                recommendation = "Reject"
            elif ratio > 20:
                repayment_risk = "Medium"
                risk_score = 70
                recommendation = "Manual Review"
            elif ratio > 5:
                repayment_risk = "Medium"
                risk_score = 50
                recommendation = "Manual Review"
            else:
                repayment_risk = "Low"
                risk_score = 20
                recommendation = "Approve"
                
            # Additional rules:
            # * fraud_risk == "High" → recommendation = "Reject"
            # * business_status != "Verified" → recommendation = "Manual Review"
            fraud_risk = fraud_intel.get("fraud_risk_level", "Low")
            business_status = biz_val.get("business_status", "Verified")
            
            if fraud_risk.lower() == "high":
                recommendation = "Reject"
            elif business_status != "Verified":
                if recommendation != "Reject":
                    recommendation = "Manual Review"
                
            # Add logging
            # * loan_amount
            # * monthly_revenue
            # * loan_to_revenue_ratio
            # * risk_score
            # * repayment_risk
            # * recommendation
            self.logger.info(f"Risk Scoring Agent - loan_amount: {loan_amount}")
            self.logger.info(f"Risk Scoring Agent - monthly_revenue: {monthly_revenue}")
            self.logger.info(f"Risk Scoring Agent - loan_to_revenue_ratio: {ratio}")
            self.logger.info(f"Risk Scoring Agent - risk_score: {risk_score}")
            self.logger.info(f"Risk Scoring Agent - repayment_risk: {repayment_risk}")
            self.logger.info(f"Risk Scoring Agent - recommendation: {recommendation}")
            
            return {
                "repayment_risk": repayment_risk,
                "repayment_risk_level": repayment_risk,
                "risk_score": risk_score,
                "key_risk_factors": [f"Excessive loan-to-revenue ratio of {ratio:.2f}x"] if ratio > 20 else [],
                "positive_factors": ["Strong revenue support"] if ratio <= 5 else [],
                "loan_suitability": "Suitable" if repayment_risk == "Low" else "Unsuitable",
                "recommendation": recommendation,
                "confidence": 0.92,
                "loan_to_revenue_ratio": ratio
            }
        
        return {}

    def _evaluate_decision(
        self,
        application: dict,
        intake_out: Any,
        doc_out: Any,
        fraud_out: Any,
        business_out: Any,
        risk_out: Any
    ) -> FinalDecisionOutput:
        """
        Applies decision rules and aggregates findings.
        """
        # Normalize inputs
        def to_dict(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump()
            elif isinstance(obj, str):
                try:
                    return json.loads(obj)
                except Exception:
                    return {}
            return obj or {}

        intake_data = to_dict(intake_out)
        doc_data = to_dict(doc_out)
        fraud_data = to_dict(fraud_out)
        biz_data = to_dict(business_out)
        risk_data = to_dict(risk_out)

        # Extract parameters for decision rules
        fraud_risk = fraud_data.get("fraud_risk_level", "Low")
        business_status = biz_data.get("business_status", "Unable to Verify")
        repayment_risk = risk_data.get("repayment_risk_level", "Low")

        # Apply Decision Rules:
        # 1. If fraud risk is High: final_recommendation = "Reject"
        # 2. Else if repayment risk is High: final_recommendation = "Manual Review"
        # 3. Else if business status is "Unable to Verify": final_recommendation = "Additional Verification"
        # 4. Else: final_recommendation = "Approve"
        
        if fraud_risk.lower() == "high":
            final_rec = "Reject"
            next_action = "Reject the application immediately and flag in the fraud registry."
        elif repayment_risk.lower() == "high":
            final_rec = "Manual Review"
            next_action = "Refer to the Senior Credit Committee for manual underwriting."
        elif business_status == "Unable to Verify":
            final_rec = "Additional Verification"
            next_action = "Request additional documentation and schedule a site visit."
        else:
            final_rec = "Approve"
            next_action = "Send official approval letter and initiate loan contract signing."

        # Aggregate key reasons
        reasons = []
        if fraud_risk.lower() == "high":
            reasons.append("High fraud risk flag triggered by Fraud Intelligence Agent.")
        if repayment_risk.lower() == "high":
            reasons.append(f"High credit risk score of {risk_data.get('risk_score', 'N/A')} indicating high default probability.")
        if business_status == "Unable to Verify":
            reasons.append("Legitimacy of the business could not be confirmed via public registries or MCP historical records.")

        # Add other relevant details
        if biz_data.get("positive_signals"):
            reasons.extend([f"Business check: {s}" for s in biz_data["positive_signals"]])
        if biz_data.get("concerns"):
            reasons.extend([f"Business check: {c}" for c in biz_data["concerns"]])
        if risk_data.get("key_risk_factors"):
            reasons.extend([f"Risk factor: {r}" for r in risk_data["key_risk_factors"]])
        if risk_data.get("positive_factors"):
            reasons.extend([f"Credit strength: {p}" for p in risk_data["positive_factors"]])

        if not reasons:
            reasons = ["All automated checks passed; low risk and verified business status."]

        # Calculate combined confidence score
        confidences = []
        for agent_data in [fraud_data, biz_data, risk_data]:
            conf = agent_data.get("confidence")
            if conf is not None:
                try:
                    confidences.append(float(conf))
                except ValueError:
                    pass
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.85

        decision_data = {
            "final_recommendation": final_rec,
            "fraud_risk": fraud_risk,
            "business_status": business_status,
            "repayment_risk": repayment_risk,
            "key_reasons": reasons,
            "next_action": next_action,
            "confidence": round(avg_confidence, 2)
        }

        # Print auditable report
        logger.info("\n" + "="*50 + "\n"
                    "         AUDITABLE LOAN DECISION REPORT         \n" +
                    "="*50 + f"\n"
                    f"Business Name:          {application.get('business_name', 'Unknown')}\n"
                    f"Loan Amount:            ${application.get('loan_amount', 'N/A')}\n"
                    f"--------------------------------------------------\n"
                    f"Fraud Risk:             {fraud_risk}\n"
                    f"Business Status:        {business_status}\n"
                    f"Repayment Risk:         {repayment_risk}\n"
                    f"--------------------------------------------------\n"
                    f"Final Recommendation:   {final_rec}\n"
                    f"Next Action:            {next_action}\n"
                    f"Confidence Score:       {avg_confidence:.2f}\n"
                    f"Key Reasons:\n" + 
                    "\n".join([f"  - {r}" for r in reasons]) + "\n" +
                    "="*50)

        return FinalDecisionOutput(**decision_data)
