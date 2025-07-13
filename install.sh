#!/bin/bash

echo "🚀 Setting up Super Fast Job Application Automation Tool..."
echo "="*60

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 detected"

# Create virtual environment
echo "🔄 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "🔄 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "🔄 Installing Python dependencies..."
pip install playwright asyncio pathlib

# Install Playwright browsers
echo "🔄 Installing Playwright browsers..."
playwright install

# Create files directory
echo "🔄 Creating files directory..."
mkdir -p files

# Set executable permissions
echo "🔄 Setting executable permissions..."
chmod +x main.py
chmod +x test_config.py
chmod +x speed_test.py

echo ""
echo "🎉 Setup completed successfully!"
echo "="*60
echo ""
echo "📋 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Edit config.json with your personal information"
echo "3. Place your resume.pdf and cover_letter.pdf in the files/ directory"
echo "4. Update jobs.csv with real job URLs"
echo "5. Test configuration: python test_config.py"
echo "6. Test speed: python speed_test.py"
echo "7. Run automation: python main.py jobs.csv"
echo ""
echo "🚀 Ready to apply to jobs at lightning speed!"