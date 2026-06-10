from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# 1. Gemini 2.5 Advanced Extraction & Reasoning Interface
class GeminiExtractionRequest(BaseModel):
    document_path: str = Field(..., description="Local path or cloud URI of the document")
    prompt_template: Optional[str] = Field(None, description="Custom prompt template for structured output guidance")
    target_schema: Dict[str, Any] = Field(..., description="JSON schema representing target fields to extract")

class GeminiExtractionResponse(BaseModel):
    extracted_fields: Dict[str, Any] = Field(..., description="Key-value extracted pairs mapping to target schema")
    confidence: float = Field(..., description="Extraction confidence score (0.0 to 1.0)")
    token_usage: Dict[str, int] = Field(..., description="Input, output, and reasoning tokens consumed")
    raw_response: str = Field(..., description="Raw output text from Gemini 2.5")

class IGeminiExtractor(ABC):
    @abstractmethod
    async def extract_structured_data(self, request: GeminiExtractionRequest) -> GeminiExtractionResponse:
        """
        Uses Gemini 2.5 multimodal features (PDF/Image input) to extract credit fields.
        """
        pass

    @abstractmethod
    async def explain_decision_anomalies(self, application_data: Dict[str, Any], extracted_data: Dict[str, Any]) -> str:
        """
        Generates deep reasoning trace explaining why document discrepancies exist.
        """
        pass


# 2. Google Document AI Integration Interface
class DocumentAIProcessorConfig(BaseModel):
    project_id: str = Field(..., description="GCP Project ID")
    location: str = Field("us", description="Processor location (us or eu)")
    processor_id: str = Field(..., description="Document AI Processor ID")
    mime_type: str = Field("application/pdf", description="Document mime type")

class IDocumentAIClient(ABC):
    @abstractmethod
    async def configure_processor(self, config: DocumentAIProcessorConfig) -> bool:
        """
        Initializes credentials and configures target Google Document AI processor (e.g. Lending/Tax/OCR processor).
        """
        pass

    @abstractmethod
    async def process_document(self, file_content: bytes) -> Dict[str, Any]:
        """
        Processes document bytes through Google Document AI API and returns parsed document entity tree.
        """
        pass


# 3. Alternative Credit Scoring Interface
class AlternativeCreditScoreRequest(BaseModel):
    business_id: str = Field(..., description="ID of the business entity")
    consent_given: bool = Field(True, description="Explicit user consent flag for alternative data access")
    data_sources: List[str] = Field(default=["gst", "bank_statement_transactions", "utility_history"], description="Alternative data sources to pull from")

class AlternativeCreditScoreResponse(BaseModel):
    alternative_score: int = Field(..., description="Alternative credit score value (300 to 900)")
    score_tier: str = Field(..., description="Score tier (e.g., Excellent, Good, Fair, Poor)")
    risk_probability: float = Field(..., description="Estimated default probability based on transactional flows")
    key_drivers: List[str] = Field(..., description="Top features contributing to the score")

class IAlternativeCreditScoringEngine(ABC):
    @abstractmethod
    async def calculate_alternative_score(self, request: AlternativeCreditScoreRequest) -> AlternativeCreditScoreResponse:
        """
        Calculates alternative credit metrics by scraping transactions, cashflows, and GST returns.
        """
        pass


# 4. Manual Review Workflows Interface
class ManualReviewTask(BaseModel):
    task_id: str = Field(..., description="Unique manual review task reference")
    application_id: str = Field(..., description="Linked loan application ID")
    assigned_underwriter: Optional[str] = Field(None, description="Username/ID of the assignee")
    mismatch_severity: str = Field(..., description="Mismatch severity level (LOW, MEDIUM, HIGH, CRITICAL)")
    escalation_reason: List[str] = Field(..., description="Triggered flags causing manual review")
    review_status: str = Field("Pending", description="Status: Pending, Under Review, Approved, Rejected")
    comments: List[Dict[str, Any]] = Field(default=[], description="Audit log of comments/notes")

class IManualReviewWorkflowManager(ABC):
    @abstractmethod
    async def create_review_task(self, task: ManualReviewTask) -> bool:
        """
        Enqueues an application into the underwriter review queue when warnings or high mismatches are triggered.
        """
        pass

    @abstractmethod
    async def assign_underwriter(self, task_id: str, underwriter_id: str) -> bool:
        """
        Assigns the manual review task to a specific underwriting agent.
        """
        pass

    @abstractmethod
    async def submit_decision(self, task_id: str, final_decision: str, underwriter_comments: str) -> Dict[str, Any]:
        """
        Submits the human underwriter override decision (Approve/Reject) and logs the rationale to decision history.
        """
        pass
