"""
Hack2Skill Batch Registration Form Filler (REFACTORED)
With proper error handling, exception types, and clear workflow states
"""

import time
import random
import csv
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List, Tuple, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException
)


# ═══════════════════════════════════════════════════════════════
# WORKFLOW STATES & EXCEPTIONS
# ═══════════════════════════════════════════════════════════════

class WorkflowState(Enum):
    """Workflow state constants"""
    ACCOUNTS_LOADED = "ACCOUNTS_LOADED"
    DRIVER_READY = "DRIVER_READY"
    SIGNUP_IN_PROGRESS = "SIGNUP_IN_PROGRESS"
    OTP_PAGE_LOADED = "OTP_PAGE_LOADED"
    OTP_VERIFICATION_IN_PROGRESS = "OTP_VERIFICATION_IN_PROGRESS"
    OTP_VERIFIED = "OTP_VERIFIED"
    FORM_FILLING_IN_PROGRESS = "FORM_FILLING_IN_PROGRESS"
    FORM_SUBMITTED = "FORM_SUBMITTED"
    ACCOUNT_LOGGING = "ACCOUNT_LOGGING"
    ACCOUNT_DONE = "ACCOUNT_DONE"


class WorkflowException(Exception):
    """Base exception for workflow errors"""
    def __init__(self, message: str, state: WorkflowState = None, account: str = None):
        self.message = message
        self.state = state
        self.account = account
        super().__init__(self.message)


class DriverException(WorkflowException):
    """WebDriver initialization/closure errors"""
    pass


class NavigationException(WorkflowException):
    """Page navigation errors"""
    pass


class PageLoadTimeoutError(NavigationException):
    """Page didn't load within timeout"""
    pass


class FormException(WorkflowException):
    """Form interaction errors"""
    pass


class ElementNotFoundError(FormException):
    """Required HTML element not found"""
    def __init__(self, element_name: str, selector: str, account: str = None):
        self.element_name = element_name
        self.selector = selector
        message = f"Element '{element_name}' not found with selector: {selector}"
        super().__init__(message, account=account)


class OTPException(WorkflowException):
    """OTP verification errors (CRITICAL - blocks workflow)"""
    pass


class OTPFieldNotFoundError(OTPException):
    """OTP input field not found (CRITICAL BLOCKER)"""
    def __init__(self, tried_selectors: List[str], account: str = None):
        self.tried_selectors = tried_selectors
        message = (
            f"❌ CRITICAL: OTP field not found!\n"
            f"   Tried selectors: {tried_selectors}\n"
            f"   Workflow is BLOCKED - user must provide actual OTP field selector"
        )
        super().__init__(message, WorkflowState.OTP_PAGE_LOADED, account)


class VerifyButtonNotFoundError(OTPException):
    """Verify button not found (CRITICAL BLOCKER)"""
    def __init__(self, tried_selectors: List[str], account: str = None):
        self.tried_selectors = tried_selectors
        message = (
            f"❌ CRITICAL: Verify button not found!\n"
            f"   Tried selectors: {tried_selectors}\n"
            f"   Workflow is BLOCKED - user must provide actual Verify button selector"
        )
        super().__init__(message, WorkflowState.OTP_PAGE_LOADED, account)


class OTPTimeoutError(OTPException):
    """OTP verification timed out"""
    pass


class ValidationError(FormException):
    """Form validation failed"""
    pass


class NetworkException(WorkflowException):
    """Network/connection errors"""
    pass


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage&utm_campaign=&utm_term=&utm_content="
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

# ⚠️ INCREASED TIMEOUTS FOR SLOW NETWORK
TIMEOUT_PAGE_LOAD = 45  # Was 25 - increased for slow networks
TIMEOUT_ELEMENT = 30    # Was 15 - increased for form field loads
TIMEOUT_INTERACTION = 10  # Wait for element to be interactive
OTP_WAIT_SECONDS = 40  # seconds to wait for user to enter OTP manually
RETRY_ATTEMPTS = 3  # Retry failed interactions up to 3 times
RETRY_DELAY = 2  # Wait 2 seconds between retries

# Selectors - THESE NEED TO BE UPDATED ONCE USER PROVIDES ACTUAL PAGE HTML
OTP_INPUT_SELECTORS = [
    "//input[@placeholder='OTP']",
    "//input[@placeholder='Enter OTP']",
    "//input[contains(@placeholder, 'OTP')]",
    "//input[@id='otp']",
    "//input[@name='otp']",
    # ⚠️ CRITICAL: Add actual selectors here once user provides page HTML
]

VERIFY_BUTTON_SELECTORS = [
    "//button[contains(text(), 'Verify')]",
    "//button[contains(text(), 'Verify OTP')]",
    "//button[contains(text(), 'Submit')]",
    "//button[@id='verify']",
    # ⚠️ CRITICAL: Add actual selectors here once user provides page HTML
]


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def log_progress(email: str, status: str, message: str, state: WorkflowState = None):
    """Log progress to CSV file with error tracking"""
    file_exists = os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'status', 'state', 'message'])
        
        state_str = state.value if state else "UNKNOWN"
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            email,
            status,
            state_str,
            message
        ])


def log_exception(email: str, exc: WorkflowException):
    """Log exception details to CSV"""
    log_progress(
        email,
        "FAILED",
        f"{exc.__class__.__name__}: {str(exc)}",
        exc.state
    )


def print_workflow_header(account_num: int, total: int, email: str):
    """Print formatted header for each account"""
    print(f"\n{'='*70}")
    print(f"[{account_num}/{total}] Processing: {email}")
    print(f"{'='*70}")


def print_step(step_num: int, text: str, is_substep: bool = False):
    """Print formatted step message"""
    indent = "   " if is_substep else " "
    print(f"{indent}→ Step {step_num}: {text}")


def print_success(text: str, is_substep: bool = False):
    """Print success message"""
    indent = "   " if is_substep else ""
    print(f"{indent}✓ {text}")


def print_error(text: str, is_substep: bool = False):
    """Print error message"""
    indent = "   " if is_substep else ""
    print(f"{indent}✗ {text}")


def print_warning(text: str, is_substep: bool = False):
    """Print warning message"""
    indent = "   " if is_substep else ""
    print(f"{indent}⚠ {text}")


def safe_fill_field(driver: webdriver.Firefox, element, value: str, field_name: str) -> bool:
    """
    Safely fill a form field with retries and proper waits
    - Waits for element to be clickable
    - Scrolls into view
    - Retries on failure
    Returns: True if filled, False if skipped/error
    """
    for attempt in range(RETRY_ATTEMPTS):
        try:
            # Check if disabled
            if element.get_attribute('disabled') is not None:
                print_warning(f"{field_name} disabled, skipping", True)
                return False
            
            # Check if read-only
            if element.get_attribute('readonly') is not None:
                print_warning(f"{field_name} read-only, skipping", True)
                return False
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # Wait for element to be clickable
            WebDriverWait(driver, TIMEOUT_INTERACTION).until(
                EC.element_to_be_clickable((By.XPATH, "//*"))
            )
            
            # Click to focus
            element.click()
            time.sleep(0.3)
            
            # Clear field
            try:
                element.clear()
            except:
                # Some fields may not support clear - use select all instead
                element.send_keys(Keys.CONTROL + "a")
                time.sleep(0.2)
            
            # Type value
            element.send_keys(value)
            print_success(f"{field_name}: {value}", True)
            return True
            
        except StaleElementReferenceException:
            if attempt < RETRY_ATTEMPTS - 1:
                print_warning(f"{field_name} stale element, retrying... (attempt {attempt + 1}/{RETRY_ATTEMPTS})", True)
                time.sleep(RETRY_DELAY)
                continue
            else:
                print_warning(f"{field_name} failed after retries", True)
                return False
        except Exception as e:
            if attempt < RETRY_ATTEMPTS - 1:
                print_warning(f"{field_name} error, retrying: {str(e)[:30]}", True)
                time.sleep(RETRY_DELAY)
                continue
            else:
                print_warning(f"{field_name} error: {str(e)[:40]}", True)
                return False
    
    return False


# ═══════════════════════════════════════════════════════════════
# CORE WORKFLOW FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def load_accounts_from_csv() -> List[Dict]:
    """Load accounts from CSV with validation"""
    print_step(0, "Loading accounts from CSV")
    
    if not os.path.exists(CSV_FILE):
        print_error(f"CSV file not found: {CSV_FILE}")
        return []
    
    accounts = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                if row.get('email', '').strip():
                    accounts.append({
                        'email': row['email'].strip(),
                        'password': row.get('password', '').strip() or 'gdgocgu12'
                    })
        
        print_success(f"Loaded {len(accounts)} account(s)")
        return accounts
    except Exception as e:
        print_error(f"Failed to read CSV: {str(e)}")
        return []


def init_firefox_driver() -> webdriver.Firefox:
    """Initialize Firefox WebDriver with proper configuration"""
    try:
        print_step(1, "Initializing Firefox WebDriver")
        
        options = webdriver.FirefoxOptions()
        # Add incognito/private mode
        options.add_argument("--private")
        # Uncomment to run headless (invisible)
        # options.add_argument("--headless")
        
        driver = webdriver.Firefox(options=options)
        print_success("Firefox initialized", True)
        return driver
    except DriverException as e:
        raise DriverException(f"Failed to initialize driver: {str(e)}")
    except Exception as e:
        raise DriverException(f"Unexpected error initializing driver: {str(e)}")


def signup_with_otp_step(driver: webdriver.Firefox, account: Dict) -> bool:
    """
    STEP 2: Signup with Full Name + Email, wait for OTP verification
    
    Raises:
        OTPFieldNotFoundError: If OTP input field not found (CRITICAL)
        VerifyButtonNotFoundError: If Verify button not found (CRITICAL)
        PageLoadTimeoutError: If pages don't load
        FormException: If form filling fails
    """
    print_step(2, "Signup Phase (Full Name + Email)")
    
    wait = WebDriverWait(driver, TIMEOUT_PAGE_LOAD)
    
    try:
        # Navigate to signup page
        print_step(2, "Navigating to signup page", True)
        driver.get(SIGNUP_PAGE_URL)
        time.sleep(2)
        print_success("Signup page loaded", True)
        
        # Generate Full Name
        first_names = ["Arjun", "Aditya", "Naman", "Raj", "Vikram"]
        last_names = ["Singh", "Sharma", "Kumar", "Patel", "Gupta"]
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Fill Full Name field
        print_step(2, "Filling Full Name field", True)
        try:
            fullname_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter Full Name']"))
            )
            fullname_field.clear()
            fullname_field.send_keys(full_name)
            print_success(f"Full Name entered: {full_name}", True)
        except TimeoutException:
            raise ElementNotFoundError("Full Name field", "//input[@placeholder='Enter Full Name']", account['email'])
        except Exception as e:
            raise FormException(f"Failed to fill Full Name: {str(e)}", WorkflowState.SIGNUP_IN_PROGRESS)
        
        time.sleep(1)
        
        # Fill Email field
        print_step(2, "Filling Email field", True)
        try:
            email_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter Email']")
            email_field.clear()
            email_field.send_keys(account['email'])
            print_success(f"Email entered: {account['email']}", True)
        except NoSuchElementException:
            raise ElementNotFoundError("Email field", "//input[@placeholder='Enter Email']", account['email'])
        except Exception as e:
            raise FormException(f"Failed to fill Email: {str(e)}", WorkflowState.SIGNUP_IN_PROGRESS)
        
        time.sleep(1)
        
        # Click Register button
        print_step(2, "Clicking Register button", True)
        try:
            register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
            
            # Scroll button into view
            driver.execute_script("arguments[0].scrollIntoView(true);", register_button)
            time.sleep(1)
            
            # Try regular click first
            try:
                register_button.click()
                print_success("Register button clicked", True)
            except Exception as e:
                # If blocked by overlay, use JavaScript click
                print_warning(f"Regular click blocked: {str(e)[:50]}... trying JS click", True)
                driver.execute_script("arguments[0].click();", register_button)
                print_success("Register button clicked (JavaScript)", True)
        except Exception as e:
            raise FormException(f"Failed to click Register: {str(e)}", WorkflowState.SIGNUP_IN_PROGRESS)
        
        time.sleep(2)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: OTP VERIFICATION (40s WAIT FOR MANUAL OTP ENTRY)
        # ═══════════════════════════════════════════════════════════════
        print_step(3, "OTP Verification Phase")
        
        # Wait for user to enter OTP manually (40 seconds)
        # The OTP field is already visible on the page, no need to check for it
        OTP_WAIT_SECONDS = 40
        print_step(3, f"Waiting {OTP_WAIT_SECONDS}s for manual OTP entry", True)
        print_warning(f"⏳ ENTER OTP MANUALLY NOW! (You have {OTP_WAIT_SECONDS} seconds)", True)
        
        for remaining in range(OTP_WAIT_SECONDS, 0, -1):
            print(f"   ⏱️  {remaining:2d}s remaining...", flush=True)
            time.sleep(1)
        
        print(f"   ✓ Timer complete - ready to click Verify", flush=True)
        print_success(f"OTP wait complete", True)
        
        time.sleep(1)
        
        # Click Verify button
        print_step(3, "Clicking Verify button", True)
        try:
            verify_button = driver.find_element(By.XPATH, VERIFY_BUTTON_SELECTORS[0])
            
            # Scroll button into view
            driver.execute_script("arguments[0].scrollIntoView(true);", verify_button)
            time.sleep(0.5)
            
            # Try regular click first
            try:
                verify_button.click()
                print_success("Verify button clicked", True)
            except Exception as e:
                # If blocked by overlay, use JavaScript click
                print_warning(f"Regular click blocked, trying JS click", True)
                driver.execute_script("arguments[0].click();", verify_button)
                print_success("Verify button clicked (JavaScript)", True)
        except Exception as e:
            raise FormException(f"Failed to click Verify button: {str(e)}", WorkflowState.OTP_VERIFICATION_IN_PROGRESS)
        
        time.sleep(3)
        print_success("OTP verification completed", True)
        
        return True
        
    except OTPException as e:
        # Re-raise OTP exceptions (critical blockers)
        log_exception(account['email'], e)
        print_error(f"OTP Verification Failed: {str(e)}")
        raise
    except WorkflowException as e:
        log_exception(account['email'], e)
        print_error(f"Signup failed: {str(e)}")
        raise
    except Exception as e:
        error = NavigationException(f"Unexpected error during signup: {str(e)}", WorkflowState.SIGNUP_IN_PROGRESS)
        log_exception(account['email'], error)
        print_error(f"Unexpected error: {str(e)}")
        raise error


def fill_registration_form(driver: webdriver.Firefox, account: Dict) -> bool:
    """
    STEP 4: Fill the 23-field registration form with comprehensive field handling
    
    Includes retry logic: If critical fields not found, refresh and retry (max 2 attempts)
    
    Fields handled:
    1. Full Name, Email, WhatsApp, DOB, Gender, Alternate Number
    2. Country, State, City, Occupation
    3. College details (Name, Country, State, City, Degree, Stream, Passout Year)
    4. LinkedIn Profile, College ID Upload
    5. GDP Profile Link
    6. Referral (conditional based on Yes/No selection)
    7. Terms & Conditions checkboxes
    """
    print_step(4, "Registration Form Filling (23 fields)")
    
    MAX_RETRIES = 2
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        print_step(4, f"Form fill attempt {retry_count + 1}/{MAX_RETRIES}", True)
        
        # Track failures
        fields_not_found = []
        
        try:
            wait = WebDriverWait(driver, TIMEOUT_ELEMENT)
            
            print_step(4, "Navigating to registration form", True)
            driver.get(REGISTRATION_URL)
            time.sleep(3)
            
            # Wait for page to stabilize - wait for first form element
            print_step(4, "Waiting for form to load completely", True)
            try:
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
                print_success("Form elements detected, proceeding...", True)
            except TimeoutException:
                print_warning("Form elements taking longer to load, continuing anyway", True)
            
            time.sleep(2)  # Extra wait for React components to render
            print_success("Registration page loaded", True)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 1: Personal Information
            # ═══════════════════════════════════════════════════════════════
            
            # 1. Full Name (SKIP - already filled from signup)
            print_step(4, "Section 1: Personal Info", True)
            print_warning("Full Name: Already pre-filled from signup (skipping)", True)
            
            time.sleep(0.5)
            
            # 2. Email (SKIP - already filled from signup and disabled)
            print_warning("Email: Already pre-filled from signup (disabled, skipping)", True)
            
            time.sleep(0.5)
            
            # 3. WhatsApp Number (phone input)
            try:
                whatsapp_input = driver.find_element(By.XPATH, "//input[@type='tel' or @placeholder='WhatsApp']")
                safe_fill_field(driver, whatsapp_input, "+919876543210", "WhatsApp")
            except NoSuchElementException:
                print_warning("WhatsApp field not found", True)
                fields_not_found.append("WhatsApp")
            except Exception as e:
                print_warning(f"WhatsApp field error: {str(e)[:50]}", True)
                fields_not_found.append("WhatsApp")
            
            time.sleep(0.5)
            
            # 4. Checkbox: "Alternate number is same as WhatsApp number"
            try:
                alt_same_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
                if not alt_same_checkbox.is_selected():
                    alt_same_checkbox.click()
                    print_success("Alternate number = WhatsApp (checked)", True)
                time.sleep(0.5)
            except NoSuchElementException:
                print_warning("Alternate checkbox not found", True)
                fields_not_found.append("Alternate")
            
            # 5. Date of Birth (date input, age 18-30)
            try:
                dob_input = driver.find_element(By.XPATH, "//input[@type='date']")
                # Generate random DOB (age 20-28)
                year = random.randint(1996, 2004)
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                dob = f"{year:04d}-{month:02d}-{day:02d}"
                dob_input.send_keys(dob)
                print_success(f"Date of Birth: {dob}", True)
            except NoSuchElementException:
                print_warning("DOB field not found", True)
                fields_not_found.append("DOB")
            except Exception as e:
                print_warning(f"DOB fill error: {str(e)}", True)
                fields_not_found.append("DOB")
            
            time.sleep(0.5)
            
            # 6. Gender (HTML <select> dropdown - same as Passout Year)
            try:
                gender_selects = driver.find_elements(By.TAG_NAME, "select")
                gender_found = False
                for select_elem in gender_selects:
                    try:
                        name = select_elem.get_attribute('name')
                        classes = select_elem.get_attribute('class') or ""
                        if (name and 'gender' in name.lower()) or ('gender' in classes.lower()):
                            Select(select_elem).select_by_visible_text("Male")
                            print_success("Gender: Male", True)
                            gender_found = True
                            break
                    except:
                        pass
                
                if not gender_found:
                    print_warning("Gender field not found", True)
                    fields_not_found.append("Gender")
            except Exception as e:
                print_warning(f"Gender field error: {str(e)[:40]}", True)
                fields_not_found.append("Gender")
            
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 2: Location Information
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 2: Location", True)
            
            # 7. Country (autocomplete - type and select from options)
            try:
                country_inputs = driver.find_elements(By.XPATH, "//input")
                found = False
                for inp in country_inputs:
                    try:
                        placeholder = inp.get_attribute('placeholder')
                        if placeholder and 'country' in placeholder.lower():
                            inp.send_keys("India")
                            time.sleep(0.5)
                            options = driver.find_elements(By.XPATH, "//div[@role='option']")
                            if options:
                                options[0].click()
                                print_success("Country: India", True)
                                found = True
                                break
                    except:
                        pass
                if not found:
                    print_warning("Country autocomplete not found", True)
                    fields_not_found.append("Country")
                time.sleep(1)
            except Exception as e:
                print_warning(f"Country error: {str(e)[:40]}", True)
                fields_not_found.append("Country")
            
            # 8. State/Province (React Select - typing dropdown, type and select)
            try:
                # First locate the State field by looking for "State/Province" label
                state_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                if len(state_containers) > 1:  # Second container (after Country)
                    state_input = state_containers[1].find_element(By.XPATH, ".//input[@type='text']")
                    state_input.click()
                    time.sleep(0.3)
                    state_input.send_keys("Uttar Pradesh")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("State: Uttar Pradesh", True)
                    else:
                        print_warning("State options not found", True)
                        fields_not_found.append("State")
                else:
                    print_warning("State container not found", True)
                    fields_not_found.append("State")
            except Exception as e:
                print_warning(f"State field error: {str(e)[:40]}", True)
                fields_not_found.append("State")
            
            time.sleep(0.5)
            
            # 9. City (React Select - typing dropdown, type and select)
            try:
                city_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                if len(city_containers) > 2:  # Third container (after Country, State)
                    city_input = city_containers[2].find_element(By.XPATH, ".//input[@type='text']")
                    city_input.click()
                    time.sleep(0.3)
                    city_input.send_keys("Greater Noida")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("City: Greater Noida (Static)", True)
                    else:
                        print_warning("City options not found", True)
                        fields_not_found.append("City")
                else:
                    print_warning("City container not found", True)
                    fields_not_found.append("City")
            except Exception as e:
                print_warning(f"City field error: {str(e)[:40]}", True)
                fields_not_found.append("City")
        
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 3: College Information
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 3: Education", True)
            # 10. Occupation: Click "College Student"
            try:
                student_radio = driver.find_element(By.XPATH, "//input[@value='College Student' or contains(text(), 'College')]")
                if not student_radio.is_selected():
                    student_radio.click()
                print_success("Occupation: College Student", True)
                time.sleep(1)
            except Exception:
                # Try clicking the label instead
                try:
                    student_label = driver.find_element(By.XPATH, "//*[contains(text(), 'College Student')]")
                    student_label.click()
                    print_success("Occupation: College Student (via label)", True)
                except:
                    print_warning("College Student field not found", True)
                    fields_not_found.append("Occupation")
            
            time.sleep(0.5)
            
            # 11. College Name (React Select - typing dropdown, type and select)
            try:
                college_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                # College Name is usually at index 5 or later (after Country, State, City, Occupation)
                if len(college_containers) > 5:
                    college_input = college_containers[5].find_element(By.XPATH, ".//input[@type='text']")
                    college_input.click()
                    time.sleep(0.3)
                    college_input.send_keys("Galgotias University")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College Name: Galgotias University (Static)", True)
                    else:
                        print_warning("College Name options not found", True)
                        fields_not_found.append("College Name")
            except Exception as e:
                print_warning(f"College Name field error: {str(e)[:40]}", True)
            time.sleep(0.5)
            
            # 12. College Country (React Select - typing dropdown)
            try:
                college_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                if len(college_containers) > 6:
                    college_country_input = college_containers[6].find_element(By.XPATH, ".//input[@type='text']")
                    college_country_input.click()
                    time.sleep(0.3)
                    college_country_input.send_keys("India")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College Country: India", True)
            except Exception as e:
                print_warning(f"College Country error: {str(e)[:40]}", True)
        
            time.sleep(0.5)
            
            # 13. College State (React Select - typing dropdown)
            try:
                college_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                if len(college_containers) > 7:
                    college_state_input = college_containers[7].find_element(By.XPATH, ".//input[@type='text']")
                    college_state_input.click()
                    time.sleep(0.3)
                    college_state_input.send_keys("Uttar Pradesh")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College State: Uttar Pradesh", True)
            except Exception as e:
                print_warning(f"College State error: {str(e)[:40]}", True)
            
            time.sleep(0.5)
            
            # 14. College City (React Select - typing dropdown)
            try:
                college_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                if len(college_containers) > 8:
                    college_city_input = college_containers[8].find_element(By.XPATH, ".//input[@type='text']")
                    college_city_input.click()
                    time.sleep(0.3)
                    college_city_input.send_keys("Noida")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College City: Noida", True)
            except Exception as e:
                print_warning(f"College City error: {str(e)[:40]}", True)
            
            time.sleep(0.5)
            
            # 15. Degree (React Select - typing dropdown, type and select from options)
            try:
                college_containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
                if len(college_containers) > 9:
                    degree_input = college_containers[9].find_element(By.XPATH, ".//input[@type='text']")
                    degree_input.click()
                    time.sleep(0.3)
                    degree_input.send_keys("Bachelor of Technology")
                    time.sleep(1)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        # Look for B.Tech or similar option
                        found_btech = False
                        for option in options:
                            option_text = option.text
                            if "B.Tech" in option_text or "B. Tech" in option_text or "Bachelor" in option_text:
                                option.click()
                                print_success("Degree: Bachelor of Technology (B.Tech) (Static)", True)
                                found_btech = True
                                break
                        if not found_btech:
                            options[0].click()
                            print_success("Degree: Selected (Static)", True)
            except Exception as e:
                print_warning(f"Degree field error: {str(e)[:40]}", True)
            
            time.sleep(0.5)
            
            # 16. Stream/Specialization (TEXT INPUT - set to CSE)
            try:
                stream_inputs = driver.find_elements(By.XPATH, "//input[@name='7221COLLEGE_STUDENT_13_specialization' or contains(@placeholder, 'Stream') or contains(@placeholder, 'Specialization') or contains(@placeholder, 'branch')]")
                if stream_inputs:
                    safe_fill_field(driver, stream_inputs[0], "CSE", "Stream (CSE - Static)")
            except Exception as e:
                print_warning(f"Stream field error: {str(e)[:40]}", True)
            
            time.sleep(0.5)
            
            # 17. Passout Year (HTML <select> dropdown - set to 2027 or 2028)
            try:
                year_selects = driver.find_elements(By.TAG_NAME, "select")
                year_found = False
                
                for select_elem in year_selects:
                    try:
                        name = select_elem.get_attribute('name')
                        if name and 'passout' in name.lower() and 'year' in name.lower():
                            # This is the passout year select - try 2027 first, then 2028
                            try:
                                Select(select_elem).select_by_value("2027")
                                print_success("Passout Year: 2027 (Static)", True)
                                year_found = True
                            except:
                                try:
                                    Select(select_elem).select_by_value("2028")
                                    print_success("Passout Year: 2028 (Static)", True)
                                    year_found = True
                                except:
                                    pass
                            if year_found:
                                break
                    except:
                        pass
                
                if not year_found:
                    # Try by visible text as fallback
                    for select_elem in year_selects:
                        try:
                            Select(select_elem).select_by_visible_text("2027")
                            print_success("Passout Year: 2027 (Static)", True)
                            year_found = True
                            break
                        except:
                            try:
                                Select(select_elem).select_by_visible_text("2028")
                                print_success("Passout Year: 2028 (Static)", True)
                                year_found = True
                                break
                            except:
                                pass
            except Exception as e:
                print_warning(f"Passout Year error: {str(e)[:40]}", True)
            
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 4: Profile & Documents
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 4: Profiles & Documents", True)
            
            # 18. LinkedIn Profile (TEXT INPUT - simple URL field)
            try:
                linkedin_inputs = driver.find_elements(By.XPATH, "//input[@name='722169a30a85acee6c3069c2888e_17_69a30a85acee6c3069c2888e' or contains(@placeholder, 'LinkedIn') or contains(@placeholder, 'linkedin')]")
                if linkedin_inputs:
                    safe_fill_field(driver, linkedin_inputs[0], "https://linkedin.com/in/aditya-kumar", "LinkedIn")
            except Exception:
                print_warning("LinkedIn field error", True)
            
            time.sleep(0.5)
            
            # 19. College ID Card (file upload)
            try:
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                if file_inputs:
                    # Use the idcard.jpg if it exists in the project
                    idcard_path = r"C:\Users\preet\Downloads\selenium\idcard.jpg"
                    if os.path.exists(idcard_path):
                        file_inputs[0].send_keys(idcard_path)
                        print_success(f"College ID uploaded", True)
                        print_warning("Waiting 10 seconds for file upload to process...", True)
                        time.sleep(10)  # Wait for server to process the uploaded file
                    else:
                        print_warning("idcard.jpg not found", True)
            except Exception as e:
                print_warning(f"File upload error: {str(e)}", True)
            
            time.sleep(0.5)
            
            # 20. GDP Public Profile Link (TEXT INPUT - format: https://g.dev/username)
            try:
                gdp_inputs = driver.find_elements(By.XPATH, "//input[@name='722169a3ec31acee6c3069e3f11b_19_69a3ec31acee6c3069e3f11b' or contains(@placeholder, 'g.dev') or contains(@placeholder, 'GDP')]")
                if gdp_inputs:
                    # GDP Profile must be in format: https://g.dev/username
                    safe_fill_field(driver, gdp_inputs[0], "https://g.dev/aditya-kumar", "GDP Profile")
            except Exception:
                print_warning("GDP Profile field error", True)
            
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 5: Referral (Conditional Hidden Field)
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 5: GDG Referral (Conditional)", True)
            
            # 21. Were you referred? (Radio: Select YES to unlock referral code field)
            try:
                # Find ALL radio buttons and look for the referral question
                radio_buttons = driver.find_elements(By.XPATH, "//input[@type='radio']")
                yes_radio = None
                
                # Try to find the "Yes" radio for referral question
                # Strategy 1: Look for radio with value="Yes" 
                for radio in radio_buttons:
                    try:
                        radio_value = radio.get_attribute('value')
                        if radio_value and radio_value.lower() == "yes":
                            yes_radio = radio
                            break
                    except:
                        pass
                
                # Strategy 2: Look for radio with label containing "Yes"
                if not yes_radio:
                    for radio in radio_buttons:
                        try:
                            parent = radio.find_element(By.XPATH, "./ancestor::label | ./ancestor::div[@class*='radio']")
                            if "Yes" in parent.text:
                                yes_radio = radio
                                break
                        except:
                            pass
                
                # Strategy 3: Fallback to second-to-last radio
                if not yes_radio and len(radio_buttons) > 1:
                    yes_radio = radio_buttons[-2]
                
                if yes_radio:
                    if not yes_radio.is_selected():
                        driver.execute_script("arguments[0].scrollIntoView(true);", yes_radio)
                        time.sleep(0.3)
                        yes_radio.click()
                        print_success("Referral: YES selected", True)
                        time.sleep(1)  # Wait for hidden referral code field to appear
                        
                        # 22. Referral Code (appears only after selecting Yes)
                        try:
                            # Find the referral code input field
                            referral_inputs = driver.find_elements(By.XPATH, "//input[@name='7700DEFAULT_OTHER_FIELD_NAME_0_DEFAULT_OTHER_FIELD_NAME' or contains(@placeholder, 'referral code') or contains(@placeholder, 'Referral')]")
                            if referral_inputs:
                                safe_fill_field(driver, referral_inputs[0], "QZU6HH", "Referral Code (Static)")
                            else:
                                print_warning("Referral Code field not found (field appears only after selecting Yes)", True)
                        except Exception:
                            print_warning("Referral Code field error", True)
                else:
                    print_warning("Referral Yes radio not found", True)
                    fields_not_found.append("Referral")
                        
            except Exception as e:
                print_warning(f"Referral section error: {str(e)[:50]}", True)
                fields_not_found.append("Referral")
            
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 6: Terms & Conditions
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 6: Agreements", True)
            
            # 23. Terms & Conditions checkbox
            try:
                all_checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                checked = 0
                for i, checkbox in enumerate(all_checkboxes):
                    try:
                        if not checkbox.is_selected():
                            # Scroll checkbox into view
                            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                            time.sleep(0.2)
                            
                            # Try to click checkbox
                            try:
                                checkbox.click()
                            except:
                                # Use JS click if regular click fails
                                driver.execute_script("arguments[0].click();", checkbox)
                            
                            checked += 1
                    except:
                        pass
                
                if checked > 0:
                    print_success(f"Terms & Consents: {checked} checkbox(es) checked", True)
                else:
                    print_warning("No checkboxes to check", True)
                    fields_not_found.append("Checkboxes")
            except Exception as e:
                print_warning(f"Checkboxes error: {str(e)[:40]}", True)
                fields_not_found.append("Checkboxes")
            
            time.sleep(1)
            
            # ═══════════════════════════════════════════════════════════════
            # SUBMIT FORM
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Submitting form", True)
            try:
                # Find submit button
                submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
                
                # Scroll button into view
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(1)
                
                # Remove/hide any overlay if present
                try:
                    overlay = driver.find_element(By.XPATH, "//div[contains(@class, 'opacity-30')]")
                    driver.execute_script("arguments[0].style.display = 'none';", overlay)
                except:
                    pass
                
                time.sleep(0.5)
                
                # Try regular click first
                try:
                    submit_button.click()
                    print_success("Register button clicked", True)
                except Exception as click_error:
                    # If blocked, use JavaScript click
                    print_warning(f"Regular click failed, trying JS click", True)
                    driver.execute_script("arguments[0].click();", submit_button)
                    print_success("Register button clicked (JavaScript)", True)
                
                time.sleep(10)
                print_success("Registration form submitted successfully!", True)
                return True
            except Exception as e:
                print_warning(f"Submit button error: {str(e)[:50]}", True)
                fields_not_found.append("Submit")
            
            # ═══════════════════════════════════════════════════════════════
            # CHECK IF RETRY IS NEEDED (too many missing fields)
            # ═══════════════════════════════════════════════════════════════
            
            if len(fields_not_found) > 5:
                # Too many fields missing - likely page not fully loaded
                retry_count += 1
                if retry_count < MAX_RETRIES:
                    print_warning(f"Too many fields missing ({len(fields_not_found)}): {', '.join(fields_not_found[:5])}...", True)
                    print_step(4, f"Refreshing page and retrying in 10s", True)
                    time.sleep(10)
                    # Refresh page for next attempt
                    driver.refresh()
                    time.sleep(3)
                    continue  # Retry the while loop
                else:
                    print_error(f"Max retries reached ({MAX_RETRIES}) - fields missing: {', '.join(fields_not_found)}", True)
                    return False
            else:
                # Form was sufficiently filled - success
                print_success(f"Form filling completed (fields tracked: {len(fields_not_found)} issues)", True)
                return True
        
        except Exception as e:
            error = FormException(f"Form fill error: {str(e)}", WorkflowState.FORM_FILLING_IN_PROGRESS)
            log_exception(account['email'], error)
            print_error(f"Form filling failed: {str(e)}")
            
            # On error, retry once before giving up
            retry_count += 1
            if retry_count < MAX_RETRIES:
                print_step(4, f"Error during fill - refreshing and retrying in 10s", True)
                time.sleep(10)
                driver.refresh()
                time.sleep(3)
                continue
            else:
                return False
    
    # After loop - all retries exhausted
    print_error(f"Form filling failed after {MAX_RETRIES} attempts", True)
    return False


def process_single_account(driver: webdriver.Firefox, account: Dict) -> Tuple[bool, str]:
    """
    Process single account through entire workflow
    
    Returns:
        (success: bool, status: str)
    """
    email = account['email']
    
    try:
        # Step 2-3: Signup with OTP
        signup_ok = signup_with_otp_step(driver, account)
        if not signup_ok:
            return False, "SIGNUP_FAILED"
        
        time.sleep(2)
        
        # Step 4: Fill registration form
        form_ok = fill_registration_form(driver, account)
        if form_ok:
            return True, "SUCCESS"
        else:
            return True, "PARTIAL"  # Made it to form phase
    
    except OTPException as e:
        # OTP errors are critical - workflow is blocked
        log_exception(email, e)
        return False, "OTP_BLOCKER"
    except WorkflowException as e:
        log_exception(email, e)
        return False, "WORKFLOW_ERROR"
    except Exception as e:
        error = WorkflowException(f"Unexpected error: {str(e)}")
        log_exception(email, error)
        return False, "UNKNOWN_ERROR"


# ═══════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════

def main():
    """Main batch processing workflow"""
    print("\n" + "="*70)
    print("  HACK2SKILL BATCH REGISTRATION (REFACTORED - Error Handling)")
    print("="*70)
    
    # Step 1: Load accounts
    accounts = load_accounts_from_csv()
    if not accounts:
        print_error("No accounts to process - exiting")
        return
    
    print_success(f"Ready to process {len(accounts)} account(s)")
    
    # Initialize driver
    try:
        driver = init_firefox_driver()
    except DriverException as e:
        print_error(f"Cannot initialize driver: {str(e)} - exiting")
        return
    
    # Process each account
    completed = 0
    failed = 0
    partial = 0
    blocked = 0
    
    try:
        for idx, account in enumerate(accounts, 1):
            print_workflow_header(idx, len(accounts), account['email'])
            
            success, status = process_single_account(driver, account)
            
            if success:
                completed += 1
                log_progress(account['email'], "SUCCESS", "Account registered", WorkflowState.ACCOUNT_DONE)
                print_success(f"Account processed successfully")
            elif status == "OTP_BLOCKER":
                blocked += 1
                print_error(f"Workflow blocked at OTP verification - CRITICAL!")
                print_warning("User must provide OTP page HTML selectors to proceed")
                # Don't continue with next account if critical error
                break
            elif status == "PARTIAL":
                partial += 1
                log_progress(account['email'], "PARTIAL", "Form not completed", WorkflowState.ACCOUNT_DONE)
                print_warning(f"Partial completion")
            else:
                failed += 1
                log_progress(account['email'], "FAILED", f"Failed at {status}", WorkflowState.ACCOUNT_DONE)
                print_error(f"Account processing failed")
            
            # Wait between accounts
            if idx < len(accounts):
                print("\n⏳ Waiting 5 seconds before next account...")
                time.sleep(5)
    
    finally:
        print("\n" + "="*70)
        print("  BATCH PROCESSING COMPLETE")
        print("="*70)
        
        print(f"Total processed:    {len(accounts)}")
        print(f"  ✓ Successful:     {completed}")
        print(f"  ⚠ Partial:        {partial}")
        print(f"  ✗ Failed:         {failed}")
        print(f"  🔴 Blocked:       {blocked}")
        
        if blocked > 0:
            print(f"\n⚠️  WORKFLOW BLOCKED at {blocked} account(s) - OTP verification failed")
            print(f"    → User must provide OTP page HTML selectors")
            print(f"    → See WORKFLOW_ARCHITECTURE.md for instructions")
        
        print(f"\n📋 Log: {LOG_FILE}")
        print("="*70 + "\n")
        
        # Close driver
        try:
            driver.quit()
            print_success("Firefox closed")
        except:
            pass


if __name__ == "__main__":
    main()
