# Quick Start Guide - Refactored Workflow

## 📋 What Changed?

**Old Version (v1):**
- ❌ Poor error handling
- ❌ Generic exception messages
- ❌ No retry logic
- ❌ No state tracking
- ❌ Hard to debug

**New Version (v2):**
- ✓ Custom exception types
- ✓ Clear error messages with recovery steps
- ✓ Automatic retry logic
- ✓ Workflow state tracking
- ✓ Better logging to CSV
- ✓ Proper exception hierarchy

---

## 🚀 How to Run

### Prerequisites
```bash
# 1. Install dependencies
pip install selenium

# 2. Verify Firefox is installed
firefox --version

# 3. Check GeckoDriver
python setup_geckodriver.py

# 4. Verify CSV exists
ls accounts_created.csv
```

### Run the Script

**Option A: Use OLD version (current working)**
```bash
python hack2skill_batch_form_filler.py
```

**Option B: Use NEW refactored version (better error handling)**
```bash
python hack2skill_batch_form_filler_v2.py
```

### During Execution

1. **Script starts**
   ```
   ======================================================================
     HACK2SKILL BATCH REGISTRATION (REFACTORED - Error Handling)
   ======================================================================
   ```

2. **Loads accounts**
   ```
   → Step 0: Loading accounts from CSV
   ✓ Loaded 13 account(s)
   ```

3. **First account processing**
   ```
   ======================================================================
   [1/13] Processing: cubic4355@cock.li
   ======================================================================
   ```

4. **Signup phase**
   ```
   → Step 2: Signup Phase (Full Name + Email)
      → Step 2: Navigating to signup page
      ✓ Signup page loaded
      → Step 2: Filling Full Name field
      ✓ Full Name entered: Aditya Kumar
      → Step 2: Filling Email field
      ✓ Email entered: cubic4355@cock.li
      → Step 2: Clicking Register button
      ✓ Register button clicked
   ```

5. **OTP verification - MANUAL STEP**
   ```
   → Step 3: OTP Verification Phase
      → Step 3: Locating OTP input field
      ✓ OTP field found
      → Step 3: Waiting 30s for manual OTP entry
      ⏳ ENTER OTP MANUALLY NOW! (You have 30 seconds)
      ⏱️  30s remaining...
      ⏱️  20s remaining...
      ... (countdown continues)
   ```
   **⚠️ At this point, you have 30 seconds to:**
   - Check your email for the OTP
   - Manually enter it in the browser OTP field
   - Script will auto-click the Verify button after 30s

6. **Form filling**
   ```
   → Step 4: Registration Form Filling
      → Step 4: Navigating to registration form
      ✓ Registration page loaded
      ✓ Registration form completed (partial)
   ```

7. **Result logging**
   ```
   ✓ Account processed successfully
   ```

8. **Next account** (waits 5 seconds)
   ```
   ⏳ Waiting 5 seconds before next account...
   ```

9. **Final summary**
   ```
   ======================================================================
     BATCH PROCESSING COMPLETE
   ======================================================================
   Total processed:    13
     ✓ Successful:     0
     ⚠ Partial:        0
     ✗ Failed:         13
     🔴 Blocked:       13

   ⚠️  WORKFLOW BLOCKED at 13 account(s) - OTP verification failed
       → User must provide OTP page HTML selectors
       → See WORKFLOW_ARCHITECTURE.md for instructions

   📋 Log: C:\Users\preet\Downloads\selenium\registration_log.csv
   ======================================================================
   ```

---

## 🔴 If You Get OTP Errors

### Error 1: OTPFieldNotFoundError

```
❌ CRITICAL: OTP field not found!
   Tried selectors: ['//input[@placeholder="OTP"]', ...]
   Workflow is BLOCKED - user must provide actual OTP field selector
```

**What to do:**
1. Go to the OTP verification page in the browser (from a failed run)
2. Right-click on the **OTP input field** → **Inspect Element**
3. You'll see HTML like:
   ```html
   <input id="otp-code" placeholder="Enter 6-digit code" />
   ```
4. Copy the relevant attributes (id, name, class, etc.)
5. Open `hack2skill_batch_form_filler_v2.py`
6. Find this section (around line 100):
   ```python
   OTP_INPUT_SELECTORS = [
       "//input[@placeholder='OTP']",
       "//input[@placeholder='Enter OTP']",
       # ⚠️ CRITICAL: Add actual selectors here
   ]
   ```
7. Add your actual selector:
   ```python
   OTP_INPUT_SELECTORS = [
       "//input[@id='otp-code']",  # ← YOUR ACTUAL SELECTOR
       "//input[@placeholder='OTP']",
       "//input[@placeholder='Enter OTP']",
   ]
   ```
8. Save the file
9. Run again: `python hack2skill_batch_form_filler_v2.py`

### Error 2: VerifyButtonNotFoundError

```
❌ CRITICAL: Verify button not found!
   Tried selectors: ['//button[contains(text(), "Verify")]', ...]
   Workflow is BLOCKED - user must provide actual Verify button selector
```

**What to do:**
1. Right-click on the **Verify button** → **Inspect Element**
2. You'll see HTML like:
   ```html
   <button class="btn-verify">Verify</button>
   ```
3. Find this section (around line 110):
   ```python
   VERIFY_BUTTON_SELECTORS = [
       "//button[contains(text(), 'Verify')]",
       # ⚠️ CRITICAL: Add actual selectors here
   ]
   ```
4. Add your actual selector:
   ```python
   VERIFY_BUTTON_SELECTORS = [
       "//button[@class='btn-verify']",  # ← YOUR ACTUAL SELECTOR
       "//button[contains(text(), 'Verify')]",
   ]
   ```
5. Save and run again

---

## 📊 Monitoring Results

### Check Log File

```bash
# View results in real-time
type registration_log.csv

# Expected format:
# timestamp,email,status,state,message
# 2026-04-14 10:30:45,test@cock.li,SUCCESS,ACCOUNT_DONE,Account registered
# 2026-04-14 10:35:20,test2@cock.li,FAILED,OTP_PAGE_LOADED,OTPFieldNotFoundError: ...
```

### Status Meanings

| Status | Meaning |
|--------|---------|
| SUCCESS | Account fully registered |
| PARTIAL | Reached form stage but some fields missing |
| FAILED | Blocked at early stage (signup/OTP) |
| OTP_BLOCKER | OTP selector not found (critical) |

---

## 🔧 Common Issues & Fixes

### Issue: Firefox not found
```
Error: Unable to locate firefox executable
```
**Fix:**
```bash
# Install Firefox first or modify script to add path
# Edit and add to Firefox initialization:
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
```

### Issue: GeckoDriver not found
```
Error: 'geckodriver' executable needs to be in PATH
```
**Fix:**
```bash
python setup_geckodriver.py
```

### Issue: CSV not found
```
❌ No accounts to process!
```
**Fix:**
```bash
# Make sure accounts_created.csv exists
ls accounts_created.csv
```

### Issue: Timeout waiting for page
```
⏱️  OTP page loading...
❌ Timeout: TimeoutException
```
**Fix:**
```python
# Increase timeout in script (increase these values)
TIMEOUT_PAGE_LOAD = 40  # was 25
TIMEOUT_ELEMENT = 25    # was 15
```

---

## 📚 Documentation Files

- **WORKFLOW_ARCHITECTURE.md** - Overall workflow design & states
- **ERROR_HANDLING_GUIDE.md** - Detailed exception handling & recovery
- **QUICK_START.md** (this file) - How to run & troubleshoot
- **FORM_FIELDS_REFERENCE.md** - Details on each of 23 form fields
- **SELECTOR_GUIDE.md** - CSS/XPath selector examples

---

## 🎯 Next Steps

### Immediate (Required to proceed)

1. **Run the script once:**
   ```bash
   python hack2skill_batch_form_filler_v2.py
   ```
   It will fail at OTP stage (expected)

2. **Capture the error message:**
   - Copy theTried selectors" part

3. **Inspect the page:**
   - Right-click OTP field → Inspect
   - Right-click Verify button → Inspect

4. **Update selectors in v2 script:**
   - Add your actual selectors

5. **Run again:**
   ```bash
   python hack2skill_batch_form_filler_v2.py
   ```

---

## 🎬 Start Now

```bash
# Install dependencies
pip install selenium

# Create GeckoDriver link
python setup_geckodriver.py

# Run NEW version with better error handling
python hack2skill_batch_form_filler_v2.py
```

**Key points:**
- ✓ Clear step-by-step progress
- ✓ Better error messages
- ✓ Automatic retries for common errors
- ✓ Detailed logging to CSV
- ✓ Easy to debug and fix

**Encounter OTP errors?** See ERROR_HANDLING_GUIDE.md for detailed instructions!

---

## Version Comparison

| Feature | v1 (Old) | v2 (New) |
|---------|----------|----------|
| Error handling | Generic | Custom exceptions ✓ |
| Error messages | Poor | Clear & actionable ✓ |
| Retry logic | None | Automatic ✓ |
| State tracking | No | Yes ✓ |
| Recovery strategy | No | Yes ✓ |
| Debugging | Hard | Easy ✓ |

**Recommendation:** Use v2 for better debugging and error messages!
