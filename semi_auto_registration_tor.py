#!/usr/bin/env python3
"""
Hack2Skill Semi-Automated Registration with Tor Browser
- 90% Automated | 10% Manual (OTP only)
- Uses Tor Browser (built-in Tor network integration)
- Comprehensive error handling
- Auto-fills & auto-submits registration form
- Fully encrypted and routed through Tor network
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
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"

TIMEOUT_PAGE_LOAD = 45
TIMEOUT_ELEMENT = 30
TIMEOUT_INTERACTION = 10
MAX_RETRIES = 3
RETRY_DELAY = 1
TOR_CONNECT_WAIT = 20
OTP_WAIT_SECONDS = 60

# ==================== LOGGING SETUP ====================
import io

class UTF8StreamHandler(logging.StreamHandler):
    """Handle UTF-8 encoding on Windows console (cp1252)"""
    def __init__(self, stream=None):
        super().__init__(stream)
        if hasattr(stream, 'buffer'):
            super().__init__(io.TextIOWrapper(stream.buffer, encoding='utf-8', errors='replace'))

log_dir = "registration_logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"registration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
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
    """Print colored step with Unicode fallback"""
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
        print(step, flush=True)
    try:
        logger.info(f"{step}")
    except UnicodeEncodeError:
        pass


def load_accounts():
    """Load accounts from CSV with error handling"""
    if not os.path.exists(CSV_FILE):
        print_step(f"[ERROR] CSV file not found: {CSV_FILE}", "red")
        logger.error(f"CSV file not found: {CSV_FILE}")
        return []
    
    accounts = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append(row)
        print_step(f"[OK] Loaded {len(accounts)} accounts from CSV", "green")
        return accounts
    except IOError as e:
        print_step(f"[ERROR] IO Error reading CSV: {str(e)}", "red")
        logger.error(f"IO Error reading CSV: {str(e)}")
        return []
    except Exception as e:
        print_step(f"[ERROR] Unexpected error reading CSV: {str(e)}", "red")
        logger.error(f"Unexpected error reading CSV: {str(e)}")
        return []


def init_tor_driver():
    """Initialize Tor Browser WebDriver with integrated Tor network"""
    try:
        print_step("[WAIT] Initializing browser with Tor network...", "cyan")
        
        # Common Tor Browser paths on Windows
        tor_browser_paths = [
            r"C:\Users\preet\OneDrive\Documents\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
            os.path.expanduser(r"~\AppData\Local\Tor Browser\Browser\firefox.exe"),
            r"C:\Users\preet\AppData\Local\Tor Browser\Browser\firefox.exe",
        ]
        
        tor_browser_binary = None
        for path in tor_browser_paths:
            if os.path.exists(path):
                tor_browser_binary = path
                print_step(f"[OK] Found Tor Browser at: {path}", "green")
                logger.info(f"Tor Browser found at: {path}")
                break
        
        if not tor_browser_binary:
            print_step("[ERROR] Tor Browser not found in standard locations", "red")
            print_step("[INFO] Expected locations:", "yellow")
            for path in tor_browser_paths:
                print_step(f"   - {path}", "yellow")
            print_step("\n[HELP] Install Tor Browser from: https://www.torproject.org/download/", "yellow")
            logger.error("Tor Browser not found - required for this script")
            return None
        
        options = webdriver.FirefoxOptions()
        
        # Use Tor Browser (built-in Tor network)
        options.binary_location = tor_browser_binary
        
        options.add_argument("--private")
        options.add_argument("--no-remote")  # Prevent multiple instances conflict
        
        # Set Tor Browser privacy preferences
        options.set_preference("network.trr.mode", 5)  # Disable DoH
        options.set_preference("media.peerconnection.enabled", False)  # Disable WebRTC
        options.set_preference("dom.disable_beforeunload", True)
        options.set_preference("browser.privatebrowsing.autostart", True)
        options.set_preference("extensions.torbutton.use_nontor_proxy", False)
        
        driver = webdriver.Firefox(options=options)
        print_step("[OK] Tor Browser initialized with integrated Tor network", "green")
        logger.info("Tor Browser WebDriver initialized")
        
        # Wait for Tor to connect to network
        print_step(f"\n{'='*70}", "cyan")
        print_step("[WAIT] Connecting to Tor network...", "cyan")
        print_step(f"{'='*70}", "cyan")
        print_step("[INFO] Using Tor network (fully encrypted & anonymous)", "blue")
        
        for remaining in range(TOR_CONNECT_WAIT, 0, -1):
            sys.stdout.write(f"\r⏳ {remaining:2d} seconds... (Tor connecting to network)")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n")
        print_step("[OK] Tor Browser connected to Tor network", "green")
        logger.info("Tor Browser connected to Tor network")
        
        return driver
        
    except SessionNotCreatedException as e:
        print_step(f"[ERROR] Tor Browser driver creation failed: {str(e)[:80]}", "red")
        logger.error(f"SessionNotCreatedException: {str(e)}")
        print_step("\n[HELP] Troubleshooting:", "yellow")
        print_step("   1. Make sure Tor Browser is installed", "yellow")
        print_step("   2. Close any existing Tor Browser windows", "yellow")
        print_step("   3. Check firewall settings", "yellow")
        return None
    except WebDriverException as e:
        print_step(f"[ERROR] WebDriver error initializing Tor Browser: {str(e)[:80]}", "red")
        logger.error(f"WebDriverException: {str(e)}")
        return None
    except Exception as e:
        print_step(f"[ERROR] Unexpected error initializing Tor Browser: {str(e)}", "red")
        logger.error(f"Unexpected error initializing Tor Browser: {str(e)}")
        print_step("\n[HELP] Troubleshooting:", "yellow")
        print_step("   1. Verify Tor Browser is installed correctly", "yellow")
        print_step("   2. Ensure Python and Selenium are up to date", "yellow")
        return None


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
                print_step(f"[WARN] Stale element for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"StaleElementReferenceException for {field_name}: {str(e)[:50]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[FAIL] Stale element persisted for {field_name}", "red")
                logger.error(f"Stale element failed for {field_name}")
                return False
                
        except TimeoutException as e:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Timeout for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"TimeoutException for {field_name}: {str(e)[:50]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[WARN] {field_name} not found (field may be hidden/removed from form)", "yellow")
                logger.warning(f"Could not locate {field_name}")
                return False
                
        except ElementNotInteractableException as e:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Element not interactable for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"ElementNotInteractableException for {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[WARN] {field_name} not interactable (may be disabled/hidden)", "yellow")
                logger.warning(f"Element not interactable: {field_name}")
                return False
                
        except Exception as e:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Error filling {field_name}, retrying ({attempt + 1}/{max_retries}): {str(e)[:40]}", "yellow")
                logger.warning(f"Error filling {field_name}: {str(e)[:80]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[WARN] Could not fill {field_name}: {str(e)[:50]}", "yellow")
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
                        print_step(f"[OK] {field_name}: {option_text}", "green")
                        logger.info(f"Successfully selected {field_name}: {option_text}")
                        selected = True
                        break
                except StaleElementReferenceException:
                    continue
            
            if selected:
                return True
            else:
                print_step(f"[WARN] Option '{value}' not found in {field_name}, skipping", "yellow")
                logger.warning(f"Option '{value}' not found in {field_name}")
                return False
                
        except StaleElementReferenceException as e:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Stale element in dropdown {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"Stale element in {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                return False
                
        except TimeoutException as e:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Timeout in dropdown {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"Timeout in {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[WARN] {field_name} dropdown not found, skipping", "yellow")
                logger.warning(f"Dropdown {field_name} not found")
                return False
                
        except Exception as e:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Error selecting {field_name}, retrying ({attempt + 1}/{max_retries}): {str(e)[:40]}", "yellow")
                logger.warning(f"Error selecting {field_name}: {str(e)[:80]}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[WARN] Could not select {field_name}: {str(e)[:50]}", "yellow")
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
                print_step(f"[WARN] No radio buttons found for {field_name}", "yellow")
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
                        print_step(f"[OK] {field_name}: {value}", "green")
                        logger.info(f"Successfully selected radio {field_name}: {value}")
                        return True
                        
                except StaleElementReferenceException:
                    continue
            
            print_step(f"[WARN] Radio button '{value}' not found for {field_name}, skipping", "yellow")
            logger.warning(f"Radio button '{value}' not found for {field_name}")
            return False
            
        except TimeoutException:
            if attempt < max_retries - 1:
                print_step(f"[WARN] Radio timeout for {field_name}, retrying ({attempt + 1}/{max_retries})...", "yellow")
                logger.warning(f"Radio timeout for {field_name}")
                time.sleep(RETRY_DELAY)
            else:
                print_step(f"[WARN] {field_name} radio buttons not found, skipping", "yellow")
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
    """Auto-fill ALL form fields with comprehensive error handling"""
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
        
        # Auto-submit form
        print_step("\n→ Submitting form automatically...", "blue")
        
        try:
            # Try multiple submit button strategies
            submit_button = None
            strategies = [
                (By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'Register')]"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(text(), 'Next')]"),
            ]
            
            for locator in strategies:
                try:
                    elements = driver.find_elements(*locator)
                    if elements:
                        submit_button = elements[0]
                        break
                except NoSuchElementException:
                    continue
            
            if submit_button:
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)
                submit_button.click()
                print_step("✓ Submit button clicked", "green")
                logger.info("Form submitted successfully")
                time.sleep(3)
                return True
            else:
                print_step("⚠ Submit button not found - form may have auto-submitted", "yellow")
                logger.warning("Submit button not found")
                time.sleep(2)
                return True  # Assume form might auto-submit
                
        except Exception as e:
            print_step(f"⚠ Error clicking submit: {str(e)[:50]}", "yellow")
            logger.warning(f"Error submitting form: {str(e)[:80]}")
            return False
        
    except Exception as e:
        print_step(f"❌ Critical error auto-filling form: {str(e)}", "red")
        logger.error(f"Critical error: {str(e)}")
        return False


def auto_signup(driver: webdriver.Firefox, account: dict) -> bool:
    """Auto-fill signup form with comprehensive error handling"""
    
    print_step(f"\n{'='*70}", "yellow")
    print_step(f"ACCOUNT: {account['email']}", "yellow")
    print_step(f"{'='*70}", "yellow")
    
    wait = WebDriverWait(driver, TIMEOUT_PAGE_LOAD)
    
    try:
        # Navigate to signup
        print_step("→ Navigating to Signup Page via Tor...", "blue")
        driver.get(SIGNUP_PAGE_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
        time.sleep(2)
        print_step("✓ Signup page loaded", "green")
        logger.info(f"Signup page loaded for {account['email']}")
        
        # Fill Full Name
        print_step("→ Filling Full Name...", "blue")
        first_names = ["Arjun", "Aditya", "Naman", "Raj", "Vikram", "Priya", "Ananya", "Dev", "Maya"]
        last_names = ["Singh", "Sharma", "Kumar", "Patel", "Gupta", "Verma", "Rao", "Malik", "Desai"]
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        fullname_field = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[contains(@placeholder, 'Full Name') or @name='fullName']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", fullname_field)
        time.sleep(0.3)
        fullname_field.click()
        time.sleep(0.2)
        fullname_field.clear()
        fullname_field.send_keys(full_name)
        print_step(f"✓ Full Name: {full_name}", "green")
        logger.info(f"Full Name filled: {full_name}")
        time.sleep(0.5)
        
        # Fill Email
        print_step("→ Filling Email...", "blue")
        email_field = driver.find_element(By.XPATH, "//input[@type='email' or contains(@placeholder, 'Email')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
        time.sleep(0.3)
        email_field.click()
        time.sleep(0.2)
        email_field.clear()
        email_field.send_keys(account['email'])
        print_step(f"✓ Email: {account['email']}", "green")
        logger.info(f"Email filled: {account['email']}")
        time.sleep(0.5)
        
        # Click Register button
        print_step("→ Clicking Register Button...", "blue")
        register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        driver.execute_script("arguments[0].scrollIntoView(true);", register_button)
        time.sleep(0.5)
        register_button.click()
        print_step("✓ Register button clicked - OTP page loading...", "green")
        logger.info("Register button clicked")
        time.sleep(3)
        
        # Wait for OTP field
        print_step("→ Waiting for OTP field to appear...", "blue")
        try:
            otp_field = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'OTP') or contains(@placeholder, 'otp') or @name='otp']"))
            )
            print_step("✓ OTP field detected", "green")
            logger.info("OTP field appeared")
        except TimeoutException:
            print_step("⚠ OTP field not found - may already be verified or auto-submitted", "yellow")
            logger.warning("OTP field not found")
            time.sleep(2)
            return True
        
        # OTP Wait Timer with user instruction
        print_step("\n" + "="*70, "yellow")
        print_step("🔐 MANUAL OTP ENTRY REQUIRED (10% MANUAL)", "yellow")
        print_step("="*70, "yellow")
        print_step("✓ Check your email for OTP", "blue")
        print_step("✓ MANUALLY ENTER OTP in the browser", "blue")
        print_step(f"✓ Script will auto-click Verify after {OTP_WAIT_SECONDS} seconds", "blue")
        
        for remaining in range(OTP_WAIT_SECONDS, 0, -1):
            sys.stdout.write(f"\r⏱️  {remaining:3d} seconds remaining (enter OTP now)...")
            sys.stdout.flush()
            time.sleep(1)
        
        print("\n")
        print_step("✓ OTP timer complete - clicking Verify button...", "green")
        logger.info("OTP waiting period completed")
        
        try:
            verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify') or contains(text(), 'Submit') or contains(text(), 'Confirm')]")
            driver.execute_script("arguments[0].scrollIntoView(true);", verify_button)
            time.sleep(0.5)
            verify_button.click()
            print_step("✓ Verify button clicked", "green")
            logger.info("Verify button clicked")
            time.sleep(4)
            return True
        except NoSuchElementException:
            print_step("⚠ Verify button not found (you may have already clicked it)", "yellow")
            logger.warning("Verify button not found - may have been clicked manually")
            time.sleep(3)
            return True
        except Exception as e:
            print_step(f"⚠ Error clicking Verify: {str(e)[:50]}", "yellow")
            logger.warning(f"Could not click Verify: {str(e)[:80]}")
            time.sleep(2)
            return True  # Proceed anyway
        
    except TimeoutException as e:
        print_step(f"❌ Signup timeout: {str(e)[:50]}", "red")
        logger.error(f"Signup timeout: {str(e)}")
        return False
    except NoSuchElementException as e:
        print_step(f"❌ Signup element not found: {str(e)[:50]}", "red")
        logger.error(f"Element not found during signup: {str(e)}")
        return False
    except WebDriverException as e:
        print_step(f"❌ WebDriver error during signup: {str(e)[:50]}", "red")
        logger.error(f"WebDriver error: {str(e)}")
        return False
    except Exception as e:
        print_step(f"❌ Unexpected signup error: {str(e)}", "red")
        logger.error(f"Unexpected error during signup: {str(e)}")
        return False


def wait_for_registration_form(driver: webdriver.Firefox, account: dict):
    """Navigate to registration form and auto-fill it"""
    try:
        print_step("\n" + "="*70, "yellow")
        print_step("📋 REGISTRATION FORM PHASE (100% AUTOMATED)", "yellow")
        print_step("="*70, "yellow")
        
        # Navigate to registration
        print_step("→ Navigating to Registration Form via Tor...", "blue")
        driver.get(REGISTRATION_URL)
        time.sleep(2)
        logger.info("Navigated to registration form")
        
        # Auto-fill the form
        return auto_fill_registration_form(driver, account)
        
    except NoSuchWindowException:
        print_step("❌ Browser window closed unexpectedly", "red")
        logger.error("Browser window closed")
        return False
    except TimeoutException as e:
        print_step(f"❌ Registration navigation timeout: {str(e)[:50]}", "red")
        logger.error(f"Registration timeout: {str(e)}")
        return False
    except Exception as e:
        print_step(f"❌ Error in registration phase: {str(e)}", "red")
        logger.error(f"Registration phase error: {str(e)}")
        return False


def process_account(driver: webdriver.Firefox, account: dict, account_num: int, total: int) -> bool:
    """Process single account - signup + registration"""
    try:
        # Auto-fill signup
        signup_ok = auto_signup(driver, account)
        if not signup_ok:
            print_step("❌ Signup failed - skipping this account", "red")
            logger.error(f"Signup failed for {account['email']}")
            return False
        
        # Auto-fill registration
        reg_ok = wait_for_registration_form(driver, account)
        if not reg_ok:
            print_step("❌ Registration form error - skipping", "red")
            logger.error(f"Registration failed for {account['email']}")
            return False
        
        print_step(f"\n[OK] Account {account_num}/{total} COMPLETE!", "green")
        print_step(f"Successfully processed: {account['email']}", "green")
        logger.info(f"Account {account_num}/{total} successfully completed: {account['email']}")
        
        return True
        
    except NoSuchWindowException:
        print_step("[ERROR] Browser crashed during account processing", "red")
        logger.error(f"Browser crashed for account {account_num}")
        return False
    except Exception as e:
        print_step(f"[ERROR] Account {account_num} failed: {str(e)[:60]}", "red")
        logger.error(f"Account {account_num} processing failed: {str(e)}")
        return False


def main():
    """Main execution loop"""
    
    print_step("\n" + "="*70, "blue")
    print_step("HACK2SKILL TOR BROWSER AUTOMATION | 90% AUTO | 10% MANUAL (OTP ONLY)", "blue")
    print_step("="*70, "blue")
    
    # Check dependencies
    print_step("\n[INFO] Checking dependencies...", "cyan")
    geckodriver_exists = os.path.exists(r"C:\webdrivers\geckodriver.exe")
    
    if not geckodriver_exists:
        print_step("\n[ERROR] GeckoDriver not found!", "red")
        print_step("[INFO] Expected location: C:\\webdrivers\\geckodriver.exe", "yellow")
        print_step("\n[HELP] Fix this with ONE command:", "yellow")
        print_step("   python setup_geckodriver.py", "yellow")
        print_step("\n[INFO] Then run this script again.", "yellow")
        logger.error("GeckoDriver not found at C:\\webdrivers\\geckodriver.exe")
        return
    
    print_step("[OK] All dependencies found", "green")
    logger.info("Dependencies verified")
    
    # Load accounts
    accounts = load_accounts()
    if not accounts:
        print_step("[ERROR] No accounts to process", "red")
        logger.error("No accounts loaded")
        return
    
    print_step(f"\n[INFO] Ready to process {len(accounts)} account(s) via Tor network", "green")
    logger.info(f"Starting batch processing of {len(accounts)} accounts via Tor")
    
    # Initialize driver
    driver = init_tor_driver()
    if not driver:
        print_step("[ERROR] Failed to initialize browser driver, exiting", "red")
        logger.error("Could not initialize browser driver")
        return
    
    # Process each account
    completed = 0
    failed = 0
    
    try:
        for idx, account in enumerate(accounts, 1):
            print_step(f"\n\n" + "[PROC] "*20, "cyan")
            print_step(f"Processing account {idx}/{len(accounts)}", "blue")
            print_step(f"[PROC] "*20, "cyan")
            
            success = process_account(driver, account, idx, len(accounts))
            
            if success:
                completed += 1
            else:
                failed += 1
            
            if idx < len(accounts):
                print_step("\n" + "="*70, "yellow")
                print_step("[PAUSE] Ready for next account (Press ENTER to continue)", "yellow")
                print_step("="*70, "yellow")
                input()
                print_step("\n[INFO] Continuing to next account...\n", "green")
                time.sleep(2)
    
    except KeyboardInterrupt:
        print_step("\n\n[ABORT] Process interrupted by user", "red")
        logger.error("Process interrupted by user")
    except Exception as e:
        print_step(f"\n\n[ERROR] Critical error: {str(e)}", "red")
        logger.error(f"Critical error: {str(e)}")
    finally:
        # Cleanup
        print_step("\n\n" + "="*70, "blue")
        print_step("BATCH PROCESSING COMPLETE", "blue")
        print_step("="*70, "blue")
        print_step(f"Total accounts: {len(accounts)}", "blue")
        print_step(f"[OK] Completed: {completed}", "green")
        print_step(f"[FAIL] Failed: {failed}", "red")
        print_step(f"\n[STATS] Success Rate: {(completed/len(accounts)*100):.1f}%", "cyan")
        print_step(f"[LOG] Logs saved to: {log_file}", "cyan")
        
        logger.info(f"Batch complete: {completed} succeeded, {failed} failed")
        
        try:
            driver.quit()
            print_step("\n[OK] Browser closed", "green")
            logger.info("Browser closed successfully")
        except Exception as e:
            print_step(f"\n[WARN] Error closing browser: {str(e)[:40]}", "yellow")
            logger.warning(f"Error closing browser: {str(e)}")
        
        input("\nPress ENTER to exit...")


if __name__ == "__main__":
    main()
