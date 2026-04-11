# 🤖 Hack2skill Registration Automation

**Automate bulk account registrations for Google Solution Challenge 2026 India.**

Pulls registration data from Google Sheets → Auto-fills forms → Handles OTP verification → Tracks progress.

---

## 📁 Project Structure

```
selenium/
├── main.py                       # Main automation script
├── browser_driver.py             # Selenium + stealth browser
├── email_handler.py              # OTP fetching from email
├── sheets_handler.py             # Google Sheets integration
├── captcha_handler.py            # CAPTCHA solving (manual/API)
├── config.py                     # Configuration & form selectors
├── test_setup.py                 # Setup validation script
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── SETUP_GUIDE.md               # Detailed setup instructions
├── FORM_FIELDS_REFERENCE.md     # Actual form field mappings
├── README.md                     # This file
└── images/                       # (Create) Profile images folder
```

---

## 🚀 Quick Start (5 minutes)

### 1. Clone & Install
```bash
cd selenium
pip install -r requirements.txt
```

### 2. Get Credentials
- Google Cloud: Download `credentials.json` (https://console.cloud.google.com)
- Save to project folder

### 3. Validate Setup
```bash
python test_setup.py
```

### 4. Update Form Selectors
```bash
# Open registration page in browser
# Right-click form field → Inspect → Copy id/name
# Update FORM_SELECTORS in config.py
```

### 5. Create Google Sheet
- Template name: `Hack2skill_Registrations`
- Columns: Name, Email, Password, ProjectTitle, Description, GoogleDevLink, ConditionalAnswer, AdditionalField, ImagePath, Status
- Add test rows

### 6. Run
```bash
python main.py
```

---

## 📋 Features

✅ **Data-Driven**: Pulls from Google Sheets, updates status in real-time  
✅ **Stealth Mode**: Undetected-ChromeDriver + Selenium Stealth to avoid detection  
✅ **OTP Auto-Fetch**: Reads verification code from email automatically  
✅ **Human-Like**: Random delays between actions to mimic real user  ✅ **CAPTCHA Handling**: Manual solve, 2Captcha API, or CapSolver API  ✅ **Error Handling**: Logs failures, continues with next row  
✅ **Resume Support**: Skips "Done" rows, processes pending only  

---

## 🔧 Configuration

### Form Selectors (config.py)

```python
FORM_SELECTORS = {
    "name_input": "input[name='name']",  # ← Inspect & update these
    "email_input": "input[name='email']",
    "register_now_btn": "button:contains('Register Now')",
    "otp_input": "input[name='otp']",
    "signup_btn": "button:contains('Signup')",
    "project_title": "input[name='projectTitle']",
    "project_description": "textarea[name='description']",
    "google_dev_link": "input[name='googleDevLink']",
    "conditional_yes_no": "select[name='hasAdditionalInfo']",
    "additional_field": "input[name='additionalField']",
    "image_upload": "input[type='file']",
    "submit_btn": "button:contains('Submit')",
}
```

### Email Settings

```python
EMAIL_CONFIG = {
    "email_provider": "cock.li",
    "imap_server": "mail.cock.li",
    "imap_port": 993,
}
```

### Browser Behavior

```python
SELENIUM_CONFIG = {
    "headless": False,      # Show/hide browser
    "stealth": True,        # Anti-bot detection
    "random_delay_min": 2,  # Seconds between actions
    "random_delay_max": 5,
}
```

### CAPTCHA Handling

```python
CAPTCHA_CONFIG = {
    "method": "manual",  # Options: "manual", "2captcha", "capsolver"
    "manual_pause_time": 30,  # Seconds to wait for manual solve
    
    # For 2Captcha (https://2captcha.com/)
    "2captcha_api_key": "your_api_key_here",
    
    # For CapSolver (https://www.capsolver.com/)
    "capsolver_api_key": "your_api_key_here",
    
    # Timeout
    "captcha_timeout": 120,  # Total time to wait (seconds)
}
```

**CAPTCHA Methods:**
- `"manual"` (default): Script pauses & waits for you to solve in browser
- `"2captcha"`: Automatic solving via 2Captcha API (~$1-2 per 1000)
- `"capsolver"`: Automatic solving via CapSolver API

---

## 📊 Google Sheet Format

See **[FORM_FIELDS_REFERENCE.md](FORM_FIELDS_REFERENCE.md)** for exact form field mappings.

**Basic Template:**

| Name | Email | Password | FullName | WhatsappNumber | DateOfBirth | ... | GDPProfileLink | ReferralAnswer | Status |
|------|-------|----------|----------|---|---|---|---|---|---|
| John | john@cock.li | Pass123! | John Doe | +91123... | 01.01.2000 | ... | https://g.dev/john | no | |

**Complete Column List:**
- Name, Email, Password (signup)
- FullName, WhatsappNumber, DateOfBirth, Gender, AlternateNumber, Country, StateProvince, City
- Occupation, CollegeName, CollegeCountry, CollegeState, CollegeCity, Degree, Specialization, PassoutYear
- LinkedinURL, CollegeIDPath, GDPProfileLink
- ReferralAnswer, ReferralCode
- Status (auto-updated)

---

## ⚠️ Important: Referral Field Handling

**The form has "Yes" pre-selected by default for the referral question.**

In your Google Sheet:
- If `ReferralAnswer = "no"`: Script will click "No" radio button
- If `ReferralAnswer = "yes"`: Script fills the referral code field (no click needed)
- `ReferralCode`: Only provide if referral answer is "yes"

**Example:**
```
ReferralAnswer = "no"   → "No" radio clicked, no code field filled
ReferralAnswer = "yes"  → Code field filled with ReferralCode value
```

---

## 🔐 Security

⚠️ **IMPORTANT:**
```bash
# Never commit these files
echo "credentials.json" >> .gitignore
echo ".env" >> .gitignore
```

**Best practices:**
- Use environment variables for sensitive data
- Rotate IPs if registering many accounts (use VPN)
- Don't share credentials.json publicly
- Test with 1-2 accounts before bulk automation

---

## 🧪 Testing

### Validate Setup
```bash
python test_setup.py
# Checks Python, packages, Chrome, credentials, config
```

### Test Single Registration
```python
# In main.py, uncomment lines 155-175
automation = Hack2skillAutomation()
automation.browser.initialize()
automation.run_single(
    name="Test User",
    email="test@cock.li",
    password="TestPass123!",
    form_data={...}
)
```

### Run with Google Sheet
```python
# main.py line 152
credentials_file = "credentials.json"
sheet_name = "Hack2skill_Registrations"

automation = Hack2skillAutomation(credentials_file)
automation.process_sheet(sheet_name)
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Element not found" | Update selectors in config.py (inspect page) |
| "IMAP authentication failed" | Use app-specific password for Gmail |
| Chrome version mismatch | undetected-chromedriver handles automatically |
| Form not submitting | Add wait time, check form validation |
| Detected as bot | Increase random_delay_min/max in config |
| **CAPTCHA appears** | Configure CAPTCHA_CONFIG in config.py (see above) |
| **"Yes" referral pre-selected** | Script handles this - it clicks "No" if needed |

**Debug Tips:**
```python
browser.screenshot("error.png")  # Capture screen
browser.driver.page_source      # Get page HTML
print(browser.driver.get_log('browser'))  # Browser logs
```

---

## 📝 Automation Flow

```
1. Read row from Google Sheet
   ↓
2. Navigate to registration URL
   ↓
3. SIGNUP FLOW:
   - Fill name & email
   - Click "Register Now"
   - Fetch OTP from email
   - Enter OTP
   - Click "Signup"
   ↓
4. REGISTRATION FORM:
   - Fill project title
   - Fill description
   - Fill Google Dev link
   - Select yes/no (if yes, shows additional field)
   - Upload image
   - Submit form
   ↓
5. Update sheet: Mark "Done"
   ↓
6. Delay 5-10 seconds (random)
   ↓
7. Next row...
```

---

## 🎯 Use Cases

✅ Bulk registrations for hackathons  
✅ Creating test accounts  
✅ Data migration from old platform  
✅ Account enrollment for competitions  
✅ Testing form validation at scale  

---

## ⚠️ Legal Note

**Use responsibly:**
- Comply with website's Terms of Service
- Don't violate anti-scraping policies
- Don't create fake/duplicate accounts
- Don't bypass security measures improperly
- Use for legitimate purposes only

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed setup instructions
- **config.py** - All configurable options
- **web inspector tips** - Finding form selectors

---

## 🤝 Support

Having issues? Check:
1. SETUP_GUIDE.md (Troubleshooting section)
2. test_setup.py output
3. Browser console (F12 → Console)
4. Form selector inspection (F12 → Inspector)

---

**Version:** 1.0  
**Updated:** April 2026  
**Status:** Production Ready ✅

---

## 🎓 Learning Outcomes

After using this project, you'll understand:
- Selenium browser automation
- Undetected ChromeDriver for bot detection evasion
- IMAP email protocol for OTP fetching
- Google Sheets API integration
- Form field inspection & XPath/CSS selectors
- Dynamic wait strategies
- Error handling & logging patterns

Happy automating! 🚀
