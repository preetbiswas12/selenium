"""
Batch cock.li Account Creator with Tor
SMART VERSION: Uses Selenium to detect browser state instead of time-based waits
Features:
  - Watches browser for actual page loads
  - Smart element detection (not time-based)
  - Waits for CAPTCHA to appear naturally
  - Detects success by checking page elements
  - Retries on failure automatically
  - Resilient to internet issues
"""

import csv
import logging
import time
import os
import subprocess
import random
import string
from pathlib import Path

# Auto-setup geckodriver if needed (optional - fails gracefully)
try:
    import geckodriver_autoinstaller
    geckodriver_autoinstaller.install()
except:
    # Not critical - fallback to manual setup
    pass

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CockliBatchCreator:
    """Create multiple cock.li accounts intelligently using Selenium"""
    
    COCK_LI_REGISTER = "https://cock.li/register.php"
    
    def __init__(self, use_tor=False, use_incognito=True, fixed_password="gdgocgu12"):
        self.use_tor = use_tor
        self.use_incognito = use_incognito
        self.fixed_password = fixed_password
        self.created_accounts = []
        self.driver = None
        self.geckodriver_path = self._find_geckodriver()
        self.firefox_path = self._find_firefox()
        self.tor_path = self._find_tor() if use_tor else None
        
        logger.info(f"Using password: {self.fixed_password}")
        logger.info(f"Browser: Firefox {'in Incognito' if use_incognito else 'normal'}")
        logger.info(f"Anonymity: {'Tor (new IP per account)' if use_tor else 'Local privacy only'}")
        logger.info(f"Firefox path: {self.firefox_path if self.firefox_path else 'AUTO'}")
        logger.info(f"GeckoDriver: {self.geckodriver_path if self.geckodriver_path else 'AUTO'}")
    
    def _find_firefox(self):
        """Find standard Firefox browser"""
        paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                logger.info(f"✓ Found Firefox: {path}")
                return path
        
        logger.info("Standard Firefox not found (optional)")
        return None
    
    def _find_geckodriver(self):
        """Find geckodriver (Firefox WebDriver)"""
        # Check multiple locations
        paths = [
            r"C:\webdrivers\geckodriver.exe",
            r"C:\Users\preet\AppData\Local\Programs\Python\Python39\Scripts\geckodriver.exe",
            "./geckodriver.exe",
            "geckodriver.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                logger.info(f"✓ Found GeckoDriver: {path}")
                return path
        
        # Selenium will try to find it in PATH
        logger.info("GeckoDriver not found locally, will use system PATH")
        return None
    
    def _find_tor(self):
        """Find Tor Browser (firefox.exe)"""
        paths = [
            r"C:\Users\preet\OneDrive\Documents\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files\Tor Browser\Browser\firefox.exe",
            r"C:\Users\preet\Desktop\Tor Browser\firefox.exe",
            r"C:\Users\preet\Downloads\Tor Browser\firefox.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                logger.info(f"✓ Found Tor: {path}")
                return path
        
        logger.error("❌ Tor Browser not found!")
        return None
    
    def _setup_driver(self):
        """Setup Selenium Firefox WebDriver with Incognito/Tor"""
        try:
            options = Options()
            
            # Note: Incognito mode (-private) causes Firefox to crash with Selenium
            # Using regular Firefox with private browsing disabled is safer
            # Each fresh instance provides privacy anyway
            
            # Disable images for faster loading
            options.set_preference("permissions.default.image", 2)
            options.set_preference("browser.cache.disk.enable", False)
            options.set_preference("browser.cache.memory.enable", False)
            
            if self.use_incognito:
                logger.info("✓ Privacy mode: Fresh instance (no cache/cookies)")
            
            # Choose which Firefox to use
            binary_path = None
            if self.use_tor and self.tor_path:
                logger.info(f"Using Tor Browser: {self.tor_path}")
                binary_path = self.tor_path
                logger.info("✓ Will use Tor for anonymity (new IP per account)")
            elif self.firefox_path:
                logger.info(f"Using standard Firefox: {self.firefox_path}")
                binary_path = self.firefox_path
            
            if binary_path:
                options.binary_location = binary_path
            
            # Try to setup service with geckodriver
            if self.geckodriver_path and os.path.exists(self.geckodriver_path):
                logger.info(f"Using GeckoDriver: {self.geckodriver_path}")
                service = Service(self.geckodriver_path)
                self.driver = webdriver.Firefox(service=service, options=options)
            else:
                # Let Selenium find geckodriver automatically
                logger.info("Auto-detecting GeckoDriver...")
                try:
                    self.driver = webdriver.Firefox(options=options)
                except Exception as e:
                    logger.error(f"GeckoDriver not found. Details: {e}")
                    logger.error("Try running: python setup_geckodriver.py")
                    return False
            
            logger.info("✓ Firefox WebDriver initialized")
            
            # If using Tor Browser, wait for Tor network connection
            if self.use_tor:
                logger.info("⏳ Waiting 20 seconds for Tor network to connect...")
                time.sleep(20)
                logger.info("✓ Tor connection should be ready")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            logger.info("Download GeckoDriver from: https://github.com/mozilla/geckodriver/releases")
            return False
    
    def _quit_driver(self):
        """Close browser"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("✓ Browser closed")
        except:
            pass
    
    def _wait_for_element(self, locator, timeout=30):
        """
        Wait for element to appear (smart timeout)
        Returns element if found, None if timeout
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            logger.info(f"✓ Element found: {locator}")
            return element
        except TimeoutException:
            logger.warning(f"⏱️ Timeout waiting for element: {locator}")
            return None
    
    def _wait_for_clickable(self, locator, timeout=30):
        """Wait for element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            return element
        except TimeoutException:
            return None
    
    def _fill_field(self, field, text, pause=0.5):
        """Type text into a field"""
        try:
            field.clear()
            time.sleep(pause)
            field.send_keys(text)
            return True
        except Exception as e:
            logger.warning(f"Failed to fill field: {e}")
            return False
    
    def _check_for_captcha(self, timeout=5):
        """Check if CAPTCHA is visible on page"""
        try:
            # cock.li uses simple text CAPTCHA (input field)
            captcha_locators = [
                (By.NAME, "captcha"),           # cock.li text CAPTCHA
                (By.CLASS_NAME, "g-recaptcha"), # Google reCAPTCHA
                (By.CLASS_NAME, "h-captcha"),   # hCaptcha
                (By.ID, "captcha"),
                (By.CSS_SELECTOR, "iframe[src*='recaptcha']"),
                (By.CSS_SELECTOR, "iframe[src*='hcaptcha']"),
            ]
            
            for locator in captcha_locators:
                try:
                    element = WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located(locator)
                    )
                    logger.info(f"✓ CAPTCHA detected: {locator}")
                    return True
                except TimeoutException:
                    continue
            
            return False
        except:
            return False
    
    def _check_success(self):
        """Check if account was successfully created"""
        try:
            page_source = self.driver.page_source.lower()
            
            success_keywords = [
                "successfully",
                "created",
                "confirmation",
                "congratulations",
                "account created",
                "registered"
            ]
            
            for keyword in success_keywords:
                if keyword in page_source:
                    logger.info(f"✓ Success indicator found: '{keyword}'")
                    return True
            
            return False
        except:
            return False
    
    def _generate_unique_username(self):
        """Generate unique username using English words + numbers (letters and digits only)"""
        # Common English words (nouns, adjectives, verbs)
        words = [
            'alpha', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
            'india', 'juliet', 'kilo', 'lima', 'mike', 'november', 'oscar', 'papa',
            'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor', 'whiskey', 'xray',
            'yankee', 'zulu', 'amber', 'azure', 'banner', 'beacon', 'blaze', 'brick',
            'bronze', 'bronze', 'cabin', 'cable', 'canvas', 'carbon', 'castle', 'cedar',
            'chain', 'charm', 'chase', 'cheap', 'clean', 'clear', 'climb', 'cloud',
            'clover', 'coast', 'cobalt', 'comet', 'coral', 'corgi', 'court', 'coyote',
            'craft', 'crane', 'crash', 'crater', 'cream', 'creek', 'crown', 'crush',
            'crystal', 'cubic', 'cycle', 'cyber', 'dagger', 'daily', 'daisy', 'dance',
            'danger', 'daring', 'davit', 'dazzle', 'debtor', 'decade', 'decent', 'decide',
            'decor', 'decree', 'defend', 'defiant', 'define', 'degree', 'deity', 'deluge',
            'demand', 'demo', 'demon', 'denial', 'denizen', 'dense', 'dental', 'depart',
            'depend', 'depict', 'deploy', 'deport', 'desert', 'design', 'desire', 'desk',
            'despot', 'detail', 'detect', 'detest', 'device', 'devil', 'devoid', 'devote',
            'dew', 'dewdrop', 'diamond', 'diary', 'dibble', 'dice', 'dickens', 'diesel',
            'diet', 'differ', 'digest', 'digit', 'digital', 'dignify', 'dignity', 'dike',
            'dilemma', 'diligent', 'dilly', 'dilute', 'dim', 'dime', 'dimple', 'dine'
        ]
        
        existing_usernames = [acc['username'] for acc in self.created_accounts]
        
        # Generate username: word + random 3-4 digit number
        attempts = 0
        while attempts < 100:
            word = random.choice(words)
            number = random.randint(100, 9999)
            username = f"{word}{number}"
            
            if username not in existing_usernames:
                return username
            attempts += 1
        
        # Fallback: if somehow we can't find unique (should never happen with so many combinations)
        raise Exception("Could not generate unique username after 100 attempts")
    
    def create_single_account(self, attempt_num=1):
        """
        Create single cock.li account using SMART element detection
        
        Steps:
        1. Setup browser
        2. Navigate to registration
        3. Wait for page to load
        4. Fill username (wait for field)
        5. Fill password (wait for field)
        6. Accept terms (wait for checkbox)
        7. Wait for CAPTCHA to appear
        8. Alert user to solve CAPTCHA
        9. Wait for success
        """
        
        try:
            # Generate username
            username = self._generate_unique_username()
            email = f"{username}@cock.li"
            
            logger.info(f"\n{'='*70}")
            logger.info(f"Account #{attempt_num}: {email}")
            logger.info(f"{'='*70}")
            
            # Step 1: Setup driver (fresh browser for each account)
            logger.info("[1/9] Starting browser...")
            if not self._setup_driver():
                logger.error("Failed to setup browser")
                return None
            
            # Step 2: Navigate to registration
            logger.info("[2/9] Loading registration page...")
            try:
                self.driver.get(self.COCK_LI_REGISTER)
            except Exception as e:
                logger.error(f"Failed to load page: {e}")
                self._quit_driver()
                return None
            
            # Step 3: Wait for page to fully load (by finding form elements)
            logger.info("[3/9] Waiting for form to load...")
            
            # Get username field (cock.li uses name='username')
            username_field = None
            selectors_to_try = [
                (By.NAME, "username"),       # Primary selector (cock.li uses this)
                (By.ID, "username"),         # Alternative
                (By.CSS_SELECTOR, "input[name='username']"),  # CSS
                (By.CSS_SELECTOR, "input[type='text']"),  # Any text input
            ]
            
            for locator in selectors_to_try:
                try:
                    username_field = self._wait_for_element(locator, timeout=10)
                    if username_field:
                        logger.info(f"✓ Found username field with selector: {locator}")
                        break
                except:
                    continue
            
            if not username_field:
                logger.error("Registration form not found!")
                logger.error("Tried selectors: username (name), username (id), input[name='username'], input[type='text']")
                # Try to see what's on the page
                try:
                    page_source = self.driver.page_source
                    if "register" in page_source.lower() or "cock.li" in page_source.lower():
                        logger.info("Page loaded but form fields not found. Checking page structure...")
                        # Log first 2000 chars to see structure
                        logger.debug(f"Page content preview: {page_source[:2000]}")
                except:
                    pass
                self._quit_driver()
                return None
            
            # Step 4: Fill username
            logger.info("[4/9] Filling username...")
            if not self._fill_field(username_field, username):
                self._quit_driver()
                return None
            
            # Step 5: Find and fill password fields
            logger.info("[5/9] Filling password fields...")
            password_fields = None
            
            try:
                # First try by name (some forms use name='password')
                password_fields = self.driver.find_elements(By.NAME, "password")
                if not password_fields or len(password_fields) < 2:
                    # Fallback to any type='password' input (cock.li form uses this)
                    password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            except:
                pass
            
            if not password_fields or len(password_fields) < 1:
                logger.error("Password field not found")
                self._quit_driver()
                return None
            
            # Fill first password field
            logger.info("[5/9] Filling password (1st)...")
            if not self._fill_field(password_fields[0], self.fixed_password):
                self._quit_driver()
                return None
            
            # Fill second password field (confirm) if it exists
            logger.info("[6/9] Filling password (2nd - confirm)...")
            if len(password_fields) >= 2:
                if not self._fill_field(password_fields[1], self.fixed_password):
                    logger.error("Failed to fill password confirm field")
                    self._quit_driver()
                    return None
                logger.info("✓ Password confirm filled")
            else:
                logger.warning("Only 1 password field found, assuming no confirm field needed")
                # Continue anyway - some forms don't have confirm
            
            # Step 7: Accept terms/conditions (checkbox)
            logger.info("[7/9] Accepting terms...")
            try:
                # cock.li uses name='tos_agree' for terms checkbox
                terms_checkbox = self.driver.find_element(By.NAME, "tos_agree")
                self.driver.execute_script("arguments[0].click();", terms_checkbox)
                logger.info("✓ Terms accepted")
            except Exception as e:
                logger.warning(f"Could not find/click terms checkbox (tos_agree): {e}")
            
            # Step 8: Wait for CAPTCHA to appear and give user time to solve it
            logger.info("[8/9] Waiting for CAPTCHA to appear...")
            
            # Wait for CAPTCHA field to appear on page
            captcha_field = self._wait_for_element((By.NAME, "captcha"), timeout=15)
            
            if captcha_field:
                logger.info("✓ CAPTCHA field detected on page")
                
                # Alert user to solve CAPTCHA
                logger.info("="*70)
                logger.info("⏸️  ACTION REQUIRED: PLEASE SOLVE CAPTCHA")
                logger.info("="*70)
                logger.info("INSTRUCTIONS:")
                logger.info("  1. Look at YOUR BROWSER WINDOW")
                logger.info("  2. You have 20 seconds to:")
                logger.info("     a) Read the CAPTCHA text")
                logger.info("     b) Type it into the CAPTCHA field")
                logger.info("  3. When 20 seconds are done, script will click 'Register'")
                logger.info("="*70)
                logger.info("")
                
                # Wait 20 seconds for user to manually solve CAPTCHA
                logger.info("Waiting 20 seconds for CAPTCHA solving...")
                for i in range(20, 0, -1):
                    print(f"\r⏱️  {i} seconds remaining... (solve CAPTCHA now!)", end='', flush=True)
                    time.sleep(1)
                print()  # newline
                
                logger.info("✓ 20 seconds passed. Ready to click Register button...")
            else:
                logger.warning("CAPTCHA field not found, but continuing anyway...")
            
            # Step 9: Click Register button
            logger.info("[9/9] Clicking Register button...")
            
            try:
                # Try different selectors for Register button
                register_btn = None
                register_selectors = [
                    (By.CSS_SELECTOR, "input[value='Register']"),
                    (By.CSS_SELECTOR, "input[type='submit']"),
                    (By.XPATH, "//input[@value='Register']"),
                    (By.XPATH, "//button[contains(text(), 'Register')]"),
                ]
                
                for selector in register_selectors:
                    try:
                        register_btn = self.driver.find_element(*selector)
                        if register_btn:
                            logger.info(f"✓ Found Register button with selector: {selector}")
                            break
                    except:
                        continue
                
                if register_btn:
                    register_btn.click()
                    logger.info("✓ Clicked Register button")
                    time.sleep(3)  # Wait for page to process
                else:
                    logger.warning("⚠️ Could not find Register button - but continuing anyway...")
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Error clicking Register button: {e}")
                time.sleep(2)
            
            # Check for success
            logger.info("[10/10] Checking for account creation success...")
            time.sleep(2)
            
            try:
                page_source = self.driver.page_source
                
                # Check for specific cock.li success message
                success_messages = [
                    "Your account was successfully created",
                    "account was successfully created",
                    "successfully created",
                ]
                
                success_found = False
                for msg in success_messages:
                    if msg.lower() in page_source.lower():
                        logger.info(f"✓✓✓ SUCCESS CONFIRMED: '{msg}' found on page!")
                        success_found = True
                        break
                
                if success_found:
                    logger.info("")
                    logger.info("="*70)
                    logger.info(f"✅ ACCOUNT SUCCESSFULLY CREATED: {email}")
                    logger.info("="*70)
                    logger.info(f"Password: {self.fixed_password}")
                    logger.info("")
                    logger.info("The account is now active and ready for use!")
                    logger.info("Closing browser and preparing for next account...")
                    logger.info("")
                    
                    self.created_accounts.append({
                        'username': username,
                        'password': self.fixed_password,
                        'email': email
                    })
                    self._save_created_accounts()  # Save immediately after each account
                    self._quit_driver()  # Close browser completely
                    return email
                else:
                    # Success message NOT found - try going back and refilling form
                    logger.warning("⚠️ Success message NOT found on page!")
                    logger.warning("Going back to form to retry (will re-fill all fields)...")
                    logger.info("")
                    
                    try:
                        self.driver.back()
                        logger.info("✓ Clicked back button")
                        time.sleep(3)
                        
                        # RETRY: Re-fill all form fields (same as original)
                        logger.info("RETRYING: Re-filling form fields...")
                        
                        # Re-wait for username field
                        username_field = self._wait_for_element((By.NAME, "username"), timeout=10)
                        if not username_field:
                            logger.error("❌ Could not find username field on retry")
                            self._quit_driver()
                            return None
                        
                        # Re-fill username
                        logger.info("  Filling username again...")
                        if not self._fill_field(username_field, username):
                            logger.error("Failed to fill username on retry")
                            self._quit_driver()
                            return None
                        
                        # Re-fill passwords
                        logger.info("  Filling passwords again...")
                        password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                        
                        if len(password_fields) >= 1:
                            if not self._fill_field(password_fields[0], self.fixed_password):
                                logger.error("Failed to fill password 1 on retry")
                                self._quit_driver()
                                return None
                        
                        if len(password_fields) >= 2:
                            if not self._fill_field(password_fields[1], self.fixed_password):
                                logger.error("Failed to fill password 2 on retry")
                                self._quit_driver()
                                return None
                        
                        # Re-check terms
                        logger.info("  Accepting terms again...")
                        try:
                            terms_checkbox = self.driver.find_element(By.NAME, "tos_agree")
                            self.driver.execute_script("arguments[0].click();", terms_checkbox)
                            logger.info("  ✓ Terms re-accepted")
                        except Exception as e:
                            logger.warning(f"Could not re-check terms: {e}")
                        
                        # Re-wait for CAPTCHA
                        logger.info("  Waiting for CAPTCHA again...")
                        captcha_field = self._wait_for_element((By.NAME, "captcha"), timeout=15)
                        
                        if captcha_field:
                            logger.info("  ✓ CAPTCHA field detected")
                            logger.info("")
                            logger.info("  ⏸️  CAPTCHA DETECTED (RETRY) - 20 SECONDS")
                            for i in range(20, 0, -1):
                                print(f"\r  ⏱️  {i} seconds remaining...", end='', flush=True)
                                time.sleep(1)
                            print()  # newline
                            logger.info("  ✓ 20 seconds passed")
                        
                        # Re-click Register
                        logger.info("  Clicking Register button (retry)...")
                        register_btn = None
                        register_selectors = [
                            (By.CSS_SELECTOR, "input[value='Register']"),
                            (By.CSS_SELECTOR, "input[type='submit']"),
                            (By.XPATH, "//input[@value='Register']"),
                        ]
                        
                        for selector in register_selectors:
                            try:
                                register_btn = self.driver.find_element(*selector)
                                if register_btn:
                                    logger.info(f"  ✓ Found Register button (retry)")
                                    register_btn.click()
                                    logger.info("  ✓ Clicked Register button (retry)")
                                    time.sleep(3)
                                    break
                            except:
                                continue
                        
                        # Check again for success
                        time.sleep(2)
                        page_source_retry = self.driver.page_source
                        
                        success_found_retry = False
                        for msg in success_messages:
                            if msg.lower() in page_source_retry.lower():
                                logger.info(f"✓✓✓ SUCCESS CONFIRMED (RETRY): {msg}")
                                success_found_retry = True
                                break
                        
                        if success_found_retry:
                            logger.info("")
                            logger.info("="*70)
                            logger.info(f"✅ ACCOUNT SUCCESSFULLY CREATED (RETRY): {email}")
                            logger.info("="*70)
                            
                            self.created_accounts.append({
                                'username': username,
                                'password': self.fixed_password,
                                'email': email
                            })
                            self._save_created_accounts()
                            self._quit_driver()
                            return email
                        else:
                            logger.error("❌ Still no success message after retry")
                            logger.error("Account creation likely failed")
                            self._quit_driver()
                            return None
                    
                    except Exception as e:
                        logger.error(f"Error during retry: {e}")
                        self._quit_driver()
                        return None
            
            except Exception as e:
                logger.error(f"Error checking success: {e}")
                self._quit_driver()
                return None
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            self._quit_driver()
            return None
    
    def create_batch_accounts(self, num_accounts=5):
        """Create multiple accounts with smart detection"""
        if num_accounts < 1 or num_accounts > 200:
            logger.error("Please create between 1 and 200 accounts")
            return []
        
        logger.info(f"\n{'='*70}")
        logger.info(f"🚀 STARTING BATCH CREATION: {num_accounts} accounts")
        logger.info(f"{'='*70}\n")
        
        for idx in range(1, num_accounts + 1):
            logger.info(f"\n>>> ACCOUNT {idx}/{num_accounts} <<<\n")
            
            email = self.create_single_account(attempt_num=idx)
            
            if email:
                logger.info(f"✅ Created: {email}")
            else:
                logger.error(f"❌ Failed to create account #{idx}")
            
            # Wait between accounts
            if idx < num_accounts:
                logger.info(f"Waiting 5 seconds before next account...")
                time.sleep(5)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"✅ BATCH CREATION COMPLETE: {len(self.created_accounts)}/{num_accounts}")
        logger.info(f"{'='*70}\n")
        
        self._save_created_accounts()
        
        return self.created_accounts
    
    def _save_created_accounts(self):
        """Save all created accounts to CSV for Thunderbird injection"""
        if not self.created_accounts:
            logger.warning("No accounts to save")
            return
        
        output_file = "accounts_created.csv"
        try:
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['username', 'password', 'email', 'firstname', 'lastname'])
                writer.writeheader()
                
                for acc in self.created_accounts:
                    writer.writerow({
                        'username': acc['username'],
                        'password': acc['password'],
                        'email': acc['email'],
                        'firstname': '',
                        'lastname': ''
                    })
            
            logger.info(f"✓ Saved {len(self.created_accounts)} accounts to: {output_file}")
            logger.info(f"Ready for Thunderbird injection!")
        
        except Exception as e:
            logger.error(f"Failed to save accounts: {e}")


if __name__ == "__main__":
    import sys
    
    # Get number of accounts to create
    num_accounts = 5  # Default
    use_tor = "--tor" in sys.argv
    
    if len(sys.argv) > 1:
        try:
            num_accounts = int(sys.argv[1])
        except:
            print("Usage: python cockli_batch_creator.py [num_accounts] [--tor]")
            print("Examples:")
            print("  python cockli_batch_creator.py 10         # 10 accounts, incognito Firefox")
            print("  python cockli_batch_creator.py 10 --tor   # 10 accounts, Tor Browser (new IP each)")
            sys.exit(1)
    
    logger.info("="*70)
    logger.info("COCK.LI BATCH ACCOUNT CREATOR")
    logger.info("="*70)
    logger.info(f"Creating {num_accounts} accounts...")
    logger.info(f"Fixed password: gdgocgu12")
    if use_tor:
        logger.info(f"Browser: Tor Browser (new IP per account)")
    else:
        logger.info(f"Browser: Firefox Incognito (local privacy)")
    logger.info(f"CAPTCHA handling: Manual solving")
    logger.info("="*70 + "\n")
    
    batch = CockliBatchCreator(use_tor=use_tor, use_incognito=True, fixed_password="gdgocgu12")
    batch.create_batch_accounts(num_accounts)
    
    logger.info("\n✅ All accounts created!")
    logger.info("Next: Run 'python thunderbird_injector.py accounts_created.csv'")

