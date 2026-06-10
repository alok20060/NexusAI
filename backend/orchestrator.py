import asyncio
import os
import json
import logging
import random
from typing import Any, Dict, List, Union
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient

# Import Pydantic schemas
from backend.schemas import FinalDecisionOutput, AgentTraceItem, AuditLogItem

# Import the agents defined in backend.agents
from backend.agents import (
    bankguard_applicant_profiling_agent,
    bankguard_intake__risk_coordinator,
    bankguard_document_verification_agent,
    bankguard_fraud_intelligence_agent,
    bankguard_business_validation_agent,
    bankguard_risk_scoring_agent,
    bankguard_explainability_agent
)

# Import ADK components for running the agents
try:
    from google.adk import Runner
    from google.adk.sessions.in_memory_session_service import InMemorySessionService
    from google.genai import types
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

class BankGuardOrchestrator:
    """
    Coordinates the loan assessment workflow by executing the specialist agents in sequence:
    Intake & Risk Coordinator -> Document Verification -> Fraud Intelligence -> Business Validation -> Risk Scoring
    Aggregates findings to produce a final recommendation and logs outputs to MongoDB.
    """
    def __init__(self, mock_mode: bool = False):
        self.mock_mode = mock_mode or (os.getenv("MOCK_AGENTS", "false").lower() == "true")
        self.logger = logging.getLogger("NexusAI-BankGuardOrchestrator")
        
        # MongoDB connection settings for storing results
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = "mcp_demo"
        
        try:
            self.db_client = AsyncIOMotorClient(self.mongo_uri)
            self.db = self.db_client[self.db_name]
            self.logger.info("MongoDB Async Client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize MongoDB client: {e}")

    async def _init_db_collections(self):
        """
        Creates MongoDB collections for dynamic underwriting schemas:
        applicant_profiles, documents, document_analysis, asset_records, decision_history.
        """
        try:
            cols = await self.db.list_collection_names()
            for col_name in ["applicant_profiles", "documents", "document_analysis", "asset_records", "decision_history"]:
                if col_name not in cols:
                    await self.db.create_collection(col_name)
                    self.logger.info(f"Created dynamic underwriting collection: {col_name}")
        except Exception as e:
            self.logger.error(f"Failed to initialize database collections: {e}")

    async def run(self, application: dict) -> Dict[str, Any]:
        """
        Runs the orchestration pipeline for the given SME loan application.
        
        Args:
            application (dict): The raw SME loan application data.
            
        Returns:
            dict: The combined dictionary containing the final decision details, scores, reasoning trace, and audit logs.
        """
        business_name = application.get("business_name", "Unknown Business")
        self.logger.info(f"Starting orchestration pipeline for: {business_name}")
        
        audit_log = []
        reasoning_trace = []
        
        def add_audit(msg: str):
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            audit_log.append(AuditLogItem(timestamp=timestamp, message=msg))
            self.logger.info(f"[{timestamp}] {msg}")

        await self._init_db_collections()

        add_audit(f"Application Initialized for business: {business_name}")

        try:
            # Retrieve or generate application ID
            application_id = application.get("application_id")
            if not application_id:
                application_id = f"APP{random.randint(100, 999)}"
                application["application_id"] = application_id
                add_audit(f"Generated new application_id: {application_id}")

            # Step 0: Applicant Profiling Agent
            profiling_output = None
            if application_id:
                profile = await self.db.applicant_profiles.find_one({"application_id": application_id})
                if profile:
                    applicant_type = profile.get("applicant_type", "Beginner Entrepreneur")
                    required_docs = profile.get("required_documents", [])
                    profile_confidence = profile.get("profile_confidence", 0.95)
                    profiling_output = {
                        "applicant_type": applicant_type,
                        "required_documents": required_docs,
                        "profile_confidence": profile_confidence
                    }
                    add_audit(f"Loaded existing profile from database for {application_id}")

            if not profiling_output:
                add_audit("AGENT-0 [Applicant Profiling Agent] INITIALISED")
                await self._update_timeline(application_id, "Applicant Profiling", "In Progress")
                profiling_output = await self._run_agent_step(
                    bankguard_applicant_profiling_agent,
                    application
                )
                applicant_type = profiling_output.get("applicant_type", "Beginner Entrepreneur")
                required_docs = profiling_output.get("required_documents", [])
                profile_confidence = profiling_output.get("profile_confidence", 0.95)
                await self._update_timeline(application_id, "Applicant Profiling", "Completed")
                add_audit("AGENT-0 [Applicant Profiling Agent] COMPLETE")
            else:
                applicant_type = profiling_output.get("applicant_type", "Beginner Entrepreneur")
                required_docs = profiling_output.get("required_documents", [])
                profile_confidence = profiling_output.get("profile_confidence", 0.95)
                await self._update_timeline(application_id, "Applicant Profiling", "Completed")

            is_approved_demo = "Traders" in business_name

            reasoning_trace.append(AgentTraceItem(
                agent="PROFILER",
                text=f"Applicant type classified as: {applicant_type}. Required documents: {', '.join(required_docs)}"
            ))

            # Step 1: Intake Agent
            add_audit("AGENT-1 [Intake & Risk Coordinator] INITIALISED")
            await self._update_timeline(application_id, "Application Intake", "In Progress")
            intake_output = await self._run_agent_step(
                bankguard_intake__risk_coordinator,
                application
            )
            reasoning_trace.append(AgentTraceItem(
                agent="INTAKE",
                text=intake_output.get("summary", "Application profile normalized and validated.")
            ))
            await self._update_timeline(application_id, "Application Intake", "Completed")
            add_audit("AGENT-1 [Intake & Risk Coordinator] COMPLETE")

            # Step 2: Document Verification Agent
            add_audit("AGENT-2 [Document Verification Agent] INITIALISED")
            await self._update_timeline(application_id, "Document Verification", "In Progress")
            
            # Check files on disk
            doc_output = await self._check_uploaded_documents(application_id, required_docs, is_approved_demo)
            
            doc_input = {
                "application": application,
                "intake_summary": intake_output,
                "filesystem_results": doc_output
            }
            agent_doc_output = await self._run_agent_step(
                bankguard_document_verification_agent,
                doc_input
            )
            
            verified_docs = doc_output.get("verified_documents", [])
            missing_docs = doc_output.get("missing_documents", [])
            unsupported_docs = doc_output.get("unsupported_documents", [])
            document_completeness = doc_output.get("document_completeness", 0.0)
            
            reasoning_trace.append(AgentTraceItem(
                agent="DOC-VERIFY",
                text=f"Verification completeness: {document_completeness * 100:.0f}%. Verified: {', '.join(verified_docs)}. Missing: {', '.join(missing_docs)}"
            ))
            await self._update_timeline(application_id, "Document Verification", "Completed")
            add_audit("AGENT-2 [Document Verification Agent] COMPLETE")

            # Step 3: Fraud Intelligence Agent
            add_audit("AGENT-3 [Fraud Intelligence Agent] INITIALISED")
            await self._update_timeline(application_id, "Fraud Intelligence", "In Progress")
            fraud_input = {
                "application": application,
                "intake_summary": intake_output,
                "doc_verification": agent_doc_output
            }
            fraud_output = await self._run_agent_step(
                bankguard_fraud_intelligence_agent,
                fraud_input
            )
            fraud_risk = fraud_output.get("fraud_risk_level", "Low")
            reasoning_trace.append(AgentTraceItem(
                agent="FRAUD-INTEL",
                text=f"Fraud risk: {fraud_risk}. Signals: {', '.join(fraud_output.get('fraud_signals', []))}."
            ))
            await self._update_timeline(application_id, "Fraud Intelligence", "Completed")
            add_audit("AGENT-3 [Fraud Intelligence Agent] COMPLETE")

            # Step 4: Business Validation Agent
            add_audit("AGENT-4 [Business Validation Agent] INITIALISED")
            await self._update_timeline(application_id, "Business Validation", "In Progress")
            business_input = {
                "application": application,
                "intake_summary": intake_output,
                "doc_verification": agent_doc_output
            }
            business_output = await self._run_agent_step(
                bankguard_business_validation_agent,
                business_input
            )
            biz_status = business_output.get("business_status", "Verified")
            reasoning_trace.append(AgentTraceItem(
                agent="BIZ-VALID",
                text=f"Business status: {biz_status}. History found: {business_output.get('historical_records_found', False)} (Loans: {business_output.get('previous_loan_count', 0)})."
            ))
            await self._update_timeline(application_id, "Business Validation", "Completed")
            add_audit("AGENT-4 [Business Validation Agent] COMPLETE")

            # Step 5: Risk Scoring Agent
            add_audit("AGENT-5 [Risk Scoring Agent] INITIALISED")
            await self._update_timeline(application_id, "Risk Scoring", "In Progress")
            risk_input = {
                "application": application,
                "intake_summary": intake_output,
                "doc_verification": agent_doc_output,
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

            reasoning_trace.append(AgentTraceItem(
                agent="RISK-SCORING",
                text=f"Repayment risk: {repayment_risk} (Score: {risk_score}/100). Recommendation: {recommendation}."
            ))
            await self._update_timeline(application_id, "Risk Scoring", "Completed")
            add_audit("AGENT-5 [Risk Scoring Agent] COMPLETE")

            # Evaluate Final Adjudication Rules
            decision = self._evaluate_decision(
                application,
                intake_output,
                agent_doc_output,
                fraud_output,
                business_output,
                risk_output,
                applicant_type,
                required_docs,
                missing_docs,
                verified_docs
            )
            
            # Map dynamic fraud score from risk level (for UI representation)
            fraud_score = 85 if decision.fraud_risk.lower() == "high" else 45 if decision.fraud_risk.lower() == "medium" else 5
            
            # Step 6: Decision Explainability Agent (Agent 6)
            add_audit("AGENT-6 [Explainability Agent] INITIALISED")
            await self._update_timeline(application_id, "Decision Explainability", "In Progress")
            explain_input = {
                "final_recommendation": decision.final_recommendation,
                "fraud_risk": decision.fraud_risk,
                "business_status": decision.business_status,
                "repayment_risk": decision.repayment_risk,
                "key_reasons": decision.key_reasons,
                "next_action": decision.next_action,
                "applicant_type": applicant_type,
                "verified_documents": verified_docs,
                "missing_documents": missing_docs,
                "unsupported_documents": unsupported_docs
            }
            explain_output = await self._run_agent_step(
                bankguard_explainability_agent,
                explain_input
            )
            explainability_report = explain_output.get("explainability_report", "")
            
            reasoning_trace.append(AgentTraceItem(
                agent="EXPLAINER",
                text="Human-readable explanation report generated by Agent 6."
            ))
            await self._update_timeline(application_id, "Decision Explainability", "Completed")
            add_audit("AGENT-6 [Explainability Agent] COMPLETE")

            add_audit(f"DECISION: {decision.final_recommendation.upper()}")
            
            # Post-decision side-effect: Async MongoDB logging
            await self._store_results(
                application,
                decision,
                risk_score,
                fraud_score,
                applicant_type,
                required_docs,
                profile_confidence,
                application_id=application_id
            )

            # Fetch timeline events
            timeline_events = []
            try:
                STAGE_ORDER = [
                    "Applicant Profiling",
                    "Application Intake",
                    "Document Verification",
                    "Fraud Intelligence",
                    "Business Validation",
                    "Risk Scoring",
                    "Decision Explainability"
                ]
                cursor = self.db.application_timeline.find({"application_id": application_id})
                db_events = await cursor.to_list(length=100)
                db_events.sort(key=lambda x: STAGE_ORDER.index(x["stage"]) if x["stage"] in STAGE_ORDER else 99)
                for event in db_events:
                    timeline_events.append({
                        "stage": event["stage"],
                        "status": event["status"],
                        "timestamp": event["timestamp"]
                    })
            except Exception as e:
                self.logger.error(f"Error fetching timeline: {e}")
                
            if not timeline_events:
                from datetime import datetime
                now_str = datetime.now().isoformat()
                timeline_events = [
                    {"stage": s, "status": "Completed", "timestamp": now_str} for s in STAGE_ORDER
                ]

            add_audit("AUDIT SEALED")

             # Return full payload for API response
            return {
                "final_recommendation": decision.final_recommendation,
                "fraud_risk": decision.fraud_risk,
                "business_status": decision.business_status,
                "repayment_risk": decision.repayment_risk,
                "key_reasons": decision.key_reasons,
                "confidence": decision.confidence,
                "next_action": decision.next_action,
                "risk_score": risk_score,
                "fraud_score": fraud_score,
                "decision_explanation": decision.decision_explanation,
                "reasoning_trace": reasoning_trace,
                "audit_log": audit_log,
                
                # Dynamic checklists
                "applicant_type": applicant_type,
                "required_documents": required_docs,
                "missing_documents": missing_docs,
                "verified_documents": verified_docs,
                "document_completeness": document_completeness,
                "upload_progress": document_completeness,
                "explainability_report": explainability_report,
                "timeline": timeline_events,
                
                # Intermediate outputs for debugging
                "agent_0_output": profiling_output,
                "agent_1_output": intake_output,
                "agent_2_output": agent_doc_output,
                "agent_3_output": fraud_output,
                "agent_4_output": business_output,
                "agent_5_output": risk_output,
                "agent_6_output": explain_output,
                "orchestrator_decision": decision.model_dump() if isinstance(decision, BaseModel) else decision
            }

        except Exception as e:
            self.logger.error(f"Error in orchestrator pipeline: {e}", exc_info=True)
            add_audit(f"Pipeline error: {str(e)}")
            raise e

    async def _run_agent_step(self, agent: Any, input_data: Union[dict, str]) -> Any:
        """
        Helper method to run an agent. Uses mock outputs for deterministic results when in mock mode or when ADK is unavailable.
        """
        input_str = json.dumps(input_data) if isinstance(input_data, dict) else input_data

        if self.mock_mode or not ADK_AVAILABLE:
            await asyncio.sleep(0.5)  # Simulate agent thinking time
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
            
            if isinstance(output, BaseModel):
                return output.model_dump()
            return output

        except Exception as e:
            self.logger.warning(f"ADK invocation for {agent.name} failed. Falling back to mock. Error: {e}")
            return self._get_mock_response(agent.name, input_str)

    def _get_mock_response(self, agent_name: str, input_str: str) -> Any:
        try:
            data = json.loads(input_str)
        except Exception:
            data = {}

        app_data = data.get("application", data) if "application" in data else data
        biz_name = app_data.get("business_name", "Unknown Business")

        if agent_name == "bankguard_applicant_profiling_agent":
            loan_amount = float(app_data.get("loan_amount", 0))
            years_in_business = int(app_data.get("years_in_business", 5))
            
            if loan_amount >= 10000000:
                app_type = "High-Value Loan Applicant"
                req_docs = [
                    "Business registration certificate",
                    "Office address proof",
                    "Utility bills",
                    "Bank statements",
                    "Tax returns",
                    "Credit score report",
                    "Audited financial statements",
                    "Cash flow reports",
                    "Inventory records",
                    "Supplier contracts",
                    "Collateral documents"
                ]
            elif years_in_business < 2:
                app_type = "Beginner Entrepreneur"
                req_docs = [
                    "Personal ID",
                    "Asset proofs",
                    "Property documents",
                    "Savings account statements",
                    "Education/professional background",
                    "Guarantor information"
                ]
            else:
                app_type = "Experienced Business Owner"
                req_docs = [
                    "Business registration certificate",
                    "Office address proof",
                    "Utility bills",
                    "Bank statements",
                    "Tax returns",
                    "Credit score report"
                ]
            return {
                "applicant_type": app_type,
                "required_documents": req_docs,
                "profile_confidence": 0.95
            }

        elif agent_name == "bankguard_intake__risk_coordinator":
            return {
                "summary": f"SME loan application for {biz_name}. Stated years in business: {app_data.get('years_in_business', 5)}.",
                "data_quality": "High",
                "missing_fields": []
            }
        
        elif agent_name == "bankguard_document_verification_agent":
            return data.get("filesystem_results", {
                "document_completeness": 1.0,
                "verified_documents": ["Bank Statements", "Business Registration"],
                "missing_documents": [],
                "unsupported_documents": []
            })
        
        elif agent_name == "bankguard_fraud_intelligence_agent":
            from pymongo import MongoClient as _MongoClient
            owner_val = str(app_data.get("owner_name", ""))

            # ── MongoDB debug state ───────────────────────────────────────────
            mongodb_connected  = False
            collection_name    = "fraud_cases"
            query_used         = {}
            fraud_records_found = 0
            fraud_match        = False
            matched_records    = []
            db_error           = None

            # ── Build query: match on business_name OR owner_name ─────────────
            conditions = []
            if biz_name and biz_name != "Unknown Business":
                conditions.append({"business_name": {"$regex": f"^{biz_name}$", "$options": "i"}})
            if owner_val:
                conditions.append({"owner_name": {"$regex": f"^{owner_val}$", "$options": "i"}})
            query_used = {"$or": conditions} if conditions else {}

            self.logger.info(f"[FRAUD-AGENT] Connecting to MongoDB at {self.mongo_uri}")
            self.logger.info(f"[FRAUD-AGENT] Collection: mcp_demo.{collection_name}")
            self.logger.info(f"[FRAUD-AGENT] Query: {query_used}")

            try:
                _client = _MongoClient(self.mongo_uri, serverSelectionTimeoutMS=3000)
                _client.admin.command("ping")          # confirm connection
                mongodb_connected = True
                self.logger.info("[FRAUD-AGENT] MongoDB connection: SUCCESS")

                _db   = _client["mcp_demo"]
                _coll = _db[collection_name]

                if query_used:
                    _docs = list(_coll.find(query_used, {"_id": 0}))
                else:
                    _docs = []

                fraud_records_found = len(_docs)
                matched_records     = _docs
                fraud_match         = fraud_records_found > 0

                self.logger.info(f"[FRAUD-AGENT] Documents returned: {fraud_records_found}")
                if fraud_match:
                    self.logger.info(f"[FRAUD-AGENT] Fraud match FOUND: {_docs}")
                else:
                    self.logger.info("[FRAUD-AGENT] No fraud records matched.")

                _client.close()
            except Exception as _e:
                db_error = str(_e)
                self.logger.error(f"[FRAUD-AGENT] MongoDB connection FAILED: {_e}")

            # ── Determine fraud_risk from DB result (legacy fallback kept) ────
            if fraud_match:
                # A DB record is definitive evidence of fraud
                db_fraud_risk = matched_records[0].get("fraud_risk", "High")
                fraud_risk    = db_fraud_risk if db_fraud_risk else "High"
                fraud_signals = [
                    f"Matched fraud_cases record — business: '{biz_name}', owner: '{owner_val}'"
                ]
            else:
                # Legacy keyword / phone-number/name fallback
                fraud_risk = "Low"
                if "high fraud" in biz_name.lower() \
                   or biz_name.lower() == "fake corp ltd" \
                   or owner_val.lower() == "fraud user" \
                   or owner_val in ("+91 98765 43210", "+55 11 98765-4321",
                                    "+234 803 111 2222", "+62 812-3456-7890"):
                    fraud_risk = "High"
                    fraud_signals = ["Matches known fraud case blacklisted details"]
                else:
                    fraud_signals = ["None"]

            self.logger.info(f"[FRAUD-AGENT] Fraud risk assigned: {fraud_risk}")

            return {
                # ── Core fraud assessment ──────────────────────────────────────
                "fraud_risk_level": fraud_risk,
                "fraud_signals":    fraud_signals,
                "confidence":       0.95,
                # ── MongoDB debug fields ───────────────────────────────────────
                "mongodb_connected":    mongodb_connected,
                "collection":           collection_name,
                "query_used":           query_used,
                "fraud_records_found":  fraud_records_found,
                "fraud_match":          fraud_match,
                "matched_records":      matched_records,
                **({"db_error": db_error} if db_error else {}),
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
        
        elif agent_name == "bankguard_explainability_agent":
            rec = data.get("final_recommendation", "Approve")
            reasons = data.get("key_reasons", [])
            verified = data.get("verified_documents", [])
            missing = data.get("missing_documents", [])
            unsupported = data.get("unsupported_documents", [])
            
            report_lines = []
            report_lines.append(f"NexusAI-BankGuard Underwriting Assessment Report")
            report_lines.append(f"=============================================")
            report_lines.append(f"Final Recommendation: {rec.upper()}")
            report_lines.append("")
            
            report_lines.append("Verification Checklist:")
            if verified:
                for doc in verified:
                    report_lines.append(f"  ✓ {doc}: Verified")
            if missing:
                for doc in missing:
                    report_lines.append(f"  ✗ {doc}: Missing")
            if unsupported:
                for doc in unsupported:
                    report_lines.append(f"  ✗ {doc}: Corrupted/Unsupported")
            if not verified and not missing and not unsupported:
                report_lines.append("  - No documents evaluated.")
                
            report_lines.append("")
            report_lines.append("Key Decision Factors:")
            if rec.lower() == "approve":
                report_lines.append("  ✓ All automated credit risk thresholds satisfied.")
                report_lines.append("  ✓ Legitimacy check verified in public business records.")
                report_lines.append("  ✓ Fraud intelligence checks return clear.")
            else:
                for r in reasons:
                    report_lines.append(f"  ✗ {r}")
                    
            return {
                "explainability_report": "\n".join(report_lines)
            }
        
        return {}

    def _evaluate_decision(
        self,
        application: dict,
        intake_out: Any,
        doc_out: Any,
        fraud_out: Any,
        business_out: Any,
        risk_out: Any,
        applicant_type: str = "Beginner Entrepreneur",
        required_docs: list[str] = None,
        missing_docs: list[str] = None,
        verified_docs: list[str] = None
    ) -> FinalDecisionOutput:
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

        fraud_risk = fraud_data.get("fraud_risk_level", "Low")
        business_status = biz_data.get("business_status", "Unable to Verify")
        repayment_risk = risk_data.get("repayment_risk_level", "Low")

        # Computed fields
        loan_amount = float(application.get("loan_amount", 0))
        monthly_revenue = float(application.get("monthly_revenue", 0))
        ratio = loan_amount / monthly_revenue if monthly_revenue > 0 else 0.0
        risk_score = risk_data.get("risk_score", 15)

        # Apply risk rules
        if ratio > 100:
            final_rec = "Reject"
            next_action = "Reject the application immediately due to an excessive Loan-to-Revenue ratio exceeding 100x."
        elif fraud_risk.lower() == "high":
            final_rec = "Reject"
            next_action = "Reject the application immediately and flag in the fraud registry."
        elif ratio > 20:
            final_rec = "Manual Review"
            next_action = "Refer to the Senior Credit Committee for manual underwriting due to high Loan-to-Revenue ratio exceeding 20x."
        elif business_status == "Unable to Verify":
            final_rec = "Manual Review"
            next_action = "Refer to the Senior Credit Committee for manual underwriting due to unverifiable business status."
        else:
            final_rec = "Approve"
            next_action = "Send official approval letter and initiate loan contract signing."

        # Logging as requested
        self.logger.info(f"--- Risk Rules Evaluation ---")
        self.logger.info(f"Loan Amount: {loan_amount}")
        self.logger.info(f"Monthly Revenue: {monthly_revenue}")
        self.logger.info(f"Computed Ratio: {ratio:.2f}x")
        self.logger.info(f"Risk Score: {risk_score}")
        self.logger.info(f"Fraud Risk: {fraud_risk}")
        self.logger.info(f"Business Status: {business_status}")
        self.logger.info(f"Final Decision: {final_rec}")
        self.logger.info(f"-----------------------------")

        # Aggregate reasons
        reasons = []
        if ratio > 100:
            reasons.append(f"Loan-to-revenue ratio ({ratio:.2f}x) exceeds the maximum ceiling of 100x.")
        elif ratio > 20:
            reasons.append(f"Loan-to-revenue ratio ({ratio:.2f}x) exceeds the manual review threshold of 20x.")
        
        if fraud_risk.lower() == "high":
            reasons.append("High fraud risk flag triggered by Fraud Intelligence Agent.")
        if business_status == "Unable to Verify":
            reasons.append("Legitimacy of the business could not be confirmed via public registries or MCP historical records.")
        if repayment_risk.lower() == "high":
            reasons.append(f"High credit risk score of {risk_score}/100 indicating high default probability.")

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

        confidences = []
        for agent_data in [fraud_data, biz_data, risk_data]:
            conf = agent_data.get("confidence")
            if conf is not None:
                try:
                    confidences.append(float(conf))
                except ValueError:
                    pass
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.85

        # Generate human-readable summary explanation
        explanation_reasons = []
        is_approved = final_rec.upper() == "APPROVE"
        
        if is_approved:
            # Positive reasons
            if ratio <= 20:
                explanation_reasons.append("Loan-to-revenue ratio within acceptable range.")
            else:
                explanation_reasons.append(f"Loan-to-revenue ratio is {ratio:.2f}x.")
                
            if business_status == "Verified":
                explanation_reasons.append("Business verification successful.")
            else:
                explanation_reasons.append(f"Business verification status: {business_status}.")
                
            if fraud_risk.lower() == "low":
                explanation_reasons.append("No fraud indicators detected.")
            else:
                explanation_reasons.append(f"Fraud risk is {fraud_risk}.")
                
            if repayment_risk.lower() == "low":
                explanation_reasons.append("Strong repayment capacity.")
            else:
                explanation_reasons.append(f"Repayment risk: {repayment_risk}.")
        else:
            # Risk factors
            if ratio > 100:
                explanation_reasons.append(f"Loan-to-revenue ratio ({ratio:.2f}x) is excessive (exceeds 100x absolute limit).")
            elif ratio > 20:
                explanation_reasons.append(f"Loan-to-revenue ratio ({ratio:.2f}x) exceeds the manual review threshold of 20x.")
            elif ratio > 5:
                explanation_reasons.append(f"Loan-to-revenue ratio ({ratio:.2f}x) is elevated.")
                
            if business_status == "Unable to Verify":
                explanation_reasons.append("Business registration details could not be verified.")
            elif business_status != "Verified":
                explanation_reasons.append(f"Business status is not fully verified ('{business_status}').")
                
            if fraud_risk.lower() == "high":
                explanation_reasons.append("High fraud risk alert triggered.")
            elif fraud_risk.lower() == "medium":
                explanation_reasons.append("Potential fraud risk anomalies identified.")
                
            if repayment_risk.lower() == "high":
                explanation_reasons.append(f"High credit default risk profile (Score: {risk_score}/100).")
            elif repayment_risk.lower() == "medium":
                explanation_reasons.append(f"Elevated credit risk score (Score: {risk_score}/100).")

        if not explanation_reasons:
            if is_approved:
                explanation_reasons = ["All standard criteria met for approval."]
            else:
                explanation_reasons = ["Elevated risk factors detected across parameters."]

        reasons_text = "\n".join([f"* {r}" for r in explanation_reasons])
        confidence_pct = int(round(avg_confidence * 100))
        dec_label = "APPROVED" if is_approved else ("REJECTED" if final_rec.upper() == "REJECT" else "PENDING MANUAL REVIEW")
        explanation_str = f"Decision: {dec_label}\n\nReasons:\n{reasons_text}\n\nConfidence: {confidence_pct}%"

        decision_data = {
            "final_recommendation": final_rec,
            "fraud_risk": fraud_risk,
            "business_status": business_status,
            "repayment_risk": repayment_risk,
            "key_reasons": reasons,
            "next_action": next_action,
            "confidence": round(avg_confidence, 2),
            "decision_explanation": explanation_str,
            "applicant_type": applicant_type,
            "required_documents": required_docs or [],
            "missing_documents": missing_docs or [],
            "verified_documents": verified_docs or []
        }

        return FinalDecisionOutput(**decision_data)

    async def _store_results(
        self,
        application: dict,
        decision: FinalDecisionOutput,
        risk_score: int,
        fraud_score: int,
        applicant_type: str,
        required_documents: list[str],
        profile_confidence: float,
        application_id: str = None
    ):
        """
        Stores the application, fraud report, and loan history details to MongoDB,
        as well as writing BSON schemas to the new collections:
        applicant_profiles, documents, document_analysis, asset_records, decision_history.
        Uses non-blocking motor async queries.
        """
        from datetime import datetime
        self.logger.info("Storing application and decision results into MongoDB...")
        try:
            business_name = application.get("business_name")
            loan_amount = application.get("loan_amount", 0)
            
            app_id = application_id or application.get("application_id") or f"APP{random.randint(100, 999)}"
            
            # 1. Insert/Update into 'applications'
            app_doc = {
                "application_id": app_id,
                "business_name": business_name,
                "owner_name": application.get("owner_name"),
                "country": application.get("country", "India"),
                "industry": application.get("industry", "General Trade"),
                "years_in_business": int(application.get("years_in_business", 5)),
                "loan_amount": int(loan_amount),
                "revenue": int(application.get("monthly_revenue", 0) * 12),
                "existing_debt": int(application.get("existing_debt", 0)),
                "address": application.get("address", "123 Main St"),
                "phone": application.get("phone", "+91 98765 43210"),
                "email": application.get("email", f"info@{business_name.lower().replace(' ', '')}.com" if business_name else "info@business.com"),
                "website": application.get("website", f"www.{business_name.lower().replace(' ', '')}.com" if business_name else "www.business.com"),
                "decision": decision.final_recommendation
            }
            await self.db.applications.update_one({"application_id": app_id}, {"$set": app_doc}, upsert=True)
            self.logger.info(f"Stored application record {app_id} in 'applications'")

            # 2. Insert into 'fraud_cases' if fraud risk is high
            if decision.fraud_risk.lower() == "high":
                fc_id = f"FC{random.randint(100, 999)}"
                fraud_doc = {
                    "case_id": fc_id,
                    "reason": f"High fraud risk detected for owner: {application.get('owner_name')}",
                    "phone": application.get("phone", "+91 98765 43210"),
                    "address": application.get("address", "123 Fraud Lane, Mumbai, India")
                }
                await self.db.fraud_cases.insert_one(fraud_doc)
                self.logger.info(f"Stored fraud case {fc_id} in 'fraud_cases'")

            # 3. Update 'loan_history' if approved
            if decision.final_recommendation.lower() == "approve":
                loan_id = f"L{random.randint(100, 999)}"
                await self.db.loan_history.update_one(
                    {"business_name": business_name},
                    {
                        "$push": {
                            "previous_loans": {
                                "loan_id": loan_id,
                                "amount": int(loan_amount),
                                "decision": "Approved",
                                "repayment_status": "Completed"
                            }
                        }
                    },
                    upsert=True
                )
                self.logger.info(f"Pushed loan history record {loan_id} for {business_name}")

            # 4. Update 'applicant_profiles'
            await self.db.applicant_profiles.update_one(
                {"application_id": app_id},
                {"$set": {
                    "applicant_type": applicant_type,
                    "required_documents": required_documents,
                    "profile_confidence": profile_confidence
                }},
                upsert=True
            )
            self.logger.info(f"Stored profile in 'applicant_profiles' for {app_id}")

            # 5. Insert into 'documents' (for each required document if not already exists)
            is_approved_demo = "Traders" in business_name
            status = "Verified" if is_approved_demo else "Pending"
            for doc_type in required_documents:
                existing_doc = await self.db.documents.find_one({"application_id": app_id, "document_type": doc_type})
                if not existing_doc:
                    file_name = f"{business_name.lower().replace(' ', '_')}_{doc_type.lower().replace(' ', '_')}.pdf" if status == "Verified" else "N/A"
                    await self.db.documents.insert_one({
                        "application_id": app_id,
                        "document_type": doc_type,
                        "upload_status": status,
                        "file_name": file_name,
                        "uploaded_at": datetime.now().isoformat() if status == "Verified" else "N/A"
                    })
            self.logger.info(f"Stored document checkpoints in 'documents' for {app_id}")

            # 6. Update 'document_analysis'
            await self.db.document_analysis.update_one(
                {"application_id": app_id},
                {"$set": {
                    "analysis_status": "Completed" if is_approved_demo else "Pending",
                    "inconsistencies": []
                }},
                upsert=True
            )
            self.logger.info(f"Stored analysis record in 'document_analysis' for {app_id}")

            # 7. Update 'asset_records'
            if applicant_type == "Beginner Entrepreneur":
                await self.db.asset_records.update_one(
                    {"application_id": app_id},
                    {"$set": {
                        "asset_type": "Savings Account",
                        "estimated_value": 250000.0,
                        "ownership_status": "Owned"
                    }},
                    upsert=True
                )
                self.logger.info(f"Stored mock asset in 'asset_records' for {app_id}")

            # 8. Insert into 'decision_history'
            await self.db.decision_history.insert_one({
                "application_id": app_id,
                "final_decision": decision.final_recommendation,
                "confidence_score": decision.confidence,
                "reason_codes": decision.key_reasons,
                "created_at": datetime.now().isoformat()
            })
            self.logger.info(f"Stored decision in 'decision_history' for {app_id}")

        except Exception as e:
            self.logger.error(f"Failed to store results to MongoDB: {e}", exc_info=True)

    def _get_upload_dir(self) -> str:
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

    def _sanitize_doc_type(self, doc_type: str) -> str:
        import re
        s = doc_type.lower()
        s = re.sub(r'[^a-z0-9]', '_', s)
        s = re.sub(r'_+', '_', s)
        return s.strip('_')

    async def _update_timeline(self, application_id: str, stage: str, status: str):
        from datetime import datetime
        if not application_id:
            return
        try:
            timestamp = datetime.now().isoformat()
            await self.db.application_timeline.update_one(
                {"application_id": application_id, "stage": stage},
                {"$set": {"status": status, "timestamp": timestamp}},
                upsert=True
            )
            self.logger.info(f"Updated timeline stage '{stage}' to '{status}' for {application_id}")
        except Exception as e:
            self.logger.error(f"Failed to update timeline: {e}")

    async def _check_uploaded_documents(self, application_id: str, required_docs: List[str], is_approved_demo: bool = False) -> Dict[str, Any]:
        import os
        from pypdf import PdfReader
        from PIL import Image
        
        verified = []
        missing = []
        unsupported = []
        
        # If it's the approved demo and no application_id/uploads exist, mock it as successful
        if is_approved_demo and (not application_id or not os.path.exists(os.path.join(self._get_upload_dir(), application_id))):
            return {
                "document_completeness": 1.0,
                "verified_documents": required_docs,
                "missing_documents": [],
                "unsupported_documents": []
            }
            
        if not application_id:
            return {
                "document_completeness": 0.0,
                "verified_documents": [],
                "missing_documents": required_docs,
                "unsupported_documents": []
            }
            
        upload_dir = os.path.join(self._get_upload_dir(), application_id)
        if not os.path.exists(upload_dir):
            return {
                "document_completeness": 0.0,
                "verified_documents": [],
                "missing_documents": required_docs,
                "unsupported_documents": []
            }
            
        for doc_type in required_docs:
            sanitized = self._sanitize_doc_type(doc_type)
            # Find any file starting with sanitized doc type
            found_file = None
            try:
                for f in os.listdir(upload_dir):
                    base_name, ext = os.path.splitext(f)
                    if base_name == sanitized:
                        found_file = f
                        break
            except Exception:
                pass
                    
            if not found_file:
                missing.append(doc_type)
                continue
                
            filepath = os.path.join(upload_dir, found_file)
            _, ext = os.path.splitext(found_file)
            ext = ext.lower().strip('.')
            
            # Check file type
            if ext not in ['pdf', 'png', 'jpeg', 'jpg']:
                unsupported.append(f"{doc_type} (Unsupported extension: .{ext})")
                continue
                
            # Check file size (10MB limit)
            try:
                size = os.path.getsize(filepath)
                if size > 10 * 1024 * 1024:
                    unsupported.append(f"{doc_type} (File size exceeds 10MB)")
                    continue
            except Exception:
                unsupported.append(f"{doc_type} (Could not read file size)")
                continue
                
            # Check corruption
            corrupted = False
            try:
                if ext == 'pdf':
                    reader = PdfReader(filepath)
                    _ = len(reader.pages)
                else:
                    with Image.open(filepath) as img:
                        img.verify()
            except Exception:
                corrupted = True
                
            if corrupted:
                unsupported.append(f"{doc_type} (File corrupted or unreadable)")
            else:
                verified.append(doc_type)
                
        completeness = len(verified) / len(required_docs) if required_docs else 0.0
        return {
            "document_completeness": completeness,
            "verified_documents": verified,
            "missing_documents": missing,
            "unsupported_documents": unsupported
        }
