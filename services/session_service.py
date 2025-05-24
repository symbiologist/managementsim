"""
Session service for Emergency Medicine Case Simulator
"""

from typing import Dict, Optional, List
from datetime import datetime
from models.schemas import UserSession, ChatMessage
from config.case_config import AVAILABLE_CASES


class SessionService:
    """Service for managing user sessions"""
    
    def __init__(self):
        """Initialize session service"""
        self.sessions: Dict[str, UserSession] = {}
    
    def create_session(self, user_id: str) -> UserSession:
        """
        Create a new user session.
        
        Args:
            user_id (str): User ID
            
        Returns:
            UserSession: Created session object
        """
        session = UserSession(user_id=user_id)
        self.sessions[user_id] = session
        return session
    
    def get_session(self, user_id: str) -> Optional[UserSession]:
        """
        Get existing user session.
        
        Args:
            user_id (str): User ID
            
        Returns:
            Optional[UserSession]: Session object if exists, None otherwise
        """
        return self.sessions.get(user_id)
    
    def get_or_create_session(self, user_id: str) -> UserSession:
        """
        Get existing session or create new one.
        
        Args:
            user_id (str): User ID
            
        Returns:
            UserSession: Session object
        """
        session = self.get_session(user_id)
        if session is None:
            session = self.create_session(user_id)
        return session
    
    def start_case(self, user_id: str, case_id: str) -> bool:
        """
        Start a new case for user.
        
        Args:
            user_id (str): User ID
            case_id (str): Case ID to start
            
        Returns:
            bool: True if case started successfully, False otherwise
        """
        if case_id not in AVAILABLE_CASES:
            return False
        
        session = self.get_or_create_session(user_id)
        session.current_case = case_id
        
        # Initialize chat history for this case if not exists
        if case_id not in session.chat_history:
            session.chat_history[case_id] = []
        
        return True
    
    def add_message(self, user_id: str, case_id: str, role: str, content: str) -> bool:
        """
        Add message to case chat history.
        
        Args:
            user_id (str): User ID
            case_id (str): Case ID
            role (str): Message role ('user' or 'assistant')
            content (str): Message content
            
        Returns:
            bool: True if message added successfully, False otherwise
        """
        session = self.get_session(user_id)
        if session is None:
            return False
        
        if case_id not in session.chat_history:
            session.chat_history[case_id] = []
        
        message = ChatMessage(role=role, content=content)
        session.chat_history[case_id].append(message)
        return True
    
    def get_chat_history(self, user_id: str, case_id: str) -> List[ChatMessage]:
        """
        Get chat history for a specific case.
        
        Args:
            user_id (str): User ID
            case_id (str): Case ID
            
        Returns:
            List[ChatMessage]: Chat history messages
        """
        session = self.get_session(user_id)
        if session is None:
            return []
        
        return session.chat_history.get(case_id, [])
    
    def complete_case(self, user_id: str, case_id: str, action: str) -> bool:
        """
        Mark case as completed.
        
        Args:
            user_id (str): User ID
            case_id (str): Case ID
            action (str): Completion action ('admit' or 'discharge')
            
        Returns:
            bool: True if case completed successfully, False otherwise
        """
        session = self.get_session(user_id)
        if session is None:
            return False
        
        # Add to completed cases if not already there
        if case_id not in session.completed_cases:
            session.completed_cases.append(case_id)
        
        # Clear current case
        if session.current_case == case_id:
            session.current_case = None
        
        return True
    
    def add_survey_response(self, user_id: str, case_id: str, question_index: int, rating: int) -> bool:
        """
        Add survey response for a case.
        
        Args:
            user_id (str): User ID
            case_id (str): Case ID
            question_index (int): Question index (0-3)
            rating (int): Rating (1-5)
            
        Returns:
            bool: True if response added successfully, False otherwise
        """
        session = self.get_session(user_id)
        if session is None:
            return False
        
        if case_id not in session.survey_responses:
            session.survey_responses[case_id] = {}
        
        session.survey_responses[case_id][question_index] = rating
        return True
    
    def get_survey_responses(self, user_id: str) -> Dict[str, Dict[int, int]]:
        """
        Get all survey responses for user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            Dict[str, Dict[int, int]]: Survey responses by case and question
        """
        session = self.get_session(user_id)
        if session is None:
            return {}
        
        return session.survey_responses
    
    def get_completed_cases(self, user_id: str) -> List[str]:
        """
        Get list of completed cases for user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            List[str]: List of completed case IDs
        """
        session = self.get_session(user_id)
        if session is None:
            return []
        
        return session.completed_cases
    
    def is_all_cases_completed(self, user_id: str) -> bool:
        """
        Check if user has completed all available cases.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: True if all cases completed, False otherwise
        """
        completed_cases = self.get_completed_cases(user_id)
        return len(completed_cases) >= len(AVAILABLE_CASES)
    
    def clear_session(self, user_id: str) -> bool:
        """
        Clear user session.
        
        Args:
            user_id (str): User ID
            
        Returns:
            bool: True if session cleared, False if not found
        """
        if user_id in self.sessions:
            del self.sessions[user_id]
            return True
        return False
    
    def get_next_case(self, user_id: str) -> Optional[str]:
        """
        Get next available case for user.
        
        Args:
            user_id (str): User ID
            
        Returns:
            Optional[str]: Next case ID or None if all completed
        """
        completed_cases = self.get_completed_cases(user_id)
        available_case_ids = list(AVAILABLE_CASES.keys())
        
        for case_id in available_case_ids:
            if case_id not in completed_cases:
                return case_id
        
        return None
