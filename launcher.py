#!/usr/bin/env python3
"""
🚀 Fully Automated Job Application Launcher
Provides easy access to different automation modes and configurations
"""

import asyncio
import sys
import subprocess
import webbrowser
from pathlib import Path
import json

def print_banner():
    print("=" * 80)
    print("🚀 FULLY AUTOMATED JOB APPLICATION SYSTEM")
    print("=" * 80)
    print("✨ Zero-delay form filling | Multi-tab processing | Auto-login")
    print("🔥 Lightning fast | Enterprise-grade | Error-free")
    print("=" * 80)

def print_menu():
    print("\n📋 LAUNCHER MENU:")
    print("1. 🚀 Start Fully Automated Batch (Default: 10 tabs)")
    print("2. ⚡ Ultra Fast Mode (20 tabs)")
    print("3. 🐌 Conservative Mode (5 tabs)")
    print("4. 🎯 Single Tab Test Mode")
    print("5. 📊 Open Dashboard")
    print("6. ⚙️  Configure Settings")
    print("7. 📂 Edit Jobs CSV")
    print("8. 🔧 Validate Configuration")
    print("9. 📋 Show Status")
    print("0. ❌ Exit")

def validate_config():
    """Validate configuration file"""
    print("\n🔍 Validating configuration...")
    
    config_path = Path("config.json")
    if not config_path.exists():
        print("❌ config.json not found!")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        required_sections = ["user_info", "login_credentials", "attachments", "questions", "automation_settings"]
        missing = [section for section in required_sections if section not in config]
        
        if missing:
            print(f"❌ Missing sections: {missing}")
            return False
        
        # Check login credentials
        if not config["login_credentials"]["email"] or config["login_credentials"]["email"] == "your.email@example.com":
            print("⚠️  Warning: Please update login credentials in config.json")
        
        # Check resume file
        resume_path = config["attachments"]["resume"]
        if not Path(resume_path).exists():
            print(f"⚠️  Warning: Resume file not found: {resume_path}")
        
        print("✅ Configuration validated successfully!")
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON in config.json")
        return False
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def check_jobs_csv():
    """Check if jobs.csv exists and has data"""
    csv_path = Path("jobs.csv")
    if not csv_path.exists():
        print("❌ jobs.csv not found!")
        return False
    
    try:
        with open(csv_path) as f:
            lines = f.readlines()
        
        if len(lines) < 2:  # Header + at least 1 job
            print("❌ jobs.csv is empty or only has headers!")
            return False
        
        print(f"✅ Found {len(lines) - 1} jobs in jobs.csv")
        return True
        
    except Exception as e:
        print(f"❌ Error reading jobs.csv: {e}")
        return False

def start_automation(max_tabs=10):
    """Start the fully automated job application process"""
    print(f"\n🚀 Starting FULLY AUTOMATED mode with {max_tabs} concurrent tabs...")
    
    if not validate_config():
        return
    
    if not check_jobs_csv():
        return
    
    print("\n" + "=" * 60)
    print("🔥 AUTOMATION STARTING")
    print("=" * 60)
    print(f"📊 Max Concurrent Tabs: {max_tabs}")
    print("⚡ Zero-delay form filling enabled")
    print("🔐 Auto-login enabled")
    print("🎯 Multi-step navigation enabled")
    print("📈 Real-time dashboard available")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "main.py", "jobs.csv", str(max_tabs)])
    except KeyboardInterrupt:
        print("\n⏹️  Automation stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting automation: {e}")

def open_dashboard():
    """Open the real-time dashboard"""
    print("\n📊 Opening real-time dashboard...")
    dashboard_path = Path("dashboard.html").absolute()
    webbrowser.open(f"file://{dashboard_path}")
    print("✅ Dashboard opened in your browser")

def configure_settings():
    """Interactive configuration"""
    print("\n⚙️  CONFIGURATION SETUP")
    print("=" * 40)
    
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        print("❌ config.json not found!")
        return
    
    print("Current settings:")
    print(f"📧 Email: {config.get('login_credentials', {}).get('email', 'Not set')}")
    print(f"🏃 Speed Mode: {config.get('automation_settings', {}).get('slow_mo', 25)}ms")
    print(f"⏱️  Timeout: {config.get('automation_settings', {}).get('timeout', 5000)}ms")
    print(f"🎯 Max Retries: {config.get('automation_settings', {}).get('max_retries', 1)}")
    
    print("\nTo modify settings, edit config.json manually.")
    input("Press Enter to continue...")

def edit_jobs_csv():
    """Instructions for editing jobs CSV"""
    print("\n📂 EDITING JOBS CSV")
    print("=" * 40)
    print("To add/modify jobs, edit jobs.csv with the following format:")
    print("\ncompany,url")
    print("Google,https://careers.google.com/jobs/results/...")
    print("Microsoft,https://careers.microsoft.com/us/en/job/...")
    print("\n✅ Each line should have: company_name,job_url")
    print("⚠️  Make sure URLs are complete and accessible")
    print("\nTip: You can have up to 100 jobs for batch processing!")
    input("Press Enter to continue...")

def show_status():
    """Show current system status"""
    print("\n📋 SYSTEM STATUS")
    print("=" * 40)
    
    # Check configuration
    config_status = "✅ Valid" if validate_config() else "❌ Invalid"
    
    # Check jobs CSV
    csv_status = "✅ Ready" if check_jobs_csv() else "❌ Not Ready"
    
    # Check dependencies
    try:
        import playwright
        playwright_status = "✅ Installed"
    except ImportError:
        playwright_status = "❌ Not Installed"
    
    print(f"📋 Configuration: {config_status}")
    print(f"📂 Jobs CSV: {csv_status}")
    print(f"🎭 Playwright: {playwright_status}")
    print(f"📊 Dashboard: {'✅ Available' if Path('dashboard.html').exists() else '❌ Missing'}")
    
    if Path("tracker_data.js").exists():
        print("📈 Previous runs: ✅ Data available")
    else:
        print("📈 Previous runs: ⚪ No data yet")
    
    input("Press Enter to continue...")

def main():
    """Main launcher loop"""
    while True:
        print_banner()
        print_menu()
        
        try:
            choice = input("\n🎯 Enter your choice (0-9): ").strip()
            
            if choice == "1":
                start_automation(10)
            elif choice == "2":
                print("⚡ ULTRA FAST MODE - Maximum speed with 20 concurrent tabs!")
                confirm = input("This is very intensive. Continue? (y/N): ")
                if confirm.lower() == 'y':
                    start_automation(20)
            elif choice == "3":
                print("🐌 CONSERVATIVE MODE - Safer processing with 5 tabs")
                start_automation(5)
            elif choice == "4":
                print("🎯 SINGLE TAB TEST MODE - Perfect for testing")
                start_automation(1)
            elif choice == "5":
                open_dashboard()
            elif choice == "6":
                configure_settings()
            elif choice == "7":
                edit_jobs_csv()
            elif choice == "8":
                validate_config()
                input("Press Enter to continue...")
            elif choice == "9":
                show_status()
            elif choice == "0":
                print("\n👋 Thank you for using Fully Automated Job Application System!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            
        # Clear screen equivalent for better UX
        print("\n" * 2)

if __name__ == "__main__":
    main()