"""
Authentication service for Emergency Medicine Case Simulator
"""

from config.valid_user_ids import VALID_USER_IDS


class AuthService:
    """Service for handling user authentication"""
    
    @staticmethod
    def validate_user_id(user_id: str) -> bool:
        """
        Validate if user ID is in the list of authorized users.
        
        Args:
            user_id (str): User ID to validate
            
        Returns:
            bool: True if user ID is valid, False otherwise
        """
        return user_id.strip() in VALID_USER_IDS
    
    @staticmethod
    def get_valid_user_ids() -> list:
        """
        Get list of all valid user IDs.
        
        Returns:
            list: List of valid user IDs
        """
        return VALID_USER_IDS.copy()
