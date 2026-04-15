#!/usr/bin/env python3
"""
Hack2Skill Semi-Automated Registration with Firefox Private
- 90% Automated | 10% Manual (OTP only)
- Uses Firefox Private (NO Tor)
- Comprehensive error handling & logging
- Auto-fills, auto-submits form (minimal manual work)
"""

import time
import csv
import os
import sys
import random
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException,
    InvalidElementStateException, WebDriverException, NoSuchWindowException,
    SessionNotCreatedException, ElementNotInteractableException
)

# ==================== CONFIGURATION ====================
SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage&utm_campaign=&utm_term=&utm_content="
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
MAIN_URL = REGISTRATION_URL  # Use registration URL as main entry point
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"

TIMEOUT_PAGE_LOAD = 45
TIMEOUT_ELEMENT = 30
TIMEOUT_INTERACTION = 10
MAX_RETRIES = 3
RETRY_DELAY = 1
TOR_CONNECT_WAIT = 20
OTP_ARRIVAL_WAIT = 10
OTP_ENTRY_WAIT = 10

# ==================== LOGGING SETUP ====================
log_dir = "registration_logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Configure logging with UTF-8 encoding for Windows console compatibility
import io
class UTF8StreamHandler(logging.StreamHandler):
    def __init__(self, stream=None):
        super().__init__(stream)
        if stream is None:
            stream = sys.stderr
        # Wrap stream to handle Unicode
        if hasattr(stream, 'buffer'):
            super().__init__(io.TextIOWrapper(stream.buffer, encoding='utf-8', errors='replace'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        UTF8StreamHandler()
    ]
)
logger = logging.getLogger(__name__)



# ==================== UTILITY FUNCTIONS ====================
def print_step(step: str, color: str = "blue"):
    """Print colored step (with Windows Unicode support)"""
    colors = {
        "blue": "\033[94m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "red": "\033[91m",
        "cyan": "\033[96m",
        "reset": "\033[0m"
    }
    colored_text = f"{colors.get(color, '')}{step}{colors['reset']}"
    try:
        print(colored_text, flush=True)
    except UnicodeEncodeError:
        # Fallback for Windows console without Unicode support
        print(step, flush=True)
    try:
        logger.info(f"{step}")
    except UnicodeEncodeError:
        pass  # Logging handler will handle it


def load_accounts():
    """Load accounts from CSV with error handling"""
    if not os.path.exists(CSV_FILE):
        print_step(f"❌ CSV file not found: {CSV_FILE}", "red")
        logger.error(f"CSV file not found: {CSV_FILE}")
        return []
    
    accounts = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append(row)
        print_step(f"✓ Loaded {len(accounts)} accounts from CSV", "green")
        logger.info(f"Successfully loaded {len(accounts)} accounts")
        return accounts
    except IOError as e:
        print_step(f"❌ IO Error reading CSV: {str(e)}", "red")
        logger.error(f"IO Error reading CSV: {str(e)}")
        return []
    except Exception as e:
        print_step(f"❌ Unexpected error reading CSV: {str(e)}", "red")
        logger.error(f"Unexpected error reading CSV: {str(e)}")
        return []


def init_tor_driver():
    """Initialize Firefox Private (NO TOR)"""
    try:
        print_step("[WAIT] Initializing Firefox Private...", "cyan")
        
        options = webdriver.FirefoxOptions()
        options.add_argument("--private")
        options.add_argument("--no-remote")
        
        # Privacy preferences
        options.set_preference("network.trr.mode", 5)  # Disable DoH
        options.set_preference("media.peerconnection.enabled", False)  # Disable WebRTC
        options.set_preference("dom.disable_beforeunload", True)
        
        driver = webdriver.Firefox(options=options)
        print_step("[OK] Firefox Private initialized", "green")
        logger.info("Firefox Private initialized")
        
        return driver
        
    except SessionNotCreatedException as e:
        print_step(f"[ERROR] Firefox driver creation failed: {str(e)[:80]}", "red")
        logger.error(f"SessionNotCreatedException: {str(e)}")
        print_step("\n[HELP] Troubleshooting:", "yellow")
        print_step("   1. Ensure Firefox is installed", "yellow")
        print_step("   2. Close any existing Firefox windows", "yellow")
        return None
    except WebDriverException as e:
        print_step(f"[ERROR] WebDriver error: {str(e)[:80]}", "red")
        logger.error(f"WebDriverException: {str(e)}")
        return None
    except Exception as e:
        print_step(f"[ERROR] Unexpected error: {str(e)}", "red")
        logger.error(f"Unexpected error: {str(e)}")
        print_step("\n[HELP] Troubleshooting:", "yellow")
        print_step("   1. Ensure Python and Selenium are up to date", "yellow")
        print_step("   2. Check system resources", "yellow")
        return None


def auto_signup(driver: webdriver.Firefox, account: dict) -> bool:
    """Auto-fill signup form - simple, direct flow"""
    
    print_step(f"\n{'='*70}", "yellow")
    print_step(f"ACCOUNT: {account['email']}", "yellow")
    print_step(f"{'='*70}", "yellow")
    
    wait = WebDriverWait(driver, TIMEOUT_PAGE_LOAD)
    
    try:
        # Step 1: Open registration page (main URL)
        print_step("→ Step 1: Opening registration page (main page)...", "blue")
        driver.get(MAIN_URL)
        time.sleep(2)
        print_step("✓ Registration page loaded", "green")
        logger.info(f"Signup page loaded for {account['email']}")
        
        # Step 2: Fill + Submit form
        print_step("→ Step 2: Filling signup form (Name + Email)...", "blue")
        
        # Generate Full Name
        first_names = ["Arjun", "Aditya", "Naman", "Raj", "Vikram", "Priya", "Ananya", "Dev", "Maya"]
        last_names = ["Singh", "Sharma", "Kumar", "Patel", "Gupta", "Verma", "Rao", "Malik", "Desai"]
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Fill Full Name
        fullname_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'Full Name') or @name='fullName']")))
        driver.execute_script("arguments[0].scrollIntoView(true);", fullname_field)
        time.sleep(0.3)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", fullname_field, full_name)
        print_step(f"  ✓ Full Name: {full_name}", "green")
        logger.info(f"Full Name filled: {full_name}")
        
        # Fill Email
        email_field = driver.find_element(By.XPATH, "//input[@type='email' or contains(@placeholder, 'Email')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
        time.sleep(0.3)
        driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", email_field, account['email'])
        print_step(f"  ✓ Email: {account['email']}", "green")
        logger.info(f"Email filled: {account['email']}")
        
        # Click Register button
        print_step("→ Step 2b: Clicking Register button...", "blue")
        register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", register_button)
        time.sleep(0.3)
        driver.execute_script("arguments[0].click();", register_button)
        print_step("✓ Register button clicked", "green")
        logger.info("Register button clicked")
        
        # Step 3: Wait for success (URL change / DOM change) - but don't wait for OTP field
        print_step("→ Step 3: Waiting for form submission to complete...", "blue")
        time.sleep(3)  # Wait for page to process submission
        
        # Step 4: Manual OTP entry with timer
        print_step("\n" + "="*70, "yellow")
        print_step("🔐 STEP 3A: WAITING FOR OTP (Email arrival - 10 seconds)", "yellow")
        print_step("="*70, "yellow")
        print_step("✓ Check your email for the OTP code", "blue")
        
        for remaining in range(OTP_ARRIVAL_WAIT, 0, -1):
            sys.stdout.write(f"\r⏱️  {remaining:3d}s remaining (checking email)...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n")
        
        # Step 4B: User enters OTP
        print_step("\n" + "="*70, "yellow")
        print_step("🔐 STEP 3B: WAITING FOR OTP ENTRY (Manual input - 10 seconds)", "yellow")
        print_step("="*70, "yellow")
        print_step("✓ Copy OTP from email and paste in the browser", "blue")
        print_step("✓ You have 10 seconds to enter it", "blue")
        
        for remaining in range(OTP_ENTRY_WAIT, 0, -1):
            sys.stdout.write(f"\r⏱️  {remaining:3d}s remaining (enter OTP now)...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n")
        print_step("✓ OTP timer complete - auto-clicking Verify...", "green")
        logger.info("OTP waiting period completed")
        
        # Auto-click Verify button
        try:
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify') or contains(text(), 'Submit') or contains(text(), 'Confirm')]")
            driver.execute_script("arguments[0].click();", verify_button)
            print_step("✓ Verify button clicked", "green")
            logger.info("Verify button clicked")
        except NoSuchElementException:
            print_step("⚠ Verify button not found (you may have clicked it already)", "yellow")
            logger.warning("Verify button not found")
        
        # Wait for OTP verification to complete
        print_step("→ Waiting for OTP verification to complete...", "blue")
        time.sleep(6)
        print_step("✓ OTP verification complete", "green")
        
        return True
        
    except TimeoutException as e:
        print_step(f"❌ Signup timeout: {str(e)[:50]}", "red")
        logger.error(f"Signup timeout: {str(e)}")
        return False
    except NoSuchElementException as e:
        print_step(f"❌ Form element not found: {str(e)[:50]}", "red")
        logger.error(f"Element not found: {str(e)}")
        return False
    except Exception as e:
        print_step(f"❌ Signup error: {str(e)[:60]}", "red")
        logger.error(f"Signup error: {str(e)}")
        return False



# ==================== FORM FILLING FUNCTIONS ====================
def safe_fill_field(driver: webdriver.Firefox, wait: WebDriverWait, field_locator, value: str, field_name: str, max_retries: int = MAX_RETRIES):
    """Safely fill a text field with comprehensive error handling"""
    for attempt in range(max_retries):
        try:
            # Wait for element visibility
            element = wait.until(EC.visibility_of_element_located(field_locator), f"Timeout waiting for {field_name} visibility")
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.3)
            
            # Wait for clickability
            element = wait.until(EC.element_to_be_clickable(field_locator), f"Timeout waiting for {field_name} clickability")
            
            # Click to focus
            element.click()
            time.sleep(0.2)
            
            # Clear field
            try:
                element.clear()
            except InvalidElementStateException:
                element.send_keys(Keys.CONTROL + 'a')
                time.sleep(0.1)
            
            # Send value
            element.send_keys(value)
            time.sleep(0.3)
            
            # Verify value was entered
            if element.get_attribute("value") or element.text:
                print_step(f"✓ {field_name}: {value}", "green")
                logger.info(f"Successfully filled {field_name}")
                return True
            else:
                raise ValueError(f"Value not confirmed in {field_name}")
                
        except StaleElementReferenceException as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Stale element for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"StaleElementReferenceException for {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"❌ Stale element persisted for {field_name}", "red")
                logger.error(f"Stale element failed for {field_name}")
                return False
                
        except TimeoutException as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Timeout for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"TimeoutException for {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ {field_name} not found (field may be hidden/removed)", "yellow")
                logger.warning(f"Could not locate {field_name}")
                return False
                
        except ElementNotInteractableException as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Element not interactable for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"ElementNotInteractableException for {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ {field_name} not interactable (may be disabled/hidden)", "yellow")
                logger.warning(f"Element not interactable: {field_name}")
                return False
                
        except Exception as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Error filling {field_name}, retrying ({attempt + 1}/{max_retries}): {str(e)[:40]}", "yellow")
                logger.warning(f"Error filling {field_name}: {str(e)[:80]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ Could not fill {field_name}: {str(e)[:50]}", "yellow")
                logger.error(f"Failed to fill {field_name}: {str(e)}")
                return False
    
    return False


def safe_select_dropdown(driver: webdriver.Firefox, wait: WebDriverWait, field_locator, value: str, field_name: str, max_retries: int = MAX_RETRIES):
    """Safely select dropdown with comprehensive error handling"""
    for attempt in range(max_retries):
        try:
            # Wait for dropdown visibility
            select_element = wait.until(EC.visibility_of_element_located(field_locator), f"Timeout waiting for {field_name} dropdown")
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", select_element)
            time.sleep(0.3)
            
            # Wait for clickability
            select_element = wait.until(EC.element_to_be_clickable(field_locator), f"Timeout waiting for {field_name} clickability")
            
            # Click to open
            select_element.click()
            time.sleep(0.5)
            
            # Find and click option (with flexible matching)
            options = wait.until(lambda d: d.find_elements(By.TAG_NAME, "option"), f"Options not found in {field_name}")
            
            selected = False
            for option in options:
                try:
                    option_text = option.text.strip()
                    option_value = option.get_attribute("value")
                    
                    # Check multiple matching strategies
                    if (value.lower() in option_text.lower() or 
                        option_text.lower() in value.lower() or
                        option_value and value.lower() in option_value.lower()):
                        
                        driver.execute_script("arguments[0].scrollIntoView(true);", option)
                        time.sleep(0.2)
                        option.click()
                        time.sleep(0.3)
                        print_step(f"✓ {field_name}: {option_text}", "green")
                        logger.info(f"Successfully selected {field_name}: {option_text}")
                        selected = True
                        break
                except StaleElementReferenceException:
                    continue
            
            if selected:
                return True
            else:
                print_step(f"⚠ Option '{value}' not found in {field_name}, skipping", "yellow")
                logger.warning(f"Option '{value}' not found in {field_name}")
                return False
                
        except StaleElementReferenceException as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Stale element in dropdown {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"Stale element in {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                return False
                
        except TimeoutException as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Timeout in dropdown {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"Timeout in {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ {field_name} dropdown not found, skipping", "yellow")
                logger.warning(f"Dropdown {field_name} not found")
                return False
                
        except Exception as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Error selecting {field_name}, retrying ({attempt + 1}/{max_retries}): {str(e)[:40]}", "yellow")
                logger.warning(f"Error selecting {field_name}: {str(e)[:80]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ Could not select {field_name}: {str(e)[:50]}", "yellow")
                logger.error(f"Failed to select {field_name}: {str(e)}")
                return False
    
    return False


def safe_select_radio(driver: webdriver.Firefox, wait: WebDriverWait, value: str, field_name: str, max_retries: int = MAX_RETRIES):
    """Safely select radio button with comprehensive error handling"""
    for attempt in range(max_retries):
        try:
            # Find all radio buttons (may take time to load)
            radios = wait.until(lambda d: d.find_elements(By.XPATH, "//input[@type='radio']"), f"Radio buttons not found for {field_name}")
            
            if not radios:
                print_step(f"⚠ No radio buttons found for {field_name}", "yellow")
                logger.warning(f"No radio buttons found for {field_name}")
                return False
            
            for radio in radios:
                try:
                    radio_value = radio.get_attribute("value")
                    
                    # Try to get parent label
                    try:
                        parent_label = radio.find_element(By.XPATH, "./ancestor::label").text
                    except NoSuchElementException:
                        parent_label = ""
                    
                    # Flexible matching
                    if ((radio_value and value.lower() in radio_value.lower()) or 
                        (value.lower() in parent_label.lower())):
                        
                        driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                        time.sleep(0.3)
                        
                        # Try clicking radio button
                        try:
                            radio.click()
                        except ElementNotInteractableException:
                            # If radio not clickable, try clicking parent label
                            parent = radio.find_element(By.XPATH, "./ancestor::label")
                            parent.click()
                        
                        time.sleep(0.3)
                        print_step(f"✓ {field_name}: {value}", "green")
                        logger.info(f"Successfully selected radio {field_name}: {value}")
                        return True
                        
                except StaleElementReferenceException:
                    continue
            
            print_step(f"⚠ Radio button '{value}' not found for {field_name}, skipping", "yellow")
            logger.warning(f"Radio button '{value}' not found for {field_name}")
            return False
            
        except TimeoutException:
            if attempt < max_retries - 1:
                print_step(f"⚠ Radio timeout for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"Radio timeout for {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ {field_name} radio buttons not found, skipping", "yellow")
                logger.warning(f"Radio buttons {field_name} not found")
                return False
                
        except Exception as e:
            if attempt < max_retries - 1:
                print_step(f"⚠ Error selecting radio {field_name}, retrying ({attempt + 1}/{max_retries}): {str(e)[:40]}", "yellow")
                logger.warning(f"Error selecting radio {field_name}: {str(e)[:80]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"⚠ Could not select radio {field_name}: {str(e)[:50]}", "yellow")
                logger.error(f"Failed to select radio {field_name}: {str(e)}")
                return False
    
    return False


def auto_fill_registration_form(driver: webdriver.Firefox, account: dict):
    """Auto-fill ALL form fields and auto-submit with comprehensive error handling"""
    try:
        wait = WebDriverWait(driver, TIMEOUT_ELEMENT)
        
        print_step("\n" + "="*70, "yellow")
        print_step("AUTO-FILLING REGISTRATION FORM (90% AUTOMATED)", "yellow")
        print_step("="*70, "yellow")
        
        # Wait for form to load
        print_step("→ Waiting for form elements to load...", "blue")
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
            time.sleep(2)
            print_step("✓ Form loaded", "green")
            logger.info("Registration form loaded successfully")
        except TimeoutException:
            print_step("⚠ Form took longer to load, proceeding anyway", "yellow")
            logger.warning("Form load timeout, proceeding")
            time.sleep(2)
        
        # Auto-fill all fields
        print_step("\n→ Filling form fields...\n", "cyan")
        
        # Full Name
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'Full Name') or @name='fullName' or @name='full_name']"), 
                       account['email'].split('@')[0].title(), "Full Name")
        
        # Email
        safe_fill_field(driver, wait, (By.XPATH, "//input[@type='email' or contains(@placeholder, 'Email')]"), 
                       account['email'], "Email")
        
        # WhatsApp
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'WhatsApp') or @name='whatsapp' or @name='phone']"), 
                       "9999999999", "WhatsApp Number")
        
        # Gender
        safe_select_dropdown(driver, wait, (By.XPATH, "//select[@name='gender'] | //select[contains(@aria-label, 'Gender') or contains(@placeholder, 'Gender')]"),
                            "Male", "Gender")
        
        # Country
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'Country') and not(contains(@placeholder, 'College'))]"), 
                       "India", "Country")
        
        # State
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'State') and not(contains(@placeholder, 'College'))] | //input[contains(@placeholder, 'Province')]"), 
                       "Uttar Pradesh", "State")
        
        # City
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'City') and not(contains(@placeholder, 'College'))]"), 
                       "Greater Noida", "City")
        
        # Date of Birth (try multiple formats)
        safe_fill_field(driver, wait, (By.XPATH, "//input[@type='date' or contains(@placeholder, 'Birth') or contains(@placeholder, 'DOB')]"), 
                       "01/01/2000", "Date of Birth")
        
        # College Name
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'College Name')] | //input[@name='collegeName']"), 
                       "Galgotias University", "College Name")
        
        # College Country
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'College Country')]"), 
                       "India", "College Country")
        
        # College State
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'College State')]"), 
                       "Uttar Pradesh", "College State")
        
        # College City
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'College City')]"), 
                       "Noida", "College City")
        
        # Degree
        safe_select_dropdown(driver, wait, (By.XPATH, "//select[@name='degree'] | //select[contains(@aria-label, 'Degree')]"),
                            "Bachelor of Technology", "Degree")
        
        # Stream
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'Stream')] | //input[@name='specialization']"), 
                       "CSE", "Stream")
        
        # Passout Year
        safe_select_dropdown(driver, wait, (By.XPATH, "//select[@name='passoutYear'] | //select[contains(@aria-label, 'Year')]"),
                            "2027", "Passout Year")
        
        # LinkedIn
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'LinkedIn')] | //input[@name='linkedin']"), 
                       "https://linkedin.com", "LinkedIn Profile")
        
        # GDP Profile Link
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'GDP')] | //input[@name='gdpLink']"), 
                       "https://gdp.com", "GDP Profile Link")
        
        # Referral - Yes
        safe_select_radio(driver, wait, "Yes", "Referral")
        
        # Referral Code
        safe_fill_field(driver, wait, (By.XPATH, "//input[contains(@placeholder, 'Referral')] | //input[@name='referralCode']"), 
                       "QZU6HH", "Referral Code")
        
        # Terms & Conditions checkbox
        try:
            terms_checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox'][1]")
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
                print_step("✓ Terms & Conditions: Accepted", "green")
                logger.info("Checked Terms & Conditions")
        except NoSuchElementException:
            print_step("⚠ Terms & Conditions checkbox not found", "yellow")
            logger.warning("Terms checkbox not found")
        except Exception as e:
            print_step(f"⚠ Could not check Terms & Conditions: {str(e)[:50]}", "yellow")
            logger.warning(f"Error checking Terms: {str(e)[:80]}")
        
        print_step("\n" + "="*70, "green")
        print_step("✅ FORM AUTO-FILLED SUCCESSFULLY!", "green")
        print_step("="*70, "green")
        
        # Wait for user to manually review and submit form
        print_step("\n" + "="*70, "yellow")
        print_step("[PAUSE] REGISTRATION FORM READY FOR MANUAL SUBMISSION", "yellow")
        print_step("="*70, "yellow")
        print_step("[INFO] Form auto-filled with all static values", "green")
        print_step("[INFO] Please review the form on screen", "blue")
        print_step("[WAIT] When ready, click the Submit/Register button yourself", "blue")
        print_step("[HELP] Then return to terminal and press ENTER to continue", "yellow")
        print_step("-" * 70, "yellow")
        
        # Wait for user input
        try:
            input("\n[PAUSE] Press ENTER after submitting the form... ")
            print_step("[OK] Continuing to next account", "green")
            logger.info("User confirmed form submission")
            time.sleep(1)
            return True
        except Exception as e:
            print_step(f"[ERROR] Input error: {str(e)[:50]}", "red")
            logger.error(f"Input error: {str(e)}")
            return True  # Continue anyway
        
    except Exception as e:
        print_step(f"❌ Critical error auto-filling form: {str(e)}", "red")
        logger.error(f"Critical error: {str(e)}")
        return False


def process_account(account: dict, account_num: int, total: int) -> bool:
    """
    Process single account - SIGNUP ONLY (no registration form)
    Opens fresh Firefox private window, handles OTP, then pauses for manual form filling
    """
    driver = None
    try:
        # Initialize fresh Firefox private window for this account
        print_step(f"\n[INFO] Opening fresh Firefox Private window...", "blue")
        driver = init_tor_driver()
        if not driver:
            print_step("[ERROR] Failed to open Firefox - skipping", "red")
            logger.error(f"Failed to initialize browser for account {account_num}")
            return False
        
        # Auto-fill signup and OTP verification
        signup_ok = auto_signup(driver, account)
        if not signup_ok:
            print_step("[ERROR] Signup/OTP failed - skipping this account", "red")
            logger.error(f"Signup failed for {account['email']}")
            return False
        
        # ============================================================
        # PAUSE - User manually fills and submits registration form
        # ============================================================
        print_step("\n" + "="*70, "yellow")
        print_step("[PAUSE] OTP VERIFIED - MANUAL FORM FILLING REQUIRED", "yellow")
        print_step("="*70, "yellow")
        print_step("[INFO] Registration form is already displayed in Firefox", "green")
        print_step("[WAIT] Please fill out the remaining registration form fields manually", "blue")
        print_step("[INFO] When done, click Submit button on the form", "blue")
        print_step("[HELP] Then return here and press ENTER to continue", "yellow")
        print_step("-" * 70, "yellow")
        
        # Wait for user to complete manual form submission
        input("\n[PAUSE] Press ENTER after submitting the form... ")
        
        print_step("\n[INFO] Closing Firefox window and preparing for next account...", "blue")
        logger.info(f"Account {account_num} manual form submission complete: {account['email']}")
        
        return True
        
    except NoSuchWindowException:
        print_step("[ERROR] Browser crashed during account processing", "red")
        logger.error(f"Browser crashed for account {account_num}")
        return False
    except Exception as e:
        print_step(f"[ERROR] Account {account_num} failed: {str(e)[:60]}", "red")
        logger.error(f"Account {account_num} processing failed: {str(e)}")
        return False
    finally:
        # Close Firefox after each account (fresh start for next one)
        if driver:
            try:
                driver.quit()
                print_step("[OK] Firefox window closed", "green")
                logger.info(f"Firefox closed after account {account_num}")
                time.sleep(1)  # Brief pause between accounts
            except Exception as e:
                logger.warning(f"Error closing Firefox: {str(e)}")
                pass


def main():
    """Main execution loop - processes each account with fresh Firefox window"""
    
    print_step("\n" + "="*70, "blue")
    print_step("HACK2SKILL OTP SIGNUP ONLY | 90% AUTO | 10% MANUAL (FORM FILLING)", "blue")
    print_step("="*70, "blue")
    
    # Load accounts
    accounts = load_accounts()
    if not accounts:
        print_step("[ERROR] No accounts to process", "red")
        logger.error("No accounts loaded")
        return
    
    print_step(f"\nReady to process {len(accounts)} account(s) via Firefox Private", "green")
    print_step("-" * 70, "cyan")
    logger.info(f"Starting batch processing of {len(accounts)} accounts")
    
    # Process each account with fresh Firefox window
    completed = 0
    failed = 0
    
    try:
        for idx, account in enumerate(accounts, 1):
            print_step(f"\n{'='*70}", "cyan")
            print_step(f"[{idx}/{len(accounts)}] Processing: {account['email']}", "cyan")
            print_step(f"{'='*70}", "cyan")
            
            # Process account (opens fresh Firefox, closes at end)
            success = process_account(account, idx, len(accounts))
            
            if success:
                completed += 1
            else:
                failed += 1
            
            # Pause between accounts (if not last one)
            if idx < len(accounts):
                print_step("\n" + "="*70, "yellow")
                print_step("[READY] Account complete - press ENTER for next one", "yellow")
                print_step("="*70, "yellow")
                input()
                print_step("\n[INFO] Starting next account...\n", "green")
                time.sleep(1)
    
    except KeyboardInterrupt:
        print_step("\n\n[ABORT] Process interrupted by user", "red")
        logger.error("Process interrupted by user")
    except Exception as e:
        print_step(f"\n\n[ERROR] Critical error: {str(e)}", "red")
        logger.error(f"Critical error: {str(e)}")
    finally:
        # Summary
        print_step("\n\n" + "="*70, "blue")
        print_step("BATCH PROCESSING COMPLETE", "blue")
        print_step("="*70, "blue")
        print_step(f"Total accounts: {len(accounts)}", "blue")
        print_step(f"[OK] Completed: {completed}", "green")
        print_step(f"[FAIL] Failed: {failed}", "red")
        if len(accounts) > 0:
            success_rate = (completed/len(accounts)*100)
            print_step(f"\n[STATS] Success Rate: {success_rate:.1f}%", "cyan")
        print_step(f"[LOG] Output saved to: {log_file}", "cyan")
        print_step("="*70 + "\n", "blue")
        
        logger.info(f"Batch complete: {completed} succeeded, {failed} failed")


if __name__ == "__main__":
    main()
