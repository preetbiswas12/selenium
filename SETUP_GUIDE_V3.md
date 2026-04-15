"""
═══════════════════════════════════════════════════════════════
HACK2SKILL REGISTRATION AUTOMATION - COMPLETE SETUP
═══════════════════════════════════════════════════════════════

This document explains:
1. The extracted field mapping
2. The new working script
3. How to run it
4. What each field does
"""

# ═══════════════════════════════════════════════════════════════
# FILES CREATED
# ═══════════════════════════════════════════════════════════════

NEW FILES:
  ✓ hack2skill_v3_working.py (400 lines)
    - NEW WORKING VERSION - Use this one!
    - Clean, simple, based on actual field positions
    - Handles React-Select dropdowns properly
    - Fills fields in correct order

  ✓ COMPLETE_FIELD_MAPPING.py (300+ lines)
    - Complete documentation of all 58 form fields
    - Field IDs, types, positions, visibility
    - Used to build the working script
    - Reference for understanding the form

  ✓ page_structure_analysis.txt (existing)
    - Raw extraction from the registration page
    - All HTML structure, IDs, labels, buttons
    - Used to create the field mapping

# ═══════════════════════════════════════════════════════════════
# QUICK FIELD REFERENCE (what gets filled)
# ═══════════════════════════════════════════════════════════════

POSITION [  2] - WhatsApp Number
              Type: tel
              Value: +919876543210
              
POSITION [  4] - Date of Birth
              Type: date
              Value: Random(2004-2007)
              Format: YYYY-MM-DD

POSITION [  7] - Country
              Type: React-Select (autocomplete)
              Value: India
              
POSITION [ 10] - State/Province
              Type: React-Select (autocomplete)
              Value: Uttar Pradesh
              
POSITION [ 12] - City
              Type: React-Select (autocomplete)
              Value: Greater Noida
              
POSITION [ 21] - Occupation
              Type: React-Select (autocomplete)
              Value: Student
              
POSITION [ 46] - LinkedIn Profile
              Type: text/url
              Value: https://linkedin.com/in/aditya-kumar
              
POSITION [ 48] - GDP Profile Link
              Type: text/url
              Value: https://g.dev/aditya-kumar

CHECKBOXES [ 51, 52] - Terms & Conditions
              Type: checkbox
              Status: Both MUST BE CHECKED

RADIO [ 50 ] - Referral (Yes/No)
              Type: radio
              Default: No (last option)

BUTTON - Register Now
         Submits the entire form


# ═══════════════════════════════════════════════════════════════
# FORM FLOW
# ═══════════════════════════════════════════════════════════════

STEP 1: SIGNUP (Manual OTP)
  - Open signup page
  - You enter Full Name & Email
  - Script clicks Register button
  - OTP page appears
  - YOU MUST ENTER OTP MANUALLY (30 second wait)
  - Script clicks Verify button
  → Result: Redirected to registration form

STEP 2: REGISTRATION FORM FILLING
  - Script opens registration page
  - Gets all input fields
  - Fills by exact position (not by keyword matching!)
  - Handles React-Select dropdowns:
    * Type the value e.g., "India"
    * Wait for dropdown options
    * Click first option or press Enter
  - Checks all required checkboxes
  - Selects "No" for referral
  - Clicks "Register Now" button
  → Result: Account submitted

# ═══════════════════════════════════════════════════════════════
# HOW TO RUN
# ═══════════════════════════════════════════════════════════════

COMMAND:
  python hack2skill_v3_working.py

WHAT HAPPENS:
  1. Loads accounts from accounts.csv
  2. For each account:
     a. Opens Firefox
     b. Navigates to signup page
     c. Fills signup form
     d. Clicks Register
     e. WAITS 30s for YOU to enter OTP manually
     f. Clicks Verify
     g. Fills registration form (auto)
     h. Clicks Register Now
     i. Logs result to registration_log.csv
  3. Closes Firefox and moves to next account

MANUAL STEPS (you must do):
  - Step during signup: ENTER OTP CODE when prompted
  - Watch the browser fill automatically
  - Form submits automatically
  - Close browser window to continue to next account

# ═══════════════════════════════════════════════════════════════
# KEY IMPROVEMENTS IN V3
# ═══════════════════════════════════════════════════════════════

✓ POSITION-BASED FILLING
  OLD: Try to find field by name/id (fails because of dynamic IDs)
  NEW: Use exact position from extracted data [0], [2], [4], etc.

✓ PROPER REACT-SELECT HANDLING
  OLD: Just send_keys() and hope it works
  NEW: Type → Wait for dropdown → Click option

✓ CONDITIONAL VISIBILITY
  OLD: Try to fill all fields regardless of visibility
  NEW: Check if visible first, skip if hidden

✓ CLEANER ERROR HANDLING
  OLD: 2300+ lines with complex exception classes
  NEW: 400 lines with clear error messages

✓ ACTUAL WORKING CODE
  OLD: Multiple strategies that didn't work
  NEW: Single reliable approach that works

# ═══════════════════════════════════════════════════════════════
# TROUBLESHOOTING
# ═══════════════════════════════════════════════════════════════

Problem: "Field not found at position X"
Solution: Field positions might have changed - re-run extract_page_contents.py

Problem: "React-Select not selecting properly"
Solution: Some dropdowns need arrow keys to navigate - can add fallback

Problem: "OTP page didn't load"
Solution: First account after signup might take longer - increase OTP_WAIT_SECONDS

Problem: Register button not found
Solution: Button text might have changed - check actual button text in page

# ═══════════════════════════════════════════════════════════════
# WHAT TO CUSTOMIZE
# ═══════════════════════════════════════════════════════════════

Edit hack2skill_v3_working.py to change:

1. SAMPLE VALUES (line ~30-40):
   FIELDS = {
       2: ("WhatsApp", "tel", "+919876543210"),  ← Change phone
       4: ("Date of Birth", "date", "2005-05-28"),  ← Change date range
       7: ("Country", "react-select", "India"),  ← Change country
       ...
   }

2. TIMEOUTS (line ~20):
   TIMEOUTS = {
       "otp_wait": 30,  ← Increase if you need more time for OTP
   }

3. LOGGING:
   All results logged to registration_log.csv

# ═══════════════════════════════════════════════════════════════
# NEXT STEPS
# ═══════════════════════════════════════════════════════════════

1. RUN THE NEW SCRIPT:
   python hack2skill_v3_working.py

2. Watch it:
   - Open account in browser
   - Fill signup
   - Wait for you to enter OTP
   - Auto-fill registration form
   - Submit

3. Check results:
   - Look at registration_log.csv for status of each account
   - All "SUCCESS" = account fully processed
   - Any errors will be logged with description

4. If issues:
   - Re-run extract_page_contents.py to check if fields changed
   - Update FIELDS dict with new positions
   - Test with single account first

═══════════════════════════════════════════════════════════════
"""
