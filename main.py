import json
import logging
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page, TimeoutError, Browser, BrowserContext
import sys
import csv
import datetime
import re
import time
from concurrent.futures import ThreadPoolExecutor
import signal

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

class FullyAutomatedJobApplicant:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.user_info = self.config["user_info"]
        self.attachments = self.config["attachments"]
        self.questions = self.config["questions"]
        self.settings = self.config["automation_settings"]
        self.login_credentials = self.config.get("login_credentials", {})
        self.completed_jobs = []
        self.failed_jobs = []
        self.processing_jobs = []
        logging.info("🚀 FULLY AUTOMATED Job Applicant loaded successfully.")

    def _load_config(self, config_path):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_file, 'r') as f:
            return json.load(f)

    async def run_fully_automated_batch(self, csv_file_path: str, max_concurrent_tabs: int = 10):
        """Fully automated batch processing with multi-tab support"""
        logging.info(f"🚀 Starting FULLY AUTOMATED batch processing: {csv_file_path}")
        
        try:
            with open(Path(csv_file_path), mode='r', encoding='utf-8') as csvfile:
                jobs_to_apply = list(csv.DictReader(csvfile))
        except FileNotFoundError:
            logging.critical(f"❌ jobs.csv not found: {csv_file_path}")
            return

        print(f"🎯 Found {len(jobs_to_apply)} jobs to process")
        print(f"📊 Processing {min(max_concurrent_tabs, len(jobs_to_apply))} jobs concurrently")
        
        async with async_playwright() as p:
            # Launch browser with optimized settings for speed
            browser = await p.chromium.launch(
                channel="chrome",
                headless=self.settings.get("headless", False),
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-first-run',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-background-networking',
                    '--disable-background-timer-throttling',
                    '--disable-renderer-backgrounding',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-client-side-phishing-detection',
                    '--disable-default-apps',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            # Process jobs in batches
            batch_size = max_concurrent_tabs
            for i in range(0, len(jobs_to_apply), batch_size):
                batch = jobs_to_apply[i:i + batch_size]
                
                print(f"\n{'='*100}")
                print(f"🔥 PROCESSING BATCH {(i//batch_size) + 1}: Jobs {i+1}-{min(i+batch_size, len(jobs_to_apply))}")
                print(f"{'='*100}")
                
                # Create tasks for concurrent processing
                tasks = []
                for job in batch:
                    task = self._process_single_job_fully_automated(browser, job)
                    tasks.append(task)
                
                # Run all jobs in this batch concurrently
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Show progress
                self._show_progress_dashboard()
                
                # Ask user if they want to continue with next batch
                if i + batch_size < len(jobs_to_apply):
                    print(f"\n🎯 Batch {(i//batch_size) + 1} completed!")
                    user_input = input("Press Enter to continue with next batch, or 'stop' to end: ")
                    if user_input.lower() in ['stop', 'quit', 'exit', 'q']:
                        break
            
            print(f"\n{'='*100}")
            print("🎉 FULLY AUTOMATED BATCH PROCESSING COMPLETED!")
            print(f"{'='*100}")
            self._show_final_dashboard()
            
            await browser.close()

    async def _process_single_job_fully_automated(self, browser: Browser, job_details: dict):
        """Process a single job with full automation"""
        company_name = job_details.get("company", job_details.get("url", "Unknown"))
        url = job_details.get("url", "").strip()
        
        if not url:
            logging.warning(f"⚠️  Skipping {company_name}: No URL provided")
            self.failed_jobs.append({"company": company_name, "url": url, "error": "No URL"})
            return

        job_id = f"{company_name}_{int(time.time())}"
        self.processing_jobs.append({"id": job_id, "company": company_name, "url": url})
        
        # Create new context and page for this job
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Set fast timeouts for speed
        page.set_default_timeout(5000)
        
        try:
            logging.info(f"🎯 [{company_name}] Starting fully automated processing...")
            
            # Step 1: Navigate to job page
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(1)  # Brief pause for page to stabilize
            
            # Step 2: Handle login if detected
            if await self._is_login_page(page):
                logging.info(f"🔐 [{company_name}] Login page detected - attempting automatic login")
                login_success = await self._auto_login(page, company_name)
                if not login_success:
                    raise Exception("Auto-login failed")
                await asyncio.sleep(2)  # Wait for redirect after login
            
            # Step 3: Navigate through application flow automatically
            await self._navigate_application_flow_fully_automated(page, company_name)
            
            # Step 4: Mark as completed and ready for review
            self.completed_jobs.append({
                "company": company_name,
                "url": url,
                "status": "Ready for Review",
                "completion_time": datetime.datetime.now().isoformat()
            })
            
            # Remove from processing
            self.processing_jobs = [j for j in self.processing_jobs if j["id"] != job_id]
            
            logging.info(f"✅ [{company_name}] FULLY AUTOMATED processing completed!")
            
        except Exception as e:
            logging.error(f"❌ [{company_name}] Failed: {e}")
            self.failed_jobs.append({
                "company": company_name,
                "url": url,
                "error": str(e),
                "failure_time": datetime.datetime.now().isoformat()
            })
            # Remove from processing
            self.processing_jobs = [j for j in self.processing_jobs if j["id"] != job_id]
        
        finally:
            await context.close()

    async def _navigate_application_flow_fully_automated(self, page: Page, company_name: str):
        """Navigate through the entire application flow automatically"""
        max_steps = 20  # Prevent infinite loops
        current_step = 1
        
        while current_step <= max_steps:
            logging.info(f"🔄 [{company_name}] Processing step {current_step}/{max_steps}")
            
            # Fill all forms on current page instantly
            await self._instant_fill_all_forms(page, company_name)
            
            # Look for navigation buttons (Next, Continue, Submit, etc.)
            next_action = await self._find_and_click_next_action(page, company_name)
            
            if next_action == "SUBMIT_READY":
                logging.info(f"🎯 [{company_name}] Application ready for submission!")
                break
            elif next_action == "NEXT_PAGE":
                logging.info(f"➡️ [{company_name}] Navigated to next page")
                await asyncio.sleep(1)  # Brief pause for page load
                current_step += 1
            elif next_action == "COMPLETED":
                logging.info(f"✅ [{company_name}] Application flow completed!")
                break
            else:
                logging.info(f"🏁 [{company_name}] No more actions found - application complete")
                break
        
        if current_step > max_steps:
            logging.warning(f"⚠️ [{company_name}] Reached maximum steps - may need manual review")

    async def _instant_fill_all_forms(self, page: Page, company_name: str):
        """Ultra-fast form filling - fills everything instantly"""
        logging.info(f"⚡ [{company_name}] INSTANT form filling...")
        
        # Fill text inputs with zero delay
        await self._instant_fill_text_inputs(page)
        
        # Handle questions and dropdowns instantly
        await self._instant_handle_questions(page)
        
        # Handle file uploads
        await self._instant_upload_files(page)
        
        logging.info(f"⚡ [{company_name}] INSTANT form filling completed!")

    async def _instant_fill_text_inputs(self, page: Page):
        """Fill all text inputs instantly with zero delay"""
        # Create tasks for all fields to fill simultaneously
        fill_tasks = []
        
        for key, value in self.user_info.items():
            if not value:
                continue
                
            # Ultra-fast selectors - most common patterns first
            selectors = [
                f"input[name*='{key}' i]",
                f"input[placeholder*='{key}' i]", 
                f"input[id*='{key}' i]",
                f"input[aria-label*='{key}' i]",
                f"input[data-automation-id*='{key}' i]",
                f"textarea[name*='{key}' i]",
                f"textarea[placeholder*='{key}' i]"
            ]
            
            # Add task for concurrent execution
            fill_tasks.append(self._instant_fill_field(page, selectors, value, key))
        
        # Execute all fills simultaneously for maximum speed
        await asyncio.gather(*fill_tasks, return_exceptions=True)

    async def _instant_fill_field(self, page: Page, selectors: list, value: str, field_name: str):
        """Fill a single field instantly"""
        for selector in selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    element = elements[0]
                    # Instant fill - no delays
                    await element.clear()
                    await element.fill(value)
                    return True
            except:
                continue
        return False

    async def _instant_handle_questions(self, page: Page):
        """Handle all questions and dropdowns instantly"""
        # Create tasks for all questions to process simultaneously
        question_tasks = []
        
        for question in self.questions:
            question_tasks.append(self._instant_handle_single_question(page, question))
        
        # Execute all questions simultaneously
        await asyncio.gather(*question_tasks, return_exceptions=True)

    async def _instant_handle_single_question(self, page: Page, question: dict):
        """Handle a single question instantly"""
        answer = question["answer"]
        
        for keyword in question["keywords"]:
            # Try all strategies instantly - no waiting
            strategies = [
                self._instant_dropdown(page, keyword, answer),
                self._instant_custom_dropdown(page, keyword, answer),
                self._instant_radio(page, keyword, answer),
                self._instant_checkbox(page, keyword, answer),
                self._instant_text_question(page, keyword, answer)
            ]
            
            # Try all strategies simultaneously for maximum speed
            results = await asyncio.gather(*strategies, return_exceptions=True)
            
            # If any strategy succeeded, we're done
            if any(r is True for r in results if not isinstance(r, Exception)):
                return True
        
        return False

    async def _instant_dropdown(self, page: Page, keyword: str, answer: str):
        """Instant dropdown selection"""
        selectors = [
            f"select[name*='{keyword}' i]",
            f"select[id*='{keyword}' i]",
            f"select[aria-label*='{keyword}' i]",
            f"select[data-automation-id*='{keyword}' i]"
        ]
        
        for selector in selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    select = elements[0]
                    # Try different selection methods instantly
                    try:
                        await select.select_option(label=answer)
                        return True
                    except:
                        try:
                            await select.select_option(value=answer)
                            return True
                        except:
                            # Quick partial match
                            options = await select.locator('option').all()
                            for option in options[:5]:  # Check only first 5 for speed
                                try:
                                    text = await option.inner_text()
                                    if answer.lower() in text.lower():
                                        await select.select_option(label=text)
                                        return True
                                except:
                                    continue
            except:
                continue
        return False

    async def _instant_custom_dropdown(self, page: Page, keyword: str, answer: str):
        """Instant custom dropdown handling"""
        trigger_selectors = [
            f"div[role='combobox'][aria-label*='{keyword}' i]",
            f"button[aria-label*='{keyword}' i]",
            f"div[data-automation-id*='{keyword}' i]",
            f"button[data-automation-id*='{keyword}' i]"
        ]
        
        for selector in trigger_selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    trigger = elements[0]
                    await trigger.click()
                    
                    # Minimal wait for dropdown to open
                    await asyncio.sleep(0.2)
                    
                    # Quick option selection
                    option_selectors = [
                        f"[role='option']:has-text('{answer}')",
                        f"li:has-text('{answer}')",
                        f"div:has-text('{answer}')",
                        f"button:has-text('{answer}')"
                    ]
                    
                    for option_selector in option_selectors:
                        try:
                            option_elements = await page.locator(option_selector).all()
                            if option_elements:
                                await option_elements[0].click()
                                return True
                        except:
                            continue
            except:
                continue
        return False

    async def _instant_radio(self, page: Page, keyword: str, answer: str):
        """Instant radio button selection"""
        selectors = [
            f"input[type='radio'][value*='{answer}' i]",
            f"input[type='radio'][data-automation-id*='{answer}' i]"
        ]
        
        for selector in selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    await elements[0].check()
                    return True
            except:
                continue
        return False

    async def _instant_checkbox(self, page: Page, keyword: str, answer: str):
        """Instant checkbox handling"""
        if answer.lower() not in ['yes', 'true', '1', 'agree', 'accept']:
            return False
            
        selectors = [
            f"input[type='checkbox'][name*='{keyword}' i]",
            f"input[type='checkbox'][id*='{keyword}' i]",
            f"input[type='checkbox'][data-automation-id*='{keyword}' i]"
        ]
        
        for selector in selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    await elements[0].check()
                    return True
            except:
                continue
        return False

    async def _instant_text_question(self, page: Page, keyword: str, answer: str):
        """Instant text input for questions"""
        selectors = [
            f"input[placeholder*='{keyword}' i]",
            f"textarea[placeholder*='{keyword}' i]",
            f"input[aria-label*='{keyword}' i]",
            f"textarea[aria-label*='{keyword}' i]"
        ]
        
        for selector in selectors:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    await elements[0].fill(answer)
                    return True
            except:
                continue
        return False

    async def _instant_upload_files(self, page: Page):
        """Instant file upload handling"""
        resume_path = self.attachments.get("resume")
        if not resume_path or not Path(resume_path).exists():
            return
            
        file_selectors = [
            'input[type="file"]',
            'input[accept*=".pdf"]'
        ]
        
        for selector in file_selectors:
            try:
                elements = await page.locator(selector).all()
                for element in elements:
                    try:
                        await element.set_input_files(resume_path)
                        return True
                    except:
                        continue
            except:
                continue
        return False

    async def _find_and_click_next_action(self, page: Page, company_name: str):
        """Find and click the next action button (Next, Continue, Submit, etc.)"""
        
        # Submit buttons (highest priority)
        submit_patterns = [
            "button:has-text('Submit Application')",
            "button:has-text('Submit')",
            "input[type='submit'][value*='Submit']",
            "button[data-automation-id*='submit']",
            "a:has-text('Submit Application')"
        ]
        
        for pattern in submit_patterns:
            try:
                elements = await page.locator(pattern).all()
                if elements:
                    # Found submit button - this is the final step
                    logging.info(f"🎯 [{company_name}] Found Submit button - ready for manual review")
                    return "SUBMIT_READY"
            except:
                continue
        
        # Next/Continue buttons (medium priority)
        next_patterns = [
            "button:has-text('Next')",
            "button:has-text('Continue')",
            "button:has-text('Proceed')",
            "button:has-text('Save and Continue')",
            "button[data-automation-id*='next']",
            "button[data-automation-id*='continue']",
            "a:has-text('Next')",
            "a:has-text('Continue')"
        ]
        
        for pattern in next_patterns:
            try:
                elements = await page.locator(pattern).all()
                if elements:
                    element = elements[0]
                    # Check if button is enabled
                    is_disabled = await element.get_attribute('disabled')
                    if not is_disabled:
                        await element.click()
                        logging.info(f"➡️ [{company_name}] Clicked: {pattern}")
                        return "NEXT_PAGE"
            except:
                continue
        
        # Apply/Start Application buttons (for initial pages)
        apply_patterns = [
            "button:has-text('Apply Now')",
            "button:has-text('Start Application')",
            "button:has-text('Apply')",
            "a:has-text('Apply Now')",
            "a:has-text('Start Application')"
        ]
        
        for pattern in apply_patterns:
            try:
                elements = await page.locator(pattern).all()
                if elements:
                    await elements[0].click()
                    logging.info(f"🚀 [{company_name}] Started application: {pattern}")
                    return "NEXT_PAGE"
            except:
                continue
        
        return "NO_ACTION"

    async def _is_login_page(self, page: Page):
        """Fast login page detection"""
        login_indicators = [
            "input[type='password']",
            "input[name*='password' i]",
            "input[id*='password' i]",
            "button:has-text('Sign In')",
            "button:has-text('Log In')",
            "button:has-text('Login')"
        ]
        
        for indicator in login_indicators:
            try:
                elements = await page.locator(indicator).all()
                if elements:
                    return True
            except:
                continue
        
        # Quick URL check
        url = page.url.lower()
        return any(pattern in url for pattern in ['login', 'signin', 'auth', 'sso'])

    async def _auto_login(self, page: Page, company_name: str):
        """Automatic login with provided credentials"""
        email = self.login_credentials.get("email", "")
        password = self.login_credentials.get("password", "")
        
        if not email or not password:
            logging.error(f"❌ [{company_name}] No login credentials provided")
            return False
        
        try:
            # Fill email/username
            email_selectors = [
                "input[type='email']",
                "input[name*='email' i]",
                "input[name*='username' i]",
                "input[id*='email' i]",
                "input[id*='username' i]",
                "input[placeholder*='email' i]",
                "input[placeholder*='username' i]"
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        await elements[0].fill(email)
                        email_filled = True
                        break
                except:
                    continue
            
            if not email_filled:
                logging.error(f"❌ [{company_name}] Could not find email field")
                return False
            
            # Fill password
            password_selectors = [
                "input[type='password']",
                "input[name*='password' i]",
                "input[id*='password' i]"
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        await elements[0].fill(password)
                        password_filled = True
                        break
                except:
                    continue
            
            if not password_filled:
                logging.error(f"❌ [{company_name}] Could not find password field")
                return False
            
            # Click login button
            login_buttons = [
                "button[type='submit']",
                "button:has-text('Sign In')",
                "button:has-text('Log In')",
                "button:has-text('Login')",
                "input[type='submit']"
            ]
            
            login_clicked = False
            for selector in login_buttons:
                try:
                    elements = await page.locator(selector).all()
                    if elements:
                        await elements[0].click()
                        login_clicked = True
                        break
                except:
                    continue
            
            if not login_clicked:
                logging.error(f"❌ [{company_name}] Could not find login button")
                return False
            
            # Wait for login to complete
            await asyncio.sleep(3)
            
            # Check if login was successful (no more password fields)
            password_elements = await page.locator("input[type='password']").all()
            if not password_elements:
                logging.info(f"✅ [{company_name}] Auto-login successful!")
                return True
            else:
                logging.error(f"❌ [{company_name}] Auto-login failed - still on login page")
                return False
                
        except Exception as e:
            logging.error(f"❌ [{company_name}] Auto-login error: {e}")
            return False

    def _show_progress_dashboard(self):
        """Show real-time progress dashboard"""
        print(f"\n{'='*60}")
        print("📊 REAL-TIME PROGRESS DASHBOARD")
        print(f"{'='*60}")
        print(f"✅ Completed: {len(self.completed_jobs)}")
        print(f"🔄 Processing: {len(self.processing_jobs)}")
        print(f"❌ Failed: {len(self.failed_jobs)}")
        print(f"{'='*60}")
        
        if self.completed_jobs:
            print("\n✅ COMPLETED JOBS:")
            for job in self.completed_jobs[-5:]:  # Show last 5
                print(f"   • {job['company']} - {job['status']}")
        
        if self.failed_jobs:
            print("\n❌ FAILED JOBS:")
            for job in self.failed_jobs[-3:]:  # Show last 3
                print(f"   • {job['company']} - {job['error']}")

    def _show_final_dashboard(self):
        """Show final completion dashboard"""
        total = len(self.completed_jobs) + len(self.failed_jobs)
        success_rate = (len(self.completed_jobs) / total * 100) if total > 0 else 0
        
        print(f"\n{'='*80}")
        print("🎉 FINAL AUTOMATION RESULTS")
        print(f"{'='*80}")
        print(f"📊 Total Jobs Processed: {total}")
        print(f"✅ Successfully Completed: {len(self.completed_jobs)}")
        print(f"❌ Failed: {len(self.failed_jobs)}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        print(f"{'='*80}")
        
        if self.completed_jobs:
            print("\n🎯 JOBS READY FOR MANUAL REVIEW AND SUBMISSION:")
            for i, job in enumerate(self.completed_jobs, 1):
                print(f"{i:2d}. {job['company']:<30} | {job['url']}")
        
        if self.failed_jobs:
            print("\n⚠️ FAILED JOBS (May need manual attention):")
            for i, job in enumerate(self.failed_jobs, 1):
                print(f"{i:2d}. {job['company']:<30} | Error: {job['error']}")
        
        print(f"\n{'='*80}")
        print("🚀 FULLY AUTOMATED PROCESSING COMPLETE!")
        print("👀 Please review completed applications and submit manually")
        print(f"{'='*80}")

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
                    jobs = []
        
        new_job = {
            "id": f"job-{int(datetime.datetime.now().timestamp())}",
            "company": job_details.get("company", job_details.get("url")),
            "url": job_details["url"],
            "status": "Automated - Ready for Review",
            "date": datetime.date.today().isoformat()
        }
        jobs.append(new_job)
        
        tracker_file.write_text(f"const jobData = {json.dumps(jobs, indent=2)};")


async def run_fully_automated_batch(csv_file_path: str, max_concurrent_tabs: int = 10):
    """Main function to run fully automated batch processing"""
    applicant = FullyAutomatedJobApplicant()
    await applicant.run_fully_automated_batch(csv_file_path, max_concurrent_tabs)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_jobs.csv> [max_concurrent_tabs]")
        print("Example: python main.py jobs.csv 15")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    max_tabs = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    print(f"🚀 Starting FULLY AUTOMATED Job Application System")
    print(f"📊 Max Concurrent Tabs: {max_tabs}")
    print(f"📁 Jobs File: {csv_path}")
    
    asyncio.run(run_fully_automated_batch(csv_path, max_tabs))