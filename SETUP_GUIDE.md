# Hack2skill Automation Setup Guide

## 📋 Overview
This automation script handles:
1. **Signup** - Name + Email → OTP verification
2. **Registration Form** - Project details + image upload
3. **Google Sheets** - Pull data row-by-row and track status
4. **Error Handling** - Automatic retries and status updates

---

## ⚙️ Prerequisites

### 1. Python Environment
```bash
python --version  # Should be 3.8+
pip install -r requirements.txt
```

### 2. Chrome Browser
- Download from: https://www.google.com/chrome/
- The script uses **Undetected ChromeDriver** (auto-manages version)

### 3. Google Cloud Setup
**Create Service Account for Sheets API:**
1. Go to: https://console.cloud.google.com/
2. Create new project → Enable "Google Sheets API"
3. Create Service Account → Download JSON credentials
4. Save as `credentials.json` in the project folder
5. Share your Google Sheet with the service account email

### 4. cock.li Email + Thunderbird
```bash
# Create cock.li account: https://cock.li/
# Install Thunderbird: https://www.thunderbird.net/

# Example: create user@cock.li accounts
```

---

## 📊 Google Sheet Template

**Spreadsheet Name:** `Hack2skill_Registrations`

| Name | Email | Password | ProjectTitle | Description | GoogleDevLink | ConditionalAnswer | AdditionalField | ImagePath | Status |
|------|-------|----------|--------------|-------------|---------------|-----------------|-----------------|-----------|--------|
| John Doe | john@cock.li | Pass123! | My AI App | Solves SDG poverty | https://dev.google.com/john | yes | More details | C:\images\john.jpg | |
| Jane Smith | jane@cock.li | Pass456! | Climate ML | Reduces carbon emissions | https://dev.google.com/jane | no | | C:\images\jane.jpg | |

**Column Descriptions:**
- **Name**: Full name for signup
- **Email**: cock.li email (must exist first)
- **Password**: Account password (optional, can be generated)
- **ProjectTitle**: Title of the solution
- **Description**: Project description (100+ chars)
- **GoogleDevLink**: Your public Google Developers profile URL
- **ConditionalAnswer**: `yes` or `no` (if yes, additional field appears)
- **AdditionalField**: Extra info (only if ConditionalAnswer=yes)
- **ImagePath**: Local path to profile/project image
- **Status**: Auto-updated (`Done`, `Signup Failed`, `Form Failed`, `Error`)

---

## 🚀 Quick Start

### Step 1: Configure Form Selectors
Open the registration page in browser, right-click → Inspect Element.
Update `config.py` with actual field selectors:

```python
FORM_SELECTORS = {
    "name_input": "input[id='fullName']",  # Update these!
    "email_input": "input[id='email']",
    "register_now_btn": "button[type='submit']",
    # ... update all selectors
}
```

### Step 2: Create Google Sheet
1. Go to: https://sheets.google.com/
2. Create new sheet: `Hack2skill_Registrations`
3. Add columns from template above
4. Add 1-2 test rows with your data
5. Share with service account email

### Step 3: Setup Credentials
```bash
# 1. Save Google Cloud JSON credentials
cp your_credentials.json credentials.json

# 2. Create cock.li accounts (or use generator)
# https://cock.li/  (example)
```

### Step 4: Update main.py
```python
# Line ~152
credentials_file = "credentials.json"
sheet_name = "Hack2skill_Registrations"  # Your sheet name
```

### Step 5: Run
```bash
python main.py
```

---

## 🛠️ Detailed Configuration

### FORM_SELECTORS (config.py)
**To find selectors:**
1. Visit: https://vision.hack2skill.com/event/solution-challenge-2026/registration
2. Right-click form field → Inspect
3. Copy the `id` or `name` attribute

**Example:**
```html
<!-- HTML inspect result -->
<input id="fullName" type="text" placeholder="Full Name">

<!-- config.py -->
"name_input": "#fullName",  # CSS selector
```

### EMAIL_CONFIG
```python
EMAIL_CONFIG = {
    "imap_server": "mail.cock.li",
    "imap_port": 993,
}
```

### SELENIUM_CONFIG
```python
SELENIUM_CONFIG = {
    "headless": False,  # Show browser (True = hidden)
    "stealth": True,    # Hide bot detection
    "random_delay_min": 2,  # Seconds between actions
    "random_delay_max": 5,
}
```

---

## 🔐 Security Best Practices

1. **Never commit credentials:**
   ```bash
   echo "credentials.json" >> .gitignore
   echo ".env" >> .gitignore
   ```

2. **Use environment variables:**
   ```python
   # Create .env file
   SHEET_NAME=Hack2skill_Registrations
   CREDS_PATH=credentials.json
   
   # In main.py
   from dotenv import load_dotenv
   load_dotenv()
   sheet_name = os.getenv("SHEET_NAME")
   ```

3. **Rotate IPs (optional):**
   - Use free VPN: ProtonVPN, Windscribe
   - Or paid proxy: Bright Data, Oxylabs
   - Update browser_driver.py to use proxy

---

## 🐛 Troubleshooting

### Issue: "Element not found"
**Solution:** Update selectors in config.py
```bash
# Open browser devtools
F12 → Inspector → Right-click field → Copy selector
```

### Issue: "IMAP authentication failed"
**Solution:** Check email credentials
```bash
# Test email access manually in Thunderbird first
```

### Issue: "Chrome version mismatch"
**Solution:** Let undetected-chromedriver auto-manage
```bash
# Delete any cached chrome versions
rm -r ~/.wdm/  # Linux/Mac
rmdir %USERPROFILE%\.wdm\  # Windows
```

---

## �️ CAPTCHA Handling

The registration form may include CAPTCHA protection. Configure your preferred method:

### Option 1: Manual Solve (Default)
```python
# config.py
CAPTCHA_CONFIG = {
    "method": "manual",
    "manual_pause_time": 30,  # Wait 30 seconds for you to solve
}
```
**How it works:** Script pauses when CAPTCHA detected. You solve it manually in the browser, then script continues.

### Option 2: 2Captcha (Automated)
```python
# 1. Get API key from https://2captcha.com/
# 2. Update config.py
CAPTCHA_CONFIG = {
    "method": "2captcha",
    "2captcha_api_key": "your_api_key_here",
    "captcha_timeout": 120,
}
```
Cost: ~$1-2 per 1000 CAPTCHAs solved

### Option 3: CapSolver (Automated)
```python
# 1. Get API key from https://www.capsolver.com/
# 2. Update config.py
CAPTCHA_CONFIG = {
    "method": "capsolver",
    "capsolver_api_key": "your_api_key_here",
    "captcha_timeout": 120,
}
```

---

## ⚠️ Special: Referral Field (Pre-selected "Yes")

**Important:** The form has "Yes" selected by default for "Were you referred by a GDG Organizer?"

**In Google Sheet, use:**
```
ReferralAnswer = "no"   → Script clicks "No" radio button
ReferralAnswer = "yes"  → Fills referral code field (no click needed)
```

**Example rows:**
```
ReferralAnswer | ReferralCode
no             | (empty)
yes            | ABC123
```

---

```python
# In main.py, comment line 152 and uncomment lines 155-175
automation = Hack2skillAutomation()
automation.browser.initialize()
automation.run_single(
    name="Test User",
    email="test@cock.li",
    password="TestPass123!",
    form_data={
        "project_title": "Test Project",
        "project_description": "This is a test project...",
        "google_dev_link": "https://developers.google.com/test",
        "conditional_answer": "yes",
        "additional_field": "Test additional info",
        "image_path": "C:\\Users\\preet\\Downloads\\selenium\\images\\test.jpg",
    }
)
```

---

## 📈 Advanced Features

### Multi-threaded Processing
```python
from concurrent.futures import ThreadPoolExecutor

# Process 3 registrations in parallel
with ThreadPoolExecutor(max_workers=3) as executor:
    executor.map(automation.process_single, records)
```

### Proxy Rotation
```python
# browser_driver.py
options.add_argument(f"--proxy-server=http://{proxy}:{port}")
```

### Custom Error Handling
```python
# main.py
except Exception as e:
    self.sheets_handler.update_status(spreadsheet, idx - 1, f"Error: {e}")
    self.browser.screenshot(f"error_{idx}.png")
```

---

## 📞 Support

For issues:
1. Check logs in terminal output
2. Take screenshot (auto-saved on error)
3. Verify form selectors with browser inspect
4. Test email credentials manually first

---

**Version:** 1.0  
**Last Updated:** April 2026
