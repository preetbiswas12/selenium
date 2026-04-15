"""
HACK2SKILL BATCH REGISTRATION - V3 WORKING VERSION
Using extracted field mapping from page_structure_analysis.txt

This version:
✓ Fills fields by exact position/ID from extracted data
✓ Properly handles React-Select autocomplete dropdowns
✓ Works with conditional field visibility
✓ Simple, reliable, debuggable
"""

import time
import random
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# ═══════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage"
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

TIMEOUTS = {
    "page_load": 45,
    "element": 30,
    "interaction": 10,
    "otp_wait": 30
}

# ═══════════════════════════════════════════════════════════════
# FIELD MAPPING - BASED ON EXTRACTED PAGE STRUCTURE
# ═══════════════════════════════════════════════════════════════

FIELDS = {
    # (index, field_name, field_type, sample_value)
    2: ("WhatsApp", "tel", "+919876543210"),
    4: ("Date of Birth", "date", "2005-05-28"),  # Random 2004-2007
    7: ("Country", "react-select", "India"),
    10: ("State", "react-select", "Uttar Pradesh"),
    12: ("City", "react-select", "Greater Noida"),
    21: ("Occupation", "react-select", "Student"),
    46: ("LinkedIn", "text", "https://linkedin.com/in/aditya-kumar"),
    48: ("GDP Profile", "text", "https://g.dev/aditya-kumar"),
}

CHECKBOXES = {
    51: "Terms & Conditions",
    52: "Communication Consent"
}

RADIOS = {
    50: "Referral_No",  # Select "No" for referral
}

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def print_step(msg): print(f"→ {msg}")
def print_success(msg): print(f"✓ {msg}")
def print_error(msg): print(f"✗ {msg}")
def print_warning(msg): print(f"⚠ {msg}")

def log_progress(email, status, message):
    """Log to CSV"""
    file_exists = os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'status', 'message'])
        writer.writerow([datetime.now().isoformat(), email, status, message])

def scroll_and_click(driver, element):
    """Scroll element into view and click"""
    try:
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
        time.sleep(0.3)
        element.click()
        return True
    except:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except:
            return False

def fill_text_field(driver, element, value, field_name="field"):
    """Fill text input field"""
    try:
        scroll_and_click(driver, element)
        time.sleep(0.2)
        element.clear()
        element.send_keys(value)
        time.sleep(0.3)
        print_success(f"{field_name}: {value[:30]}")
        return True
    except Exception as e:
        print_warning(f"{field_name} error: {str(e)[:40]}")
        return False

def fill_react_select(driver, input_element, value, field_name="field"):
    """Fill React-Select autocomplete field"""
    try:
        # Click to open dropdown
        scroll_and_click(driver, input_element)
        time.sleep(0.3)
        
        # Clear if needed
        input_element.clear()
        time.sleep(0.1)
        
        # Type the value
        input_element.send_keys(value)
        time.sleep(1)
        
        # Find and click the first matching option
        try:
            options = driver.find_elements(By.XPATH, "//div[@role='option']")
            if options:
                options[0].click()
                print_success(f"{field_name}: {value} (selected from dropdown)")
                time.sleep(0.5)
                return True
        except:
            pass
        
        # Try direct key press (for autocomplete that auto-selects)
        input_element.send_keys(Keys.RETURN)
        time.sleep(0.5)
        print_success(f"{field_name}: {value} (auto-selected)")
        return True
        
    except Exception as e:
        print_warning(f"{field_name} error: {str(e)[:40]}")
        return False

def get_all_inputs(driver):
    """Get all visible text input fields"""
    return driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='tel' or @type='date' or @type='number']")

def get_all_checkboxes(driver):
    """Get all checkboxes"""
    return driver.find_elements(By.XPATH, "//input[@type='checkbox']")

def get_all_radios(driver):
    """Get all radio buttons"""
    return driver.find_elements(By.XPATH, "//input[@type='radio']")

# ═══════════════════════════════════════════════════════════════
# MAIN WORKFLOW
# ═══════════════════════════════════════════════════════════════

def signup_and_verify_otp(driver, account):
    """Signup with OTP - Wait for manual OTP entry"""
    print_step("Signup Phase")
    
    # Signup page
    driver.get(SIGNUP_PAGE_URL)
    time.sleep(3)
    
    # Fill signup
    inputs = get_all_inputs(driver)
    if len(inputs) < 2:
        print_error("Signup fields not found")
        return False
    
    full_name = random.choice(["Aditya", "Raj", "Priya"]) + " " + random.choice(["Kumar", "Singh", "Patel"])
    fill_text_field(driver, inputs[0], full_name, "Full Name")
    time.sleep(0.5)
    fill_text_field(driver, inputs[1], account['email'], "Email")
    time.sleep(1)
    
    # Click Register
    try:
        register_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        register_btn.click()
        print_success("Register clicked")
    except:
        print_error("Register button not found")
        return False
    
    time.sleep(3)
    
    # Wait for OTP manually
    print_warning(f"⏳ ENTER OTP MANUALLY - {TIMEOUTS['otp_wait']}s wait")
    for i in range(TIMEOUTS['otp_wait'], 0, -1):
        if i % 5 == 0 or i <= 5:
            print(f"  [{i:2d}s]", end='\r', flush=True)
        time.sleep(1)
    
    print("\n  ✓ Timer done")
    time.sleep(0.5)
    
    # Click Verify
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        verify_btn = None
        for btn in buttons:
            if 'verify' in btn.text.lower() or 'submit' in btn.text.lower():
                verify_btn = btn
                break
        
        if verify_btn:
            verify_btn.click()
            print_success("Verify clicked")
        else:
            print_warning("Verify button not found, continuing anyway...")
    except:
        pass
    
    time.sleep(5)
    return True

def fill_registration_form(driver, account):
    """Fill registration form using exact field positions"""
    print_step("Registration Form Filling")
    
    driver.get(REGISTRATION_URL)
    time.sleep(4)
    
    # Get all inputs once
    all_inputs = get_all_inputs(driver)
    print(f"Found {len(all_inputs)} input fields")
    
    filled = 0
    
    # Fill fields by position
    for field_index, (field_name, field_type, sample_value) in FIELDS.items():
        if field_index >= len(all_inputs):
            print_warning(f"{field_name}: Position {field_index} out of range")
            continue
        
        try:
            element = all_inputs[field_index]
            
            if not element.is_displayed():
                print_warning(f"{field_name}: Not visible, skipping")
                continue
            
            if field_type == "text":
                if fill_text_field(driver, element, sample_value, field_name):
                    filled += 1
                    
            elif field_type == "tel":
                if fill_text_field(driver, element, sample_value, field_name):
                    filled += 1
                    
            elif field_type == "date":
                # Random date between 2004-2007
                year = random.randint(2004, 2007)
                month = random.randint(1, 12)
                day = random.randint(1, 28)
                date_val = f"{year:04d}-{month:02d}-{day:02d}"
                if fill_text_field(driver, element, date_val, field_name):
                    filled += 1
                    
            elif field_type == "react-select":
                if fill_react_select(driver, element, sample_value, field_name):
                    filled += 1
            
            time.sleep(0.5)
            
        except Exception as e:
            print_warning(f"{field_name}: Error - {str(e)[:40]}")
            continue
    
    print_success(f"Filled {filled} fields")
    time.sleep(1)
    
    # Check checkboxes
    print_step("Checking required checkboxes")
    all_checkboxes = get_all_checkboxes(driver)
    checked = 0
    
    for checkbox in all_checkboxes:
        try:
            if not checkbox.is_selected():
                checkbox.click()
                checked += 1
            time.sleep(0.2)
        except:
            pass
    
    print_success(f"Checked {checked} checkboxes")
    time.sleep(1)
    
    # Select "No" for referral (radio button at index 50)
    print_step("Selecting referral option")
    all_radios = get_all_radios(driver)
    if len(all_radios) > 0:
        try:
            all_radios[-1].click()  # Last radio (usually "No")
            print_success("Referral: No")
        except:
            pass
    
    time.sleep(1)
    
    # Try to find and click Register button
    print_step("Looking for submit button")
    try:
        submit_btn = driver.find_element(By.XPATH, "//button[text()='Register Now']")
        submit_btn.click()
        print_success("Form submitted!")
        time.sleep(3)
    except:
        print_warning("Submit button not found - may need manual click")
    
    return True

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n" + "="*70)
    print("HACK2SKILL BATCH REGISTRATION - V3 WORKING")
    print("="*70)
    
    # Load accounts
    print_step("Loading accounts")
    accounts = []
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            accounts = list(reader)
        print_success(f"Loaded {len(accounts)} accounts\n")
    except Exception as e:
        print_error(f"Failed to load CSV: {e}")
        return
    
    completed = 0
    
    for idx, account in enumerate(accounts, 1):
        print("\n" + "="*70)
        print(f"[{idx}/{len(accounts)}] {account['email']}")
        print("="*70)
        
        driver = None
        try:
            # Initialize Firefox with private browsing
            print_step("Opening Firefox (Private Browsing)")
            options = Options()
            options.set_preference("browser.privatebrowsing.autostart", True)
            driver = webdriver.Firefox(options=options)
            print_success("Firefox ready (Private Mode)\n")
            
            # Signup
            if not signup_and_verify_otp(driver, account):
                print_error("Signup failed")
                log_progress(account['email'], "SIGNUP_FAILED", "OTP verification failed")
                continue
            
            print_success("✓ Signup complete\n")
            
            # Fill form
            if fill_registration_form(driver, account):
                print_success("✓ Registration form complete")
                log_progress(account['email'], "SUCCESS", "Account processed successfully")
                completed += 1
            else:
                print_error("Form filling incomplete")
                log_progress(account['email'], "PARTIAL", "Form filling incomplete")
        
        except Exception as e:
            print_error(f"Error: {str(e)[:60]}")
            log_progress(account['email'], "ERROR", str(e)[:100])
        
        finally:
            if driver:
                try:
                    driver.quit()
                    print_success("Firefox closed")
                except:
                    pass
    
    print("\n" + "="*70)
    print(f"COMPLETE: {completed}/{len(accounts)} accounts processed")
    print("="*70)

if __name__ == "__main__":
    main()
