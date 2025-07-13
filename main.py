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

class EnhancedUniversalApplicant:
    def __init__(self, config_path="config.json"):
        self.config = self._load_config(config_path)
        self.user_info = self.config["user_info"]
        self.attachments = self.config["attachments"]
        self.questions = self.config["questions"]
        self.settings = self.config["automation_settings"]
        logging.info("Enhanced configuration loaded successfully.")

    def _load_config(self, config_path):
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        with open(config_file, 'r') as f:
            return json.load(f)

    async def apply(self, page: Page, job_details: dict):
        company_name = job_details.get("company", job_details.get("url"))
        logging.info(f"Starting enhanced application process for {company_name}.")
        
        # Wait for page to fully load
        await self._wait_for_page_load(page)
        
        # Fill in order: text inputs, dropdowns, checkboxes, then upload files
        await self._fill_text_inputs(page)
        await self._handle_all_form_elements(page)
        await self._upload_attachments(page)
        
        self._update_tracker(job_details)
        logging.info(f"Enhanced automated tasks for {company_name} are complete.")

    async def _wait_for_page_load(self, page: Page):
        """Wait for page to be fully loaded and interactive"""
        try:
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_load_state('networkidle', timeout=10000)
            await asyncio.sleep(2)  # Additional wait for dynamic content
        except TimeoutError:
            logging.info("Page load timeout - proceeding anyway")

    async def _fill_text_inputs(self, page: Page):
        """Enhanced text input filling with better selectors and retry logic"""
        logging.info("Filling text inputs with enhanced detection.")
        
        # Extended mapping for better field detection
        field_mappings = {
            'first_name': ['first', 'fname', 'firstname', 'given', 'name'],
            'last_name': ['last', 'lname', 'lastname', 'surname', 'family'],
            'email': ['email', 'mail', 'e-mail'],
            'phone': ['phone', 'tel', 'telephone', 'mobile', 'number'],
            'address': ['address', 'street', 'location'],
            'city': ['city', 'town'],
            'state': ['state', 'province', 'region'],
            'zip_code': ['zip', 'postal', 'postcode'],
            'linkedin': ['linkedin', 'profile'],
            'portfolio': ['portfolio', 'website', 'site'],
            'cover_letter': ['cover', 'letter', 'motivation'],
            'salary': ['salary', 'compensation', 'expected', 'wage']
        }
        
        for field_key, value in self.user_info.items():
            if not value: 
                continue
                
            # Get all possible keywords for this field
            keywords = field_mappings.get(field_key, [field_key])
            
            for keyword in keywords:
                if await self._try_fill_text_field(page, keyword, value):
                    break
            else:
                logging.debug(f"Could not find text input for: {field_key}")

    async def _try_fill_text_field(self, page: Page, keyword: str, value: str) -> bool:
        """Try to fill a text field using multiple selector strategies"""
        selectors = [
            f"input[name*='{keyword}' i]",
            f"input[id*='{keyword}' i]",
            f"input[placeholder*='{keyword}' i]",
            f"input[aria-label*='{keyword}' i]",
            f"input[data-testid*='{keyword}' i]",
            f"textarea[name*='{keyword}' i]",
            f"textarea[placeholder*='{keyword}' i]",
            f"[contenteditable='true'][aria-label*='{keyword}' i]"
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    await element.click(timeout=3000)
                    await element.fill(value, timeout=3000)
                    logging.info(f"SUCCESS: Filled '{keyword}' with '{value}'")
                    return True
            except TimeoutError:
                continue
        return False

    async def _handle_all_form_elements(self, page: Page):
        """Enhanced form element handling including dropdowns, checkboxes, and radio buttons"""
        logging.info("Handling all form elements with enhanced detection.")
        
        for question in self.questions:
            await self._handle_single_question(page, question)

    async def _handle_single_question(self, page: Page, question: dict):
        """Handle a single question with multiple strategies"""
        answer = question["answer"]
        keywords = question["keywords"]
        
        for keyword in keywords:
            # Try multiple strategies in order
            strategies = [
                self._handle_native_dropdown,
                self._handle_custom_dropdown,
                self._handle_radio_buttons,
                self._handle_checkboxes,
                self._handle_text_input_question
            ]
            
            for strategy in strategies:
                try:
                    if await strategy(page, keyword, answer):
                        logging.info(f"SUCCESS: Handled '{keyword}' with '{answer}' using {strategy.__name__}")
                        return True
                except Exception as e:
                    logging.debug(f"Strategy {strategy.__name__} failed for '{keyword}': {e}")
                    continue
        
        logging.warning(f"Could not handle question with keywords: {keywords}")
        return False

    async def _handle_native_dropdown(self, page: Page, keyword: str, answer: str) -> bool:
        """Handle traditional HTML select dropdowns"""
        selectors = [
            f"select[name*='{keyword}' i]",
            f"select[id*='{keyword}' i]",
            f"select[aria-label*='{keyword}' i]",
            f"label:has-text('{keyword}') + select",
            f"label:has-text('{keyword}') ~ select",
            f"div:has-text('{keyword}') select"
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    # Try different selection methods
                    try:
                        await element.select_option(label=answer, timeout=3000)
                        return True
                    except:
                        try:
                            await element.select_option(value=answer, timeout=3000)
                            return True
                        except:
                            # Find option by partial text match
                            options = await element.locator('option').all()
                            for option in options:
                                option_text = await option.inner_text()
                                if answer.lower() in option_text.lower():
                                    await element.select_option(label=option_text, timeout=3000)
                                    return True
            except TimeoutError:
                continue
        return False

    async def _handle_custom_dropdown(self, page: Page, keyword: str, answer: str) -> bool:
        """Handle modern custom dropdowns (div-based)"""
        # Common patterns for custom dropdowns
        dropdown_triggers = [
            f"div[role='combobox']:has-text('{keyword}')",
            f"button:has-text('{keyword}')",
            f"div[class*='dropdown']:has-text('{keyword}')",
            f"div[class*='select']:has-text('{keyword}')",
            f"div[data-testid*='{keyword}']",
            f"label:has-text('{keyword}') + div[role='combobox']",
            f"label:has-text('{keyword}') ~ div[role='combobox']"
        ]
        
        for trigger_selector in dropdown_triggers:
            try:
                trigger = page.locator(trigger_selector).first
                if await trigger.count() > 0:
                    # Click to open dropdown
                    await trigger.click(timeout=3000)
                    await asyncio.sleep(1)  # Wait for dropdown to open
                    
                    # Try to find and click the option
                    option_selectors = [
                        f"[role='option']:has-text('{answer}')",
                        f"li:has-text('{answer}')",
                        f"div[class*='option']:has-text('{answer}')",
                        f"button:has-text('{answer}')",
                        f"a:has-text('{answer}')"
                    ]
                    
                    for option_selector in option_selectors:
                        try:
                            option = page.locator(option_selector).first
                            if await option.count() > 0:
                                await option.click(timeout=3000)
                                return True
                        except:
                            continue
                    
                    # If exact match fails, try partial match
                    for option_selector in option_selectors:
                        try:
                            options = await page.locator(option_selector.split(':has-text')[0]).all()
                            for option in options:
                                option_text = await option.inner_text()
                                if answer.lower() in option_text.lower():
                                    await option.click(timeout=3000)
                                    return True
                        except:
                            continue
                            
            except TimeoutError:
                continue
        return False

    async def _handle_radio_buttons(self, page: Page, keyword: str, answer: str) -> bool:
        """Handle radio button groups"""
        try:
            # Find radio button by label
            radio_selectors = [
                f"input[type='radio'][value*='{answer}' i]",
                f"label:has-text('{answer}') input[type='radio']",
                f"input[type='radio'] + label:has-text('{answer}')"
            ]
            
            for selector in radio_selectors:
                try:
                    radio = page.locator(selector).first
                    if await radio.count() > 0:
                        await radio.check(timeout=3000)
                        return True
                except:
                    continue
            
            # Try fieldset approach
            fieldset = page.locator(f"fieldset:has(legend:text-matches('{keyword}', 'i'))")
            if await fieldset.count() > 0:
                radio = fieldset.get_by_label(answer, exact=False).first
                if await radio.count() > 0:
                    await radio.check(timeout=3000)
                    return True
                    
        except Exception:
            pass
        return False

    async def _handle_checkboxes(self, page: Page, keyword: str, answer: str) -> bool:
        """Handle checkboxes"""
        if answer.lower() in ['yes', 'true', '1', 'agree', 'accept']:
            selectors = [
                f"input[type='checkbox'][name*='{keyword}' i]",
                f"label:has-text('{keyword}') input[type='checkbox']",
                f"input[type='checkbox'] + label:has-text('{keyword}')"
            ]
            
            for selector in selectors:
                try:
                    checkbox = page.locator(selector).first
                    if await checkbox.count() > 0:
                        await checkbox.check(timeout=3000)
                        return True
                except:
                    continue
        return False

    async def _handle_text_input_question(self, page: Page, keyword: str, answer: str) -> bool:
        """Handle text inputs for questions"""
        selectors = [
            f"input[placeholder*='{keyword}' i]",
            f"textarea[placeholder*='{keyword}' i]",
            f"label:has-text('{keyword}') + input",
            f"label:has-text('{keyword}') + textarea"
        ]
        
        for selector in selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    await element.fill(answer, timeout=3000)
                    return True
            except:
                continue
        return False

    async def _upload_attachments(self, page: Page):
        """Enhanced file upload handling"""
        logging.info("Uploading attachments with enhanced detection.")
        
        resume_path = self.attachments.get("resume")
        cover_letter_path = self.attachments.get("cover_letter")
        
        # Handle resume upload
        if resume_path and Path(resume_path).exists():
            await self._upload_file(page, resume_path, "resume")
        
        # Handle cover letter upload
        if cover_letter_path and Path(cover_letter_path).exists():
            await self._upload_file(page, cover_letter_path, "cover")

    async def _upload_file(self, page: Page, file_path: str, file_type: str):
        """Upload a specific file with multiple strategies"""
        upload_selectors = [
            f'input[type="file"][accept*=".pdf"]',
            f'input[type="file"]',
            f'button:has-text("Upload {file_type.title()}")',
            f'button:has-text("Attach {file_type.title()}")',
            f'button:has-text("Browse")',
            f'button:has-text("Choose File")',
            f'[data-testid*="{file_type}"]',
            f'[aria-label*="{file_type}" i]'
        ]
        
        for selector in upload_selectors:
            try:
                element = page.locator(selector).first
                if await element.count() > 0:
                    # Check if it's a file input
                    if 'input[type="file"]' in selector:
                        await element.set_input_files(file_path)
                        logging.info(f"SUCCESS: Uploaded {file_type} directly via file input")
                        return True
                    else:
                        # Click button and handle file chooser
                        async with page.expect_file_chooser(timeout=5000) as fc_info:
                            await element.click()
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(file_path)
                        logging.info(f"SUCCESS: Uploaded {file_type} via file chooser")
                        return True
            except Exception as e:
                logging.debug(f"Upload strategy failed for {selector}: {e}")
                continue
        
        logging.warning(f"Could not upload {file_type}")
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


async def run_batch_mode(csv_file_path: str):
    """Enhanced batch mode with better error handling"""
    logging.info(f"Starting Enhanced Batch Mode from file: {csv_file_path}")
    try:
        with open(Path(csv_file_path), mode='r', encoding='utf-8') as csvfile:
            jobs_to_apply = list(csv.DictReader(csvfile))
    except FileNotFoundError:
        logging.critical(f"FATAL: jobs.csv file not found at {csv_file_path}")
        return

    applicant = EnhancedUniversalApplicant()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            channel="chrome",
            headless=applicant.settings.get("headless", False),
            slow_mo=applicant.settings.get("slow_mo", 100),
            args=['--disable-blink-features=AutomationControlled', '--no-first-run']
        )
        
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()
        page.set_default_timeout(applicant.settings.get("timeout", 30000))

        for i, job in enumerate(jobs_to_apply):
            url = job.get("url", "").strip()
            if not url:
                logging.warning(f"Skipping empty URL in row {i+2} of jobs.csv")
                continue

            company_name = job.get("company", url)
            print("\n" + "="*60)
            logging.info(f"--- Processing Job {i+1}/{len(jobs_to_apply)}: {company_name} ---")
            print(f"--- Processing Job {i+1}/{len(jobs_to_apply)}: {company_name} ---")
            
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await applicant.apply(page, job)
            except Exception as e:
                logging.error(f"CRITICAL ERROR processing {url}: {e}")
                print(f"ERROR: Failed to process {url}. Check logs. Moving to next job.")
                continue

            print("\n>>> ACTION REQUIRED <<<")
            print("The enhanced bot has executed its mission. Review the application, complete any remaining fields, and click submit.")
            user_input = input("Press Enter to continue to the next job, or type 'stop' to end: ")
            
            if user_input.lower() in ['stop', 'quit', 'exit', 'q']:
                logging.info("User stopped the batch process.")
                break
        
        logging.info("--- Enhanced batch mode finished ---")
        print("\n" + "="*60)
        print("Enhanced batch mode finished. Closing browser.")
        await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_jobs.csv>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    asyncio.run(run_batch_mode(csv_path))