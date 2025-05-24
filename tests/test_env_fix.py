#!/usr/bin/env python3
"""
Environment fix and Google Drive test
"""

import os
import sys
import json

def load_env_file():
    """Load environment variables from .env file"""
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        return False
    
    print("📁 Loading .env file...")
    
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                print(f"✅ Set {key}")
    
    return True

def test_google_drive():
    """Test Google Drive integration"""
    print("\n🔍 Testing Google Drive Integration")
    print("-" * 40)
    
    # Check environment variables
    google_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    if not google_key:
        print("❌ GOOGLE_SERVICE_ACCOUNT_KEY not set")
        return False
    
    if not folder_id:
        print("❌ GOOGLE_DRIVE_FOLDER_ID not set")
        return False
    
    print("✅ Environment variables are set")
    
    # Test JSON parsing
    try:
        credentials = json.loads(google_key)
        print("✅ Service account JSON is valid")
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in credentials]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        else:
            print("✅ Service account has all required fields")
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in service account: {e}")
        return False
    
    # Test Google Drive service
    try:
        print("\n🔧 Testing Google Drive service...")
        
        # Import and test the service
        sys.path.append('services')
        from services.google_drive_service import GoogleDriveService
        
        drive_service = GoogleDriveService()
        
        if drive_service.is_available():
            print("✅ Google Drive service initialized successfully")
            print(f"✅ Using folder: {drive_service.folder_id}")
            return True
        else:
            print("❌ Google Drive service failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Google Drive service: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("\n📦 Testing Dependencies")
    print("-" * 30)
    
    try:
        import google.auth
        print("✅ google-auth")
    except ImportError:
        print("❌ google-auth - Run: uv add google-auth")
        return False
    
    try:
        import googleapiclient
        print("✅ google-api-python-client")
    except ImportError:
        print("❌ google-api-python-client - Run: uv add google-api-python-client")
        return False
    
    try:
        import pandas
        print("✅ pandas")
    except ImportError:
        print("❌ pandas - Run: uv add pandas")
        return False
    
    return True

def main():
    """Main test function"""
    print("🏥 Emergency Medicine Case Simulator")
    print("Environment Fix & Google Drive Test")
    print("=" * 60)
    
    # Load environment variables
    if not load_env_file():
        return
    
    # Test dependencies
    if not test_dependencies():
        print("\n❌ Missing dependencies. Please install them and try again.")
        return
    
    # Test Google Drive
    if test_google_drive():
        print("\n🎉 SUCCESS!")
        print("✅ Environment variables loaded correctly")
        print("✅ Google Drive service is working")
        print("✅ Ready to test file uploads")
        
        print("\n📋 Next steps:")
        print("1. Run your FastAPI application: python run.py")
        print("2. Complete a case to test actual file uploads")
        print("3. Check your Google Drive folder for uploaded files")
        
    else:
        print("\n❌ FAILED!")
        print("Google Drive integration has issues.")
        print("Please check your credentials and permissions.")

if __name__ == "__main__":
    main()
