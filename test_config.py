#!/usr/bin/env python3
"""
Configuration Test Script for Enhanced Job Application Automation Tool
"""

import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConfigTester:
    def __init__(self):
        self.config = None
        self.errors = []
        self.warnings = []

    def load_config(self):
        """Load and validate configuration"""
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            logging.info("✅ Configuration loaded successfully")
            return True
        except FileNotFoundError:
            self.errors.append("❌ config.json file not found")
            return False
        except json.JSONDecodeError as e:
            self.errors.append(f"❌ Invalid JSON in config.json: {e}")
            return False

    def validate_config_structure(self):
        """Validate configuration structure"""
        required_sections = ['user_info', 'attachments', 'questions', 'automation_settings']
        
        for section in required_sections:
            if section not in self.config:
                self.errors.append(f"❌ Missing required section: {section}")
            else:
                logging.info(f"✅ Found section: {section}")

        # Validate user_info fields
        required_user_fields = ['first_name', 'last_name', 'email', 'phone']
        for field in required_user_fields:
            if field not in self.config.get('user_info', {}):
                self.warnings.append(f"⚠️  Missing user_info field: {field}")
            elif not self.config['user_info'][field]:
                self.warnings.append(f"⚠️  Empty user_info field: {field}")

    def validate_attachments(self):
        """Validate attachment files"""
        attachments = self.config.get('attachments', {})
        
        for file_type, file_path in attachments.items():
            if file_path:
                if Path(file_path).exists():
                    logging.info(f"✅ Found {file_type}: {file_path}")
                else:
                    self.warnings.append(f"⚠️  File not found: {file_path}")
            else:
                self.warnings.append(f"⚠️  No path specified for {file_type}")

    def validate_questions(self):
        """Validate questions configuration"""
        questions = self.config.get('questions', [])
        
        if not questions:
            self.warnings.append("⚠️  No questions configured")
            return

        for i, question in enumerate(questions):
            if 'keywords' not in question:
                self.errors.append(f"❌ Question {i+1} missing 'keywords'")
            elif not question['keywords']:
                self.errors.append(f"❌ Question {i+1} has empty keywords")
            
            if 'answer' not in question:
                self.errors.append(f"❌ Question {i+1} missing 'answer'")
            elif not question['answer']:
                self.warnings.append(f"⚠️  Question {i+1} has empty answer")

        logging.info(f"✅ Validated {len(questions)} questions")

    async def test_browser_automation(self):
        """Test basic browser automation"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Create a simple test HTML page
                test_html = """
                <!DOCTYPE html>
                <html>
                <head><title>Test Form</title></head>
                <body>
                    <form>
                        <input name="first_name" placeholder="First Name" />
                        <input name="email" placeholder="Email" />
                        <select name="experience">
                            <option value="">Select Experience</option>
                            <option value="1-2">1-2 years</option>
                            <option value="3-5">3-5 years</option>
                            <option value="5+">5+ years</option>
                        </select>
                        <input type="radio" name="willing" value="yes" /> Yes
                        <input type="radio" name="willing" value="no" /> No
                        <input type="checkbox" name="agree" /> I agree
                    </form>
                </body>
                </html>
                """
                
                await page.set_content(test_html)
                
                # Test filling text inputs
                await page.fill('input[name="first_name"]', 'Test')
                await page.fill('input[name="email"]', 'test@example.com')
                
                # Test dropdown selection
                await page.select_option('select[name="experience"]', '5+')
                
                # Test radio button
                await page.check('input[name="willing"][value="yes"]')
                
                # Test checkbox
                await page.check('input[name="agree"]')
                
                await browser.close()
                logging.info("✅ Browser automation test passed")
                return True
                
        except Exception as e:
            self.errors.append(f"❌ Browser automation test failed: {e}")
            return False

    def run_all_tests(self):
        """Run all validation tests"""
        print("🧪 Testing Enhanced Job Application Automation Configuration...\n")
        
        # Test configuration loading
        if not self.load_config():
            self.print_results()
            return False
        
        # Run validation tests
        self.validate_config_structure()
        self.validate_attachments()
        self.validate_questions()
        
        # Print results
        self.print_results()
        
        return len(self.errors) == 0

    async def run_browser_test(self):
        """Run browser automation test"""
        print("\n🌐 Testing browser automation...")
        await self.test_browser_automation()

    def print_results(self):
        """Print test results"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS")
        print("="*60)
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if not self.errors and not self.warnings:
            print("\n🎉 All tests passed! Your configuration looks good.")
        elif not self.errors:
            print("\n✅ Configuration is valid but has some warnings.")
        else:
            print("\n❌ Configuration has errors that need to be fixed.")
        
        print("\n" + "="*60)

async def main():
    tester = ConfigTester()
    
    # Run configuration tests
    config_valid = tester.run_all_tests()
    
    if config_valid:
        # Run browser test if config is valid
        await tester.run_browser_test()
        
        print("\n🚀 Ready to run the automation tool!")
        print("Run: python main.py jobs.csv")
    else:
        print("\n🔧 Please fix the configuration errors before proceeding.")

if __name__ == "__main__":
    asyncio.run(main())