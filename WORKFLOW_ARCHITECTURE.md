# Hack2Skill Registration Workflow Architecture

## 🎯 Overall Workflow

```
┌─────────────────────────────────────────────────────────────┐
│         HACK2SKILL BATCH REGISTRATION SYSTEM                │
└─────────────────────────────────────────────────────────────┘
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │  STEP 1: LOAD & VALIDATE ACCOUNTS FROM CSV          │
    │  - Read accounts_created.csv                        │
    │  - Validate email format                            │
    │  - Filter duplicates                                │
    │  Status: ACCOUNTS_LOADED                            │
    └──────────────────────────────────────────────────────┘
                            ↓
    FOR EACH ACCOUNT (LOOP):
    ┌──────────────────────────────────────────────────────┐
    │  STEP 2: INITIALIZE FIREFOX WEBDRIVER               │
    │  - Create new Firefox instance (incognito mode)     │
    │  - Clear cache/cookies                              │
    │  - Status: DRIVER_READY                             │
    └──────────────────────────────────────────────────────┘
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │  STEP 3: SIGNUP (Full Name + Email)                 │
    │  - Navigate to signup page                          │
    │  - Generate random Full Name (Indian)               │
    │  - Fill Full Name field                             │
    │  - Fill Email field (from CSV)                      │
    │  - Click Register button                            │
    │  - Wait for OTP page                                │
    │  Possible States:                                   │
    │    ✓ OTP_PAGE_LOADED                                │
    │    ✗ SIGNUP_FAILED (field not found)               │
    │    ✗ TIMEOUT (page didn't load)                     │
    │    ✗ NETWORK_ERROR                                  │
    └──────────────────────────────────────────────────────┘
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │  STEP 4: OTP VERIFICATION (MANUAL INPUT)             │
    │  - Detect OTP input field                           │
    │  - Start 30-second countdown timer                  │
    │  - Wait for user to manually enter OTP              │
    │  - Click Verify button                              │
    │  - Wait for form redirect                           │
    │  Possible States:                                   │
    │    ✓ OTP_VERIFIED (page transitioned)              │
    │    ✗ OTP_TIMEOUT (no verification within 30s)      │
    │    ✗ OTP_FIELD_NOT_FOUND (selector mismatch)       │
    │    ✗ VERIFY_BUTTON_NOT_FOUND (selector mismatch)   │
    │  CRITICAL: User must provide OTP selectors         │
    │  If these fail, script cannot proceed                │
    └──────────────────────────────────────────────────────┘
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │  STEP 5: FILL REGISTRATION FORM                      │
    │  - Wait for registration page to load               │
    │  - Fill 23 form fields:                             │
    │    1. Full Name      2. DOB          3. Gender      │
    │    4. WhatsApp       5. Alt Number   6. Country     │
    │    7. State          8. City         9. Occupation  │
    │    10. College Name  11. Coll State  12. Coll City  │
    │    13. Degree        14. Stream      15. Passout    │
    │    16. LinkedIn      17. ID Upload   18. GDP Link   │
    │    19. GDG Referral  20. Ref Code    21. Terms      │
    │    22. Submit                                       │
    │  Possible States:                                   │
    │    ✓ FORM_SUBMITTED (all fields filled + submit)   │
    │    ⚠ FORM_PARTIAL (some fields missing/failed)     │
    │    ✗ FIELD_NOT_FOUND (selector mismatch)           │
    │    ✗ VALIDATION_ERROR (form rejected input)        │
    │    ✗ TIMEOUT (page load took too long)             │
    │    ✗ NETWORK_ERROR (dropped connection)            │
    └──────────────────────────────────────────────────────┘
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │  STEP 6: LOG RESULT & CLEANUP                        │
    │  - Write status to registration_log.csv             │
    │  - Possible outcomes:                               │
    │    ✓ SUCCESS (all steps completed)                  │
    │    ⚠ PARTIAL (completed multiple steps)            │
    │    ✗ FAILED (blocked at early step)                │
    │  - Close driver                                     │
    │  - Clean temp files                                 │
    │  Status: ACCOUNT_DONE                              │
    └──────────────────────────────────────────────────────┘
                            ↓
                   (NEXT ACCOUNT)
                            ↓
    ┌──────────────────────────────────────────────────────┐
    │  FINAL SUMMARY                                       │
    │  - Total accounts processed                         │
    │  - Successful registrations                         │
    │  - Failed accounts (with reasons)                   │
    │  - Partial completions                              │
    │  - Log file location                                │
    └──────────────────────────────────────────────────────┘
```

---

## 🔴 CRITICAL BLOCKER: OTP Verification

The current workflow is **BLOCKED** at Step 4 (OTP Verification) because:

### Problem
- OTP input field selector doesn't match actual page HTML
- Verify button selector unknown
- Current selectors tried:
  ```xpath
  //input[@placeholder='OTP' or @placeholder='Enter OTP' or contains(@placeholder, 'OTP')]
  ```
  **Result:** NoSuchElementException (element not found)

### What's Needed
User must provide **ONE of the following**:

#### Option A: HTML Source Code
Paste the raw HTML of the OTP verification page, especially:
- OTP input field markup
- Verify button markup
- Page container/form elements

#### Option B: Browser Inspector Output
From browser Developer Tools:
- Right-click OTP input field → Inspect → Copy the HTML element
- Right-click Verify button → Inspect → Copy the HTML element

#### Option C: Visual Description
- Exact text on Verify button (e.g., "Verify OTP", "Verify", "Submit", "Confirm")
- OTP field placeholder text or label
- Any other visible components (progress bar, timer, info text)

### Once Provided
Will update selectors in `signup_and_verify_otp()` function:
```python
otp_field = wait.until(EC.presence_of_element_located((By.XPATH, "[YOUR_ACTUAL_SELECTOR]")))
verify_button = driver.find_element(By.XPATH, "[YOUR_ACTUAL_SELECTOR]")
```

---

## ⚠️ Exception Handling Strategy

### Exception Types
```
WorkflowException (Base)
├── DriverException
│   ├── DriverInitializationError
│   └── DriverClosureError
├── NavigationException
│   ├── PageLoadTimeoutError
│   └── NavigationFailedError
├── FormException
│   ├── ElementNotFoundError
│   ├── FieldFillError
│   └── ValidationError
├── OTPException (CRITICAL - blocks workflow)
│   ├── OTPFieldNotFoundError ⚠️ CURRENT BLOCKER
│   ├── VerifyButtonNotFoundError ⚠️ CURRENT BLOCKER
│   ├── OTPTimeoutError
│   └── OTPVerificationFailedError
└── NetworkException
    ├── ConnectionTimeoutError
    └── ConnectionDroppedError
```

### Recovery Strategies
```
Level 1 (Automatic Retry):
  - Page load timeout → Retry page load (3 times)
  - Field not found → Try alternate selectors
  - Network timeout → Wait 5s and retry

Level 2 (Skip Field):
  - Optional field missing → Log warning and continue
  - Non-critical selector → Use fallback CSS selector

Level 3 (Skip Account):
  - Required field not found → Skip account
  - OTP verification failed → Skip account
  - Form submission blocked → Skip account

Level 4 (Manual Intervention):
  - OTP selector unknown → Request user input
  - Unrecoverable error → Pause and ask user
```

---

## 📊 State Transitions

Allowed state transitions:
```
ACCOUNTS_LOADED
    ↓
[FOR EACH ACCOUNT]
    ↓
DRIVER_READY
    ↓
SIGNUP_IN_PROGRESS → OTP_PAGE_LOADED
                   → SIGNUP_FAILED (skip to next)
    ↓
OTP_VERIFICATION_IN_PROGRESS → OTP_VERIFIED
                              → OTP_TIMEOUT (skip to next)
                              → OTP_FIELD_NOT_FOUND (skip to next)
    ↓
FORM_FILLING_IN_PROGRESS → FORM_SUBMITTED (final: SUCCESS)
                         → FORM_PARTIAL (final: PARTIAL)
                         → FORM_FAILED (final: FAILED)
    ↓
ACCOUNT_LOGGING
    ↓
[RESULTS LOGGED]
```

---

## 🛡️ Error Handling Implementation

### Timeout Configuration
```python
WebDriver Wait Times:
  - Page navigation: 25 seconds
  - Element visibility: 15 seconds
  - Form submission: 10 seconds
  - OTP field: 25 seconds
  - Verify button: 10 seconds
  
Sleep Delays (safety):
  - Between steps: 1-3 seconds
  - Between accounts: 5 seconds
  - After form submit: 3 seconds
```

### Retry Logic
```python
Max Retries:
  - Page load retry: 3 attempts
  - Field location retry: 2 attempts
  - Form submission: 1 attempt (no retry)
  - OTP verification: 1 attempt (manual step)
```

---

## 📝 Logging Strategy

### Log File: `registration_log.csv`
```
timestamp              | email              | status     | message
2026-04-14 10:30:45   | test@cock.li      | SUCCESS    | Registered as Aditya Kumar
2026-04-14 10:35:20   | test2@cock.li     | FAILED     | OTP field selector not found
2026-04-14 10:40:15   | test3@cock.li     | PARTIAL    | Form submitted but missing college city
```

### Console Output
```
🟢 [10:30:45] [1/15] test@cock.li → SUCCESS
🔴 [10:35:20] [2/15] test2@cock.li → FAILED (OTP field not found)
🟡 [10:40:15] [3/15] test3@cock.li → PARTIAL (fields missing)
```

---

## 🚀 How to Run

```bash
# Check dependencies
python verify_setup.py

# Run batch registration
python hack2skill_batch_form_filler.py

# Monitor progress
tail -f registration_log.csv
```

---

## 📋 Checklist Before Running

- [ ] Firefox WebDriver downloaded and accessible
- [ ] `accounts_created.csv` present with valid emails
- [ ] Know OTP page HTML structure (or ready to provide it)
- [ ] Have 30 seconds per account for OTP entry
- [ ] Understand that form fill may be incomplete for first run
- [ ] Have registration_log.csv for monitoring results

---

## 🔧 Customization Points

To modify workflow, edit these variables:
```python
SIGNUP_PAGE_URL = "..."
REGISTRATION_URL = "..."
CSV_FILE = "..."
LOG_FILE = "..."
TIMEOUT_PAGE_LOAD = 25
TIMEOUT_ELEMENT = 15
OTP_WAIT_SECONDS = 30
```

---

## 📚 Related Files

- `hack2skill_batch_form_filler.py` → Main workflow script (needs refactoring)
- `accounts_created.csv` → Input: 15 email accounts
- `registration_log.csv` → Output: Results per account
- `FORM_FIELDS_REFERENCE.md` → Form field documentation
- `SELECTOR_GUIDE.md` → CSS/XPath selector examples

