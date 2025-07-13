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

class FastUniversalApplicant:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.user_info = self.config["user_info"]
        self.attachments = self.config["attachments"]
        self.questions = self.config["questions"]
        self.settings = self.config["automation_settings"]
        logging.info("🚀 Fast Universal Applicant loaded successfully.")

    def _load_config(self, config_path):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_file, 'r') as f:
            return json.load(f)

    async def apply(self, page: Page, job_details: dict):
        company_name = job_details.get("company", job_details.get("url"))
        logging.info(f"🎯 Starting application process for {company_name}")
        
        # Wait for initial page load
        await self._wait_for_page_load(page)
        
        # Check for login requirement
        if await self._detect_and_handle_login(page):
            logging.info("✅ Login completed, proceeding with application...")
            # Wait a bit more after login
            await asyncio.sleep(2)
        
        # Use original proven form filling logic (but faster)
        await self._fill_text_inputs(page)
        await self._upload_attachments(page)
        await self._handle_questions(page)
        
        self._update_tracker(job_details)
        logging.info(f"✅ Application completed for {company_name}")

    async def _wait_for_page_load(self, page: Page):
        """Wait for page to be fully loaded"""
        try:
            await page.wait_for_load_state('domcontentloaded', timeout=10000)
            await page.wait_for_load_state('networkidle', timeout=5000)
            await asyncio.sleep(1)  # Reduced from 2 seconds
        except TimeoutError:
            logging.info("Page load timeout - proceeding anyway")

    async def _detect_and_handle_login(self, page: Page) -> bool:
        """Improved login detection"""
        logging.info("🔍 Checking for login requirements...")
        
        # More comprehensive login detection
        login_indicators = [
            "input[type='password']",
            "input[name*='password' i]",
            "input[id*='password' i]",
            "input[name*='login' i]",
            "input[id*='login' i]",
            "button:has-text('Sign In')",
            "button:has-text('Log In')",
            "button:has-text('Login')",
            "button:has-text('Sign On')",
            "a:has-text('Sign In')",
            "a:has-text('Log In')",
            "a:has-text('Login')",
            "[data-automation-id*='login']",
            "[data-automation-id*='signin']",
            "form[name*='login' i]",
            "form[action*='login' i]",
            "form[action*='signin' i]",
            ".login-form",
            ".signin-form",
            "#login-form",
            "#signin-form",
            "[role='form']:has(input[type='password'])"
        ]
        
        # Check URL and title patterns
        try:
            url = page.url.lower()
            title = await page.title()
            title_lower = title.lower()
            
            login_url_patterns = ['login', 'signin', 'auth', 'sso', 'oauth', 'account', 'portal']
            login_title_patterns = ['login', 'sign in', 'authenticate', 'log in', 'portal', 'sso']
            
            url_login = any(pattern in url for pattern in login_url_patterns)
            title_login = any(pattern in title_lower for pattern in login_title_patterns)
            
            if url_login or title_login:
                logging.info(f"🔐 Login detected in URL/title: {url} | {title}")
                return await self._handle_login_interaction(page)
                
        except Exception as e:
            logging.debug(f"Error checking URL/title: {e}")
        
        # Check for login form elements
        for indicator in login_indicators:
            try:
                if await page.locator(indicator).count() > 0:
                    logging.info(f"🔐 Login detected: {indicator}")
                    return await self._handle_login_interaction(page)
            except Exception as e:
                logging.debug(f"Error checking {indicator}: {e}")
        
        return False

    async def _handle_login_interaction(self, page: Page) -> bool:
        """Handle user login interaction"""
        print("\n" + "🔐" * 80)
        print("🔐 LOGIN REQUIRED - WORKDAY/ENTERPRISE PORTAL DETECTED")
        print("🔐" * 80)
        print(f"🌐 URL: {page.url}")
        print(f"📄 Title: {await page.title()}")
        print("\n🚨 MANUAL LOGIN REQUIRED")
        print("Please complete the following steps:")
        print("1. 👤 Enter your username/email")
        print("2. 🔑 Enter your password")
        print("3. 🔒 Complete SSO/2FA if required")
        print("4. ✅ Wait for the main application page to load")
        print("5. 🚀 The automation will resume automatically")
        print("\n⏳ Waiting for you to complete login...")
        
        # Wait for user to complete login
        while True:
            try:
                user_input = input("\n✋ Press Enter when login is complete (or 'skip' to bypass): ").strip()
                
                if user_input.lower() == 'skip':
                    print("⏭️  Skipping login detection...")
                    return False
                
                # Wait for page to load after login
                await asyncio.sleep(3)
                
                # Check if we're still on login page
                if await self._is_still_login_page(page):
                    print("⚠️  Still on login page. Please complete login and try again.")
                    continue
                else:
                    print("✅ Login successful! Resuming automation...")
                    return True
                    
            except KeyboardInterrupt:
                print("\n❌ User cancelled login process")
                return False
            except Exception as e:
                print(f"❌ Error during login: {e}")
                return False

    async def _is_still_login_page(self, page: Page) -> bool:
        """Check if we're still on a login page"""
        try:
            # Wait for any redirects to complete
            await page.wait_for_load_state('networkidle', timeout=5000)
            
            # Check for password fields (strong indicator of login page)
            if await page.locator("input[type='password']").count() > 0:
                return True
            
            # Check for login buttons
            login_buttons = [
                "button:has-text('Sign In')",
                "button:has-text('Log In')",
                "button:has-text('Login')"
            ]
            
            for button in login_buttons:
                if await page.locator(button).count() > 0:
                    return True
            
            # Check for common application form elements (indicates successful login)
            app_indicators = [
                "input[placeholder*='first name' i]",
                "input[placeholder*='last name' i]",
                "input[placeholder*='email' i]",
                "button:has-text('Apply')",
                "button:has-text('Submit')",
                "button:has-text('Submit Application')",
                "[data-automation-id*='apply']",
                ".application-form",
                "#application-form",
                "form:has(input[placeholder*='name' i])"
            ]
            
            for indicator in app_indicators:
                if await page.locator(indicator).count() > 0:
                    return False  # Found application form, login successful
            
            return True  # Assume still on login page
            
        except Exception as e:
            logging.debug(f"Error checking login page: {e}")
            return False  # Assume login was successful

    async def _fill_text_inputs(self, page: Page):
        """Original proven text input filling logic with speed optimizations"""
        logging.info("📝 Filling text inputs...")
        
        for key, value in self.user_info.items():
            if not value: 
                continue
                
            # Original proven selectors - keep the same logic but faster timeouts
            selectors = [
                f"input[name*='{key}' i]", 
                f"input[id*='{key}' i]",
                f"input[placeholder*='{key}' i]", 
                f"input[aria-label*='{key}' i]",
                f"input[data-automation-id*='{key}' i]",
                f"textarea[name*='{key}' i]",
                f"textarea[placeholder*='{key}' i]"
            ]
            
            try:
                # Use original selector approach but with faster timeout
                element = page.locator(", ".join(selectors)).first
                if await element.count() > 0:
                    await element.fill(value, timeout=3000)  # Faster than original 5000
                    logging.info(f"✅ Filled '{key}' with '{value}'")
                else:
                    logging.debug(f"⚠️  Could not find input for key: {key}")
            except TimeoutError:
                logging.debug(f"⚠️  Timeout filling '{key}'")
            except Exception as e:
                logging.debug(f"⚠️  Error filling '{key}': {e}")

    async def _upload_attachments(self, page: Page):
        """Original proven file upload logic"""
        logging.info("📎 Uploading attachments...")
        
        resume_path = self.attachments.get("resume")
        if resume_path and Path(resume_path).exists():
            selectors = [
                'input[type="file"]',
                'input[accept*=".pdf"]',
                'button:has-text("Attach Resume")', 
                'button:has-text("Upload Resume")',
                'button:has-text("Browse")',
                'button:has-text("Choose File")',
                '[data-automation-id*="resume"]',
                '[data-automation-id*="upload"]'
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if await element.count() > 0:
                        if 'input[type="file"]' in selector:
                            await element.set_input_files(resume_path)
                            logging.info(f"✅ Uploaded resume: {resume_path}")
                            break
                        else:
                            async with page.expect_file_chooser(timeout=3000) as fc_info:
                                await element.click()
                            file_chooser = await fc_info.value
                            await file_chooser.set_files(resume_path)
                            logging.info(f"✅ Uploaded resume: {resume_path}")
                            break
                except Exception as e:
                    logging.debug(f"Upload attempt failed for {selector}: {e}")
                    continue
        else:
            logging.warning("⚠️  Resume file not found")

    async def _handle_questions(self, page: Page):
        """Original proven question handling logic with speed optimizations"""
        logging.info("❓ Handling questions...")
        
        for question in self.questions:
            handled = False
            
            for keyword in question["keywords"]:
                if handled:
                    break
                    
                try:
                    # Strategy 1: Handle Dropdowns (HTML select) - Original approach
                    dropdown_selectors = [
                        f"select[name*='{keyword}' i]",
                        f"select[id*='{keyword}' i]",
                        f"select[aria-label*='{keyword}' i]",
                        f"select[data-automation-id*='{keyword}' i]"
                    ]
                    
                    for selector in dropdown_selectors:
                        try:
                            element = page.locator(selector).first
                            if await element.count() > 0:
                                # Try different selection methods
                                try:
                                    await element.select_option(label=question["answer"], timeout=2000)
                                    logging.info(f"✅ Selected dropdown '{keyword}' = '{question['answer']}'")
                                    handled = True
                                    break
                                except:
                                    try:
                                        await element.select_option(value=question["answer"], timeout=2000)
                                        handled = True
                                        break
                                    except:
                                        # Partial match
                                        options = await element.locator('option').all()
                                        for option in options:
                                            try:
                                                option_text = await option.inner_text()
                                                if question["answer"].lower() in option_text.lower():
                                                    await element.select_option(label=option_text, timeout=2000)
                                                    logging.info(f"✅ Selected dropdown '{keyword}' = '{option_text}'")
                                                    handled = True
                                                    break
                                            except:
                                                continue
                                        if handled:
                                            break
                        except Exception as e:
                            logging.debug(f"Dropdown attempt failed: {e}")
                            continue
                    
                    if handled:
                        break
                    
                    # Strategy 2: Handle Custom Dropdowns (div-based) - Original approach
                    custom_dropdown_triggers = [
                        f"div[role='combobox'][aria-label*='{keyword}' i]",
                        f"button[aria-label*='{keyword}' i]",
                        f"div[data-automation-id*='{keyword}' i]",
                        f"button[data-automation-id*='{keyword}' i]"
                    ]
                    
                    for trigger_selector in custom_dropdown_triggers:
                        try:
                            trigger = page.locator(trigger_selector).first
                            if await trigger.count() > 0:
                                await trigger.click(timeout=2000)
                                await asyncio.sleep(0.5)  # Wait for dropdown to open
                                
                                # Find and click option
                                option_selectors = [
                                    f"[role='option']:has-text('{question['answer']}')",
                                    f"li:has-text('{question['answer']}')",
                                    f"div:has-text('{question['answer']}')",
                                    f"button:has-text('{question['answer']}')"
                                ]
                                
                                for option_selector in option_selectors:
                                    try:
                                        option = page.locator(option_selector).first
                                        if await option.count() > 0:
                                            await option.click(timeout=2000)
                                            logging.info(f"✅ Selected custom dropdown '{keyword}' = '{question['answer']}'")
                                            handled = True
                                            break
                                    except:
                                        continue
                                
                                if handled:
                                    break
                        except Exception as e:
                            logging.debug(f"Custom dropdown attempt failed: {e}")
                            continue
                    
                    if handled:
                        break
                    
                    # Strategy 3: Handle Radio Buttons - Original approach
                    radio_selectors = [
                        f"input[type='radio'][value*='{question['answer']}' i]",
                        f"input[type='radio'][data-automation-id*='{question['answer']}' i]"
                    ]
                    
                    for selector in radio_selectors:
                        try:
                            radio = page.locator(selector).first
                            if await radio.count() > 0:
                                await radio.check(timeout=2000)
                                logging.info(f"✅ Selected radio '{keyword}' = '{question['answer']}'")
                                handled = True
                                break
                        except Exception as e:
                            logging.debug(f"Radio attempt failed: {e}")
                            continue
                    
                    if handled:
                        break
                    
                    # Strategy 4: Handle Checkboxes - Original approach
                    if question["answer"].lower() in ['yes', 'true', '1', 'agree', 'accept']:
                        checkbox_selectors = [
                            f"input[type='checkbox'][name*='{keyword}' i]",
                            f"input[type='checkbox'][id*='{keyword}' i]",
                            f"input[type='checkbox'][data-automation-id*='{keyword}' i]"
                        ]
                        
                        for selector in checkbox_selectors:
                            try:
                                checkbox = page.locator(selector).first
                                if await checkbox.count() > 0:
                                    await checkbox.check(timeout=2000)
                                    logging.info(f"✅ Checked '{keyword}'")
                                    handled = True
                                    break
                            except Exception as e:
                                logging.debug(f"Checkbox attempt failed: {e}")
                                continue
                    
                    if handled:
                        break
                    
                    # Strategy 5: Handle Text Inputs for questions - Original approach
                    text_selectors = [
                        f"input[placeholder*='{keyword}' i]",
                        f"textarea[placeholder*='{keyword}' i]",
                        f"input[aria-label*='{keyword}' i]",
                        f"textarea[aria-label*='{keyword}' i]"
                    ]
                    
                    for selector in text_selectors:
                        try:
                            element = page.locator(selector).first
                            if await element.count() > 0:
                                await element.fill(question["answer"], timeout=2000)
                                logging.info(f"✅ Filled text '{keyword}' = '{question['answer']}'")
                                handled = True
                                break
                        except Exception as e:
                            logging.debug(f"Text input attempt failed: {e}")
                            continue
                    
                except Exception as e:
                    logging.debug(f"Error handling question for keyword '{keyword}': {e}")
                    continue
            
            if not handled:
                logging.warning(f"⚠️  Could not handle question: {question['keywords']}")

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
        logging.info(f"📊 Updated tracker: {new_job['company']}")


async def run_fast_batch_mode(csv_file_path: str):
    """Fast batch mode with reliable login handling"""
    logging.info(f"🚀 Starting FAST batch mode: {csv_file_path}")
    
    try:
        with open(Path(csv_file_path), mode='r', encoding='utf-8') as csvfile:
            jobs_to_apply = list(csv.DictReader(csvfile))
    except FileNotFoundError:
        logging.critical(f"❌ jobs.csv not found: {csv_file_path}")
        return

    applicant = FastUniversalApplicant()
    
    async with async_playwright() as p:
        # Optimized browser settings for speed while maintaining compatibility
        browser = await p.chromium.launch(
            channel="chrome",
            headless=applicant.settings.get("headless", False),
            slow_mo=applicant.settings.get("slow_mo", 50),  # Balanced speed
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-background-networking'
            ]
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()
        page.set_default_timeout(applicant.settings.get("timeout", 15000))  # Balanced timeout

        for i, job in enumerate(jobs_to_apply):
            url = job.get("url", "").strip()
            if not url:
                logging.warning(f"⚠️  Skipping empty URL in row {i+2}")
                continue

            company_name = job.get("company", url)
            print(f"\n{'='*80}")
            print(f"🎯 Processing Job {i+1}/{len(jobs_to_apply)}: {company_name}")
            print(f"🌐 URL: {url}")
            print(f"{'='*80}")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await applicant.apply(page, job)
                
                print(f"\n✅ Automation completed for {company_name}")
                print("👀 Please review the filled form and click Submit if everything looks correct.")
                
            except Exception as e:
                logging.error(f"❌ Error processing {url}: {e}")
                print(f"❌ Failed to process {url}. Moving to next job.")
                continue

            print(f"\n{'='*80}")
            print("🎉 AUTOMATION COMPLETED")
            print(f"{'='*80}")
            
            user_input = input("Press Enter to continue to next job, or type 'stop' to end: ")
            
            if user_input.lower() in ['stop', 'quit', 'exit', 'q']:
                logging.info("User stopped the batch process.")
                break
        
        print(f"\n{'='*80}")
        print("🎉 BATCH PROCESSING COMPLETED")
        print(f"{'='*80}")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_jobs.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    asyncio.run(run_fast_batch_mode(csv_path))