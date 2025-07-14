from celery import Celery
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import logging
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright, Page, TimeoutError, Browser, BrowserContext
import sys
import datetime
import re
import time
import os
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', stream=sys.stdout)

# Load environment
load_dotenv()

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/b2c_platform_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Celery app
from backend.celery_config import celery_app

# Import models (adjust path as needed)
sys.path.append('..')
from backend.models import User, Profile, Application, JobBoardCredential, TaskStatus

class B2CJobApplicant:
    def __init__(self, application_id: int):
        self.application_id = application_id
        self.db = SessionLocal()
        self.application = self.db.query(Application).filter(Application.id == application_id).first()
        if not self.application:
            raise ValueError(f"Application {application_id} not found")
        
        self.user = self.db.query(User).filter(User.id == self.application.user_id).first()
        self.profile = self.db.query(Profile).filter(Profile.user_id == self.user.id).first()
        
        if not self.profile:
            raise ValueError(f"Profile not found for user {self.user.id}")
        
        # Build user info config similar to the original config.json
        self.user_info = self._build_user_info()
        self.questions = self._build_questions_config()
        self.attachments = self._build_attachments()
        
        logging.info(f"🚀 B2C Job Applicant initialized for application {application_id}")

    def _build_user_info(self):
        return {
            "first_name": self.profile.first_name,
            "last_name": self.profile.last_name,
            "email": self.user.email,
            "phone": self.profile.phone or "",
            "address": self.profile.address or "",
            "city": self.profile.city or "",
            "state": self.profile.state or "",
            "zip_code": self.profile.zip_code or "",
            "linkedin": self.profile.linkedin or "",
            "portfolio": self.profile.portfolio or "",
            "salary": self.profile.salary_expectation or "",
            "cover_letter": self.profile.cover_letter or ""
        }

    def _build_questions_config(self):
        if self.profile.questions_config:
            return self.profile.questions_config
        
        # Default questions if none configured
        return [
            {"keywords": ["experience", "years", "work", "years of experience"], "answer": "5+ years"},
            {"keywords": ["authorized", "visa", "work authorization", "eligible", "legally authorized"], "answer": "Yes"},
            {"keywords": ["degree", "education", "qualification", "bachelor"], "answer": "Bachelor's Degree"},
            {"keywords": ["relocate", "relocation", "move", "willing to relocate"], "answer": "Yes"},
            {"keywords": ["salary", "compensation", "expected salary", "pay", "wage"], "answer": self.profile.salary_expectation or "120000"},
            {"keywords": ["start", "available", "notice", "when can you start", "availability"], "answer": "2 weeks"},
            {"keywords": ["remote", "work from home", "hybrid", "location"], "answer": "Yes"}
        ]

    def _build_attachments(self):
        return {
            "resume": f"uploads/resumes/{self.user.id}_{self.profile.resume_filename}" if self.profile.resume_filename else None,
            "cover_letter": f"uploads/cover_letters/{self.user.id}_{self.profile.cover_letter_filename}" if self.profile.cover_letter_filename else None
        }

    def _update_application_status(self, status: str, message: str = None, error_message: str = None):
        self.application.status = status
        if message:
            self.application.notes = message
        if error_message:
            self.application.error_message = error_message
        self.db.commit()

    def _create_task_status(self, status: str, message: str = None, screenshot_path: str = None):
        task_status = TaskStatus(
            task_id=self.application.task_id,
            application_id=self.application.id,
            status=status,
            message=message,
            screenshot_path=screenshot_path
        )
        self.db.add(task_status)
        self.db.commit()

    def _get_job_board_credentials(self, domain: str):
        credentials = self.db.query(JobBoardCredential).filter(
            JobBoardCredential.user_id == self.user.id,
            JobBoardCredential.domain == domain,
            JobBoardCredential.is_active == True
        ).first()
        return credentials

    async def process_application(self):
        """Main method to process a job application"""
        try:
            self._update_application_status("In Progress", "Starting application process")
            self._create_task_status("IN_PROGRESS", "Browser launched, navigating to job URL")
            
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)  # Keep visible for debugging
                context = await browser.new_context()
                page = await context.new_page()
                
                # Navigate to job URL
                await page.goto(self.application.job_url)
                await page.wait_for_load_state('networkidle')
                
                # Check if login is required
                if await self._is_login_page(page):
                    login_success = await self._handle_login(page)
                    if not login_success:
                        self._create_task_status("WAITING_FOR_CREDENTIALS", 
                                                f"Need credentials for {self.application.company}")
                        await browser.close()
                        return
                
                # Navigate through application flow
                await self._navigate_application_flow(page)
                
                # Fill all forms
                await self._fill_all_forms(page)
                
                # Take screenshot for review
                screenshot_path = f"uploads/screenshots/{self.application.id}_review.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Pause for manual review
                self._create_task_status("WAITING_FOR_REVIEW", 
                                        f"Application ready for review: {self.application.company} - {self.application.job_title}",
                                        screenshot_path)
                
                # Don't close browser - keep it open for manual review
                logging.info(f"⏸️ Application paused for manual review: {self.application.company}")
                
        except Exception as e:
            logging.error(f"❌ Error processing application {self.application.id}: {str(e)}")
            self._update_application_status("Failed", error_message=str(e))
            self._create_task_status("FAILED", f"Error: {str(e)}")

    async def _is_login_page(self, page: Page):
        """Check if current page is a login page"""
        login_indicators = [
            'input[type="password"]',
            'input[name*="password"]',
            'input[id*="password"]',
            'button[type="submit"]:has-text("Sign In")',
            'button:has-text("Log In")',
            'a:has-text("Sign In")',
            'a:has-text("Log In")'
        ]
        
        for indicator in login_indicators:
            if await page.locator(indicator).count() > 0:
                return True
        return False

    async def _handle_login(self, page: Page):
        """Handle login process"""
        # Extract domain from current URL
        domain = page.url.split('/')[2]
        
        # Check if we have credentials for this domain
        credentials = self._get_job_board_credentials(domain)
        
        if not credentials:
            logging.info(f"🔐 No credentials found for domain: {domain}")
            return False
        
        try:
            # Find email/username field
            email_selectors = [
                'input[type="email"]',
                'input[name*="email"]',
                'input[name*="username"]',
                'input[id*="email"]',
                'input[id*="username"]'
            ]
            
            email_field = None
            for selector in email_selectors:
                if await page.locator(selector).count() > 0:
                    email_field = page.locator(selector).first
                    break
            
            if email_field:
                await email_field.fill(credentials.email)
            
            # Find password field
            password_field = page.locator('input[type="password"]').first
            if await password_field.count() > 0:
                # Decrypt password (implement proper decryption)
                decrypted_password = credentials.encrypted_password  # TODO: Implement decryption
                await password_field.fill(decrypted_password)
            
            # Click login button
            login_buttons = [
                'button[type="submit"]',
                'button:has-text("Sign In")',
                'button:has-text("Log In")',
                'input[type="submit"]'
            ]
            
            for button_selector in login_buttons:
                if await page.locator(button_selector).count() > 0:
                    await page.locator(button_selector).first.click()
                    break
            
            # Wait for navigation
            await page.wait_for_load_state('networkidle')
            
            # Update last used timestamp
            credentials.last_used = datetime.datetime.utcnow()
            self.db.commit()
            
            logging.info(f"✅ Successfully logged in to {domain}")
            return True
            
        except Exception as e:
            logging.error(f"❌ Login failed for {domain}: {str(e)}")
            return False

    async def _navigate_application_flow(self, page: Page):
        """Navigate through application flow similar to original implementation"""
        max_clicks = 10
        clicks = 0
        
        while clicks < max_clicks:
            # Look for "Apply" or "Apply Now" buttons first
            apply_buttons = [
                'button:has-text("Apply")',
                'a:has-text("Apply")',
                'button:has-text("Apply Now")',
                'a:has-text("Apply Now")',
                'input[value*="Apply"]'
            ]
            
            for button_selector in apply_buttons:
                if await page.locator(button_selector).count() > 0:
                    await page.locator(button_selector).first.click()
                    await page.wait_for_load_state('networkidle')
                    logging.info(f"🔘 Clicked Apply button")
                    return
            
            # Look for Next/Continue buttons
            next_buttons = [
                'button:has-text("Next")',
                'button:has-text("Continue")',
                'input[value*="Next"]',
                'input[value*="Continue"]'
            ]
            
            clicked = False
            for button_selector in next_buttons:
                if await page.locator(button_selector).count() > 0:
                    await page.locator(button_selector).first.click()
                    await page.wait_for_load_state('networkidle')
                    logging.info(f"🔘 Clicked Next/Continue button")
                    clicked = True
                    break
            
            if not clicked:
                break
            
            clicks += 1

    async def _fill_all_forms(self, page: Page):
        """Fill all forms on the page"""
        await self._fill_text_inputs(page)
        await self._handle_questions(page)
        await self._upload_files(page)

    async def _fill_text_inputs(self, page: Page):
        """Fill basic text input fields"""
        field_mappings = {
            "first_name": ["first", "fname", "firstName", "given"],
            "last_name": ["last", "lname", "lastName", "surname", "family"],
            "email": ["email", "mail"],
            "phone": ["phone", "telephone", "mobile"],
            "address": ["address", "street"],
            "city": ["city"],
            "state": ["state", "province"],
            "zip_code": ["zip", "postal", "zipcode"],
            "linkedin": ["linkedin"],
            "portfolio": ["portfolio", "website", "url"]
        }
        
        for field_name, keywords in field_mappings.items():
            value = self.user_info.get(field_name, "")
            if value:
                await self._fill_field_by_keywords(page, keywords, value, field_name)

    async def _fill_field_by_keywords(self, page: Page, keywords: list, value: str, field_name: str):
        """Fill a field by searching for keywords in name, id, or placeholder"""
        for keyword in keywords:
            selectors = [
                f'input[name*="{keyword}" i]',
                f'input[id*="{keyword}" i]',
                f'input[placeholder*="{keyword}" i]',
                f'textarea[name*="{keyword}" i]',
                f'textarea[id*="{keyword}" i]',
                f'textarea[placeholder*="{keyword}" i]'
            ]
            
            for selector in selectors:
                elements = page.locator(selector)
                if await elements.count() > 0:
                    try:
                        await elements.first.fill(value)
                        logging.info(f"✅ Filled {field_name}: {value}")
                        return
                    except Exception as e:
                        logging.debug(f"Failed to fill {field_name} with selector {selector}: {e}")
                        continue

    async def _handle_questions(self, page: Page):
        """Handle dynamic questions like dropdowns, radio buttons, etc."""
        for question in self.questions:
            keywords = question["keywords"]
            answer = question["answer"]
            
            for keyword in keywords:
                # Try dropdown
                await self._handle_dropdown(page, keyword, answer)
                # Try radio buttons
                await self._handle_radio(page, keyword, answer)
                # Try checkboxes
                await self._handle_checkbox(page, keyword, answer)
                # Try text inputs
                await self._handle_text_question(page, keyword, answer)

    async def _handle_dropdown(self, page: Page, keyword: str, answer: str):
        """Handle dropdown selections"""
        dropdown_selectors = [
            f'select:has(option:text-matches("{keyword}", "i"))',
            f'select[name*="{keyword}" i]',
            f'select[id*="{keyword}" i]'
        ]
        
        for selector in dropdown_selectors:
            if await page.locator(selector).count() > 0:
                try:
                    await page.locator(selector).first.select_option(label=answer)
                    logging.info(f"✅ Selected dropdown {keyword}: {answer}")
                    return
                except:
                    continue

    async def _handle_radio(self, page: Page, keyword: str, answer: str):
        """Handle radio button selections"""
        # Find radio buttons related to the keyword
        radio_containers = page.locator(f'*:has-text("{keyword}"):has(input[type="radio"])')
        
        if await radio_containers.count() > 0:
            # Look for radio button with matching answer
            radio_with_answer = radio_containers.locator(f'input[type="radio"]:near(text="{answer}")')
            if await radio_with_answer.count() > 0:
                try:
                    await radio_with_answer.first.check()
                    logging.info(f"✅ Selected radio {keyword}: {answer}")
                    return
                except:
                    pass

    async def _handle_checkbox(self, page: Page, keyword: str, answer: str):
        """Handle checkbox selections"""
        if answer.lower() in ['yes', 'true', '1']:
            checkbox_selectors = [
                f'input[type="checkbox"][name*="{keyword}" i]',
                f'input[type="checkbox"][id*="{keyword}" i]'
            ]
            
            for selector in checkbox_selectors:
                if await page.locator(selector).count() > 0:
                    try:
                        await page.locator(selector).first.check()
                        logging.info(f"✅ Checked checkbox {keyword}")
                        return
                    except:
                        continue

    async def _handle_text_question(self, page: Page, keyword: str, answer: str):
        """Handle text input questions"""
        text_selectors = [
            f'input[type="text"][placeholder*="{keyword}" i]',
            f'textarea[placeholder*="{keyword}" i]',
            f'input[name*="{keyword}" i]',
            f'textarea[name*="{keyword}" i]'
        ]
        
        for selector in text_selectors:
            if await page.locator(selector).count() > 0:
                try:
                    await page.locator(selector).first.fill(answer)
                    logging.info(f"✅ Filled text question {keyword}: {answer}")
                    return
                except:
                    continue

    async def _upload_files(self, page: Page):
        """Upload resume and cover letter files"""
        file_inputs = page.locator('input[type="file"]')
        file_count = await file_inputs.count()
        
        if file_count > 0 and self.attachments["resume"]:
            try:
                # Upload resume to first file input
                await file_inputs.first.set_input_files(self.attachments["resume"])
                logging.info(f"✅ Uploaded resume: {self.attachments['resume']}")
                
                # If there's a second file input and we have a cover letter, upload it
                if file_count > 1 and self.attachments["cover_letter"]:
                    await file_inputs.nth(1).set_input_files(self.attachments["cover_letter"])
                    logging.info(f"✅ Uploaded cover letter: {self.attachments['cover_letter']}")
                    
            except Exception as e:
                logging.error(f"❌ File upload failed: {str(e)}")

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()

# Celery Tasks
@celery_app.task(bind=True)
def apply_to_job(self, application_id: int):
    """Main task to process a job application"""
    try:
        applicant = B2CJobApplicant(application_id)
        
        # Run the async process
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(applicant.process_application())
        loop.close()
        
        return {"status": "completed", "application_id": application_id}
        
    except Exception as e:
        logging.error(f"Task failed for application {application_id}: {str(e)}")
        return {"status": "failed", "application_id": application_id, "error": str(e)}

@celery_app.task
def resume_application_task(application_id: int):
    """Resume a paused application task"""
    try:
        # This would be called when admin clicks "Resume Task"
        applicant = B2CJobApplicant(application_id)
        applicant._update_application_status("In Progress", "Task resumed by admin")
        
        # Here you could implement logic to resume from where it left off
        return {"status": "resumed", "application_id": application_id}
        
    except Exception as e:
        logging.error(f"Resume task failed for application {application_id}: {str(e)}")
        return {"status": "failed", "application_id": application_id, "error": str(e)}