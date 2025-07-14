#!/usr/bin/env python3
"""
Enhanced Job Application Automation Tool Setup Script
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error {description}: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def setup_project():
    """Set up the entire project"""
    print("🚀 Setting up Enhanced Job Application Automation Tool...")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Install pip requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Install Playwright browsers
    if not run_command("playwright install", "Installing Playwright browsers"):
        return False
    
    # Create files directory if it doesn't exist
    files_dir = Path("files")
    if not files_dir.exists():
        files_dir.mkdir()
        print("✅ Created files/ directory for your documents")
    
    # Check if config file exists
    config_file = Path("config.json")
    if config_file.exists():
        print("✅ config.json found")
    else:
        print("⚠️  Please edit config.json with your personal information")
    
    # Check if jobs file exists
    jobs_file = Path("jobs.csv")
    if jobs_file.exists():
        print("✅ jobs.csv found")
    else:
        print("⚠️  Please edit jobs.csv with actual job URLs")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit config.json with your personal information")
    print("2. Place your resume.pdf and cover_letter.pdf in the files/ directory")
    print("3. Update jobs.csv with real job URLs")
    print("4. Run: python main.py jobs.csv")
    
    return True

if __name__ == "__main__":
    success = setup_project()
    if not success:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully! You're ready to automate job applications.")