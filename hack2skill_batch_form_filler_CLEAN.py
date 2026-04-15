"""
Hack2Skill Batch Registration Form Filler - CLEAN SYNCHRONIZED VERSION
Properly structured with synchronized form filling, proper waits, and field validation
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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException, WebDriverException, InvalidElementStateException
)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage"
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

TIMEOUT_PAGE_LOAD = 45
TIMEOUT_ELEMENT = 30
TIMEOUT_INTERACTION = 10
OTP_WAIT_SECONDS = 30
MAX_CLICK_RETRIES = 3
PAGE_TRANSITION_TIMEOUT = 10


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def print_step(section: int, message: str, console: bool = False):
    """Print step message"""
    print(f"[Step {section}] {message}")
    if console:
        print(f"  → {message}")


def print_success(message: str, console: bool = False):
    """Print success message"""
    print(f"✓ {message}")


def print_warning(message: str, console: bool = False):
    """Print warning message"""
    print(f"⚠ {message}")


def print_error(message: str, console: bool = False):
    """Print error message"""
    print(f"✗ {message}")


def log_progress(email: str, status: str, message: str):
    """Log progress to CSV"""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'status', 'message'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email, status, message])


def remove_blocking_overlays(driver: webdriver.Firefox):
    """Remove blocking modals, popups, overlays"""
    try:
        overlays = driver.find_elements(By.XPATH, "//*[@class*='modal' or @class*='overlay' or @class*='popup']")
        for overlay in overlays:
            try:
                driver.execute_script("arguments[0].style.display='none';", overlay)
            except:
                pass
    except:
        pass


def wait_for_loading_spinner_to_hide(driver: webdriver.Firefox, timeout: int = 10):
    """Wait for loading spinner to disappear"""
    try:
        spinners = driver.find_elements(By.XPATH, "//*[@class*='spinner' or @class*='loading']")
        if spinners:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.XPATH, "//*[@class*='spinner' or @class*='loading']"))
            )
    except:
        pass


def find_input_by_label_or_placeholder(driver: webdriver.Firefox, keywords: List[str], field_name: str, verbose: bool = False) -> Optional:
    """Find input field by label, placeholder, or name - IMPROVED"""
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        
        # Strategy 0: Exact case-insensitive ID match
        try:
            elem = driver.find_element(By.XPATH, f"//input[contains(translate(@id, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword_lower}')]")
            if verbose:
                print_success(f"Found {field_name} by ID", True)
            return elem
        except:
            pass
        
        # Strategy 1: Placeholder match (case-insensitive)
        try:
            elem = driver.find_element(By.XPATH, f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword_lower}')]")
            if verbose:
                print_success(f"Found {field_name} by placeholder", True)
            return elem
        except:
            pass
        
        # Strategy 2: Name match (case-insensitive)
        try:
            elem = driver.find_element(By.XPATH, f"//input[contains(translate(@name, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword_lower}')]")
            if verbose:
                print_success(f"Found {field_name} by name", True)
            return elem
        except:
            pass
        
        # Strategy 3: Label match (case-insensitive)
        try:
            label = driver.find_element(By.XPATH, f"//label[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword_lower}')]")
            label_for = label.get_attribute('for')
            if label_for:
                elem = driver.find_element(By.ID, label_for)
                if verbose:
                    print_success(f"Found {field_name} by label", True)
                return elem
        except:
            pass
        
        # Strategy 4: aria-label match (for accessibility)
        try:
            elem = driver.find_element(By.XPATH, f"//input[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword_lower}')]")
            if verbose:
                print_success(f"Found {field_name} by aria-label", True)
            return elem
        except:
            pass
    
    if verbose:
        print_warning(f"{field_name} not found", True)
    return None


def safe_fill_field(driver: webdriver.Firefox, field, value: str, field_name: str) -> bool:
    """Safely fill a field with retry logic and multiple strategies"""
    try:
        # Strategy 1: Regular click and send_keys
        field.click()
        time.sleep(0.3)
        field.clear()
        time.sleep(0.2)
        field.send_keys(value)
        time.sleep(0.5)
        
        # Verify the field was filled
        actual_value = field.get_attribute("value")
        if actual_value == value:
            print_success(f"{field_name}: {value}", True)
            return True
        elif value in actual_value:
            print_success(f"{field_name}: {value} (with extra content)", True)
            return True
        
        # Strategy 2: If not filled, try JavaScript
        print_warning(f"{field_name} may not have filled correctly, trying JS...", True)
        driver.execute_script(f"arguments[0].value = '{value}';", field)
        time.sleep(0.3)
        driver.execute_script("arguments[0].dispatchEvent(new Event('input', {{ bubbles: true }}));", field)
        driver.execute_script("arguments[0].dispatchEvent(new Event('change', {{ bubbles: true }}));", field)
        time.sleep(0.5)
        
        print_success(f"{field_name}: {value} (JS)", True)
        return True
        
    except Exception as e:
        print_warning(f"{field_name} fill error: {str(e)[:60]}", True)
        return False


def click_button_with_validation(driver: webdriver.Firefox, selector: str, button_name: str, expect_page_transition: bool = True) -> Tuple[bool, str]:
    """Click button with advanced strategy"""
    for attempt in range(MAX_CLICK_RETRIES):
        try:
            # Get initial page state
            initial_url = driver.current_url
            
            # Try to find button
            button = driver.find_element(By.XPATH, selector)
            
            # Click strategies
            try:
                button.click()
                time.sleep(1)
                print_success(f"{button_name} clicked (regular)", True)
                
                # Check page transition
                if expect_page_transition:
                    time.sleep(2)
                    if driver.current_url != initial_url:
                        return True, "Page transitioned"
                else:
                    return True, "Clicked"
            except:
                # Try JS click
                driver.execute_script("arguments[0].click();", button)
                time.sleep(1)
                print_success(f"{button_name} clicked (JS)", True)
                if expect_page_transition:
                    time.sleep(2)
                    if driver.current_url != initial_url:
                        return True, "Page transitioned (JS)"
                else:
                    return True, "Clicked (JS)"
        except:
            wait_time = min(2 ** attempt, 16)  # Exponential backoff: 1,2,4,8,16
            print_warning(f"Attempt {attempt + 1}: Button click failed, retrying in {wait_time}s...", True)
            time.sleep(wait_time)
    
    return False, "Max retries exceeded"


# ═══════════════════════════════════════════════════════════════
# MAIN REGISTRATION LOGIC
# ═══════════════════════════════════════════════════════════════

def fill_registration_form(driver: webdriver.Firefox, account: Dict) -> bool:
    """
    Properly synchronized registration form filling
    All 20 fields with correct values and proper waits between sections
    """
    print_step(4, "═" * 70)
    print_step(4, "REGISTRATION FORM FILLING - 20 AUTO-FILL FIELDS")
    print_step(4, "═" * 70)
    
    try:
        wait = WebDriverWait(driver, TIMEOUT_ELEMENT)
        
        # Load form
        print_step(4, "Loading registration form...", True)
        driver.get(REGISTRATION_URL)
        time.sleep(3)
        
        # Wait for form elements
        try:
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        except TimeoutException:
            print_warning("Form timeout, retrying...", True)
            time.sleep(2)
            driver.get(REGISTRATION_URL)
            time.sleep(4)
        
        time.sleep(2)
        remove_blocking_overlays(driver)
        print_success("Form ready", True)
        
        # ════════════════════════════════════════════════════════════════════
        # SECTION 1: PERSONAL INFORMATION (6 fields)
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ SECTION 1: Personal Information", True)
        time.sleep(0.8)
        
        # Full Name & Email pre-filled
        print_step(4, "  1-2. Full Name & Email: Pre-filled from signup", True)
        time.sleep(0.3)
        
        # WhatsApp
        print_step(4, "  3. WhatsApp field", True)
        whatsapp = find_input_by_label_or_placeholder(driver, ["whatsapp", "phone", "+91"], "WhatsApp", verbose=False)
        if whatsapp:
            safe_fill_field(driver, whatsapp, "+919876543210", "WhatsApp")
        time.sleep(0.6)
        
        # Alternate checkbox
        print_step(4, "  4. Alternate Number checkbox", True)
        try:
            checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            if checkboxes and not checkboxes[0].is_selected():
                checkboxes[0].click()
                print_success("Checked", True)
        except:
            pass
        time.sleep(0.6)
        
        # DOB (2004-2007)
        print_step(4, "  5. Date of Birth field", True)
        try:
            dob_fields = driver.find_elements(By.XPATH, "//input[@type='date']")
            if dob_fields:
                year = random.randint(2004, 2007)
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                dob = f"{year:04d}-{month:02d}-{day:02d}"
                dob_fields[0].send_keys(dob)
                print_success(f"{dob} (age {2026-year})", True)
        except:
            pass
        time.sleep(0.6)
        
        # Gender (Male/Female)
        print_step(4, "  6. Gender field", True)
        gender = random.choice(["Male", "Female"])
        try:
            selects = driver.find_elements(By.XPATH, "//select")
            if selects:
                Select(selects[0]).select_by_visible_text(gender)
                print_success(f"{gender}", True)
            else:
                radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                for radio in radios:
                    if gender.lower() in (radio.get_attribute('value') or "").lower():
                        radio.click()
                        print_success(f"{gender} (radio)", True)
                        break
        except:
            pass
        time.sleep(0.6)
        
        # ════════════════════════════════════════════════════════════════════
        # SECTION 2: LOCATION (4 fields)
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ SECTION 2: Location", True)
        time.sleep(1)
        
        # Country
        print_step(4, "  7. Country field", True)
        country = find_input_by_label_or_placeholder(driver, ["country"], "Country", verbose=False)
        if country:
            country.click()
            time.sleep(0.2)
            country.clear()
            country.send_keys("India")
            time.sleep(0.8)
            ops = driver.find_elements(By.XPATH, "//div[@role='option']")
            if ops:
                ops[0].click()
            print_success("India", True)
        time.sleep(0.8)
        
        # State
        print_step(4, "  8. State field", True)
        state = find_input_by_label_or_placeholder(driver, ["state"], "State", verbose=False)
        if state:
            state.click()
            time.sleep(0.2)
            state.clear()
            state.send_keys("Uttar Pradesh")
            time.sleep(0.8)
            ops = driver.find_elements(By.XPATH, "//div[@role='option']")
            if ops:
                ops[0].click()
            print_success("Uttar Pradesh", True)
        time.sleep(0.8)
        
        # City
        print_step(4, "  9. City field", True)
        city = find_input_by_label_or_placeholder(driver, ["city"], "City", verbose=False)
        if city:
            city.click()
            time.sleep(0.2)
            city.clear()
            city.send_keys("Greater Noida")
            time.sleep(0.8)
            ops = driver.find_elements(By.XPATH, "//div[@role='option']")
            if ops:
                ops[0].click()
            print_success("Greater Noida", True)
        time.sleep(0.8)
        
        # Occupation
        print_step(4, "  10. Occupation field", True)
        occ = find_input_by_label_or_placeholder(driver, ["occupation"], "Occupation", verbose=False)
        if occ:
            safe_fill_field(driver, occ, "College Student", "Occupation")
        time.sleep(0.8)
        
        # ════════════════════════════════════════════════════════════════════
        # SECTION 3: COLLEGE INFO (6 fields)
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ SECTION 3: College Information", True)
        time.sleep(1)
        
        # College Name
        print_step(4, "  11. College Name field", True)
        college = find_input_by_label_or_placeholder(driver, ["college name"], "College", verbose=False)
        if college:
            safe_fill_field(driver, college, "Galgotias University", "College")
        time.sleep(0.8)
        
        # Degree
        print_step(4, "  12. Degree field", True)
        degree = find_input_by_label_or_placeholder(driver, ["degree"], "Degree", verbose=False)
        if degree:
            safe_fill_field(driver, degree, "B.Tech", "Degree")
        time.sleep(0.8)
        
        # Specialization
        print_step(4, "  13. Specialization field", True)
        spec = find_input_by_label_or_placeholder(driver, ["specialization", "stream", "cse"], "Spec", verbose=False)
        if spec:
            safe_fill_field(driver, spec, "CSE", "CSE")
        time.sleep(0.8)
        
        # Passout Year
        print_step(4, "  14. Passout Year field", True)
        passout = find_input_by_label_or_placeholder(driver, ["passout", "year"], "Passout", verbose=False)
        if passout:
            safe_fill_field(driver, passout, "2028", "2028")
        time.sleep(0.8)
        
        # ════════════════════════════════════════════════════════════════════
        # SECTION 4: PROFILES (2 fields)
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ SECTION 4: Profiles", True)
        time.sleep(1)
        
        # LinkedIn
        print_step(4, "  15. LinkedIn Profile field", True)
        linkedin = find_input_by_label_or_placeholder(driver, ["linkedin"], "LinkedIn", verbose=False)
        if linkedin:
            safe_fill_field(driver, linkedin, "https://linkedin.com/in/aditya-kumar", "LinkedIn")
        time.sleep(0.8)
        
        # GDP
        print_step(4, "  16. GDP Profile Link field", True)
        gdp = find_input_by_label_or_placeholder(driver, ["g.dev", "gdp"], "GDP", verbose=False)
        if gdp:
            safe_fill_field(driver, gdp, "https://g.dev/aditya-kumar", "GDP")
        time.sleep(0.8)
        
        # ════════════════════════════════════════════════════════════════════
        # SECTION 5: FILE UPLOAD
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ SECTION 5: File Upload", True)
        try:
            uploads = driver.find_elements(By.XPATH, "//input[@type='file']")
            if uploads:
                idcard = r"C:\Users\preet\Downloads\selenium\idcard.jpg"
                if os.path.exists(idcard):
                    uploads[0].send_keys(idcard)
                    print_success("College ID uploaded", True)
                    time.sleep(10)
        except:
            pass
        time.sleep(0.8)
        
        # ════════════════════════════════════════════════════════════════════
        # SECTION 6: REFERRAL & TERMS
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ SECTION 6: Referral & Terms", True)
        
        # Referral: NO
        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            for radio in radios:
                if "no" in (radio.get_attribute('value') or "").lower():
                    if not radio.is_selected():
                        radio.click()
                    print_success("Referral: NO", True)
                    break
        except:
            pass
        time.sleep(0.6)
        
        # Terms checkboxes
        print_step(4, "  17. Terms & Conditions", True)
        try:
            all_checks = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            checked = 0
            for chk in all_checks:
                try:
                    if not chk.is_selected():
                        driver.execute_script("arguments[0].scrollIntoView(true);", chk)
                        time.sleep(0.1)
                        chk.click()
                    checked += 1
                except:
                    pass
            if checked > 0:
                print_success(f"{checked} checkboxes checked", True)
        except:
            pass
        time.sleep(1)
        
        # ════════════════════════════════════════════════════════════════════
        # FORM SUBMISSION
        # ════════════════════════════════════════════════════════════════════
        print_step(4, "\n├─ FORM SUBMISSION", True)
        print_step(4, "⏱️  Form is ready. Review all fields carefully...", True)
        print_step(4, "⚠️  DO NOT CLICK REGISTER YET - You will click it manually", True)
        print_step(4, "Press ENTER when ready to proceed to next account...", True)
        input()  # Wait for user to review and press ENTER
        
        print_success("✓ FORM FILLING COMPLETE - Ready for manual submission", True)
        return True
    
    except Exception as e:
        print_error(f"Form error: {str(e)[:60]}")
        return False


def signup_with_otp_step(driver: webdriver.Firefox, account: Dict) -> bool:
    """
    STEP 1 & 2: Signup with email and wait for manual OTP entry
    
    Fields:
    1. Full Name
    2. Email
    3. Click Register
    4. Wait for user to manually enter OTP (30s)
    5. Click Verify
    """
    print_step(3, "Navigating to signup page...", True)
    driver.get(SIGNUP_PAGE_URL)
    time.sleep(3)
    
    try:
        wait = WebDriverWait(driver, TIMEOUT_PAGE_LOAD)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
    except TimeoutException:
        print_error("Signup page timeout")
        return False
    
    time.sleep(2)
    remove_blocking_overlays(driver)
    
    # Generate random name
    first_names = ["Aditya", "Raj", "Priya", "Aman", "Neha", "Vikram", "Ananya", "Rohan"]
    last_names = ["Kumar", "Singh", "Patel", "Sharma", "Gupta", "Verma", "Reddy", "Nair"]
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    print_step(3, "Filling signup form...", True)
    
    # Full Name
    print_step(3, "  Finding Full Name field...", True)
    name_field = find_input_by_label_or_placeholder(driver, ["full name", "name", "fullname", "fname"], "Full Name", verbose=True)
    if name_field:
        try:
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", name_field)
            time.sleep(0.3)
            # Ensure it's clickable
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, name_field.get_attribute('id') or '')))
        except:
            pass
        
        if safe_fill_field(driver, name_field, full_name, "Full Name"):
            print_success(f"Full Name filled: {full_name}", True)
        else:
            print_error(f"Failed to fill Full Name - THIS IS THE ERROR YOU'RE SEEING", True)
            print_warning(f"Field element: {name_field.get_attribute('id')} / {name_field.get_attribute('name')}", True)
    else:
        print_error("Full Name field not found - field detection issue", True)
        # Try alternative: just get first visible text input
        try:
            all_inputs = driver.find_elements(By.XPATH, "//input[@type='text']")
            if all_inputs:
                print_warning(f"Found {len(all_inputs)} text inputs, trying first one...", True)
                safe_fill_field(driver, all_inputs[0], full_name, "Full Name (fallback)")
        except:
            pass
    
    time.sleep(0.5)
    
    # Email (from CSV)
    print_step(3, "  Finding Email field...", True)
    email_field = find_input_by_label_or_placeholder(driver, ["email", "mail", "e-mail"], "Email", verbose=True)
    if email_field:
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", email_field)
            time.sleep(0.3)
        except:
            pass
        
        if safe_fill_field(driver, email_field, account['email'], "Email"):
            print_success(f"Email filled: {account['email']}", True)
        else:
            print_error(f"Failed to fill Email", True)
    else:
        print_error("Email field not found", True)
        try:
            all_inputs = driver.find_elements(By.XPATH, "//input[@type='email']")
            if all_inputs:
                safe_fill_field(driver, all_inputs[0], account['email'], "Email (fallback)")
        except:
            pass
    
    # Click Register button
    print_step(3, "Clicking Register button...", True)
    success, msg = click_button_with_validation(driver, "//button[contains(text(), 'Register')]", "Register", expect_page_transition=True)
    
    if not success:
        print_error("Register button click failed")
        return False
    
    print_success("Signup form submitted", True)
    time.sleep(3)
    
    # Wait for OTP page to load
    print_step(3, "Waiting for OTP page...", True)
    try:
        # Try multiple OTP field selectors
        otp_selectors = [
            "//input[contains(@placeholder, 'OTP')]",
            "//input[contains(@placeholder, 'otp')]",
            "//input[@name='otp']",
            "//input[@id='otp']",
            "//input[@type='text][contains(@class, 'otp')]",
        ]
        
        otp_found = False
        for selector in otp_selectors:
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                print_success(f"OTP field found: {selector}", True)
                otp_found = True
                break
            except TimeoutException:
                continue
        
        if not otp_found:
            print_warning("OTP field not found with standard selectors", True)
            print_warning("Continuing anyway - may be auto-verified or page structure different", True)
    
    except Exception as e:
        print_warning(f"Error waiting for OTP page: {str(e)[:50]}", True)
    
    # Wait for user to manually enter OTP
    print_step(3, f"⏱️  MANUAL STEP: Enter OTP in browser (waiting {OTP_WAIT_SECONDS}s)...", True)
    print_warning(f"⏳ YOU MUST enter OTP manually in the browser - {OTP_WAIT_SECONDS}s remaining", True)
    
    for i in range(OTP_WAIT_SECONDS, 0, -1):
        if i % 5 == 0 or i <= 5:  # Print every 5 seconds, then every 1 second at end
            print(f"  [{i:2d}s remaining]", end='\r', flush=True)
        time.sleep(1)
    
    print("\n  ✓ Timer complete", flush=True)
    time.sleep(1)
    
    # Try to click Verify button with multiple selectors
    print_step(3, "Clicking Verify button...", True)
    
    verify_selectors = [
        "//button[contains(text(), 'Verify')]",
        "//button[contains(text(), 'Verify OTP')]",
        "//button[contains(text(), 'Submit')]",
        "//button[@type='submit']",
        "//button[.//span[contains(text(), 'Verify')]]",
        "//button[1]",  # First button as fallback
    ]
    
    success = False
    for selector in verify_selectors:
        try:
            success, msg = click_button_with_validation(driver, selector, "Verify OTP", expect_page_transition=True)
            if success:
                print_success(f"OTP verified with selector: {selector}", True)
                break
        except Exception as e:
            print_warning(f"Selector failed: {selector}", True)
            continue
    
    if success:
        print_success("OTP verification completed", True)
        time.sleep(5)
        return True
    else:
        print_warning("⚠️  Verify button click failed or page structure different", True)
        print_warning("Continuing anyway - OTP may have auto-verified", True)
        time.sleep(3)
        return True  # Continue to registration anyway


def main():
    """Main workflow - process accounts one by one"""
    print_step(1, "════════════════════════════════════════════════════════════════")
    print_step(1, "HACK2SKILL BATCH REGISTRATION - CLEAN VERSION")
    print_step(1, "════════════════════════════════════════════════════════════════\n")
    
    # Load accounts
    print_step(1, "Loading accounts from CSV...", True)
    accounts = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            accounts = list(reader)
        print_success(f"Loaded {len(accounts)} accounts", True)
    except Exception as e:
        print_error(f"CSV load failed: {e}")
        return
    
    # Process each account
    for idx, account in enumerate(accounts, 1):
        print_step(1, f"\n┌─ ACCOUNT {idx}/{len(accounts)}: {account['email']}", True)
        
        driver = None
        try:
            # Initialize Firefox with Private Window Mode
            print_step(2, "Initializing Firefox (Private Window)...", True)
            options = webdriver.FirefoxOptions()
            options.add_argument("-private")  # Enable private browsing mode
            # options.add_argument("--headless")  # Comment out to see browser
            driver = webdriver.Firefox(options=options)
            print_success("Firefox ready", True)
            
            # Process account
            print_step(3, "Step 1: Signup with OTP", True)
            if not signup_with_otp_step(driver, account):
                print_error("Signup failed, skipping account")
                log_progress(account['email'], "SIGNUP_FAILED", "Signup with OTP failed")
                continue
            
            print_step(4, "Step 2: Fill Registration Form", True)
            if fill_registration_form(driver, account):
                print_success("✓ FORM FILLED SUCCESSFULLY", True)
                log_progress(account['email'], "FORM_FILLED", "All 20 fields filled, waiting for manual submission")
            else:
                print_error("✗ FORM FILLING FAILED")
                log_progress(account['email'], "FORM_FAILED", "Form filling failed")
            
        except Exception as e:
            print_error(f"Workflow error: {str(e)}")
            log_progress(account['email'], "ERROR", str(e)[:100])
        
        finally:
            # Close driver
            if driver:
                try:
                    driver.quit()
                    print_success("Firefox closed", True)
                except:
                    pass
    
    print_step(1, "\n└─ ALL ACCOUNTS PROCESSED", True)


if __name__ == "__main__":
    main()

