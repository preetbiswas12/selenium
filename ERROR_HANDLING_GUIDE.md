# Error Handling & Exception Guide

## Overview

The refactored workflow (`hack2skill_batch_form_filler_v2.py`) includes comprehensive error handling organized by exception type, recovery strategy, and severity.

---

## Exception Hierarchy

```
WorkflowException (Base)
│
├── DriverException
│   ├── DriverInitializationError
│   └── DriverClosureError
│
├── NavigationException
│   ├── PageLoadTimeoutError
│   └── NavigationFailedError
│
├── FormException
│   ├── ElementNotFoundError
│   ├── FieldFillError
│   └── ValidationError
│
├── OTPException (⚠️ CRITICAL - BLOCKS WORKFLOW)
│   ├── OTPFieldNotFoundError ⚠️⚠️⚠️ REQUIRES USER ACTION
│   ├── VerifyButtonNotFoundError ⚠️⚠️⚠️ REQUIRES USER ACTION
│   ├── OTPTimeoutError
│   └── OTPVerificationFailedError
│
└── NetworkException
    ├── ConnectionTimeoutError
    └── ConnectionDroppedError
```

---

## Exception Details & Recovery

### 🔴 CRITICAL EXCEPTIONS - Require User Action

#### 1. **OTPFieldNotFoundError** ⚠️⚠️⚠️

**When it occurs:**
- Script navigates to OTP verification page
- Attempts to locate OTP input field
- Tried all built-in selectors
- No matching element found in DOM

**Error Message:**
```
❌ CRITICAL: OTP field not found!
   Tried selectors: [list of attempted selectors]
   Workflow is BLOCKED - user must provide actual OTP field selector
```

**Why it happens:**
- Website uses custom HTML structure
- OTP field uses non-standard attribute names
- Field may be inside React/dynamic component
- Placeholder text is different than expected

**How to fix:**
1. Open browser and navigate to OTP verification page
2. Right-click on OTP input field → "Inspect Element"
3. Look at the HTML element:
   ```html
   <input id="otp-code" type="text" placeholder="Enter 6-digit code" />
   <!-- or you might see: -->
   <input name="verification_code" data-otp="true" />
   <!-- or: -->
   <input class="otp-field" />
   ```
4. Extract the selector (use id, name, class, data-*, or xpath)
5. Add to `OTP_INPUT_SELECTORS` list in script:
   ```python
   OTP_INPUT_SELECTORS = [
       'YOUR_ACTUAL_SELECTOR_HERE',  # ← Add here
       # ... existing selectors ...
   ]
   ```

**Examples of selectors:**
```python
# By ID
"//input[@id='otp']"

# By name
"//input[@name='otp_code']"

# By class
"//input[@class='otp-field']"

# By data attribute
"//input[@data-testid='otp-input']"

# By placeholder (if different)
"//input[@placeholder='Enter 6-digit code']"

# Complex: within form
"//form[@id='otp-form']//input[@type='text']"
```

**Workaround (temporary):**
- Manually enter OTP and click Verify
- Script will detect if you completed it

**Resolution:**
Once user provides actual selector → Update script → Rerun

---

#### 2. **VerifyButtonNotFoundError** ⚠️⚠️⚠️

**When it occurs:**
- OTP field was found successfully
- User enters OTP manually
- Script attempts to click Verify button
- No matching button element found

**Error Message:**
```
❌ CRITICAL: Verify button not found!
   Tried selectors: [list of attempted selectors]
   Workflow is BLOCKED - user must provide actual Verify button selector
```

**How to fix:**
1. On OTP verification page, right-click Verify button → "Inspect Element"
2. Look at the HTML:
   ```html
   <button class="verify-btn">Verify OTP</button>
   <!-- or: -->
   <button id="verify-button" type="submit">Confirm</button>
   ```
3. Extract the selector
4. Add to `VERIFY_BUTTON_SELECTORS` in script:
   ```python
   VERIFY_BUTTON_SELECTORS = [
       'YOUR_ACTUAL_SELECTOR_HERE',  # ← Add here
       # ... existing selectors ...
   ]
   ```

**Examples of selectors:**
```python
# By text content (exact)
"//button[contains(text(), 'Verify OTP')]"

# By ID
"//button[@id='verify']"

# By class
"//button[@class='btn-verify']"

# Flexible text search
"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'verify')]"
```

---

### 🟡 HIGH-PRIORITY EXCEPTIONS - Automatic Recovery Possible

#### 3. **ElementNotFoundError**

**When it occurs:**
- During signup: Full Name, Email, Register button not found
- During form filling: Specific form field not found

**Possible causes:**
- Selector mismatch (website changed)
- Element not loaded yet (timing issue)
- Element is hidden/disabled
- Dynamic content not rendered

**Automatic recovery:**
```python
✓ Retry 2 times with 2-second delays
✓ Try alternate selectors (CSS, XPath alternatives)
✓ Skip optional fields and continue
✗ Fail account if critical field not found
```

**Example in logs:**
```
✗ Element 'Full Name field' not found
  → Retry 1/2... 
  → Still not found
  → Account marked as FAILED
  → Continue to next account
```

---

#### 4. **PageLoadTimeoutError**

**When it occurs:**
- Page navigation doesn't complete within 25 seconds
- Element wait exceeds timeout

**Automatic recovery:**
```python
✓ Retry navigation up to 3 times
✓ Wait 5 seconds between retries
✓ If repeated failures, skip account
```

**Log example:**
```
→ Navigating to signup page
  Timeout 1/3... retrying in 5s
  Timeout 2/3... retrying in 5s
  Timeout 3/3... giving up
✗ Page load failed - Account marked FAILED
```

---

### 🟢 LOW-PRIORITY EXCEPTIONS - Gracefully Handled

#### 5. **FieldFillError**

**When it occurs:**
- `send_keys()` fails (stale element, not interactable)
- Field is read-only or disabled
- Text validation fails

**Automatic recovery:**
```python
✓ Log warning message
✓ Try to scroll to element (make visible)
✓ Retry send_keys() once
✓ If fails, skip field and continue
✓ Mark account as PARTIAL (not FAILED)
```

**Example:**
```
⚠ Could not fill "College Name" field
  → Element not interactable
  → Skipping this field
  → Account marked as PARTIAL
```

---

#### 6. **ValidationError**

**When it occurs:**
- Form rejects invalid input (format error)
- Required field missing
- Server-side validation fails

**Automatic recovery:**
```python
✓ Log which field failed validation
✓ Try with alternate data
✓ If still fails, skip field
✓ Submit partial form
```

---

## Error Handling Flow Diagram

```
┌─────────────────────────────────────┐
│   Workflow Step (e.g., Signup)      │
└────────────┬────────────────────────┘
             │
             ▼
        Attempt Action
             │
        ┌────┴──────┐
        │            │
      SUCCESS    EXCEPTION
        │            │
        ▼       ┌────┴──────────────┐
       NEXT     │                   │
      STEP   CRITICAL?         NOT CRITICAL
        │     ╱    ╲               │
        │    /      \              │
        │   /        ╲             │
       CONTINUE  BLOCKING       TRY RECOVERY
                    │              │
                LOG & STOP    ┌────┴──────┐
                WORKFLOW      │            │
                              SUCCESS   FAILS
                              │          │
                          NEXT STEP  LOG & SKIP
                              │        FIELD
                          CONTINUE     │
                                    ACCOUNT
                                    CONTINUES
```

---

## Logging Strategy

### Log File Format: `registration_log.csv`

```csv
timestamp              | email              | status     | state                      | message
2026-04-14 10:30:45   | test@cock.li      | SUCCESS    | ACCOUNT_DONE               | Account registered
2026-04-14 10:35:20   | test2@cock.li     | FAILED     | OTP_PAGE_LOADED            | OTPFieldNotFoundError: ...
2026-04-14 10:40:15   | test3@cock.li     | PARTIAL    | FORM_SUBMITTED             | Some fields missing
2026-04-14 10:45:31   | test4@cock.li     | FAILED     | SIGNUP_IN_PROGRESS         | ElementNotFoundError: Full Name
```

### Console Output

Real-time color-coded feedback:
```
70] tests@cock.li
✓ Step 1: Loading accounts from CSV
✓ Step 2: Signup Phase (Full Name + Email)
   → Step 2: Navigating to signup page
   ✓ Signup page loaded
   → Step 2: Filling Full Name field
   ✓ Full Name entered: Aditya Kumar
   → Step 2: Filling Email field
   ✓ Email entered: test@cock.li
   → Step 2: Clicking Register button
   ✓ Register button clicked
✓ Step 3: OTP Verification Phase
   → Step 3: Locating OTP input field
   ✓ OTP field found with selector: //input[@placeholder='OTP']
   → Step 3: Waiting 30s for manual OTP entry
   ⏳ ENTER OTP MANUALLY NOW! (You have 30 seconds)
   ⏱️  30s remaining...
   ⏱️  15s remaining...
   ✓ Timer complete
   ✓ OTP detected: 6 character(s)
   → Step 3: Locating Verify button
   ✓ Verify button found with selector: //button[contains(text(), 'Verify')]
   → Step 3: Clicking Verify button
   ✓ Verify button clicked
   ✓ OTP verification completed
✓ Step 4: Registration Form Filling
   → Step 4: Navigating to registration form
   ✓ Registration page loaded
   ⚠ Form filling in BASIC mode (not all 23 fields)
   ⚠ Update fill_registration_form() for full form support
   ✓ Registration form completed (partial)
✓ Account processed successfully
```

---

## Configuration & Customization

### Timeout Settings

```python
TIMEOUT_PAGE_LOAD = 25      # seconds to wait for page navigation
TIMEOUT_ELEMENT = 15        # seconds to wait for element to appear
OTP_WAIT_SECONDS = 30       # seconds to wait for user OTP entry
```

Modify in script if needed:
```python
# For slower network
TIMEOUT_PAGE_LOAD = 40
TIMEOUT_ELEMENT = 25
```

### Retry Configuration

Currently hardcoded in exception handlers:
```python
# Page navigation retries
Max retries for page load: 3
Delay between retries: 5 seconds

# Element location retries
Max retries for element: 2
Delay between retries: 2 seconds

# Form submission
No retries (one attempt)
```

To increase retries, modify the function:
```python
MAX_PAGE_LOAD_RETRIES = 3    # ← Change this
RETRY_DELAY_SECONDS = 5      # ← Change this
```

---

## Testing & Validation

### Test Scenarios

1. **Happy Path (No Errors)**
   - All selectors correct
   - User enters OTP within 30s
   - Form fills completely
   - Expected: SUCCESS

2. **OTP Field Missing** ⚠️
   - OTP selector incorrect
   - Expected: OTPFieldNotFoundError

3. **Verify Button Missing** ⚠️
   - Verify selector incorrect
   - Expected: VerifyButtonNotFoundError

4. **Network Timeout**
   - Simulate slow connection
   - Expected: Retry then fail after 3 attempts

5. **Missing Form Fields**
   - Form field selector wrong
   - Expected: Log warning, skip field, mark PARTIAL

### How to Test Without Real Account

```bash
# Modify script to use test account
python hack2skill_batch_form_filler_v2.py
# Will fail at OTP stage (expected)
# Review error messages and fix selectors
```

---

## Debugging Tips

### Enable Verbose Logging

```python
# Add to script:
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.debug(f"Element found: {element.get_attribute('outerHTML')}")
```

### Inspect Elements Interactively

```python
# Pause script at specific point
import time; time.sleep(10)  # ← Gives 10 seconds to inspect browser

# Then manually check:
# Right-click → Inspect → Find element
# Copy CSS selector or XPath
```

### Screenshot on Error

```python
# Add to exception handler:
driver.save_screenshot(f"error_{account['email']}.png")
```

---

## Summary Table

| Exception | Severity | Recovery | Action |
|-----------|----------|----------|--------|
| OTPFieldNotFoundError | 🔴 CRITICAL | None | User provides selector |
| VerifyButtonNotFoundError | 🔴 CRITICAL | None | User provides selector |
| PageLoadTimeoutError | 🟡 HIGH | Retry 3x | Skip account if fails |
| ElementNotFoundError | 🟡 HIGH | Retry 2x | Skip optional field |
| FieldFillError | 🟢 LOW | Retry 1x | Skip field, mark PARTIAL |
| ValidationError | 🟢 LOW | Retry 1x | Skip field, mark PARTIAL |
| NetworkException | 🟡 HIGH | Retry 3x | Skip account if fails |

---

## Next Steps

1. **Run v2 script:**
   ```bash
   python hack2skill_batch_form_filler_v2.py
   ```

2. **Capture errors:**
   - First account will likely fail at OTP
   - Copy error message and selectors needed

3. **Provide page HTML:**
   - Share OTP page HTML with user
   - Update selectors in script
   - Rerun script

4. **Validate results:**
   - Check `registration_log.csv`
   - Review accounts that succeeded
   - Debug failed accounts

