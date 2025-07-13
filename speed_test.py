#!/usr/bin/env python3
"""
Speed Test Script for Super Fast Job Application Automation
Tests the enhanced speed and login detection features
"""

import asyncio
import time
from pathlib import Path
from playwright.async_api import async_playwright
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SpeedTester:
    def __init__(self):
        self.test_results = []

    async def test_login_detection(self):
        """Test login detection on various login pages"""
        print("🧪 Testing Login Detection...")
        
        # Test URLs with login pages
        test_urls = [
            "https://www.linkedin.com/jobs/",
            "https://www.indeed.com/account/login",
            "https://www.glassdoor.com/index.htm"
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, slow_mo=50)
            page = await browser.new_page()
            
            for url in test_urls:
                print(f"\n🔍 Testing: {url}")
                try:
                    await page.goto(url, timeout=15000)
                    login_detected = await self._detect_login_page(page)
                    
                    if login_detected:
                        print(f"✅ LOGIN DETECTED: {url}")
                    else:
                        print(f"❌ No login detected: {url}")
                        
                except Exception as e:
                    print(f"⚠️  Error testing {url}: {e}")
            
            await browser.close()

    async def _detect_login_page(self, page):
        """Simplified login detection for testing"""
        login_indicators = [
            "input[type='password']",
            "input[name*='password' i]",
            "button:has-text('Sign In')",
            "button:has-text('Log In')",
            "button:has-text('Login')"
        ]
        
        for indicator in login_indicators:
            try:
                if await page.locator(indicator).count() > 0:
                    print(f"🔐 Found login indicator: {indicator}")
                    return True
            except:
                continue
        
        # Check URL patterns
        url = page.url.lower()
        if any(pattern in url for pattern in ['login', 'signin', 'auth']):
            print(f"🔐 Login detected in URL: {url}")
            return True
            
        return False

    async def test_form_filling_speed(self):
        """Test form filling speed on a sample form"""
        print("\n⚡ Testing Form Filling Speed...")
        
        # Create a test HTML page with various form elements
        test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Speed Test Form</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .form-group { margin: 10px 0; }
                input, select, textarea { width: 200px; padding: 5px; margin: 5px; }
                button { padding: 10px 20px; margin: 10px; }
            </style>
        </head>
        <body>
            <h1>Job Application Form - Speed Test</h1>
            <form>
                <div class="form-group">
                    <label>First Name:</label>
                    <input name="first_name" placeholder="Enter first name" />
                </div>
                <div class="form-group">
                    <label>Last Name:</label>
                    <input name="last_name" placeholder="Enter last name" />
                </div>
                <div class="form-group">
                    <label>Email:</label>
                    <input name="email" type="email" placeholder="Enter email" />
                </div>
                <div class="form-group">
                    <label>Phone:</label>
                    <input name="phone" type="tel" placeholder="Enter phone" />
                </div>
                <div class="form-group">
                    <label>Experience:</label>
                    <select name="experience">
                        <option value="">Select Experience</option>
                        <option value="1-2">1-2 years</option>
                        <option value="3-5">3-5 years</option>
                        <option value="5+">5+ years</option>
                        <option value="10+">10+ years</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Work Authorization:</label>
                    <input type="radio" name="authorized" value="yes" /> Yes
                    <input type="radio" name="authorized" value="no" /> No
                </div>
                <div class="form-group">
                    <label>Willing to relocate:</label>
                    <input type="checkbox" name="relocate" /> Yes
                </div>
                <div class="form-group">
                    <label>Cover Letter:</label>
                    <textarea name="cover_letter" placeholder="Enter cover letter"></textarea>
                </div>
                <div class="form-group">
                    <label>Resume:</label>
                    <input type="file" name="resume" accept=".pdf,.doc,.docx" />
                </div>
                <button type="submit">Submit Application</button>
            </form>
        </body>
        </html>
        """
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,
                slow_mo=20,  # Super fast mode
                args=['--disable-images', '--disable-plugins']
            )
            page = await browser.new_page()
            
            # Load test page
            await page.set_content(test_html)
            
            # Time the form filling
            start_time = time.time()
            
            # Fill form fields quickly
            await page.fill('input[name="first_name"]', 'John')
            await page.fill('input[name="last_name"]', 'Doe')
            await page.fill('input[name="email"]', 'john.doe@email.com')
            await page.fill('input[name="phone"]', '+1-555-123-4567')
            await page.select_option('select[name="experience"]', '5+')
            await page.check('input[name="authorized"][value="yes"]')
            await page.check('input[name="relocate"]')
            await page.fill('textarea[name="cover_letter"]', 'I am excited about this opportunity!')
            
            end_time = time.time()
            fill_time = end_time - start_time
            
            print(f"⚡ Form filled in {fill_time:.2f} seconds")
            
            # Wait a moment to see the results
            await asyncio.sleep(3)
            
            await browser.close()
            
            return fill_time

    async def run_comprehensive_speed_test(self):
        """Run comprehensive speed tests"""
        print("🚀 SUPER FAST AUTOMATION - COMPREHENSIVE SPEED TEST")
        print("="*60)
        
        # Test 1: Login Detection
        await self.test_login_detection()
        
        # Test 2: Form Filling Speed
        fill_time = await self.test_form_filling_speed()
        
        # Results
        print("\n" + "🎯" * 60)
        print("🎯 SPEED TEST RESULTS")
        print("🎯" * 60)
        print(f"⚡ Form Filling Speed: {fill_time:.2f} seconds")
        
        if fill_time < 5:
            print("🔥 EXCELLENT: Lightning fast form filling!")
        elif fill_time < 10:
            print("✅ GOOD: Fast form filling")
        else:
            print("⚠️  SLOW: Consider optimizing settings")
        
        print("\n🎉 Speed test completed!")

async def main():
    """Run the speed test"""
    tester = SpeedTester()
    await tester.run_comprehensive_speed_test()

if __name__ == "__main__":
    asyncio.run(main())