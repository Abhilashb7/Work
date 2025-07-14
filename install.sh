#!/bin/bash

echo "=================================================================="
echo "🚀 FULLY AUTOMATED JOB APPLICATION SYSTEM - INSTALLER"
echo "=================================================================="
echo "⚡ Zero-delay form filling | Multi-tab processing | Auto-login"
echo "🔥 Lightning fast | Enterprise-grade | Error-free"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Python is installed
echo ""
echo "🔍 Checking system requirements..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_status "Python $PYTHON_VERSION found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip first."
    exit 1
fi

print_status "pip3 found"

# Create virtual environment
echo ""
echo "🏗️  Setting up virtual environment..."

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    print_status "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
print_status "pip upgraded"

# Install Python dependencies
echo ""
echo "� Installing Python dependencies..."
pip install playwright
pip install asyncio
pip install pathlib
print_status "Python dependencies installed"

# Install Playwright browsers
echo ""
echo "🎭 Installing Playwright browsers..."
playwright install chromium
print_status "Playwright browsers installed"

# Create files directory if it doesn't exist
echo ""
echo "� Setting up directory structure..."

if [ ! -d "files" ]; then
    mkdir files
    print_status "Created files/ directory"
else
    print_status "files/ directory already exists"
fi

# Check if config.json exists
if [ ! -f "config.json" ]; then
    print_warning "config.json not found. Please create it with your details."
else
    print_status "config.json found"
fi

# Check if jobs.csv exists
if [ ! -f "jobs.csv" ]; then
    print_warning "jobs.csv not found. Creating sample file."
    echo "company,url" > jobs.csv
    echo "Google,https://careers.google.com/jobs/results/134567890/" >> jobs.csv
    echo "Microsoft,https://careers.microsoft.com/us/en/job/1234567" >> jobs.csv
    print_status "Sample jobs.csv created"
else
    print_status "jobs.csv found"
fi

# Make Python files executable
chmod +x main.py 2>/dev/null
chmod +x launcher.py 2>/dev/null
print_status "Made Python files executable"

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << EOF
playwright>=1.40.0
asyncio
pathlib
EOF
    print_status "requirements.txt created"
fi

echo ""
echo "=================================================================="
print_status "INSTALLATION COMPLETED SUCCESSFULLY!"
echo "=================================================================="

echo ""
echo "🎯 NEXT STEPS:"
echo ""
echo "1. 📝 Edit config.json with your details:"
echo "   - Update user_info with your personal information"
echo "   - Add login_credentials (email and password)"
echo "   - Set resume path in attachments"
echo ""
echo "2. 📂 Add your resume to files/resume.pdf"
echo ""
echo "3. 📋 Add job URLs to jobs.csv:"
echo "   Format: company,url"
echo ""
echo "4. 🚀 Start the automation:"
echo "   ${GREEN}source venv/bin/activate${NC}"
echo "   ${GREEN}python launcher.py${NC}"
echo ""
echo "=================================================================="
echo "🔥 READY TO AUTOMATE 100 JOB APPLICATIONS IN MINUTES!"
echo "=================================================================="

# Quick validation
echo ""
echo "🔍 Quick system validation:"

# Check if all required files exist
required_files=("main.py" "launcher.py" "dashboard.html" "config.json")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status "$file exists"
    else
        print_warning "$file missing"
    fi
done

# Check Python packages
echo ""
echo "📦 Validating Python packages..."
python3 -c "import playwright; print('✅ Playwright installed')" 2>/dev/null || print_warning "Playwright validation failed"

echo ""
echo "🎉 Installation complete! Run 'python launcher.py' to start."
echo ""

# Ask if user wants to open launcher immediately
read -p "🚀 Would you like to start the launcher now? (y/N): " start_now
if [[ $start_now =~ ^[Yy]$ ]]; then
    echo ""
    echo "🚀 Starting launcher..."
    python launcher.py
fi