"""
Pydantic models for Emergency Medicine Case Simulator
"""

from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Request model for user login"""
    user_id: str = Field(..., min_length=1, description="User ID for authentication")


class LoginResponse(BaseModel):
    """Response model for successful login"""
    success: bool
    message: str
    user_id: str


class ChatMessage(BaseModel):
    """Model for chat messages"""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., min_length=1, description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    message: str = Field(..., min_length=1, description="User message")


class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    message: str
    summary: str


class CaseInfo(BaseModel):
    """Model for case information"""
    id: str
    title: str
    description: str


class CaseListResponse(BaseModel):
    """Response model for available cases"""
    cases: List[CaseInfo]


class CaseStartResponse(BaseModel):
    """Response model for starting a case"""
    success: bool
    message: str
    initial_message: str
    summary: str


class CaseCompleteRequest(BaseModel):
    """Request model for completing a case"""
    action: str = Field(..., description="Action taken: 'admit' or 'discharge'")


class CaseCompleteResponse(BaseModel):
    """Response model for case completion"""
    success: bool
    message: str


class SurveyResponse(BaseModel):
    """Model for individual survey response"""
    case_id: str
    question_index: int = Field(..., ge=0, le=3, description="Question index (0-3)")
    rating: int = Field(..., ge=1, le=5, description="Likert scale rating (1-5)")


class SurveySubmitRequest(BaseModel):
    """Request model for submitting survey responses"""
    responses: List[SurveyResponse]


class SurveySubmitResponse(BaseModel):
    """Response model for survey submission"""
    success: bool
    message: str


class UserSession(BaseModel):
    """Model for user session data"""
    user_id: str
    current_case: Optional[str] = None
    completed_cases: List[str] = []
    chat_history: Dict[str, List[ChatMessage]] = {}
    survey_responses: Dict[str, Dict[int, int]] = {}  # case_id -> question_index -> rating
    started_at: datetime = Field(default_factory=datetime.now)


class CaseSummaryData(BaseModel):
    """Model for case summary data"""
    case_id: str
    title: str
    description: str
    chat_messages: List[ChatMessage]
    completion_action: Optional[str] = None


class FinalSummaryResponse(BaseModel):
    """Response model for final summary page"""
    completed_cases: List[CaseSummaryData]
    survey_questions: List[str]
    existing_responses: Dict[str, Dict[int, int]]
