#!/usr/bin/env python3
"""
Test script for Google Drive integration
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add src to path so we can import our services
sys.path.append('services')

from services.google_drive_service import GoogleDriveService

async def test_google_drive_upload():
    """Test Google Drive upload functionality"""
    
    print("🔍 Testing Google Drive Integration")
    print("=" * 50)
    
    # Check environment variables
    print("1. Checking environment variables...")
    
    google_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not google_key:
        print("❌ GOOGLE_SERVICE_ACCOUNT_KEY not found in environment")
        print("   Please set this in your .env file")
        return False
    
    if not folder_id:
        print("❌ GOOGLE_DRIVE_FOLDER_ID not found in environment")
        print("   Please set this in your .env file")
        return False
    
    print("✅ Environment variables found")
    print(f"   Folder ID: {folder_id}")
    
    # Initialize Google Drive service
    print("\n2. Initializing Google Drive service...")
    
    try:
        drive_service = GoogleDriveService()
        print("✅ Google Drive service initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Google Drive service: {e}")
        return False
    
    # Create test CSV content
    print("\n3. Creating test CSV content...")
    
    test_content = """timestamp,user_id,test_type,message
{timestamp},test_user,google_drive_test,"Test message from Emergency Medicine Case Simulator"
{timestamp},test_user,google_drive_test,"This is a test to verify Google Drive integration is working"
{timestamp},test_user,google_drive_test,"If you see this file in Google Drive, the integration is successful!"
""".format(timestamp=datetime.now().isoformat())
    
    print("✅ Test CSV content created")
    
    # Test file upload
    print("\n4. Testing file upload to Google Drive...")
    
    test_filename = f"test_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        file_url = await drive_service.upload_chat_log(
            user_id="test_user",
            case_id="test_case",
            case_title="Google Drive Test Case",
            chat_messages=[
                {"role": "system", "content": "Test message 1", "timestamp": datetime.now().isoformat()},
                {"role": "user", "content": "Test user message", "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": "Test AI response", "timestamp": datetime.now().isoformat()}
            ]
        )
        
        print("✅ Chat log upload successful!")
        print(f"   File URL: {file_url}")
        
    except Exception as e:
        print(f"❌ Chat log upload failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Try a direct file upload as fallback
        print("\n4b. Trying direct file upload...")
        try:
            file_url = await drive_service.upload_file(
                content=test_content,
                filename=test_filename,
                mime_type="text/csv"
            )
            print("✅ Direct file upload successful!")
            print(f"   File URL: {file_url}")
        except Exception as e2:
            print(f"❌ Direct file upload also failed: {e2}")
            return False
    
    # Test survey response upload
    print("\n5. Testing survey response upload...")
    
    try:
        survey_url = await drive_service.upload_survey_responses(
            user_id="test_user",
            responses=[
                {"case_id": "test_case", "question_index": 0, "rating": 5},
                {"case_id": "test_case", "question_index": 1, "rating": 4},
                {"case_id": "test_case", "question_index": 2, "rating": 3},
                {"case_id": "test_case", "question_index": 3, "rating": 4}
            ]
        )
        
        print("✅ Survey response upload successful!")
        print(f"   File URL: {survey_url}")
        
    except Exception as e:
        print(f"❌ Survey response upload failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All Google Drive tests passed!")
    print("✅ The integration is working correctly")
    print(f"✅ Check your Google Drive folder: https://drive.google.com/drive/folders/{folder_id}")
    
    return True

async def test_credentials():
    """Test just the credentials and basic connection"""
    
    print("🔐 Testing Google Drive Credentials")
    print("=" * 40)
    
    google_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    if not google_key:
        print("❌ No credentials found")
        return False
    
    try:
        import json
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        
        # Parse credentials
        credentials_info = json.loads(google_key)
        credentials = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        
        # Build service
        service = build('drive', 'v3', credentials=credentials)
        
        # Test basic API call
        results = service.files().list(pageSize=1).execute()
        
        print("✅ Credentials are valid")
        print("✅ Successfully connected to Google Drive API")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in GOOGLE_SERVICE_ACCOUNT_KEY: {e}")
        return False
    except Exception as e:
        print(f"❌ Credential test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🏥 Emergency Medicine Case Simulator")
    print("Google Drive Integration Test")
    print("=" * 60)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env")
    except ImportError:
        print("⚠️  python-dotenv not available, using system environment")
    except Exception as e:
        print(f"⚠️  Could not load .env file: {e}")
    
    # Run credential test first
    print("\nPhase 1: Credential Test")
    print("-" * 30)
    
    if not asyncio.run(test_credentials()):
        print("\n❌ Credential test failed. Please check your GOOGLE_SERVICE_ACCOUNT_KEY")
        return
    
    # Run full upload test
    print("\nPhase 2: Upload Test")
    print("-" * 20)
    
    success = asyncio.run(test_google_drive_upload())
    
    if success:
        print("\n🎉 SUCCESS: Google Drive integration is working!")
        print("You should see test files in your Google Drive folder.")
    else:
        print("\n❌ FAILED: Google Drive integration needs attention.")
        print("Please check your credentials and folder permissions.")

if __name__ == "__main__":
    main()
