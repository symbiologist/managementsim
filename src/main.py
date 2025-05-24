"""
Main FastAPI application for Emergency Medicine Case Simulator
"""

import os
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

# Load environment variables from .env file
def load_env_variables():
    """Load environment variables from .env file if it exists"""
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load environment variables at startup
load_env_variables()

# Import services
from services.auth_service import AuthService
from services.openai_service import OpenAIService  
from services.google_drive_service import GoogleDriveService
from services.session_service import SessionService

# Import models
from models.schemas import (
    LoginRequest, LoginResponse, ChatRequest, ChatResponse,
    CaseListResponse, CaseInfo, CaseStartResponse, 
    CaseCompleteRequest, CaseCompleteResponse,
    SurveySubmitRequest, SurveySubmitResponse,
    FinalSummaryResponse, CaseSummaryData
)

# Import configuration
from config.case_config import AVAILABLE_CASES
from config.survey_questions import SURVEY_QUESTIONS

# Initialize FastAPI app
app = FastAPI(
    title="Emergency Medicine Case Simulator",
    description="LLM-based clinical management simulation for assessing physicians",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize services
auth_service = AuthService()
openai_service = OpenAIService()
google_drive_service = GoogleDriveService()
session_service = SessionService()

# Store for user authentication (in-memory for simplicity)
authenticated_users: Dict[str, bool] = {}


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    """Render login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and create session.
    
    Args:
        request (LoginRequest): Login request with user ID
        
    Returns:
        LoginResponse: Login response with success status
        
    Raises:
        HTTPException: If user ID is invalid
    """
    if not auth_service.validate_user_id(request.user_id):
        raise HTTPException(status_code=401, detail="Invalid user ID")
    
    # Mark user as authenticated
    authenticated_users[request.user_id] = True
    
    # Create or get session
    session_service.get_or_create_session(request.user_id)
    
    return LoginResponse(
        success=True,
        message="Login successful",
        user_id=request.user_id
    )


@app.get("/case/{user_id}", response_class=HTMLResponse)
async def case_page(request: Request, user_id: str):
    """Render case interface page"""
    if user_id not in authenticated_users:
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse("case.html", {
        "request": request,
        "user_id": user_id
    })


@app.get("/summary/{user_id}", response_class=HTMLResponse)
async def summary_page(request: Request, user_id: str):
    """Render final summary page"""
    if user_id not in authenticated_users:
        return RedirectResponse(url="/")
    
    return templates.TemplateResponse("summary.html", {
        "request": request,
        "user_id": user_id
    })


@app.get("/api/cases", response_model=CaseListResponse)
async def get_cases():
    """
    Get list of available cases.
    
    Returns:
        CaseListResponse: List of available cases
    """
    cases = [
        CaseInfo(
            id=case_data["id"],
            title=case_data["title"],
            description=case_data["description"]
        )
        for case_data in AVAILABLE_CASES.values()
    ]
    
    return CaseListResponse(cases=cases)


@app.post("/api/cases/{case_id}/start/{user_id}", response_model=CaseStartResponse)
async def start_case(case_id: str, user_id: str):
    """
    Start a specific case for user.
    
    Args:
        case_id (str): Case ID to start
        user_id (str): User ID
        
    Returns:
        CaseStartResponse: Case start response with initial message
        
    Raises:
        HTTPException: If user not authenticated or case not found
    """
    if user_id not in authenticated_users:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    if case_id not in AVAILABLE_CASES:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Start case in session
    if not session_service.start_case(user_id, case_id):
        raise HTTPException(status_code=400, detail="Failed to start case")
    
    try:
        # Get initial case presentation
        case_data = AVAILABLE_CASES[case_id]
        initial_message = openai_service.get_case_presentation(case_data["content"])
        
        # Add initial message to session
        session_service.add_message(user_id, case_id, "assistant", initial_message)
        
        # Generate initial summary
        chat_history = session_service.get_chat_history(user_id, case_id)
        summary = openai_service.generate_case_summary([msg.dict() for msg in chat_history])
        
        return CaseStartResponse(
            success=True,
            message="Case started successfully",
            initial_message=initial_message,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting case: {str(e)}")


@app.post("/api/cases/{case_id}/chat/{user_id}", response_model=ChatResponse)
async def chat(case_id: str, user_id: str, request: ChatRequest):
    """
    Handle chat message in case.
    
    Args:
        case_id (str): Case ID
        user_id (str): User ID
        request (ChatRequest): Chat request with user message
        
    Returns:
        ChatResponse: Chat response with AI message and summary
        
    Raises:
        HTTPException: If user not authenticated or error occurs
    """
    if user_id not in authenticated_users:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    if case_id not in AVAILABLE_CASES:
        raise HTTPException(status_code=404, detail="Case not found")
    
    try:
        # Add user message to session
        session_service.add_message(user_id, case_id, "user", request.message)
        
        # Get chat history
        chat_history = session_service.get_chat_history(user_id, case_id)
        history_dicts = [msg.dict() for msg in chat_history]
        
        # Get AI response
        case_data = AVAILABLE_CASES[case_id]
        ai_response = openai_service.get_chat_response(
            case_data["content"], 
            history_dicts, 
            request.message
        )
        
        # Add AI response to session
        session_service.add_message(user_id, case_id, "assistant", ai_response)
        
        # Generate updated summary
        updated_history = session_service.get_chat_history(user_id, case_id)
        summary = openai_service.generate_case_summary([msg.dict() for msg in updated_history])
        
        return ChatResponse(
            message=ai_response,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.post("/api/cases/{case_id}/complete/{user_id}", response_model=CaseCompleteResponse)
async def complete_case(case_id: str, user_id: str, request: CaseCompleteRequest):
    """
    Complete a case with admit/discharge action.
    
    Args:
        case_id (str): Case ID
        user_id (str): User ID
        request (CaseCompleteRequest): Completion request with action
        
    Returns:
        CaseCompleteResponse: Completion response
        
    Raises:
        HTTPException: If user not authenticated or error occurs
    """
    if user_id not in authenticated_users:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    if case_id not in AVAILABLE_CASES:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if request.action not in ["admit", "discharge"]:
        raise HTTPException(status_code=400, detail="Invalid action. Must be 'admit' or 'discharge'")
    
    try:
        # Mark case as completed
        session_service.complete_case(user_id, case_id, request.action)
        
        # Save chat log to Google Drive using synchronous method
        chat_history = session_service.get_chat_history(user_id, case_id)
        if chat_history and google_drive_service.is_available():
            messages_dict = [msg.dict() for msg in chat_history]
            case_title = AVAILABLE_CASES[case_id]["title"]
            # Use synchronous method to avoid async/await issues
            google_drive_service.upload_chat_log_sync(messages_dict, user_id, case_id, case_title)
        elif not google_drive_service.is_available():
            print("Warning: Google Drive service not available, chat log not saved")
        
        return CaseCompleteResponse(
            success=True,
            message=f"Case completed with action: {request.action}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing case: {str(e)}")


@app.get("/api/summary/{user_id}", response_model=FinalSummaryResponse)
async def get_final_summary(user_id: str):
    """
    Get final summary with completed cases and survey questions.
    
    Args:
        user_id (str): User ID
        
    Returns:
        FinalSummaryResponse: Final summary data
        
    Raises:
        HTTPException: If user not authenticated
    """
    if user_id not in authenticated_users:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    # Get completed cases
    completed_case_ids = session_service.get_completed_cases(user_id)
    
    # Build case summary data
    completed_cases = []
    for case_id in completed_case_ids:
        if case_id in AVAILABLE_CASES:
            case_data = AVAILABLE_CASES[case_id]
            chat_messages = session_service.get_chat_history(user_id, case_id)
            
            completed_cases.append(CaseSummaryData(
                case_id=case_id,
                title=case_data["title"],
                description=case_data["description"],
                chat_messages=chat_messages
            ))
    
    # Get existing survey responses
    existing_responses = session_service.get_survey_responses(user_id)
    
    return FinalSummaryResponse(
        completed_cases=completed_cases,
        survey_questions=SURVEY_QUESTIONS,
        existing_responses=existing_responses
    )


@app.post("/api/survey/submit/{user_id}", response_model=SurveySubmitResponse)
async def submit_survey(user_id: str, request: SurveySubmitRequest):
    """
    Submit survey responses.
    
    Args:
        user_id (str): User ID
        request (SurveySubmitRequest): Survey responses
        
    Returns:
        SurveySubmitResponse: Submission response
        
    Raises:
        HTTPException: If user not authenticated or error occurs
    """
    if user_id not in authenticated_users:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    try:
        # Add survey responses to session
        for response in request.responses:
            session_service.add_survey_response(
                user_id, 
                response.case_id, 
                response.question_index, 
                response.rating
            )
        
        # Save survey responses to Google Drive using synchronous method
        survey_data = session_service.get_survey_responses(user_id)
        if survey_data and google_drive_service.is_available():
            # Use synchronous method to avoid async/await issues
            google_drive_service.upload_survey_responses_sync(survey_data, user_id)
        elif not google_drive_service.is_available():
            print("Warning: Google Drive service not available, survey responses not saved")
        
        return SurveySubmitResponse(
            success=True,
            message="Survey responses submitted successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting survey: {str(e)}")


@app.get("/api/next-case/{user_id}")
async def get_next_case(user_id: str):
    """
    Get next available case for user.
    
    Args:
        user_id (str): User ID
        
    Returns:
        dict: Next case info or completion status
        
    Raises:
        HTTPException: If user not authenticated
    """
    if user_id not in authenticated_users:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    next_case_id = session_service.get_next_case(user_id)
    
    if next_case_id:
        case_data = AVAILABLE_CASES[next_case_id]
        return {
            "has_next": True,
            "case_id": next_case_id,
            "title": case_data["title"],
            "description": case_data["description"]
        }
    else:
        return {
            "has_next": False,
            "message": "All cases completed"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
