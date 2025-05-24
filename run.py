#!/usr/bin/env python3
"""
Emergency Medicine Case Simulator - Development Runner
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required tools are installed"""
    requirements = {
        'uv': 'uv package manager',
        'python': 'Python 3.12+'
    }
    
    missing = []
    for cmd, desc in requirements.items():
        try:
            subprocess.run([cmd, '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            missing.append(f"{cmd} ({desc})")
    
    if missing:
        print("❌ Missing requirements:")
        for item in missing:
            print(f"  - {item}")
        print("\nPlease install the missing requirements and try again.")
        return False
    
    return True

def setup_environment():
    """Set up Python environment and install dependencies"""
    print("🔧 Setting up Python environment...")
    
    # Create virtual environment if it doesn't exist
    if not Path('.venv').exists():
        subprocess.run(['uv', 'venv'], check=True)
        print("✅ Created virtual environment")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run(['uv', 'pip', 'install', '-r', 'pyproject.toml'], check=True)
    print("✅ Dependencies installed")

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("📝 Creating .env file from template...")
        
        # Copy .env.example to .env
        with open('.env.example', 'r') as src, open('.env', 'w') as dst:
            dst.write(src.read())
        
        print("✅ Created .env file")
        print("🔑 Please update .env with your API keys before running the application")
        return False
    
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY']
    missing_vars = []
    
    with open('.env', 'r') as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=your_" in content or f"{var}=" not in content:
                missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing or incomplete environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("🔑 Please update .env with your actual API keys")
        return False
    
    return True

def run_application():
    """Run the FastAPI application"""
    print("🚀 Starting Emergency Medicine Case Simulator...")
    print("🌐 Application will be available at: http://localhost:8000")
    print("👤 Use user ID 'dwu' to test the application")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run with uvicorn
        subprocess.run([
            'python', '-m', 'uvicorn', 
            'src.main:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped")

def main():
    """Main function"""
    print("🏥 Emergency Medicine Case Simulator - Setup & Run")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check environment file
    env_ready = check_env_file()
    
    if not env_ready:
        print("\n⚠️  Environment setup incomplete")
        print("Please update your .env file with the required API keys and run again.")
        sys.exit(1)
    
    print("\n✅ Setup complete!")
    
    # Ask if user wants to run the application
    response = input("\n🚀 Start the application now? (y/N): ").strip().lower()
    if response in ['y', 'yes']:
        run_application()
    else:
        print("👍 Setup complete. Run 'python run.py' to start the application later.")

if __name__ == "__main__":
    main()
