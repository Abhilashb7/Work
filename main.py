import json
import logging
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page, TimeoutError
import sys
import csv
import datetime
import re
import time

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

class SuperFastUniversalApplicant:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.user_info = self.config["user_info"]
        self.attachments = self.config["attachments"]
        self.questions = self.config["questions"]
        self.settings = self.config["automation_settings"]
        self.login_handled = False
        logging.info("🚀 Super Fast Enhanced configuration loaded successfully.")

    def _load_config(self, config_path):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_file, 'r') as f:
            return json.load(f)

    async def apply(self, page: Page, job_details: dict):
        company_name = job_details.get("company", job_details.get("url"))
        logging.info(f"🎯 Starting SUPER FAST application process for {company_name}")
        
        # Check for login page first
        if await self._detect_and_handle_login(page):
            logging.info("🔐 Login detected and handled, proceeding with application...")
        
        # Fast form filling pipeline
        await self._super_fast_fill_pipeline(page)
        
        self._update_tracker(job_details)
        logging.info(f"⚡ SUPER FAST automation completed for {company_name}")

    async def _detect_and_handle_login(self, page: Page) -> bool:
        """Detect login pages and handle user authentication"""
        logging.info("🔍 Checking for login requirements...")
        
        # Wait briefly for page to load
        await asyncio.sleep(1)
        
        # Login detection patterns
        login_indicators = [
            "input[type='password']",
            "input[name*='password' i]",
            "input[id*='password' i]",
            "button:has-text('Sign In')",
            "button:has-text('Log In')",
            "button:has-text('Login')",
            "a:has-text('Sign In')",
            "a:has-text('Log In')",
            "[data-testid*='login']",
            "[data-testid*='signin']",
            "form[action*='login']",
            "form[action*='signin']",
            ".login-form",
            ".signin-form",
            "#login-form",
            "#signin-form"
        ]
        
        # Check for login indicators
        login_detected = False
        for indicator in login_indicators:
            try:
                if await page.locator(indicator).count() > 0:
                    login_detected = True
                    logging.info(f"🔐 Login detected: {indicator}")
                    break
            except:
                continue
        
        # Also check for common login page titles/URLs
        try:
            url = page.url.lower()
            title = await page.title()
            title_lower = title.lower()
            
            login_url_patterns = ['login', 'signin', 'auth', 'sso', 'oauth', 'account']
            login_title_patterns = ['login', 'sign in', 'authenticate', 'log in']
            
            if any(pattern in url for pattern in login_url_patterns):
                login_detected = True
                logging.info(f"🔐 Login detected in URL: {url}")
            
            if any(pattern in title_lower for pattern in login_title_patterns):
                login_detected = True
                logging.info(f"🔐 Login detected in title: {title}")
                
        except:
            pass
        
        if login_detected:
            return await self._handle_login_interaction(page)
        
        return False

    async def _handle_login_interaction(self, page: Page) -> bool:
        """Handle user login interaction"""
        print("\n" + "🔐" * 60)
        print("🔐 LOGIN REQUIRED")
        print("🔐" * 60)
        print(f"📱 Current URL: {page.url}")
        print(f"📄 Page Title: {await page.title()}")
        print("\n🚨 ATTENTION: This page requires login/authentication")
        print("👤 Please complete the login process manually in the browser")
        print("🔑 This may include:")
        print("   • Username/Password login")
        print("   • SSO (Single Sign-On)")
        print("   • Two-factor authentication")
        print("   • Account creation if needed")
        print("\n⏳ The automation will resume once you're logged in...")
        
        # Wait for user to complete login
        while True:
            user_input = input("\n✋ Have you completed the login? (y/n/skip): ").lower().strip()
            
            if user_input in ['y', 'yes']:
                # Verify login was successful
                await asyncio.sleep(2)  # Wait for page to load after login
                
                # Check if we're still on a login page
                still_on_login = await self._is_still_login_page(page)
                
                if not still_on_login:
                    print("✅ Login successful! Resuming automation...")
                    return True
                else:
                    print("⚠️  Still appears to be on login page. Please complete login and try again.")
                    continue
                    
            elif user_input in ['n', 'no']:
                print("⏳ Waiting for you to complete login...")
                await asyncio.sleep(5)  # Wait 5 seconds before asking again
                continue
                
            elif user_input == 'skip':
                print("⏭️  Skipping login detection, proceeding with automation...")
                return False
                
            else:
                print("❓ Please enter 'y' for yes, 'n' for no, or 'skip' to skip login")

    async def _is_still_login_page(self, page: Page) -> bool:
        """Check if we're still on a login page"""
        try:
            # Quick check for password fields (most reliable indicator)
            password_fields = await page.locator("input[type='password']").count()
            if password_fields > 0:
                return True
            
            # Check for common post-login elements
            post_login_indicators = [
                "button:has-text('Apply')",
                "button:has-text('Submit Application')",
                "input[placeholder*='first name' i]",
                "input[placeholder*='last name' i]",
                "input[placeholder*='email' i]",
                "[data-testid*='apply']",
                ".application-form",
                "#application-form"
            ]
            
            for indicator in post_login_indicators:
                if await page.locator(indicator).count() > 0:
                    return False  # Found application form elements
            
            return True  # Still seems to be login page
            
        except:
            return False  # Assume login was successful if we can't determine

    async def _super_fast_fill_pipeline(self, page: Page):
        """Super fast form filling pipeline with minimal delays"""
        logging.info("⚡ Starting SUPER FAST form filling pipeline...")
        
        # Minimal wait for dynamic content
        await asyncio.sleep(0.5)
        
        # Parallel execution of form filling tasks
        tasks = [
            self._lightning_fill_text_inputs(page),
            self._lightning_handle_all_form_elements(page),
            self._lightning_upload_attachments(page)
        ]
        
        # Run all tasks concurrently for maximum speed
        await asyncio.gather(*tasks, return_exceptions=True)
        
        logging.info("⚡ SUPER FAST form filling pipeline completed!")

    async def _lightning_fill_text_inputs(self, page: Page):
        """Lightning fast text input filling"""
        logging.info("⚡ Lightning fast text input filling...")
        
        # Optimized field mappings with faster selectors
        fast_field_mappings = {
            'first_name': ['[name*="first" i]', '[placeholder*="first" i]', '[id*="first" i]'],
            'last_name': ['[name*="last" i]', '[placeholder*="last" i]', '[id*="last" i]'],
            'email': ['[name*="email" i]', '[placeholder*="email" i]', '[type="email"]'],
            'phone': ['[name*="phone" i]', '[placeholder*="phone" i]', '[type="tel"]'],
            'address': ['[name*="address" i]', '[placeholder*="address" i]'],
            'city': ['[name*="city" i]', '[placeholder*="city" i]'],
            'state': ['[name*="state" i]', '[placeholder*="state" i]'],
            'zip_code': ['[name*="zip" i]', '[placeholder*="zip" i]', '[placeholder*="postal" i]'],
            'linkedin': ['[name*="linkedin" i]', '[placeholder*="linkedin" i]'],
            'portfolio': ['[name*="portfolio" i]', '[placeholder*="website" i]'],
            'salary': ['[name*="salary" i]', '[placeholder*="salary" i]']
        }
        
        # Create all fill tasks
        fill_tasks = []
        for field_key, value in self.user_info.items():
            if value and field_key in fast_field_mappings:
                selectors = fast_field_mappings[field_key]
                fill_tasks.append(self._fast_fill_field(page, selectors, value, field_key))
        
        # Execute all fills concurrently
        await asyncio.gather(*fill_tasks, return_exceptions=True)

    async def _fast_fill_field(self, page: Page, selectors: list, value: str, field_name: str):
        """Fast field filling with minimal timeout"""
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    await element.fill(value, timeout=1500)  # Reduced timeout for speed
                    logging.info(f"⚡ FAST: Filled {field_name}")
                    return True
            except:
                continue
        return False

    async def _lightning_handle_all_form_elements(self, page: Page):
        """Lightning fast form element handling"""
        logging.info("⚡ Lightning fast form element handling...")
        
        # Create all question handling tasks
        question_tasks = []
        for question in self.questions:
            question_tasks.append(self._lightning_handle_question(page, question))
        
        # Execute all questions concurrently
        await asyncio.gather(*question_tasks, return_exceptions=True)

    async def _lightning_handle_question(self, page: Page, question: dict):
        """Lightning fast single question handling"""
        answer = question["answer"]
        keywords = question["keywords"]
        
        # Fast strategy execution
        for keyword in keywords:
            # Try the most common strategies first (fastest to slowest)
            if await self._fast_native_dropdown(page, keyword, answer):
                return True
            if await self._fast_custom_dropdown(page, keyword, answer):
                return True
            if await self._fast_radio_buttons(page, keyword, answer):
                return True
            if await self._fast_checkboxes(page, keyword, answer):
                return True
            if await self._fast_text_input_question(page, keyword, answer):
                return True
        
        return False

    async def _fast_native_dropdown(self, page: Page, keyword: str, answer: str) -> bool:
        """Super fast native dropdown handling"""
        fast_selectors = [
            f"select[name*='{keyword}' i]",
            f"select[id*='{keyword}' i]",
            f"select[aria-label*='{keyword}' i]"
        ]
        
        for selector in fast_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    # Try fastest selection methods
                    try:
                        await element.select_option(label=answer, timeout=1000)
                        logging.info(f"⚡ FAST: Selected dropdown '{keyword}' = '{answer}'")
                        return True
                    except:
                        try:
                            await element.select_option(value=answer, timeout=1000)
                            return True
                        except:
                            # Fast partial match
                            options = await element.locator('option').all()
                            for option in options[:10]:  # Limit to first 10 options for speed
                                try:
                                    option_text = await option.inner_text()
                                    if answer.lower() in option_text.lower():
                                        await element.select_option(label=option_text, timeout=1000)
                                        return True
                                except:
                                    continue
            except:
                continue
        return False

    async def _fast_custom_dropdown(self, page: Page, keyword: str, answer: str) -> bool:
        """Super fast custom dropdown handling"""
        fast_triggers = [
            f"[role='combobox'][aria-label*='{keyword}' i]",
            f"button[aria-label*='{keyword}' i]",
            f"div[data-testid*='{keyword}' i]"
        ]
        
        for trigger_selector in fast_triggers:
            try:
                trigger = page.locator(trigger_selector).first
                if await trigger.count() > 0:
                    await trigger.click(timeout=1000)
                    await asyncio.sleep(0.3)  # Minimal wait for dropdown
                    
                    # Fast option selection
                    fast_options = [
                        f"[role='option']:has-text('{answer}')",
                        f"li:has-text('{answer}')",
                        f"button:has-text('{answer}')"
                    ]
                    
                    for option_selector in fast_options:
                        try:
                            option = page.locator(option_selector).first
                            if await option.count() > 0:
                                await option.click(timeout=1000)
                                logging.info(f"⚡ FAST: Selected custom dropdown '{keyword}' = '{answer}'")
                                return True
                        except:
                            continue
            except:
                continue
        return False

    async def _fast_radio_buttons(self, page: Page, keyword: str, answer: str) -> bool:
        """Super fast radio button handling"""
        fast_radio_selectors = [
            f"input[type='radio'][value*='{answer}' i]",
            f"label:has-text('{answer}') input[type='radio']"
        ]
        
        for selector in fast_radio_selectors:
            try:
                radio = page.locator(selector).first
                if await radio.count() > 0:
                    await radio.check(timeout=1000)
                    logging.info(f"⚡ FAST: Selected radio '{keyword}' = '{answer}'")
                    return True
            except:
                continue
        return False

    async def _fast_checkboxes(self, page: Page, keyword: str, answer: str) -> bool:
        """Super fast checkbox handling"""
        if answer.lower() in ['yes', 'true', '1', 'agree', 'accept']:
            fast_checkbox_selectors = [
                f"input[type='checkbox'][name*='{keyword}' i]",
                f"input[type='checkbox'][id*='{keyword}' i]"
            ]
            
            for selector in fast_checkbox_selectors:
                try:
                    checkbox = page.locator(selector).first
                    if await checkbox.count() > 0:
                        await checkbox.check(timeout=1000)
                        logging.info(f"⚡ FAST: Checked '{keyword}'")
                        return True
                except:
                    continue
        return False

    async def _fast_text_input_question(self, page: Page, keyword: str, answer: str) -> bool:
        """Super fast text input handling for questions"""
        fast_selectors = [
            f"input[placeholder*='{keyword}' i]",
            f"textarea[placeholder*='{keyword}' i]"
        ]
        
        for selector in fast_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    await element.fill(answer, timeout=1000)
                    logging.info(f"⚡ FAST: Filled text '{keyword}' = '{answer}'")
                    return True
            except:
                continue
        return False

    async def _lightning_upload_attachments(self, page: Page):
        """Lightning fast file upload"""
        logging.info("⚡ Lightning fast file upload...")
        
        upload_tasks = []
        
        resume_path = self.attachments.get("resume")
        if resume_path and Path(resume_path).exists():
            upload_tasks.append(self._fast_upload_file(page, resume_path, "resume"))
        
        cover_letter_path = self.attachments.get("cover_letter")
        if cover_letter_path and Path(cover_letter_path).exists():
            upload_tasks.append(self._fast_upload_file(page, cover_letter_path, "cover"))
        
        # Execute uploads concurrently
        await asyncio.gather(*upload_tasks, return_exceptions=True)

    async def _fast_upload_file(self, page: Page, file_path: str, file_type: str):
        """Super fast file upload with minimal timeout"""
        fast_upload_selectors = [
            f'input[type="file"]',
            f'input[accept*=".pdf"]',
            f'button:has-text("Upload")',
            f'button:has-text("Browse")'
        ]
        
        for selector in fast_upload_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    if 'input[type="file"]' in selector:
                        await element.set_input_files(file_path)
                        logging.info(f"⚡ FAST: Uploaded {file_type}")
                        return True
                    else:
                        async with page.expect_file_chooser(timeout=2000) as fc_info:
                            await element.click()
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(file_path)
                        logging.info(f"⚡ FAST: Uploaded {file_type}")
                        return True
            except:
                continue
        return False

    def _update_tracker(self, job_details: dict):
        """Update job application tracker"""
        tracker_file = Path("tracker_data.js")
        jobs = []
        if tracker_file.exists():
            content = tracker_file.read_text()
            json_str_match = content[content.find('['):content.rfind(']')+1]
            if json_str_match:
                try:
                    jobs = json.loads(json_str_match)
                except json.JSONDecodeError:
                    logging.error("Could not parse tracker_data.js. Starting fresh.")
                    jobs = []
        
        new_job = {
            "id": f"job-{int(datetime.datetime.now().timestamp())}",
            "company": job_details.get("company", job_details.get("url")),
            "url": job_details["url"],
            "status": "Applied",
            "date": datetime.date.today().isoformat()
        }
        jobs.append(new_job)
        
        tracker_file.write_text(f"const jobData = {json.dumps(jobs, indent=2)};")
        logging.info(f"Updated tracker with new application for {new_job['company']}.")


async def run_super_fast_batch_mode(csv_file_path: str):
    """Super fast batch mode with login handling"""
    logging.info(f"🚀 Starting SUPER FAST Batch Mode from file: {csv_file_path}")
    try:
        with open(Path(csv_file_path), mode='r', encoding='utf-8') as csvfile:
            jobs_to_apply = list(csv.DictReader(csvfile))
    except FileNotFoundError:
        logging.critical(f"FATAL: jobs.csv file not found at {csv_file_path}")
        return

    applicant = SuperFastUniversalApplicant()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=applicant.settings.get("headless", False),
            slow_mo=applicant.settings.get("slow_mo", 20),  # Much faster!
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Disable images for faster loading
                '--disable-background-networking',
                '--disable-background-timer-throttling',
                '--disable-renderer-backgrounding',
                '--disable-backgrounding-occluded-windows',
                '--disable-client-side-phishing-detection'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()
        
        # Super fast timeouts
        page.set_default_timeout(10000)  # Much faster timeout
        
        # Disable unnecessary requests for speed
        await page.route("**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}", lambda route: route.abort())

        for i, job in enumerate(jobs_to_apply):
            url = job.get("url", "").strip()
            if not url:
                logging.warning(f"Skipping empty URL in row {i+2} of jobs.csv")
                continue

            company_name = job.get("company", url)
            print("\n" + "⚡" * 60)
            logging.info(f"⚡ Processing Job {i+1}/{len(jobs_to_apply)}: {company_name}")
            print(f"⚡ SUPER FAST Processing Job {i+1}/{len(jobs_to_apply)}: {company_name}")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await applicant.apply(page, job)
                
                print(f"\n✅ SUPER FAST automation completed for {company_name}")
                print("🔍 Please review the filled form and click submit if everything looks good.")
                
            except Exception as e:
                logging.error(f"CRITICAL ERROR processing {url}: {e}")
                print(f"ERROR: Failed to process {url}. Check logs. Moving to next job.")
                continue

            print("\n" + "⚡" * 60)
            print("⚡ SUPER FAST AUTOMATION COMPLETED")
            print("⚡" * 60)
            user_input = input("Press Enter to continue to next job, or type 'stop' to end: ")
            
            if user_input.lower() in ['stop', 'quit', 'exit', 'q']:
                logging.info("User stopped the batch process.")
                break
        
        logging.info("🎉 SUPER FAST batch mode finished!")
        print("\n" + "🎉" * 60)
        print("🎉 SUPER FAST batch mode finished! All jobs processed.")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_jobs.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    asyncio.run(run_super_fast_batch_mode(csv_path))