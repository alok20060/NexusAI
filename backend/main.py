import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Any

# Ensure project root is in sys.path for Vercel deployment and local runs
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import schemas and orchestrator
from backend.schemas import LoanAnalysisInput, LoanAnalysisResponse
from backend.orchestrator import BankGuardOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("NexusAI-BankGuardAPI")

app = FastAPI(title="NexusAI-BankGuard Neural Credit API", version="2.4")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate the Orchestrator
orchestrator = BankGuardOrchestrator()

@app.post("/analyze-loan", response_model=LoanAnalysisResponse)
async def analyze_loan(payload: LoanAnalysisInput):
    """
    Accepts an SME loan application request, coordinates the multi-agent neural assessment,
    evaluates loan eligibility, logs results to MongoDB, and returns the full audit decision.
    """
    logger.info(f"Received loan request for business: {payload.business_name}")
    try:
        # Convert input schema to dict structure expected by the orchestrator
        application_data = {
            "business_name": payload.business_name,
            "owner_name": payload.owner_name,
            "loan_amount": payload.loan_amount,
            "monthly_revenue": payload.monthly_revenue,
            "industry": payload.industry,
            "loan_purpose": payload.loan_purpose,
            "years_in_business": 5, # default/mock Operational parameters
            "country": "India"      # default geographical zone
        }
        
        # Execute the orchestrator
        result = await orchestrator.run(application_data)
        
        # Prepare final response sub-object
        final_resp = {
            "final_recommendation": result["final_recommendation"],
            "fraud_risk": result["fraud_risk"],
            "business_status": result["business_status"],
            "repayment_risk": result["repayment_risk"],
            "key_reasons": result["key_reasons"],
            "confidence": result["confidence"],
            "next_action": result["next_action"],
            
            # Dynamic and audit UI variables
            "reference_id": result["audit_log"][0].message.split("business:")[0].split("application ")[-1].strip() if "application" in result["audit_log"][0].message else f"NBG-{os.urandom(3).hex().upper()}",
            "risk_score": result["risk_score"],
            "fraud_score": result["fraud_score"],
            "loan_to_revenue_ratio": round(payload.loan_amount / payload.monthly_revenue, 2) if payload.monthly_revenue > 0 else 0.0,
            "reasoning_trace": result["reasoning_trace"],
            "audit_log": result["audit_log"],
            "decision_explanation": result["decision_explanation"]
        }
        
        # Ensure reference ID makes sense
        if not final_resp["reference_id"] or "Application" in final_resp["reference_id"]:
            # extract code like BG-XXXX-XXXX
            words = result["audit_log"][0].message.split()
            ref_word = [w for w in words if w.startswith("NBG-")]
            if ref_word:
                final_resp["reference_id"] = ref_word[0]
            else:
                final_resp["reference_id"] = f"NBG-{os.urandom(3).hex().upper()}"

        logger.info(f"Completed loan request processing for business: {payload.business_name} with decision: {result['final_recommendation']}")
        
        # Construct the detailed debugging structure requested by the user
        debug_response = {
            "input": {
                "business_name": payload.business_name,
                "owner_name": payload.owner_name,
                "loan_amount": payload.loan_amount,
                "monthly_revenue": payload.monthly_revenue,
                "industry": payload.industry,
                "loan_purpose": payload.loan_purpose
            },
            "agent_1_output": result["agent_1_output"],
            "agent_2_output": result["agent_2_output"],
            "agent_3_output": result["agent_3_output"],
            "agent_4_output": result["agent_4_output"],
            "agent_5_output": result["agent_5_output"],
            "orchestrator_decision": result["orchestrator_decision"],
            "final_response": final_resp
        }
        return debug_response

    except Exception as e:
        logger.error(f"Error executing loan analysis: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal multi-agent system failure: {str(e)}")

@app.get("/health")
def health():
    return {"status": "online"}

@app.get("/")
async def get_frontend():
    """
    Serves the NexusAI-BankGuard interactive credit analysis tool index page.
    """
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        # Fallback to serving the root-level bankagent.html if frontend/index.html is missing
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bankagent.html")
        if os.path.exists(fallback_path):
            return FileResponse(fallback_path)
        raise HTTPException(status_code=404, detail="NexusAI-BankGuard frontend interface not found.")
