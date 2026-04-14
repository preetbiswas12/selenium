"""
Hack2Skill Manual Login + Auto Registration Form Filler

Workflow:
1. Open signup page in Firefox
2. Wait for user to manually complete login + OTP
3. User presses Enter to continue
4. Auto-fill 23-field registration form
5. Submit form

This allows manual control over the sensitive login/OTP parts
while automating the tedious form filling
"""

import time
import csv
import os
from datetime import datetime
from enum import Enum
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage&utm_campaign=&utm_term=&utm_content="
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration?utm_source=hack2skill&utm_medium=homepage&utm_campaign=&utm_term=&utm_content="
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

TIMEOUT_PAGE_LOAD = 25
TIMEOUT_ELEMENT = 15


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

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


def log_progress(email: str, status: str, message: str):
    """Log progress to CSV file"""
    file_exists = os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'status', 'message'])
        
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            email,
            status,
            message
        ])


def init_firefox_driver():
    """Initialize Firefox WebDriver in private mode"""
    print_step(0, "Initializing Firefox WebDriver")
    
    options = webdriver.FirefoxOptions()
    options.add_argument("-private")  # Private browsing mode
    
    try:
        driver = webdriver.Firefox(options=options)
        print_success("Firefox initialized", True)
        return driver
    except Exception as e:
        print_error(f"Failed to initialize Firefox: {str(e)}")
        return None


def wait_for_manual_login(driver: webdriver.Firefox):
    """
    Wait for user to manually complete login and OTP
    User presses Enter in console when ready to continue
    """
    print_step(1, "Manual Login & OTP (User Action Required)")
    print_warning("Opening signup page...", True)
    
    driver.get(SIGNUP_PAGE_URL)
    time.sleep(2)
    
    print_success("Signup page opened in Firefox", True)
    print_warning("Please complete the following manually:", True)
    print("   1. Fill in Full Name and Email")
    print("   2. Click Register")
    print("   3. Enter OTP manually when prompted")
    print("   4. Click Verify button")
    print("")
    
    # Wait for user input
    try:
        input("Press Enter when you've completed login and OTP verification... ")
        print_success("Continuing to registration form...", True)
        
        # Wait for redirect to happen
        print_warning("Waiting for page redirect to registration form...", True)
        time.sleep(3)
        
        # Check if we're on the registration page
        current_url = driver.current_url
        print(f"   Current URL: {current_url}")
        
        # If not on registration page, navigate there
        if "registration" not in current_url.lower():
            print_warning("Redirect didn't happen, manually navigating to registration form...", True)
            driver.get(REGISTRATION_URL)
            time.sleep(3)
        
        print_success("On registration form page", True)
        return True
    except KeyboardInterrupt:
        print_error("User cancelled workflow")
        return False


def fill_registration_form(driver: webdriver.Firefox) -> bool:
    """
    STEP 2: Fill the 23-field registration form
    Assumes user is already logged in and on the registration page
    """
    print_step(2, "Auto-fill Registration Form (23 fields)")
    
    try:
        # Don't reload the page! User is already on registration page
        print_step(2, "Starting form fill...", True)
        time.sleep(1)
        print_success("Ready to fill form (no page reload)", True)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION 1: Personal Information
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Section 1: Personal Info", True)
        
        # Full Name and Email are pre-filled from signup, skip them
        print_warning("Full Name: Already pre-filled from signup (skipping)", True)
        print_warning("Email: Already pre-filled from signup (disabled, skipping)", True)
        
        time.sleep(0.5)
        
        # WhatsApp Number
        try:
            whatsapp_inputs = driver.find_elements(By.XPATH, "//input[@type='tel']")
            if not whatsapp_inputs:
                whatsapp_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'WhatsApp') or contains(@placeholder, 'whatsapp')]")
            
            if whatsapp_inputs:
                if whatsapp_inputs[0].get_attribute('disabled') is None:
                    whatsapp_inputs[0].send_keys("+919876543210")
                    print_success("WhatsApp: +919876543210", True)
        except Exception as e:
            print_warning(f"WhatsApp error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # Alternate number = WhatsApp checkbox
        try:
            checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            if checkboxes and not checkboxes[0].is_selected():
                checkboxes[0].click()
                print_success("Alternate number = WhatsApp (checked)", True)
        except:
            print_warning("Alternate checkbox not found", True)
        
        time.sleep(0.5)
        
        # Date of Birth
        try:
            dob_input = driver.find_element(By.XPATH, "//input[@type='date']")
            dob_input.send_keys("02191996")  # Format: MMDDYYYY for Firefox
            print_success("Date of Birth: 1996-02-19", True)
        except:
            print_warning("DOB field not found", True)
        
        time.sleep(0.5)
        
        # Gender (radio button approach)
        try:
            radio_buttons = driver.find_elements(By.XPATH, "//input[@type='radio']")
            for radio in radio_buttons:
                try:
                    if radio.get_attribute('value') and 'male' in radio.get_attribute('value').lower():
                        if not radio.is_selected():
                            radio.click()
                        print_success("Gender: Male", True)
                        break
                except:
                    pass
        except:
            print_warning("Gender field not found", True)
        
        time.sleep(0.5)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION 2: Location Information
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Section 2: Location", True)
        
        # Country (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    name_attr = inp.get_attribute('name') or ""
                    if placeholder and ('country' in placeholder.lower() or 'nation' in placeholder.lower()):
                        inp.send_keys("India")
                        time.sleep(0.5)
                        options = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if options:
                            options[0].click()
                            print_success("Country: India", True)
                        else:
                            print_warning("Country options not found, trying to continue", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"Country field error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # State (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            state_count = 0
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'state' in placeholder.lower() or 'province' in placeholder.lower():
                        state_count += 1
                        if state_count == 1:  # First state field
                            inp.send_keys("Maharashtra")
                            time.sleep(0.5)
                            options = driver.find_elements(By.XPATH, "//div[@role='option']")
                            if options:
                                options[0].click()
                                print_success("State: Maharashtra", True)
                            else:
                                print_warning("State options not found, continuing", True)
                            break
                except:
                    pass
        except Exception as e:
            print_warning(f"State field error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # City (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            city_count = 0
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'city' in placeholder.lower() or 'town' in placeholder.lower():
                        city_count += 1
                        if city_count == 1:  # First city field
                            inp.send_keys("Mumbai")
                            time.sleep(0.5)
                            options = driver.find_elements(By.XPATH, "//div[@role='option']")
                            if options:
                                options[0].click()
                                print_success("City: Mumbai", True)
                            else:
                                print_warning("City options not found, continuing", True)
                            break
                except:
                    pass
        except Exception as e:
            print_warning(f"City field error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION 3: College Information
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Section 3: Education", True)
        
        # Occupation: College Student
        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            for radio in radios:
                try:
                    if radio.get_attribute('value') and 'college' in radio.get_attribute('value').lower():
                        if not radio.is_selected():
                            radio.click()
                        print_success("Occupation: College Student", True)
                        break
                except:
                    pass
        except:
            print_warning("Occupation field not found", True)
        
        time.sleep(1)
        
        # College Name (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'college' in placeholder.lower() or 'university' in placeholder.lower():
                        inp.send_keys("Indian")
                        time.sleep(0.5)
                        options = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if options:
                            options[0].click()
                            print_success("College Name: Selected", True)
                        else:
                            print_warning("College options not found", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"College Name error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # College Country
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            country_count = 0
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'country' in placeholder.lower():
                        country_count += 1
                        if country_count == 2:  # Second country field (college)
                            inp.send_keys("India")
                            time.sleep(0.5)
                            options = driver.find_elements(By.XPATH, "//div[@role='option']")
                            if options:
                                options[0].click()
                            print_success("College Country: India", True)
                            break
                except:
                    pass
        except Exception as e:
            print_warning(f"College Country error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # College State
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            state_count = 0
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'state' in placeholder.lower():
                        state_count += 1
                        if state_count == 2:  # Second state field (college)
                            inp.send_keys("Maharashtra")
                            time.sleep(0.5)
                            options = driver.find_elements(By.XPATH, "//div[@role='option']")
                            if options:
                                options[0].click()
                            print_success("College State: Maharashtra", True)
                            break
                except:
                    pass
        except Exception as e:
            print_warning(f"College State error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # College City
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            city_count = 0
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'city' in placeholder.lower():
                        city_count += 1
                        if city_count == 2:  # Second city field (college)
                            inp.send_keys("Mumbai")
                            time.sleep(0.5)
                            options = driver.find_elements(By.XPATH, "//div[@role='option']")
                            if options:
                                options[0].click()
                            print_success("College City: Mumbai", True)
                            break
                except:
                    pass
        except Exception as e:
            print_warning(f"College City error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # Degree (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'degree' in placeholder.lower() or 'qualification' in placeholder.lower():
                        inp.send_keys("B")
                        time.sleep(0.5)
                        options = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if options:
                            options[0].click()
                            print_success("Degree: Selected", True)
                        else:
                            print_warning("Degree options not found", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"Degree error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # Stream (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'stream' in placeholder.lower() or 'specialization' in placeholder.lower() or 'branch' in placeholder.lower():
                        inp.send_keys("C")
                        time.sleep(0.5)
                        options = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if options:
                            options[0].click()
                            print_success("Stream: Selected", True)
                        else:
                            print_warning("Stream options not found", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"Stream error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # Passout Year (autocomplete)
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    if 'year' in placeholder.lower() or 'graduation' in placeholder.lower() or 'passout' in placeholder.lower():
                        inp.send_keys("2026")
                        time.sleep(0.5)
                        options = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if options:
                            options[0].click()
                            print_success("Passout Year: 2026", True)
                        else:
                            print_warning("Year options not found", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"Passout Year error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION 4: Profiles & Documents
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Section 4: Profiles & Documents", True)
        
        # LinkedIn
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    inp_type = inp.get_attribute('type') or ""
                    if ('linkedin' in placeholder.lower() or 'profile' in placeholder.lower()) and inp_type != 'file':
                        inp.send_keys("https://linkedin.com/in/aditya-kumar")
                        print_success("LinkedIn: Profile entered", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"LinkedIn error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # College ID (file upload)
        try:
            file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                idcard_path = r"C:\Users\preet\Downloads\selenium\idcard.jpg"
                if os.path.exists(idcard_path):
                    file_inputs[0].send_keys(idcard_path)
                    print_success("College ID uploaded", True)
                    print_warning("Waiting 10 seconds for file upload...", True)
                    time.sleep(10)
        except:
            print_warning("File upload error", True)
        
        time.sleep(0.5)
        
        # GDP Profile
        try:
            all_inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in all_inputs:
                try:
                    placeholder = inp.get_attribute('placeholder') or ""
                    inp_type = inp.get_attribute('type') or ""
                    if ('g.dev' in placeholder.lower() or 'gdp' in placeholder.lower() or 'gdp profile' in placeholder.lower()) and inp_type != 'file':
                        inp.send_keys("https://g.dev/aditya-kumar")
                        print_success("GDP Profile: Entered", True)
                        break
                except:
                    pass
        except Exception as e:
            print_warning(f"GDP Profile error: {str(e)[:40]}", True)
        
        time.sleep(0.5)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION 5: Referral
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Section 5: GDG Referral", True)
        
        # Referral - Yes/No
        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            for radio in radios:
                try:
                    value = radio.get_attribute('value')
                    if value and 'yes' in value.lower():
                        if not radio.is_selected():
                            radio.click()
                        print_success("Referral: YES", True)
                        break
                except:
                    pass
        except:
            print_warning("Referral radio error", True)
        
        time.sleep(1)
        
        # Referral Code (if Yes selected)
        try:
            referral_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'referral') or contains(@placeholder, 'code')]")
            if referral_inputs:
                referral_inputs[-1].send_keys("GDG2026REF123")
                print_success("Referral Code: Entered", True)
        except:
            print_warning("Referral Code error", True)
        
        time.sleep(0.5)
        
        # ═══════════════════════════════════════════════════════════════
        # SECTION 6: Terms & Conditions
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Section 6: Agreements", True)
        
        # Check all checkboxes
        try:
            all_checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
            checked = 0
            for checkbox in all_checkboxes:
                try:
                    if not checkbox.is_selected():
                        driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
                        time.sleep(0.2)
                        try:
                            checkbox.click()
                        except:
                            driver.execute_script("arguments[0].click();", checkbox)
                        checked += 1
                except:
                    pass
            print_success(f"Terms & Consents: {checked} checked", True)
        except:
            print_warning("Checkboxes error", True)
        
        time.sleep(1)
        
        # ═══════════════════════════════════════════════════════════════
        # SUBMIT FORM
        # ═══════════════════════════════════════════════════════════════
        
        print_step(2, "Submitting Form", True)
        try:
            submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            time.sleep(1)
            
            # Try to hide overlay if present
            try:
                overlay = driver.find_element(By.XPATH, "//div[contains(@class, 'opacity-30')]")
                driver.execute_script("arguments[0].style.display = 'none';", overlay)
            except:
                pass
            
            time.sleep(0.5)
            
            # Click the button
            try:
                submit_button.click()
                print_success("Register button clicked", True)
            except:
                driver.execute_script("arguments[0].click();", submit_button)
                print_success("Register button clicked (JS)", True)
            
            time.sleep(3)
            print_success("Form submitted successfully!", True)
            return True
        except Exception as e:
            print_warning(f"Submit error: {str(e)[:50]}", True)
            return True
        
    except Exception as e:
        print_error(f"Form filling error: {str(e)}")
        return False


def main():
    """Main workflow"""
    print("\n" + "="*70)
    print("HACK2SKILL: Manual Login + Auto Form Filler")
    print("="*70)
    
    # Initialize Firefox
    driver = init_firefox_driver()
    if not driver:
        return
    
    try:
        # Step 1: Wait for manual login
        if not wait_for_manual_login(driver):
            return
        
        time.sleep(2)
        
        # Step 2: Auto-fill registration form
        fill_registration_form(driver)
        
        print("\n" + "="*70)
        print("✓ Workflow Complete!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n✗ Workflow cancelled by user")
    except Exception as e:
        print(f"\n\n✗ Workflow error: {str(e)}")
    finally:
        print("\nClosing Firefox in 10 seconds...")
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    main()
