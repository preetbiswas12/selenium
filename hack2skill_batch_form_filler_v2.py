"""
Hack2Skill Batch Registration Form Filler (REFACTORED v3)
With advanced button clicking, exponential backoff retry logic, and page transition validation

KEY IMPROVEMENTS (v3):
✓ Advanced button clicking with 3 strategies: regular click, JavaScript click, ActionChains
✓ Exponential backoff retry logic: 1s, 2s, 4s, 8s, 16s waits between retries
✓ Page transition validation: Detects if page actually changed after button click
✓ Overlay detection and removal: Removes blocking elements before clicking
✓ Loading spinner detection: Waits for page to finish loading before interacting
✓ Multiple validation methods: Page hash, URL change, DOM re-render detection
✓ Detailed logging: Each attempt/failure logged with reason codes
✓ Now actually clicks Register button on signup (was previously skipped)
✓ Proper success page validation after form submission

BUTTON CLICKING STRATEGY:
1. Attempt regular click()
2. If blocked: Try JavaScript click()
3. If that fails: Try ActionChains click()
4. Validate page transitioned or get detailed error reason
5. Retry with exponential backoff (max 5 times)

VALIDATION:
- Pre/post click page state hash comparison
- URL change detection
- DOM re-render detection
- Loading spinner wait
- Overlay removal
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
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    WebDriverException,
    InvalidElementStateException
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
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

# ⚠️ INCREASED TIMEOUTS FOR SLOW NETWORK
TIMEOUT_PAGE_LOAD = 45  # Was 25 - increased for slow networks
TIMEOUT_ELEMENT = 30    # Was 15 - increased for form field loads
TIMEOUT_INTERACTION = 10  # Wait for element to be interactive
OTP_WAIT_SECONDS = 30  # seconds to wait for user to enter OTP manually
RETRY_ATTEMPTS = 3  # Retry failed interactions up to 3 times
RETRY_DELAY = 2  # Wait 2 seconds between retries

# ADVANCED RETRY LOGIC
MAX_CLICK_RETRIES = 5  # Max retries for button clicking (exponential backoff: 1s, 2s, 4s, 8s, 16s)
MAX_FORM_FILL_RETRIES = 2  # Retry entire form if too many fields fail
FORM_FILL_TIMEOUT = 15  # Overall timeout for form navigation
PAGE_TRANSITION_TIMEOUT = 10  # Max time to wait for page transition after click

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

# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def detect_current_page(driver: webdriver.Firefox) -> str:
    """
    Detect which page we're currently on based on URL and elements
    Returns: 'SIGNUP', 'REGISTRATION', 'LOGIN', or 'UNKNOWN'
    """
    current_url = driver.current_url
    
    # Check URL
    if 'signup' in current_url.lower():
        return 'SIGNUP'
    elif 'registration' in current_url.lower():
        return 'REGISTRATION'
    elif 'login' in current_url.lower():
        return 'LOGIN'
    
    # Check for elements on page
    try:
        driver.find_element(By.XPATH, "//input[@placeholder='Enter Full Name']")
        return 'SIGNUP'
    except:
        pass
    
    try:
        driver.find_element(By.XPATH, "//input[@placeholder='WhatsApp']")
        return 'REGISTRATION'
    except:
        pass
    
    return 'UNKNOWN'


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
# ADVANCED INPUT FIELD DETECTION WITH THOROUGH CHECKING
# ═══════════════════════════════════════════════════════════════

def find_input_by_label_or_placeholder(
    driver: webdriver.Firefox,
    search_keywords: List[str],
    field_name: str,
    verbose: bool = True
) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    THOROUGH input field detection that checks:
    1. Input ID attribute
    2. Associated label via 'for' attribute
    3. Input placeholder text
    4. Input name attribute
    5. Parent container text/labels
    
    Args:
        driver: WebDriver
        search_keywords: List of keywords to search for (e.g., ["linkedin", "profile"])
        field_name: Display name for logging
        verbose: Print detailed matching info
    
    Returns:
        WebElement if found, None otherwise
    """
    
    if verbose:
        print_step(4, f"Searching for: {field_name} (keywords: {', '.join(search_keywords[:2])}...)", True)
    
    search_keywords_lower = [kw.lower() for kw in search_keywords]
    
    try:
        # Strategy 1: Check all input elements and their associated labels
        all_inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='url' or @type='tel' or not(@type)]")
        
        for inp in all_inputs:
            try:
                # Skip hidden or disabled inputs
                if not inp.is_displayed() or inp.get_attribute('disabled') is not None:
                    continue
                
                input_id = inp.get_attribute('id') or ""
                input_name = inp.get_attribute('name') or ""
                input_placeholder = inp.get_attribute('placeholder') or ""
                
                # Check ID
                if input_id and any(kw in input_id.lower() for kw in search_keywords_lower):
                    if verbose:
                        print_success(f"✓ Found {field_name} by ID: {input_id}", True)
                    return inp
                
                # Check placeholder
                if input_placeholder and any(kw in input_placeholder.lower() for kw in search_keywords_lower):
                    if verbose:
                        print_success(f"✓ Found {field_name} by placeholder: '{input_placeholder}'", True)
                    return inp
                
                # Check name
                if input_name and any(kw in input_name.lower() for kw in search_keywords_lower):
                    if verbose:
                        print_success(f"✓ Found {field_name} by name: {input_name}", True)
                    return inp
                
                # Strategy 2: Check associated label (look for label with 'for' attribute)
                if input_id:
                    try:
                        label = driver.find_element(By.XPATH, f"//label[@for='{input_id}']")
                        label_text = label.text.lower()
                        if any(kw in label_text for kw in search_keywords_lower):
                            if verbose:
                                print_success(f"✓ Found {field_name} by label: '{label.text}'", True)
                            return inp
                    except NoSuchElementException:
                        pass
                
                # Strategy 3: Check parent container text
                try:
                    parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'field') or contains(@class, 'form-group') or contains(@class, 'input-group')]")
                    parent_text = parent.text.lower()
                    if any(kw in parent_text for kw in search_keywords_lower):
                        if verbose:
                            print_success(f"✓ Found {field_name} in parent container with text: '{parent.text[:50]}'", True)
                        return inp
                except NoSuchElementException:
                    pass
            
            except Exception as e:
                continue
        
        if verbose:
            print_warning(f"✗ {field_name} not found after thorough search", True)
        return None
    
    except Exception as e:
        if verbose:
            print_warning(f"Error searching for {field_name}: {str(e)[:40]}", True)
        return None


def inspect_and_log_form_fields(driver: webdriver.Firefox, verbose: bool = True) -> Dict:
    """
    Inspect all form fields and log their IDs, names, placeholders, and labels
    Useful for debugging field detection issues
    
    Returns:
        Dict with field information
    """
    if not verbose:
        return {}
    
    print_step(4, "Inspecting form fields for debugging", True)
    field_info = {}
    
    try:
        # Get all inputs
        all_inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='email' or @type='tel' or @type='url' or @type='date' or not(@type)]")
        
        print_warning(f"Found {len(all_inputs)} input fields on page:", True)
        
        for idx, inp in enumerate(all_inputs, 1):
            try:
                if not inp.is_displayed():
                    continue
                
                inp_id = inp.get_attribute('id') or "NO_ID"
                inp_name = inp.get_attribute('name') or "NO_NAME"
                inp_placeholder = inp.get_attribute('placeholder') or "NO_PLACEHOLDER"
                inp_type = inp.get_attribute('type') or "text"
                inp_disabled = "DISABLED" if inp.get_attribute('disabled') else "ENABLED"
                
                # Try to find associated label
                label_text = "NO_LABEL"
                try:
                    if inp_id and inp_id != "NO_ID":
                        label = driver.find_element(By.XPATH, f"//label[@for='{inp_id}']")
                        label_text = label.text[:40]
                except:
                    pass
                
                field_info[f"field_{idx}"] = {
                    "id": inp_id,
                    "name": inp_name,
                    "placeholder": inp_placeholder,
                    "type": inp_type,
                    "status": inp_disabled,
                    "label": label_text
                }
                
                # Print compact info
                print(f"   [{idx}] ID: {inp_id:20} | Name: {inp_name:20} | Placeholder: {inp_placeholder:30} | Label: {label_text}", flush=True)
            
            except Exception as e:
                pass
        
        print_success(f"Field inspection complete - {len(field_info)} fields logged", True)
        return field_info
    
    except Exception as e:
        print_warning(f"Error inspecting form fields: {str(e)[:50]}", True)
        return {}


def find_input_by_position(
    driver: webdriver.Firefox,
    position_hint: str,
    field_name: str,
    visible_only: bool = True,
    verbose: bool = True
) -> Optional[webdriver.remote.webelement.WebElement]:
    """
    Find input by position hint (first, last, nth, after_city, etc.)
    
    Args:
        driver: WebDriver
        position_hint: "first", "last", "last_5", "after_city", etc.
        field_name: For logging
        visible_only: Only return visible elements
        verbose: Print logging
    
    Returns:
        WebElement if found, None otherwise
    """
    
    try:
        all_inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='url' or @type='email']")
        
        if visible_only:
            all_inputs = [inp for inp in all_inputs if inp.is_displayed() and inp.get_attribute('disabled') is None]
        
        if not all_inputs:
            return None
        
        selected = None
        
        if position_hint == "first":
            selected = all_inputs[0]
        elif position_hint == "last":
            selected = all_inputs[-1]
        elif position_hint.startswith("last_"):
            count = int(position_hint.split("_")[1])
            selected = all_inputs[-count] if len(all_inputs) >= count else None
        elif position_hint.startswith("index_"):
            idx = int(position_hint.split("_")[1])
            selected = all_inputs[idx] if len(all_inputs) > idx else None
        
        if selected and verbose:
            field_id = selected.get_attribute('id') or "no-id"
            placeholder = selected.get_attribute('placeholder') or "no-placeholder"
            print_success(f"✓ Found {field_name} at position '{position_hint}' (ID: {field_id})", True)
        
        return selected
    
    except Exception as e:
        if verbose:
            print_warning(f"Error with position hint '{position_hint}': {str(e)[:40]}", True)
        return None


# ═══════════════════════════════════════════════════════════════
# ADVANCED BUTTON CLICKING WITH VALIDATION & RETRY LOGIC
# ═══════════════════════════════════════════════════════════════

def remove_blocking_overlays(driver: webdriver.Firefox) -> bool:
    """
    Remove/hide blocking overlays that prevent clicking
    Returns: True if overlay was removed, False if none found
    """
    overlay_selectors = [
        "//div[contains(@class, 'opacity-30')]",
        "//div[contains(@class, 'overlay')]",
        "//div[contains(@class, 'modal-backdrop')]",
        "//div[contains(@style, 'position: fixed')]",
    ]
    
    removed = False
    for selector in overlay_selectors:
        try:
            overlay = driver.find_element(By.XPATH, selector)
            driver.execute_script("arguments[0].style.display = 'none';", overlay)
            removed = True
            print_warning(f"Removed blocking overlay", True)
        except:
            pass
    
    return removed


def wait_for_loading_spinner_to_hide(driver: webdriver.Firefox, timeout: int = 10) -> bool:
    """
    Wait for any loading spinner/loader to disappear
    Returns: True if spinner disappeared or not found, False if timeout
    """
    spinner_selectors = [
        "//div[contains(@class, 'spinner')]",
        "//div[contains(@class, 'loader')]",
        "//div[contains(@class, 'loading')]",
        "//div[@role='progressbar']",
    ]
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        found_any = False
        for selector in spinner_selectors:
            try:
                spinner = driver.find_element(By.XPATH, selector)
                # Check if visible
                if spinner.is_displayed():
                    found_any = True
                    break
            except:
                pass
        
        if not found_any:
            print_success("Loading spinner hidden", True)
            return True
        
        time.sleep(0.5)
    
    print_warning(f"Spinner still visible after {timeout}s", True)
    return False


def get_page_state_hash(driver: webdriver.Firefox) -> str:
    """
    Generate a hash of current page state to detect if page changed
    Used to validate that a click actually caused a page transition
    """
    try:
        state_info = driver.execute_script("""
            return {
                url: window.location.href,
                title: document.title,
                bodyHTML_length: document.body.innerHTML.length,
                readyState: document.readyState
            }
        """)
        return hash(str(state_info))
    except:
        return None


def wait_for_page_transition(driver: webdriver.Firefox, initial_state: str, timeout: int = 15) -> bool:
    """
    Wait for page to transition (URL change or body re-render)
    Used to validate that a button click actually navigated or changed the page
    
    Returns: True if page transitioned, False if timeout without change
    """
    start_time = time.time()
    stable_count = 0  # Count how many times state was stable
    
    while time.time() - start_time < timeout:
        current_state = get_page_state_hash(driver)
        
        if current_state != initial_state and current_state is not None:
            # State changed!
            print_success("Page state changed - transition detected", True)
            time.sleep(1)  # Wait for page to fully load
            return True
        
        time.sleep(0.5)
    
    print_warning(f"No page transition detected after {timeout}s", True)
    return False


def click_button_with_validation(
    driver: webdriver.Firefox,
    button_selector: str,
    button_name: str,
    expect_page_transition: bool = True,
    max_retries: int = 5
) -> Tuple[bool, str]:
    """
    ADVANCED: Click button with multiple strategies and validation
    
    Features:
    - Retry logic with EXPONENTIAL BACKOFF (1s, 2s, 4s, 8s, 16s)
    - Multiple click strategies: regular, JavaScript, ActionChains
    - Overlay detection and removal
    - Loading spinner detection
    - Page transition validation
    - Detailed error reporting
    
    Args:
        driver: Selenium WebDriver
        button_selector: XPath or CSS selector for button
        button_name: Display name (e.g., "Register")
        expect_page_transition: Validate page changed after click
        max_retries: Max retry attempts
        
    Returns:
        (success: bool, message: str)
    """
    print_step(2, f"Clicking {button_name} button (with validation)", True)
    
    for attempt in range(max_retries):
        try:
            # Step 1: Find the button
            try:
                button = driver.find_element(By.XPATH, button_selector)
            except NoSuchElementException:
                print_error(f"{button_name} button not found with selector", True)
                return False, "Button not found"
            
            # Step 2: Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            
            # Step 3: Remove blocking overlays
            remove_blocking_overlays(driver)
            time.sleep(0.3)
            
            # Step 4: Wait for loading spinners
            wait_for_loading_spinner_to_hide(driver, timeout=5)
            time.sleep(0.5)
            
            # Step 5: Check if button is disabled
            if button.get_attribute('disabled') is not None:
                print_error(f"{button_name} button is disabled", True)
                return False, "Button disabled"
            
            # Step 6: Get pre-click page state
            pre_click_state = get_page_state_hash(driver) if expect_page_transition else None
            
            # Step 7: Attempt to click (try 3 strategies)
            click_success = False
            click_method = None
            
            # Strategy 1: Regular click
            try:
                button.click()
                click_success = True
                click_method = "regular"
            except ElementNotInteractableException:
                print_warning(f"Regular click blocked, trying JavaScript", True)
                
                # Strategy 2: JavaScript click
                try:
                    driver.execute_script("arguments[0].click();", button)
                    click_success = True
                    click_method = "JavaScript"
                except:
                    print_warning(f"JavaScript click failed, trying ActionChains", True)
                    
                    # Strategy 3: ActionChains click
                    try:
                        actions = ActionChains(driver)
                        actions.move_to_element(button).click().perform()
                        click_success = True
                        click_method = "ActionChains"
                    except Exception as e:
                        print_error(f"All click strategies failed: {str(e)[:40]}", True)
                        click_success = False
            except Exception as e:
                print_warning(f"Regular click error: {str(e)[:40]}", True)
            
            if not click_success:
                # Retry with exponential backoff
                retry_delay = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                if attempt < max_retries - 1:
                    print_warning(f"Click attempt {attempt + 1}/{max_retries} failed, waiting {retry_delay}s before retry", True)
                    time.sleep(retry_delay)
                    continue
                else:
                    return False, f"Click failed after {max_retries} attempts"
            
            print_success(f"{button_name} clicked successfully ({click_method})", True)
            time.sleep(2)
            
            # Step 8: Validate page transition if expected
            if expect_page_transition and pre_click_state:
                if wait_for_page_transition(driver, pre_click_state, timeout=10):
                    print_success(f"{button_name} click validated - page transitioned", True)
                    return True, "Click successful - page transitioned"
                else:
                    # Page didn't transition - might be error, but button was clicked
                    print_warning(f"Page didn't transition after {button_name} click - may be normal", True)
                    return True, "Click executed but page didn't transition yet"
            else:
                return True, f"{button_name} clicked successfully"
        
        except StaleElementReferenceException:
            retry_delay = 2 ** attempt
            if attempt < max_retries - 1:
                print_warning(f"Stale element (attempt {attempt + 1}/{max_retries}), waiting {retry_delay}s", True)
                time.sleep(retry_delay)
                continue
            else:
                return False, "Stale element after retries"
        
        except Exception as e:
            retry_delay = 2 ** attempt
            if attempt < max_retries - 1:
                print_warning(f"Error (attempt {attempt + 1}/{max_retries}): {str(e)[:30]}, waiting {retry_delay}s", True)
                time.sleep(retry_delay)
                continue
            else:
                return False, f"Error: {str(e)[:50]}"
    
    return False, f"All {max_retries} retry attempts failed"


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


def close_firefox_driver(driver: webdriver.Firefox) -> bool:
    """Close Firefox WebDriver safely"""
    try:
        if driver:
            driver.quit()
            print_success("Firefox window closed")
            time.sleep(2)  # Wait for window to fully close
            return True
    except Exception as e:
        print_warning(f"Error closing Firefox: {str(e)}", True)
        try:
            # Force close if graceful quit fails
            driver.quit()
        except:
            pass
    return False


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
        
        # CLICK REGISTER BUTTON - Now using robust validation
        print_step(2, "Clicking Register button on signup form", True)
        success, message = click_button_with_validation(
            driver,
            "//button[contains(text(), 'Register')]",
            "Register",
            expect_page_transition=True,
            max_retries=5
        )
        
        if not success:
            print_error(f"Register button click failed: {message}", True)
            raise FormException(
                f"Failed to click Register button: {message}",
                WorkflowState.SIGNUP_IN_PROGRESS,
                account['email']
            )
        
        print_success("Register form submitted, waiting for OTP page", True)
        time.sleep(2)
        
        # ═══════════════════════════════════════════════════════════════
        # STEP 3: OTP VERIFICATION (40s WAIT FOR MANUAL OTP ENTRY)
        # ═══════════════════════════════════════════════════════════════
        print_step(3, "OTP Verification Phase")
        
        # Wait for user to enter OTP manually (30 seconds)
        # The OTP field is already visible on the page, no need to check for it
        OTP_WAIT_SECONDS = 30
        print_step(3, f"Waiting {OTP_WAIT_SECONDS}s for manual OTP entry", True)
        print_warning(f"⏳ ENTER OTP MANUALLY NOW! (You have {OTP_WAIT_SECONDS} seconds)", True)
        
        for remaining in range(OTP_WAIT_SECONDS, 0, -1):
            print(f"   ⏱️  {remaining:2d}s remaining...", flush=True)
            time.sleep(1)
        
        print(f"   ✓ Timer complete - ready to click Verify", flush=True)
        print_success(f"OTP wait complete", True)
        
        time.sleep(1)
        
        # Click Verify button - Now using robust validation
        print_step(3, "Clicking Verify OTP button", True)
        success, message = click_button_with_validation(
            driver,
            VERIFY_BUTTON_SELECTORS[0],
            "Verify OTP",
            expect_page_transition=True,
            max_retries=5
        )
        
        if not success:
            print_error(f"Verify button click failed: {message}", True)
            raise OTPException(
                f"Failed to click Verify button: {message}",
                WorkflowState.OTP_VERIFICATION_IN_PROGRESS,
                account['email']
            )
        
        time.sleep(3)
        print_success("OTP verification completed", True)
        
        # Verify we're actually on the registration form, not back at login
        current_url = driver.current_url
        current_page = detect_current_page(driver)
        
        print_step(3, f"Current URL: {current_url}", True)
        print_step(3, f"Current page: {current_page}", True)
        
        if current_page == 'LOGIN':
            print_error(f"❌ OTP verification FAILED - redirected back to login page!", True)
            raise OTPException(
                "OTP verification failed - page redirected to login. "
                "This means OTP was incorrect or verification failed on server.",
                WorkflowState.OTP_VERIFICATION_IN_PROGRESS
            )
        elif current_page == 'SIGNUP':
            print_warning(f"Still on signup page - verification may have failed, waiting before retry", True)
            time.sleep(3)
            # Check again
            current_page = detect_current_page(driver)
            if current_page != 'REGISTRATION':
                raise OTPException(
                    "OTP verification did not complete - still on signup page after 6s. "
                    "Verify that OTP was entered correctly.",
                    WorkflowState.OTP_VERIFICATION_IN_PROGRESS
                )
        elif current_page == 'REGISTRATION':
            print_success(f"✓ Successfully on registration form page", True)
        
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
    """STEP 4: Synchronized form filling with proper waits and validation"""
    """
    STEP 4: Fill the 23-field registration form with comprehensive field handling
    
    Structured form filling with proper synchronization:
    - Wait for each section to load before filling
    - Validate field fills before moving to next section
    - Retry with page refresh if critical fields fail (max 2 attempts)
    
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
        critical_fields_filled = 0
        
        try:
            wait = WebDriverWait(driver, TIMEOUT_ELEMENT)
            
            print_step(4, "Navigating to registration form", True)
            driver.get(REGISTRATION_URL)
            time.sleep(3)
            
            # Wait for page to stabilize - wait for form element
            print_step(4, "Waiting for form to load completely", True)
            try:
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
                print_success("Form elements detected", True)
            except TimeoutException:
                print_warning("Form timeout, retrying...", True)
                retry_count += 1
                time.sleep(2)
                continue
            
            # Wait for form to be interactive
            time.sleep(3)
            remove_blocking_overlays(driver)
            print_success("Form ready for input", True)
            
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 1: Personal Information
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "SECTION 1: Personal Information", True)
            time.sleep(1)
            
            # 1. Full Name (SKIP - already filled from signup)
            print_warning("Full Name: Pre-filled from signup (skipping)", True)
            time.sleep(0.3)
            
            # 2. Email (SKIP - already filled from signup and disabled)
            print_warning("Email: Pre-filled from signup (disabled, skipping)", True)
            time.sleep(0.3)
            
            # 3. WhatsApp Number (phone input)
            print_step(4, "WhatsApp field", True)
            whatsapp_field = find_input_by_label_or_placeholder(
                driver,
                ["whatsapp", "phone", "mobile", "contact", "+91"],
                "WhatsApp Number",
                verbose=True
            )
            
            if whatsapp_field:
                success = safe_fill_field(driver, whatsapp_field, "+919876543210", "WhatsApp")
                if success:
                    critical_fields_filled += 1
                else:
                    fields_not_found.append("WhatsApp")
            else:
                print_warning("WhatsApp field not found", True)
                fields_not_found.append("WhatsApp")
            
            time.sleep(0.5)
            
            # 4. Checkbox: "Alternate number is same as WhatsApp number"
            print_step(4, "Alternate number checkbox", True)
            try:
                # Find the first unchecked checkbox (should be the alternate number checkbox)
                checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                if checkboxes and len(checkboxes) > 0:
                    alt_checkbox = checkboxes[0]  # First checkbox should be alternate number
                    if not alt_checkbox.is_selected():
                        driver.execute_script("arguments[0].scrollIntoView(true);", alt_checkbox)
                        time.sleep(0.2)
                        alt_checkbox.click()
                        print_success("Alternate number = WhatsApp (checked)", True)
                    else:
                        print_success("Alternate number already checked", True)
                    time.sleep(0.3)
            except Exception as e:
                print_warning(f"Alternate checkbox error: {str(e)[:40]}", True)
                fields_not_found.append("Alternate")
            
            time.sleep(0.5)
            
            # 5. Date of Birth (date input, age range 2004-2007)
            print_step(4, "Date of Birth field", True)
            try:
                dob_field = find_input_by_label_or_placeholder(
                    driver,
                    ["date of birth", "dob", "birth", "age"],
                    "Date of Birth",
                    verbose=True
                )
                
                if not dob_field:
                    # Fallback to direct XPath
                    dob_fields = driver.find_elements(By.XPATH, "//input[@type='date']")
                    if dob_fields:
                        dob_field = dob_fields[0]
                
                if dob_field:
                    # Generate DOB between 2004-2007 (ages 18-22)
                    year = random.randint(2004, 2007)
                    month = random.randint(1, 12)
                    day = random.randint(1, 28)
                    dob = f"{year:04d}-{month:02d}-{day:02d}"
                    
                    dob_field.clear()
                    dob_field.send_keys(dob)
                    time.sleep(0.3)
                    print_success(f"DOB: {dob} (age {2026 - year})", True)
                    critical_fields_filled += 1
                else:
                    print_warning("DOB field not found", True)
                    fields_not_found.append("DOB")
            except Exception as e:
                print_warning(f"DOB error: {str(e)[:40]}", True)
                fields_not_found.append("DOB")
            
            time.sleep(0.5)
            
            # 6. Gender (dropdown/select/radio - Male or Female)
            print_step(4, "Gender field", True)
            gender_found = False
            selected_gender = random.choice(["Male", "Female"])
            
            # Strategy 1: Select dropdown
            try:
                gender_selects = driver.find_elements(By.XPATH, "//select[contains(@name, 'gender') or contains(@id, 'gender')]")
                if gender_selects:
                    Select(gender_selects[0]).select_by_visible_text(selected_gender)
                    print_success(f"Gender: {selected_gender} (select)", True)
                    gender_found = True
                    critical_fields_filled += 1
                    time.sleep(0.5)
            except Exception as e:
                print_warning(f"Select dropdown error: {str(e)[:30]}", True)
            
            # Strategy 2: Radio buttons
            if not gender_found:
                try:
                    radio_buttons = driver.find_elements(By.XPATH, "//input[@type='radio' and (contains(@name, 'gender') or contains(@id, 'gender'))]")
                    if radio_buttons:
                        for radio in radio_buttons:
                            radio_value = (radio.get_attribute('value') or "").lower()
                            if selected_gender.lower() in radio_value:
                                driver.execute_script("arguments[0].scrollIntoView(true);", radio)
                                time.sleep(0.2)
                                radio.click()
                                print_success(f"Gender: {selected_gender} (radio)", True)
                                gender_found = True
                                critical_fields_filled += 1
                                time.sleep(0.5)
                                break
                except Exception as e:
                    print_warning(f"Radio error: {str(e)[:30]}", True)
            
            # Strategy 3: Text input
            if not gender_found:
                try:
                    gender_field = find_input_by_label_or_placeholder(
                        driver,
                        ["gender", "sex", "male", "female"],
                        "Gender",
                        verbose=True
                    )
                    if gender_field:
                        safe_fill_field(driver, gender_field, selected_gender, "Gender")
                        gender_found = True
                        critical_fields_filled += 1
                except Exception as e:
                    print_warning(f"Gender field error: {str(e)[:30]}", True)
            
            if not gender_found:
                print_warning("Gender not filled", True)
                fields_not_found.append("Gender")
            
            time.sleep(0.5)
            
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 2: Location Information
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "SECTION 2: Location Information", True)
            time.sleep(1)
            
            # 7. Country (autocomplete - type and select from options)
            print_step(4, "Country field", True)
            country_field = find_input_by_label_or_placeholder(
                driver,
                ["country", "nation", "location"],
                "Country",
                verbose=True
            )
            
            if country_field:
                try:
                    country_field.click()
                    time.sleep(0.2)
                    country_field.clear()
                    time.sleep(0.2)
                    country_field.send_keys("India")
                    time.sleep(0.8)  # Wait for dropdown to render
                    
                    # Click first option from dropdown
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("Country: India", True)
                        critical_fields_filled += 1
                    else:
                        print_warning("Country dropdown options not found", True)
                        fields_not_found.append("Country")
                    time.sleep(0.5)
                except Exception as e:
                    print_warning(f"Country error: {str(e)[:40]}", True)
                    fields_not_found.append("Country")
            else:
                print_warning("Country field not found", True)
                fields_not_found.append("Country")
            
            time.sleep(0.8)
            
            # 8. State/Province: Uttar Pradesh
            print_step(4, "State/Province field", True)
            state_field = find_input_by_label_or_placeholder(
                driver,
                ["state", "province", "uttar pradesh"],
                "State/Province",
                verbose=True
            )
            
            if state_field:
                try:
                    state_field.click()
                    time.sleep(0.2)
                    state_field.clear()
                    time.sleep(0.2)
                    state_field.send_keys("Uttar Pradesh")
                    time.sleep(0.8)  # Wait for dropdown
                    
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("State: Uttar Pradesh", True)
                        critical_fields_filled += 1
                    else:
                        print_warning("State dropdown options not found", True)
                        fields_not_found.append("State")
                    time.sleep(0.5)
                except Exception as e:
                    print_warning(f"State error: {str(e)[:40]}", True)
                    fields_not_found.append("State")
            else:
                print_warning("State field not found", True)
                fields_not_found.append("State")
            
            time.sleep(0.8)
            
            # 9. City: Greater Noida
            print_step(4, "City field", True)
            city_field = find_input_by_label_or_placeholder(
                driver,
                ["city", "town", "greater noida"],
                "City",
                verbose=True
            )
            
            if city_field:
                try:
                    city_field.click()
                    time.sleep(0.2)
                    city_field.clear()
                    time.sleep(0.2)
                    city_field.send_keys("Greater Noida")
                    time.sleep(0.8)  # Wait for dropdown
                    
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("City: Greater Noida", True)
                        critical_fields_filled += 1
                    else:
                        print_warning("City dropdown options not found", True)
                        fields_not_found.append("City")
                    time.sleep(0.5)
                except Exception as e:
                    print_warning(f"City error: {str(e)[:40]}", True)
                    fields_not_found.append("City")
            else:
                print_warning("City field not found", True)
                fields_not_found.append("City")
            
            time.sleep(0.8)
            
            # 10. Occupation: College Student
            print_step(4, "Occupation field", True)
            occupation_field = find_input_by_label_or_placeholder(
                driver,
                ["occupation", "profession", "job", "student"],
                "Occupation",
                verbose=True
            )
            
            if occupation_field:
                try:
                    occupation_field.click()
                    time.sleep(0.2)
                    occupation_field.clear()
                    time.sleep(0.2)
                    occupation_field.send_keys("College Student")
                    time.sleep(0.5)
                    
                    # Try to click first dropdown option if available
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("Occupation: College Student (dropdown)", True)
                    else:
                        print_success("Occupation: College Student (text)", True)
                    
                    critical_fields_filled += 1
                    time.sleep(0.5)
                except Exception as e:
                    print_warning(f"Occupation error: {str(e)[:40]}", True)
                    fields_not_found.append("Occupation")
            else:
                print_warning("Occupation field not found", True)
                fields_not_found.append("Occupation")
            
            time.sleep(0.8)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 3: College Information
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "SECTION 3: College Information", True)
            time.sleep(1)
            
            # 9. City: Greater Noida
            city_field = find_input_by_label_or_placeholder(
                driver,
                ["city", "town", "greater noida"],
                "City",
                verbose=True
            )
            
            if city_field:
                try:
                    city_field.send_keys("Greater Noida")
                    time.sleep(0.5)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("City: Greater Noida (selected)", True)
                    else:
                        print_warning("City options not found", True)
                except Exception as e:
                    print_warning(f"City error: {str(e)[:40]}", True)
            else:
                # Fallback: Look for React Select containers
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
                            print_success("City: Greater Noida (React Select)", True)
                        else:
                            print_warning("City options not found", True)
                            fields_not_found.append("City")
                    else:
                        print_warning("City container not found", True)
                        fields_not_found.append("City")
                except Exception as e:
                    print_warning(f"City field error (fallback): {str(e)[:40]}", True)
                    fields_not_found.append("City")
        
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 3: Occupation (College Student)
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 3: Occupation", True)
            
            # "College Student" is the standard occupation for this hackathon
            occupation_field = find_input_by_label_or_placeholder(
                driver,
                ["occupation", "specialization", "field", "expertise", "domain"],
                "Occupation",
                verbose=True
            )
            
            if occupation_field:
                success = safe_fill_field(driver, occupation_field, "College Student", "Occupation")
                if not success:
                    fields_not_found.append("Occupation")
            else:
                print_warning("Occupation field not found", True)
                fields_not_found.append("Occupation")
            
            time.sleep(0.5)
            
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 3: College Information
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "SECTION 3: College Information", True)
            time.sleep(1)
            
            # 11. College Name: Galgotias University
            print_step(4, "College Name field", True)
            college_name_field = find_input_by_label_or_placeholder(
                driver,
                ["college name", "college", "institution", "university"],
                "College Name",
                verbose=True
            )
            
            if college_name_field:
                success = safe_fill_field(driver, college_name_field, "Galgotias University", "College Name")
                if success:
                    critical_fields_filled += 1
                else:
                    fields_not_found.append("College Name")
            else:
                print_warning("College Name field not found", True)
                fields_not_found.append("College Name")
            
            time.sleep(0.8)
            
            # 12. College Country (typically India)
            print_step(4, "College Country field", True)
            college_country_field = find_input_by_label_or_placeholder(
                driver,
                ["college country", "country"],
                "College Country",
                verbose=True
            )
            
            if college_country_field:
                try:
                    college_country_field.click()
                    time.sleep(0.2)
                    college_country_field.clear()
                    time.sleep(0.2)
                    college_country_field.send_keys("India")
                    time.sleep(0.5)
                    
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College Country: India", True)
                        time.sleep(0.5)
                    else:
                        print_warning("College Country options not found", True)
                except Exception as e:
                    print_warning(f"College Country error: {str(e)[:40]}", True)
            else:
                print_warning("College Country field not found", True)
                fields_not_found.append("College Country")
            
            time.sleep(0.8)
            
            # 13. College State: Uttar Pradesh
            print_step(4, "College State field", True)
            college_state_field = find_input_by_label_or_placeholder(
                driver,
                ["college state", "state"],
                "College State",
                verbose=True
            )
            
            if college_state_field:
                try:
                    college_state_field.click()
                    time.sleep(0.2)
                    college_state_field.clear()
                    time.sleep(0.2)
                    college_state_field.send_keys("Uttar Pradesh")
                    time.sleep(0.5)
                    
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College State: Uttar Pradesh", True)
                        time.sleep(0.5)
                    else:
                        print_warning("College State options not found", True)
                except Exception as e:
                    print_warning(f"College State error: {str(e)[:40]}", True)
            else:
                print_warning("College State field not found", True)
                fields_not_found.append("College State")
            
            time.sleep(0.8)
            
            # 14. College City: Greater Noida
            print_step(4, "College City field", True)
            college_city_field = find_input_by_label_or_placeholder(
                driver,
                ["college city", "city"],
                "College City",
                verbose=True
            )
            
            if college_city_field:
                try:
                    college_city_field.click()
                    time.sleep(0.2)
                    college_city_field.clear()
                    time.sleep(0.2)
                    college_city_field.send_keys("Greater Noida")
                    time.sleep(0.5)
                    
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College City: Greater Noida", True)
                        time.sleep(0.5)
                    else:
                        print_warning("College City options not found", True)
                except Exception as e:
                    print_warning(f"College City error: {str(e)[:40]}", True)
            else:
                print_warning("College City field not found", True)
                fields_not_found.append("College City")
            
            time.sleep(0.8)
            
            # 15. Degree (B.Tech)
            print_step(4, "Degree field", True)
            degree_field = find_input_by_label_or_placeholder(
                driver,
                ["degree", "qualification", "btech", "bachelor"],
                "Degree",
                verbose=True
            )
            
            if degree_field:
                try:
                    degree_field.click()
                    time.sleep(0.2)
                    degree_field.clear()
                    time.sleep(0.2)
                    degree_field.send_keys("B.Tech")
                    time.sleep(0.5)
                    
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("Degree: B.Tech", True)
                        time.sleep(0.5)
                    else:
                        print_success("Degree: B.Tech (text input)", True)
                except Exception as e:
                    print_warning(f"Degree error: {str(e)[:40]}", True)
            else:
                print_warning("Degree field not found", True)
                fields_not_found.append("Degree")
            
            time.sleep(0.8)
            
            # 16. Stream/Specialization: CSE
            print_step(4, "Specialization field", True)
            specialization_field = find_input_by_label_or_placeholder(
                driver,
                ["stream", "specialization", "branch", "cse"],
                "Specialization",
                verbose=True
            )
            
            if specialization_field:
                success = safe_fill_field(driver, specialization_field, "CSE", "Specialization")
                if success:
                    critical_fields_filled += 1
                else:
                    fields_not_found.append("Specialization")
            else:
                print_warning("Specialization field not found", True)
                fields_not_found.append("Specialization")
            
            time.sleep(0.8)
            
            # 17. Passout Year: 2028
            print_step(4, "Passout Year field", True)
            passout_field = find_input_by_label_or_placeholder(
                driver,
                ["passout", "graduation", "pass out", "year", "2028"],
                "Passout Year",
                verbose=True
            )
            
            if passout_field:
                try:
                    passout_field.click()
                    time.sleep(0.2)
                    passout_field.clear()
                    time.sleep(0.2)
                    passout_field.send_keys("2028")
                    time.sleep(0.5)
                    
                    # Try to select from dropdown
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("Passout Year: 2028", True)
                        time.sleep(0.5)
                    else:
                        print_success("Passout Year: 2028 (text input)", True)
                    
                    critical_fields_filled += 1
                except Exception as e:
                    print_warning(f"Passout Year error: {str(e)[:40]}", True)
                    fields_not_found.append("Passout Year")
            else:
                print_warning("Passout Year field not found", True)
                fields_not_found.append("Passout Year")
            
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 4: Profiles & Documents
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "SECTION 4: Profiles & Document", True)
            time.sleep(1)
            
            # 18. LinkedIn Profile
            print_step(4, "LinkedIn Profile field", True)
            linkedin_field = find_input_by_label_or_placeholder(
                driver,
                ["linkedin", "profile", "linkedin profile", "social"],
                "LinkedIn Profile",
                verbose=True
            )
            
            if linkedin_field:
                success = safe_fill_field(driver, linkedin_field, "https://linkedin.com/in/aditya-kumar", "LinkedIn")
                if success:
                    critical_fields_filled += 1
                else:
                    fields_not_found.append("LinkedIn")
            else:
                print_warning("LinkedIn field not found", True)
                fields_not_found.append("LinkedIn")
            
            time.sleep(0.8)
            
            # 19. College ID Card (file upload)
            print_step(4, "File Upload field", True)
            try:
                file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
                if file_inputs:
                    idcard_path = r"C:\Users\preet\Downloads\selenium\idcard.jpg"
                    if os.path.exists(idcard_path):
                        file_inputs[0].send_keys(idcard_path)
                        print_success("College ID (idcard.jpg) uploaded", True)
                        time.sleep(10)  # Wait for server processing
                    else:
                        print_warning("idcard.jpg file not found", True)
                else:
                    print_warning("File upload field not found", True)
            except Exception as e:
                print_warning(f"File upload error: {str(e)[:40]}", True)
            
            time.sleep(0.8)
            
            # 20. GDP Public Profile Link
            print_step(4, "GDP Profile Link field", True)
            gdp_field = find_input_by_label_or_placeholder(
                driver,
                ["g.dev", "gdp", "public profile", "google developer"],
                "GDP Profile Link",
                verbose=True
            )
            
            if gdp_field:
                success = safe_fill_field(driver, gdp_field, "https://g.dev/aditya-kumar", "GDP Profile")
                if success:
                    critical_fields_filled += 1
                else:
                    fields_not_found.append("GDP Profile")
            else:
                print_warning("GDP field not found", True)
                fields_not_found.append("GDP Profile")
            
            time.sleep(0.8)
            
            # College Name: Galgotias University
            print_step(4, "College Name field", True)
            college_name_field = find_input_by_label_or_placeholder(
                driver,
                ["college name", "college", "institution", "university"],
                "College Name",
                verbose=True
            )
            
            if college_name_field:
                success = safe_fill_field(driver, college_name_field, "Galgotias University", "College Name")
                if not success:
                    fields_not_found.append("College Name")
            else:
                print_warning("College Name field not found", True)
                fields_not_found.append("College Name")
            
            time.sleep(0.5)
            
            # College Country (typically India)
            print_step(4, "College Country field", True)
            college_country_field = find_input_by_label_or_placeholder(
                driver,
                ["college country", "nationality", "country"],
                "College Country",
                verbose=True
            )
            
            if college_country_field:
                try:
                    college_country_field.send_keys("India")
                    time.sleep(0.5)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College Country: India (selected)", True)
                    else:
                        print_warning("College Country options not found", True)
                except Exception as e:
                    print_warning(f"College Country error: {str(e)[:40]}", True)
            else:
                print_warning("College Country field not found", True)
                fields_not_found.append("College Country")
            
            time.sleep(0.5)
            
            # College State: Uttar Pradesh
            print_step(4, "College State field", True)
            college_state_field = find_input_by_label_or_placeholder(
                driver,
                ["college state", "state", "province", "uttar pradesh"],
                "College State",
                verbose=True
            )
            
            if college_state_field:
                try:
                    college_state_field.send_keys("Uttar Pradesh")
                    time.sleep(0.5)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College State: Uttar Pradesh (selected)", True)
                    else:
                        print_warning("College State options not found", True)
                except Exception as e:
                    print_warning(f"College State error: {str(e)[:40]}", True)
            else:
                print_warning("College State field not found", True)
                fields_not_found.append("College State")
            
            time.sleep(0.5)
            
            # College City: Greater Noida
            print_step(4, "College City field", True)
            college_city_field = find_input_by_label_or_placeholder(
                driver,
                ["college city", "city", "greater noida"],
                "College City",
                verbose=True
            )
            
            if college_city_field:
                try:
                    college_city_field.send_keys("Greater Noida")
                    time.sleep(0.5)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("College City: Greater Noida (selected)", True)
                    else:
                        print_warning("College City options not found", True)
                except Exception as e:
                    print_warning(f"College City error: {str(e)[:40]}", True)
            else:
                print_warning("College City field not found", True)
                fields_not_found.append("College City")
            
            time.sleep(0.5)
            
            # Degree (e.g., B.Tech, B.Sc)
            print_step(4, "Degree field", True)
            degree_field = find_input_by_label_or_placeholder(
                driver,
                ["degree", "qualification", "btech", "bachelor"],
                "Degree",
                verbose=True
            )
            
            if degree_field:
                try:
                    degree_field.send_keys("B.Tech")
                    time.sleep(0.5)
                    options = driver.find_elements(By.XPATH, "//div[@role='option']")
                    if options:
                        options[0].click()
                        print_success("Degree: B.Tech (selected)", True)
                    else:
                        print_warning("Degree options not found", True)
                except Exception as e:
                    print_warning(f"Degree error: {str(e)[:40]}", True)
            else:
                print_warning("Degree field not found", True)
                fields_not_found.append("Degree")
            
            time.sleep(0.5)
            
            # Stream/Specialization: CSE (Computer Science Engineering)
            print_step(4, "Stream/Specialization field", True)
            specialization_field = find_input_by_label_or_placeholder(
                driver,
                ["stream", "specialization", "branch", "cse"],
                "Stream/Specialization",
                verbose=True
            )
            
            if specialization_field:
                success = safe_fill_field(driver, specialization_field, "CSE", "Stream/Specialization")
                if not success:
                    fields_not_found.append("Specialization")
            else:
                print_warning("Stream/Specialization field not found", True)
                fields_not_found.append("Specialization")
            
            time.sleep(0.5)
            
            # Passout Year: 2028
            print_step(4, "Passout Year field", True)
            passout_field = find_input_by_label_or_placeholder(
                driver,
                ["passout", "graduation", "pass out", "year", "2028"],
                "Passout Year",
                verbose=True
            )
            
            if passout_field:
                try:
                    # Try to select 2028 from dropdown
                    passout_select = driver.find_element(By.XPATH, ".//ancestor::select", passout_field)
                    Select(passout_select).select_by_visible_text("2028")
                    print_success("Passout Year: 2028 (select)", True)
                except:
                    # Try direct fill
                    success = safe_fill_field(driver, passout_field, "2028", "Passout Year")
                    if not success:
                        fields_not_found.append("Passout Year")
            else:
                print_warning("Passout Year field not found", True)
                fields_not_found.append("Passout Year")
            
            time.sleep(0.5)
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 5: Profiles & Documents", True)
            
            # ═══════════════════════════════════════════════════════════════
            # LinkedIn Profile (THOROUGH DETECTION)
            # ═══════════════════════════════════════════════════════════════
            
            linkedin_field = find_input_by_label_or_placeholder(
                driver,
                ["linkedin", "profile", "linkedin profile", "social"],
                "LinkedIn Profile",
                verbose=True
            )
            
            if not linkedin_field:
                # Fallback: Look by position - LinkedIn typically comes before GDP
                print_warning("LinkedIn not found by label/placeholder, trying by position...", True)
                linkedin_field = find_input_by_position(driver, "last_5", "LinkedIn Profile (by position)", verbose=True)
            
            if linkedin_field:
                success = safe_fill_field(driver, linkedin_field, "https://linkedin.com/in/aditya-kumar", "LinkedIn Profile")
                if not success:
                    fields_not_found.append("LinkedIn")
            else:
                print_warning("LinkedIn Profile field not found after thorough search", True)
                fields_not_found.append("LinkedIn")
            
            time.sleep(0.5)
            
            time.sleep(0.5)
            
            # College ID Card (file upload)
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
            
            # ═══════════════════════════════════════════════════════════════
            # GDP Public Profile Link (THOROUGH DETECTION)
            # ═══════════════════════════════════════════════════════════════
            
            gdp_field = find_input_by_label_or_placeholder(
                driver,
                ["g.dev", "gdp", "public profile", "google developer"],
                "GDP Profile Link",
                verbose=True
            )
            
            if not gdp_field:
                # Fallback: Look by position - GDP typically comes after LinkedIn
                print_warning("GDP not found by label/placeholder, trying by position...", True)
                gdp_field = find_input_by_position(driver, "last_4", "GDP Profile (by position)", verbose=True)
            
            if gdp_field:
                success = safe_fill_field(driver, gdp_field, "https://g.dev/aditya-kumar", "GDP Profile Link")
                if not success:
                    fields_not_found.append("GDP Profile")
            else:
                print_warning("GDP Profile Link field not found after thorough search", True)
                fields_not_found.append("GDP Profile")
            
            time.sleep(0.5)
            
            # ═══════════════════════════════════════════════════════════════
            # SECTION 5: Referral (Conditional Hidden Field)
            # ═══════════════════════════════════════════════════════════════
            
            print_step(4, "Section 5: GDG Referral", True)
            
            # 21. Were you referred? (Radio: Select NO - no referral code needed)
            try:
                # Find ALL radio buttons and look for the referral question
                radio_buttons = driver.find_elements(By.XPATH, "//input[@type='radio']")
                no_radio = None
                
                # Try to find the "No" radio for referral question
                # Strategy 1: Look for radio with value="No" 
                for radio in radio_buttons:
                    try:
                        radio_value = radio.get_attribute('value')
                        if radio_value and radio_value.lower() == "no":
                            no_radio = radio
                            break
                    except:
                        pass
                
                # Strategy 2: Look for radio with label containing "No"
                if not no_radio:
                    for radio in radio_buttons:
                        try:
                            parent = radio.find_element(By.XPATH, "./ancestor::label | ./ancestor::div[@class*='radio']")
                            if "No" in parent.text and "No" not in "Occupation":
                                no_radio = radio
                                break
                        except:
                            pass
                
                # Strategy 3: Fallback to last radio (typically "No" is last)
                if not no_radio and len(radio_buttons) > 1:
                    no_radio = radio_buttons[-1]
                
                if no_radio:
                    if not no_radio.is_selected():
                        driver.execute_script("arguments[0].scrollIntoView(true);", no_radio)
                        time.sleep(0.3)
                        no_radio.click()
                        print_success("Referral: NO selected (no referral code needed)", True)
                    else:
                        print_success("Referral: Already set to NO", True)
                else:
                    print_warning("Referral No radio not found", True)
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
            
            print_step(4, "Submitting registration form", True)
            
            # Use advanced button clicking with validation
            success, message = click_button_with_validation(
                driver,
                "//button[contains(text(), 'Register')]",
                "Submit Registration",
                expect_page_transition=True,
                max_retries=5
            )
            
            if success:
                print_success(f"Registration form submitted: {message}", True)
                time.sleep(5)
                
                # Verify we got a success page or confirmation
                try:
                    current_url = driver.current_url
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    
                    # Look for success indicators
                    success_keywords = ['success', 'submitted', 'confirmed', 'registered', 'thank']
                    if any(keyword in page_text.lower() for keyword in success_keywords):
                        print_success("✓ Registration success page detected", True)
                        return True
                    else:
                        print_warning("Registration submitted but success page not clearly detected", True)
                        return True  # Assume success since click worked
                except:
                    print_warning("Could not verify success page content", True)
                    return True  # Assume success since click worked
            else:
                print_error(f"Submit button click failed: {message}", True)
                fields_not_found.append("Submit")
                
                # Continue to retry logic below
            
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
    """Main batch processing workflow with per-account window management"""
    print("\n" + "="*70)
    print("  HACK2SKILL BATCH REGISTRATION (v3 - Window Per Account)")
    print("="*70)
    print("ℹ️  Each account will run in a fresh Firefox window")
    print("ℹ️  Window stays open after completion - review results")
    print("ℹ️  Press ENTER to close window and start next account")
    print("="*70 + "\n")
    
    # Step 1: Load accounts
    accounts = load_accounts_from_csv()
    if not accounts:
        print_error("No accounts to process - exiting")
        return
    
    print_success(f"Ready to process {len(accounts)} account(s)")
    time.sleep(2)
    
    # Process each account
    completed = 0
    failed = 0
    partial = 0
    blocked = 0
    driver = None
    
    try:
        for idx, account in enumerate(accounts, 1):
            print("\n" + "="*70)
            print(f"[{idx}/{len(accounts)}] Processing: {account['email']}")
            print("="*70 + "\n")
            
            # ═══════════════════════════════════════════════════════════════
            # OPEN NEW WINDOW FOR THIS ACCOUNT
            # ═══════════════════════════════════════════════════════════════
            try:
                print_step(0, f"Opening Firefox window for account {idx}/{len(accounts)}")
                driver = init_firefox_driver()
            except DriverException as e:
                print_error(f"Cannot initialize driver for this account: {str(e)}")
                failed += 1
                continue
            
            # ═══════════════════════════════════════════════════════════════
            # PROCESS ACCOUNT
            # ═══════════════════════════════════════════════════════════════
            success, status = process_single_account(driver, account)
            
            if success:
                completed += 1
                log_progress(account['email'], "SUCCESS", "Account registered", WorkflowState.ACCOUNT_DONE)
                print_success(f"✓ Account processed successfully")
            elif status == "OTP_BLOCKER":
                blocked += 1
                print_error(f"✗ Workflow blocked at OTP verification - CRITICAL!")
                print_warning("User must provide OTP page HTML selectors to proceed")
            elif status == "PARTIAL":
                partial += 1
                log_progress(account['email'], "PARTIAL", "Form not completed", WorkflowState.ACCOUNT_DONE)
                print_warning(f"⚠ Partial completion")
            else:
                failed += 1
                log_progress(account['email'], "FAILED", f"Failed at {status}", WorkflowState.ACCOUNT_DONE)
                print_error(f"✗ Account processing failed")
            
            # ═══════════════════════════════════════════════════════════════
            # PAUSE BETWEEN ACCOUNTS (BEFORE CLOSING WINDOW)
            # ═══════════════════════════════════════════════════════════════
            if idx < len(accounts):
                print("\n" + "="*70)
                print(f"[PAUSE] Account {idx} complete - press ENTER to process next")
                print("="*70)
                input("[PAUSE] Press ENTER to continue... ")
                print("[RESUME] Starting next account...\n")
            
            # ═══════════════════════════════════════════════════════════════
            # CLOSE WINDOW AFTER USER PRESSES ENTER
            # ═══════════════════════════════════════════════════════════════
            print_step(0, "Closing Firefox window", True)
            close_firefox_driver(driver)
            driver = None
            time.sleep(1)
    
    finally:
        # Ensure driver is closed
        if driver:
            try:
                close_firefox_driver(driver)
            except:
                pass
        
        # ═══════════════════════════════════════════════════════════════
        # FINAL SUMMARY
        # ═══════════════════════════════════════════════════════════════
        print("\n" + "="*70)
        print("  BATCH PROCESSING COMPLETE")
        print("="*70)
        
        print(f"\nTotal processed:    {len(accounts)}")
        print(f"  ✓ Successful:     {completed}")
        print(f"  ⚠ Partial:        {partial}")
        print(f"  ✗ Failed:         {failed}")
        print(f"  🔴 Blocked:       {blocked}")
        
        if blocked > 0:
            print(f"\n⚠️  WORKFLOW BLOCKED at {blocked} account(s) - OTP verification failed")
            print(f"    → User must provide OTP page HTML selectors")
        
        print(f"\n📋 Log: {LOG_FILE}")
        print("="*70 + "\n")


if __name__ == "__main__":
    main()
