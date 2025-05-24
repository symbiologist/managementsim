#!/usr/bin/env python3
"""
Simple Google Drive test - minimal dependencies
"""

import os
import json
from datetime import datetime

def test_env_variables():
    """Test if environment variables are set"""
    print("📋 Checking Environment Variables")
    print("-" * 40)
    
    # Check for .env file
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Try to load it manually
        with open('.env', 'r') as f:
            env_content = f.read()
            
        if 'GOOGLE_SERVICE_ACCOUNT_KEY=' in env_content:
            print("✅ GOOGLE_SERVICE_ACCOUNT_KEY found in .env")
        else:
            print("❌ GOOGLE_SERVICE_ACCOUNT_KEY not found in .env")
            
        if 'GOOGLE_DRIVE_FOLDER_ID=' in env_content:
            print("✅ GOOGLE_DRIVE_FOLDER_ID found in .env")
        else:
            print("❌ GOOGLE_DRIVE_FOLDER_ID not found in .env")
    else:
        print("❌ .env file not found")
    
    # Check environment variables
    google_key = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY')
    folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    print(f"\nEnvironment Variables:")
    print(f"  GOOGLE_SERVICE_ACCOUNT_KEY: {'✅ Set' if google_key else '❌ Not set'}")
    print(f"  GOOGLE_DRIVE_FOLDER_ID: {'✅ Set' if folder_id else '❌ Not set'}")
    print(f"  OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not set'}")
    
    if google_key:
        try:
            # Try to parse the JSON
            credentials = json.loads(google_key)
            print("✅ GOOGLE_SERVICE_ACCOUNT_KEY is valid JSON")
            
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in credentials]
            
            if missing_fields:
                print(f"❌ Missing required fields in service account: {missing_fields}")
            else:
                print("✅ Service account JSON has all required fields")
                
        except json.JSONDecodeError as e:
            print(f"❌ GOOGLE_SERVICE_ACCOUNT_KEY is not valid JSON: {e}")
    
    return google_key and folder_id

def test_dependencies():
    """Test if required dependencies are installed"""
    print("\n📦 Checking Dependencies")
    print("-" * 30)
    
    required_packages = [
        'google-auth',
        'google-auth-oauthlib', 
        'google-auth-httplib2',
        'google-api-python-client',
        'openai',
        'fastapi',
        'uvicorn'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google-auth':
                import google.auth
            elif package == 'google-auth-oauthlib':
                import google_auth_oauthlib
            elif package == 'google-auth-httplib2':
                import google_auth_httplib2
            elif package == 'google-api-python-client':
                import googleapiclient
            elif package == 'openai':
                import openai
            elif package == 'fastapi':
                import fastapi
            elif package == 'uvicorn':
                import uvicorn
            
            print(f"✅ {package}")
            
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Run: uv add " + " ".join(missing_packages))
        return False
    
    return True

def main():
    """Main test function"""
    print("🏥 Emergency Medicine Case Simulator")
    print("Simple Environment Test")
    print("=" * 50)
    
    # Test environment variables
    env_ok = test_env_variables()
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    print("\n" + "=" * 50)
    if env_ok and deps_ok:
        print("🎉 Basic setup looks good!")
        print("Run: python test_google_drive.py")
        print("To test the full Google Drive integration.")
    else:
        print("❌ Setup issues found.")
        if not env_ok:
            print("   Please check your .env file and API keys")
        if not deps_ok:
            print("   Please install missing dependencies")

if __name__ == "__main__":
    main()
