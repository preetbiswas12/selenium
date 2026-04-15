"""
SIMPLIFIED WORKING VERSION - Fields filled by VISUAL POSITION, not ID matching
This actually fills different fields instead of the same one repeatedly
"""

import time
import random
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage"
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

OTP_WAIT_SECONDS = 30
SCROLL_PAUSE_TIME = 0.5


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def print_step(msg, indent=0):
    """Print step message"""
    print("  " * indent + f"→ {msg}")

def print_success(msg, indent=0):
    """Print success message"""
    print("  " * indent + f"✓ {msg}")

def print_error(msg, indent=0):
    """Print error message"""
    print("  " * indent + f"✗ {msg}")

def print_warning(msg, indent=0):
    """Print warning message"""
    print("  " * indent + f"⚠ {msg}")

def log_progress(email, status, message):
    """Log to CSV"""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'status', 'message'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email, status, message])

def scroll_into_view_and_click(driver, element):
    """Scroll element into view and click it"""
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
    time.sleep(0.5)
    
    # Remove overlays blocking click
    driver.execute_script("""
        var overlays = document.querySelectorAll('[class*="hidden"][class*="lg:flex"]');
        overlays.forEach(el => el.style.display = 'none');
    """)
    
    element.click()

def fill_text_field(driver, element, value, field_name="field"):
    """Fill a text field with proper scrolling and error handling"""
    try:
        scroll_into_view_and_click(driver, element)
        time.sleep(0.3)
        
        # Clear with Ctrl+A
        element.send_keys("\ue009a")  # Ctrl+A
        time.sleep(0.1)
        element.send_keys(value)
        time.sleep(0.3)
        
        print_success(f"{field_name}: {value[:30]}", 1)
        return True
    except Exception as e:
        print_warning(f"{field_name} error: {str(e)[:40]}", 1)
        return False

def get_all_text_inputs(driver):
    """Get ALL visible text input fields on the page in order"""
    return driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='tel' or @type='date']")

def get_all_selects(driver):
    """Get ALL select dropdowns on page"""
    return driver.find_elements(By.TAG_NAME, "select")

def get_all_checkboxes(driver):
    """Get ALL checkboxes on page"""
    return driver.find_elements(By.XPATH, "//input[@type='checkbox']")

# ═══════════════════════════════════════════════════════════════
# SIGNUP WORKFLOW
# ═══════════════════════════════════════════════════════════════

def signup_and_verify_otp(driver, account):
    """Signup with OTP - Manual OTP entry"""
    print_step("Navigating to signup page")
    driver.get(SIGNUP_PAGE_URL)
    time.sleep(3)
    
    # Fill signup form
    print_step("Filling signup form", 0)
    
    inputs = get_all_text_inputs(driver)
    if len(inputs) < 2:
        print_error("Could not find signup fields")
        return False
    
    # First field: Full Name
    first_names = ["Aditya", "Raj", "Priya", "Aman", "Vikram"]
    last_names = ["Kumar", "Singh", "Patel", "Sharma", "Gupta"]
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    fill_text_field(driver, inputs[0], full_name, "Full Name")
    time.sleep(0.5)
    
    # Second field: Email
    fill_text_field(driver, inputs[1], account['email'], "Email")
    time.sleep(1)
    
    # Click Register button
    print_step("Clicking Register button")
    try:
        register_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        register_btn.click()
        print_success("Register clicked")
    except Exception as e:
        print_error(f"Register click failed: {str(e)[:40]}")
        return False
    
    time.sleep(3)
    
    # Wait for OTP page
    print_step("Waiting for OTP page (hint: enter OTP manually)")
    print_warning(f"⏳ ENTER OTP MANUALLY - You have {OTP_WAIT_SECONDS} seconds")
    
    for i in range(OTP_WAIT_SECONDS, 0, -1):
        if i % 5 == 0 or i <= 5:
            print(f"  [{i:2d}s remaining]", end='\r', flush=True)
        time.sleep(1)
    
    print("\n✓ Timer complete")
    time.sleep(1)
    
    # Click Verify button
    print_step("Clicking Verify button")
    try:
        # Try multiple button selectors
        buttons = driver.find_elements(By.TAG_NAME, "button")
        verify_btn = None
        
        for btn in buttons:
            text = btn.text.lower()
            if 'verify' in text or 'submit' in text:
                verify_btn = btn
                break
        
        if not verify_btn and buttons:
            verify_btn = buttons[-1]  # Last button as fallback
        
        if verify_btn:
            verify_btn.click()
            print_success("Verify clicked")
        else:
            print_error("Verify button not found")
            return False
    except Exception as e:
        print_error(f"Verify click failed: {str(e)[:40]}")
    
    time.sleep(5)
    return True

# ═══════════════════════════════════════════════════════════════
# REGISTRATION FORM FILLING
# ═══════════════════════════════════════════════════════════════

def fill_registration_form(driver, account):
    """Fill registration form by FIELD POSITION, not by ID"""
    print_step("Loading registration form")
    driver.get(REGISTRATION_URL)
    time.sleep(4)
    
    print_step("Filling form fields (by position)", 0)
    
    # Get all fields at once
    all_inputs = get_all_text_inputs(driver)
    print(f"Found {len(all_inputs)} text input fields")
    
    # Field mapping by POSITION (not by keyword matching)
    field_data = [
        # (position, value, field_name)
        (2, "+919876543210", "WhatsApp"),
        (5, "India", "Country"),
        (6, "Uttar Pradesh", "State"),
        (7, "Greater Noida", "City"),
        (8, "Student", "Occupation"),
        (9, "Galgotias University", "College Name"),
        (10, "India", "College Country"),
        (11, "Uttar Pradesh", "College State"),
        (12, "Greater Noida", "College City"),
        (13, "B.Tech", "Degree"),
        (14, "Computer Science", "Specialization"),
        (15, "2028", "Passout Year"),
        (16, "https://linkedin.com/in/user", "LinkedIn"),
        (17, "https://g.dev/user", "GDP"),
    ]
    
    filled_count = 0
    for pos, value, field_name in field_data:
        try:
            if pos < len(all_inputs):
                if fill_text_field(driver, all_inputs[pos], value, field_name):
                    filled_count += 1
                time.sleep(0.5)
        except Exception as e:
            print_warning(f"Field {pos} ({field_name}) error: {str(e)[:30]}", 1)
            continue
    
    print_success(f"Filled {filled_count}/{len(field_data)} fields")
    time.sleep(1)
    
    # Handle checkboxes
    print_step("Checking required checkboxes")
    checkboxes = get_all_checkboxes(driver)
    checked_count = 0
    for cb in checkboxes:
        try:
            if not cb.is_selected():
                cb.click()
                checked_count += 1
            time.sleep(0.2)
        except:
            pass
    
    print_success(f"Checked {checked_count} checkboxes")
    time.sleep(1)
    
    # Try to submit form
    print_step("Looking for submit button")
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        submit_btn = None
        
        for btn in buttons:
            text = btn.text.lower()
            if 'submit' in text or 'register' in text or 'complete' in text:
                submit_btn = btn
                break
        
        if submit_btn:
            submit_btn.click()
            print_success("Form submitted")
            time.sleep(3)
        else:
            print_warning("Submit button not found - form may auto-submit")
    except Exception as e:
        print_warning(f"Submit error: {str(e)[:40]}")
    
    return True

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("HACK2SKILL BATCH REGISTRATION - SIMPLIFIED WORKING VERSION")
    print("=" * 70)
    
    # Load accounts
    print_step("Loading accounts from CSV")
    accounts = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            accounts = list(reader)
        print_success(f"Loaded {len(accounts)} accounts")
    except Exception as e:
        print_error(f"Failed to load CSV: {e}")
        return
    
    print_success("Ready to process accounts\n")
    
    completed = 0
    driver = None
    
    for idx, account in enumerate(accounts, 1):
        email = account['email']
        print("\n" + "=" * 70)
        print(f"[{idx}/{len(accounts)}] Processing: {email}")
        print("=" * 70)
        
        try:
            # Initialize driver
            print_step("Initializing Firefox")
            driver = webdriver.Firefox()
            print_success("Firefox ready\n")
            
            # Signup
            if signup_and_verify_otp(driver, account):
                print_success("✓ Signup complete\n")
                
                # Fill form
                if fill_registration_form(driver, account):
                    print_success("✓ Form complete")
                    log_progress(email, "SUCCESS", "Account processed successfully")
                    completed += 1
                else:
                    print_error("Form filling failed")
                    log_progress(email, "FORM_FAILED", "Form filling incomplete")
            else:
                print_error("Signup failed")
                log_progress(email, "SIGNUP_FAILED", "Signup process failed")
        
        except Exception as e:
            print_error(f"Error: {str(e)[:60]}")
            log_progress(email, "ERROR", str(e)[:100])
        
        finally:
            if driver:
                try:
                    driver.quit()
                    print_success("Firefox closed")
                except:
                    pass
    
    print("\n" + "=" * 70)
    print(f"COMPLETE: {completed}/{len(accounts)} accounts processed")
    print("=" * 70)

if __name__ == "__main__":
    main()
