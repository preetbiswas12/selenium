import logging
import time
import os
from browser_driver import BrowserDriver
from email_handler import EmailOTPHandler, ManualOTPHandler
from sheets_handler import SheetsHandler
from captcha_handler import CaptchaHandler
from config import FORM_SELECTORS, SELENIUM_CONFIG, URLS, SHEET_CONFIG, CAPTCHA_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Hack2skillAutomation:
    """Main automation controller"""
    
    def __init__(self, sheets_credentials_path=None, use_tor=True):
        self.browser = BrowserDriver(
            headless=SELENIUM_CONFIG["headless"],
            use_tor=use_tor
        )
        self.sheets_handler = None
        self.otp_handler = None
        
        if sheets_credentials_path and os.path.exists(sheets_credentials_path):
            try:
                self.sheets_handler = SheetsHandler(sheets_credentials_path)
            except Exception as e:
                logger.error(f"Failed to setup sheets: {e}")
    
    def signup(self, name, email, password=None):
        """
        Step 1: Signup with name and email
        Step 2: Verify OTP
        """
        try:
            logger.info(f"Starting signup for: {email}")
            
            # Step 1: Fill name and email
            logger.info("Step 1: Filling signup form...")
            name_field = self.browser.find_element(FORM_SELECTORS["name_input"])
            email_field = self.browser.find_element(FORM_SELECTORS["email_input"])
            
            if name_field and email_field:
                self.browser.type_text(name_field, name)
                self.browser.type_text(email_field, email)
                
                # Click Register Now button
                register_btn = self.browser.find_element(FORM_SELECTORS["register_now_btn"])
                if register_btn:
                    self.browser.click(register_btn)
                    self.browser.random_delay(3, 5)
                else:
                    logger.error("Register Now button not found")
                    return False
            
            # Step 2: OTP verification
            logger.info("Step 2: Waiting for OTP...")
            otp = self._get_otp(email)
            
            if otp:
                otp_field = self.browser.find_element(FORM_SELECTORS["otp_input"])
                if otp_field:
                    self.browser.type_text(otp_field, otp)
                    
                    # Click Signup button
                    signup_btn = self.browser.find_element(FORM_SELECTORS["signup_btn"])
                    if signup_btn:
                        self.browser.click(signup_btn)
                        self.browser.random_delay(3, 5)
                        logger.info(f"✅ Signup successful for: {email}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Signup failed: {e}")
            return False
    
    def fill_registration_form(self, form_data):
        """
        Step 3: Fill comprehensive Hack2skill registration form
        
        form_data dict should contain:
        - full_name
        - email
        - whatsapp_number
        - date_of_birth (dd.mm.yyyy)
        - gender
        - alternate_number
        - country
        - state_province
        - city
        - occupation
        - college_name
        - college_country
        - college_state
        - college_city
        - degree
        - specialization
        - passout_year
        - linkedin_url
        - college_id_path (file)
        - gdp_profile_link
        - referral_answer (yes/no)
        - referral_code (if yes)
        """
        try:
            logger.info("Step 3: Filling registration form...")
            
            # Personal Information
            self._fill_text_field("full_name", form_data.get("full_name", ""))
            self._fill_text_field("email", form_data.get("email", ""))
            self._fill_text_field("whatsapp_number", form_data.get("whatsapp_number", ""))
            self._fill_date_field("date_of_birth", form_data.get("date_of_birth", ""))
            self._fill_dropdown("gender", form_data.get("gender", ""))
            self._fill_text_field("alternate_number", form_data.get("alternate_number", ""))
            self._fill_dropdown("country", form_data.get("country", "India"))
            self._fill_text_field("state_province", form_data.get("state_province", ""))
            self._fill_text_field("city", form_data.get("city", ""))
            
            self.browser.random_delay(1, 2)
            
            # Education Information
            self._fill_dropdown("occupation", form_data.get("occupation", ""))
            self._fill_text_field("college_name", form_data.get("college_name", ""))
            self._fill_dropdown("college_country", form_data.get("college_country", "India"))
            self._fill_text_field("college_state", form_data.get("college_state", ""))
            self._fill_text_field("college_city", form_data.get("college_city", ""))
            self._fill_text_field("degree", form_data.get("degree", ""))
            self._fill_text_field("specialization", form_data.get("specialization", ""))
            self._fill_dropdown("passout_year", form_data.get("passout_year", ""))
            
            self.browser.random_delay(1, 2)
            
            # Profile & Links
            self._fill_text_field("linkedin_url", form_data.get("linkedin_url", ""))
            self._fill_text_field("gdp_profile_link", form_data.get("gdp_profile_link", ""))
            
            # File Upload
            college_id_path = form_data.get("college_id_path")
            if college_id_path and os.path.exists(college_id_path):
                self._upload_file("college_id_file", college_id_path)
            
            self.browser.random_delay(1, 2)
            
            # Referral Handling (IMPORTANT: Yes is pre-selected, handle with care)
            referral_answer = form_data.get("referral_answer", "no").lower()
            
            if referral_answer == "yes" or referral_answer == "y":
                # "Yes" is already selected by default, just fill the code
                self._fill_text_field("referral_code_input", form_data.get("referral_code", ""))
                logger.info("Referral: Yes (code provided)")
            else:
                # Need to click "No" radio button
                self._click_radio_button("referral_no_radio")
                logger.info("Referral: No (radio button clicked)")
            
            self.browser.random_delay(1, 2)
            
            # Terms & Consent Checkboxes
            self._check_checkbox("terms_checkbox")
            self._check_checkbox("consent_checkbox")
            
            self.browser.random_delay(2, 4)
            
            # Check for CAPTCHA before submitting
            if self._handle_captcha_if_present():
                logger.info("CAPTCHA handled, proceeding with submission")
            
            # Submit Form
            submit_btn = self.browser.find_element(FORM_SELECTORS["register_btn"])
            if submit_btn:
                self.browser.click(submit_btn)
                self.browser.random_delay(3, 5)
                logger.info("✅ Registration form submitted")
                return True
            else:
                logger.error("Register button not found")
                return False
            
        except Exception as e:
            logger.error(f"Form filling failed: {e}")
            self.browser.screenshot(f"form_error_{int(time.time())}.png")
            return False
    
    def _fill_text_field(self, field_key, value):
        """Fill text input field"""
        if not value:
            return
        
        try:
            field = self.browser.find_element(FORM_SELECTORS.get(field_key))
            if field:
                self.browser.type_text(field, str(value))
                logger.debug(f"Filled {field_key}")
        except Exception as e:
            logger.warning(f"Failed to fill {field_key}: {e}")
    
    def _fill_date_field(self, field_key, date_str):
        """Fill date field (dd.mm.yyyy format)"""
        if not date_str:
            return
        
        try:
            field = self.browser.find_element(FORM_SELECTORS.get(field_key))
            if field:
                # Try to fill directly
                field.send_keys(date_str)
                logger.debug(f"Filled {field_key} with {date_str}")
        except Exception as e:
            logger.warning(f"Failed to fill date {field_key}: {e}")
    
    def _fill_dropdown(self, field_key, value):
        """Select from dropdown"""
        if not value:
            return
        
        try:
            element = self.browser.find_element(FORM_SELECTORS.get(field_key))
            if element:
                self.browser.select_dropdown(element, str(value))
                logger.debug(f"Selected {field_key}: {value}")
        except Exception as e:
            logger.warning(f"Failed to select {field_key}: {e}")
    
    def _upload_file(self, field_key, file_path):
        """Upload file"""
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return
        
        try:
            file_input = self.browser.find_element(FORM_SELECTORS.get(field_key))
            if file_input:
                self.browser.upload_file(file_input, os.path.abspath(file_path))
                logger.info(f"Uploaded file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to upload file: {e}")
    
    def _click_radio_button(self, radio_key):
        """Click radio button"""
        try:
            radio = self.browser.find_element(FORM_SELECTORS.get(radio_key))
            if radio:
                self.browser.click(radio)
                logger.debug(f"Clicked radio button: {radio_key}")
        except Exception as e:
            logger.warning(f"Failed to click radio button {radio_key}: {e}")
    
    def _check_checkbox(self, checkbox_key):
        """Check checkbox"""
        try:
            checkbox = self.browser.find_element(FORM_SELECTORS.get(checkbox_key))
            if checkbox and not checkbox.is_selected():
                self.browser.click(checkbox)
                logger.debug(f"Checked checkbox: {checkbox_key}")
        except Exception as e:
            logger.warning(f"Failed to check checkbox {checkbox_key}: {e}")
    
    def _handle_captcha_if_present(self):
        """Detect and handle CAPTCHA if present"""
        try:
            # Check for common CAPTCHA indicators
            captcha_selectors = [
                "div[class*='recaptcha']",
                "iframe[src*='recaptcha']",
                "div[id*='captcha']",
            ]
            
            for selector in captcha_selectors:
                try:
                    element = self.browser.driver.find_elements("css selector", selector)
                    if element:
                        logger.warning("🔴 CAPTCHA detected!")
                        captcha_handler = CaptchaHandler(CAPTCHA_CONFIG["method"])
                        return captcha_handler.handle_captcha(self.browser.driver)
                except:
                    pass
            
            logger.info("No CAPTCHA detected")
            return True
            
        except Exception as e:
            logger.warning(f"CAPTCHA check failed: {e}")
            return True  # Continue anyway
    
    def _get_otp(self, email_address):
        """Get OTP - auto-fetch or manual"""
        try:
            # Try auto-fetch first
            if self.otp_handler is None:
                password = input(f"Enter password for {email_address}: ")
                self.otp_handler = EmailOTPHandler(email_address, password)
                if self.otp_handler.connect():
                    return self.otp_handler.get_latest_otp()
            
            # Fallback to manual
            logger.warning("Using manual OTP input")
            return ManualOTPHandler.get_otp()
            
        except Exception as e:
            logger.error(f"OTP retrieval failed: {e}")
            return ManualOTPHandler.get_otp()
    
    def process_sheet(self, sheet_name_or_id, worksheet_name="Sheet1", skip_done=True):
        """
        Process all registrations from Google Sheet
        """
        if not self.sheets_handler:
            logger.error("Sheets handler not configured")
            return
        
        try:
            spreadsheet = self.sheets_handler.get_sheet(sheet_name_or_id)
            
            # Get records
            if skip_done:
                records = self.sheets_handler.get_pending_records(spreadsheet, 0, "Status")
            else:
                records = self.sheets_handler.get_all_records(spreadsheet, 0)
            
            logger.info(f"Processing {len(records)} registrations...")
            
            for idx, record in enumerate(records, 1):
                logger.info(f"\n{'='*60}")
                logger.info(f"Registration {idx}/{len(records)}")
                logger.info(f"{'='*60}")
                
                try:
                    # Navigate to registration page
                    self.browser.get(URLS["registration"])
                    
                    # Signup
                    name = record.get("Name", "")
                    email = record.get("Email", "")
                    password = record.get("Password", "")
                    
                    if not name or not email:
                        logger.warning(f"Missing name or email in row {idx}")
                        continue
                    
                    if self.signup(name, email, password):
                        # Fill registration form
                        form_data = {
                            # Personal Information
                            "full_name": record.get("FullName", name),
                            "email": record.get("Email", email),
                            "whatsapp_number": record.get("WhatsappNumber", ""),
                            "date_of_birth": record.get("DateOfBirth", ""),
                            "gender": record.get("Gender", ""),
                            "alternate_number": record.get("AlternateNumber", ""),
                            "country": record.get("Country", "India"),
                            "state_province": record.get("StateProvince", ""),
                            "city": record.get("City", ""),
                            
                            # Education
                            "occupation": record.get("Occupation", "College Student"),
                            "college_name": record.get("CollegeName", ""),
                            "college_country": record.get("CollegeCountry", "India"),
                            "college_state": record.get("CollegeState", ""),
                            "college_city": record.get("CollegeCity", ""),
                            "degree": record.get("Degree", ""),
                            "specialization": record.get("Specialization", ""),
                            "passout_year": record.get("PassoutYear", ""),
                            
                            # Profile & Documents
                            "linkedin_url": record.get("LinkedinURL", ""),
                            "college_id_path": record.get("CollegeIDPath", ""),
                            "gdp_profile_link": record.get("GDPProfileLink", ""),
                            
                            # Referral
                            "referral_answer": record.get("ReferralAnswer", "no"),
                            "referral_code": record.get("ReferralCode", ""),
                        }
                        
                        if self.fill_registration_form(form_data):
                            # Update sheet: mark as Done
                            self.sheets_handler.update_status(spreadsheet, idx - 1, "Done")
                            logger.info(f"✅ Completed registration {idx}")
                        else:
                            self.sheets_handler.update_status(spreadsheet, idx - 1, "Form Failed")
                    else:
                        self.sheets_handler.update_status(spreadsheet, idx - 1, "Signup Failed")
                    
                    # Delay between registrations
                    self.browser.random_delay(5, 10)
                    
                except Exception as e:
                    logger.error(f"Error processing row {idx}: {e}")
                    try:
                        self.sheets_handler.update_status(spreadsheet, idx - 1, f"Error: {str(e)[:20]}")
                    except:
                        pass
                    continue
            
            logger.info("\n✅ All registrations processed!")
            
        except Exception as e:
            logger.error(f"Sheet processing failed: {e}")
        finally:
            self.browser.close()
    
    def run_single(self, name, email, password, form_data):
        """Run single registration (for testing)"""
        try:
            self.browser.initialize()
            self.browser.get(URLS["registration"])
            
            if self.signup(name, email, password):
                self.fill_registration_form(form_data)
            
        finally:
            self.browser.close()


if __name__ == "__main__":
    # Example usage
    
    # Option 1: Process from Google Sheet
    credentials_file = "path/to/credentials.json"
    sheet_name = "Hack2skill_Registrations"
    
    automation = Hack2skillAutomation(credentials_file)
    automation.process_sheet(sheet_name)
    
    # Option 2: Single registration for testing
    # automation = Hack2skillAutomation()
    # automation.browser.initialize()
    # automation.run_single(
    #     name="Test User",
    #     email="test@cock.li",
    #     password="password123",
    #     form_data={
    #         # Personal Information
    #         "full_name": "Test User",
    #         "email": "test@cock.li",
    #         "whatsapp_number": "+911234567890",
    #         "date_of_birth": "01.01.2000",
    #         "gender": "Male",
    #         "alternate_number": "+911234567890",
    #         "country": "India",
    #         "state_province": "Maharashtra",
    #         "city": "Mumbai",
    #         
    #         # Education
    #         "occupation": "College Student",
    #         "college_name": "Test University",
    #         "college_country": "India",
    #         "college_state": "Maharashtra",
    #         "college_city": "Mumbai",
    #         "degree": "B.Tech",
    #         "specialization": "Computer Science",
    #         "passout_year": "2026",
    #         
    #         # Profile & Documents
    #         "linkedin_url": "https://linkedin.com/in/testuser",
    #         "college_id_path": "C:\\Users\\preet\\Downloads\\selenium\\images\\id.jpg",
    #         "gdp_profile_link": "https://g.dev/testuser",
    #         
    #         # Referral (Important: "Yes" is pre-selected by default)
    #         "referral_answer": "no",  # or "yes"
    #         "referral_code": "",  # Only needed if referral_answer is "yes"
    #     }
    # )
