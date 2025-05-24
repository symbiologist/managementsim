"""
Google Drive service for Emergency Medicine Case Simulator
"""

import os
import io
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


class GoogleDriveService:
    """Service for handling Google Drive operations"""
    
    def __init__(self):
        """Initialize Google Drive service"""
        self.service = None
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "1mLOznW0Jtcdb_2AJKKu3y94L913Y26ji")
        self._initialize_service()
    
    def _initialize_service(self):
        """
        Initialize Google Drive API service using service account credentials.
        
        Raises:
            Exception: If credentials are not found or service initialization fails
        """
        try:
            # Get credentials from environment variable
            creds_info = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")
            if not creds_info:
                raise Exception("Google service account key not found in environment variables")
            
            # Parse JSON credentials
            creds_dict = json.loads(creds_info)
            
            # Create credentials
            creds = service_account.Credentials.from_service_account_info(
                creds_dict, 
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            # Build service
            self.service = build('drive', 'v3', credentials=creds)
            
        except Exception as e:
            print(f"Warning: Could not initialize Google Drive service: {e}")
            self.service = None
    
    def is_available(self) -> bool:
        """
        Check if Google Drive service is available.
        
        Returns:
            bool: True if service is available, False otherwise
        """
        return self.service is not None
    
    async def upload_file(self, content: str, filename: str, mime_type: str = "text/csv") -> Optional[str]:
        """
        Upload a file to Google Drive.
        
        Args:
            content (str): File content
            filename (str): Name for the file
            mime_type (str): MIME type of the file
            
        Returns:
            Optional[str]: File URL if successful, None otherwise
        """
        if not self.is_available():
            raise Exception("Google Drive service not available")
        
        try:
            # Create buffer
            content_buffer = io.BytesIO(content.encode('utf-8'))
            
            # Upload file
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            media_body = MediaIoBaseUpload(
                content_buffer, 
                mimetype=mime_type, 
                resumable=True
            )
            
            result = self.service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id,webViewLink'
            ).execute()
            
            file_id = result.get('id')
            file_url = f"https://drive.google.com/file/d/{file_id}/view"
            
            print(f"File uploaded successfully: {filename}")
            return file_url
            
        except Exception as e:
            print(f"Error uploading file: {e}")
            raise
    
    async def upload_chat_log(self, user_id: str, case_id: str, case_title: str, chat_messages: List[Dict]) -> Optional[str]:
        """
        Upload chat log to Google Drive.
        
        Args:
            user_id (str): User ID
            case_id (str): Case ID  
            case_title (str): Case title for filename
            chat_messages (List[Dict]): Chat messages to upload
            
        Returns:
            Optional[str]: File URL if successful, None otherwise
        """
        if not chat_messages:
            raise Exception("No messages to upload")
        
        try:
            # Create DataFrame from messages
            df = pd.DataFrame(chat_messages)
            
            # Create CSV content
            csv_content = df.to_csv(index=False, encoding='utf-8')
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_case_title = case_title.replace(':', '').replace(' ', '_').replace('/', '_')
            filename = f"{user_id}_{case_id}_{safe_case_title}_chat_log_{timestamp}.csv"
            
            # Upload file
            return await self.upload_file(csv_content, filename, 'text/csv')
            
        except Exception as e:
            print(f"Error uploading chat log: {e}")
            raise
    
    async def upload_survey_responses(self, user_id: str, responses: List[Dict]) -> Optional[str]:
        """
        Upload survey responses to Google Drive.
        
        Args:
            user_id (str): User ID
            responses (List[Dict]): Survey responses data
            
        Returns:
            Optional[str]: File URL if successful, None otherwise
        """
        if not responses:
            raise Exception("No survey responses to upload")
        
        try:
            # Add timestamp to each response
            for response in responses:
                response['user_id'] = user_id
                response['timestamp'] = datetime.now().isoformat()
            
            # Create DataFrame
            df = pd.DataFrame(responses)
            
            # Create CSV content
            csv_content = df.to_csv(index=False, encoding='utf-8')
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}_survey_responses_{timestamp}.csv"
            
            # Upload file
            return await self.upload_file(csv_content, filename, 'text/csv')
            
        except Exception as e:
            print(f"Error uploading survey responses: {e}")
            raise
    
    # Legacy synchronous methods for backward compatibility
    def upload_chat_log_sync(self, messages: List[Dict], user_id: str, case_id: str, case_title: str) -> bool:
        """
        Synchronous version of upload_chat_log for backward compatibility.
        
        Args:
            messages (List[Dict]): Chat messages to upload
            user_id (str): User ID
            case_id (str): Case ID  
            case_title (str): Case title for filename
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.is_available():
            print("Google Drive service not available")
            return False
        
        if not messages:
            print("No messages to upload")
            return False
        
        try:
            # Create DataFrame from messages
            df = pd.DataFrame(messages)
            
            # Create CSV buffer
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_buffer.seek(0)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_case_title = case_title.replace(':', '').replace(' ', '_').replace('/', '_')
            filename = f"{user_id}_{case_id}_{safe_case_title}_chat_log_{timestamp}.csv"
            
            # Upload file
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            media_body = MediaIoBaseUpload(
                csv_buffer, 
                mimetype='text/csv', 
                resumable=True
            )
            
            self.service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id'
            ).execute()
            
            print(f"Chat log uploaded successfully: {filename}")
            return True
            
        except Exception as e:
            print(f"Error uploading chat log: {e}")
            return False
    
    def upload_survey_responses_sync(self, survey_data: Dict, user_id: str) -> bool:
        """
        Synchronous version of upload_survey_responses for backward compatibility.
        
        Args:
            survey_data (Dict): Survey responses data
            user_id (str): User ID
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.is_available():
            print("Google Drive service not available")
            return False
        
        if not survey_data:
            print("No survey data to upload")
            return False
        
        try:
            # Convert survey data to DataFrame format
            rows = []
            for case_id, responses in survey_data.items():
                for question_index, rating in responses.items():
                    rows.append({
                        'user_id': user_id,
                        'case_id': case_id,
                        'question_index': question_index,
                        'rating': rating,
                        'timestamp': datetime.now().isoformat()
                    })
            
            if not rows:
                print("No survey responses to upload")
                return False
            
            # Create DataFrame
            df = pd.DataFrame(rows)
            
            # Create CSV buffer
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8')
            csv_buffer.seek(0)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{user_id}_survey_responses_{timestamp}.csv"
            
            # Upload file
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id]
            }
            
            media_body = MediaIoBaseUpload(
                csv_buffer,
                mimetype='text/csv',
                resumable=True
            )
            
            self.service.files().create(
                body=file_metadata,
                media_body=media_body,
                fields='id'
            ).execute()
            
            print(f"Survey responses uploaded successfully: {filename}")
            return True
            
        except Exception as e:
            print(f"Error uploading survey responses: {e}")
            return False
    
    def upload_combined_data(self, chat_data: Dict[str, List[Dict]], survey_data: Dict, user_id: str) -> bool:
        """
        Upload combined chat logs and survey responses to Google Drive.
        
        Args:
            chat_data (Dict[str, List[Dict]]): Chat data by case ID
            survey_data (Dict): Survey responses data
            user_id (str): User ID
            
        Returns:
            bool: True if upload successful, False otherwise
        """
        if not self.is_available():
            print("Google Drive service not available")
            return False
        
        try:
            # Upload individual chat logs
            for case_id, messages in chat_data.items():
                if messages:
                    case_title = f"Case_{case_id}"
                    self.upload_chat_log_sync(messages, user_id, case_id, case_title)
            
            # Upload survey responses
            if survey_data:
                self.upload_survey_responses_sync(survey_data, user_id)
            
            return True
            
        except Exception as e:
            print(f"Error uploading combined data: {e}")
            return False
    
    def set_folder_id(self, folder_id: str):
        """
        Set the Google Drive folder ID for uploads.
        
        Args:
            folder_id (str): Google Drive folder ID
        """
        self.folder_id = folder_id
