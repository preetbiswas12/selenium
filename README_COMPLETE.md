# 🚀 COMPLETE HACK2SKILL AUTOMATION - Full Pipeline

**Complete automation system for Google Solution Challenge 2026 India registrations.**

Automates: **cock.li email creation** → **Google Developer Profile setup** → **Hack2skill registration**

---

## 🎯 What This Does

### Stage 1: Cock.li Email Creation
```
cockli_automation.py
├─ Create email account (username@cock.li)
├─ Handle CAPTCHA (manual pause)
├─ Return: john@cock.li
└─ Store in Google Sheet
```

### Stage 2: Google Developer Profile Creation
```
gdp_automation.py
├─ Login to Google account
├─ Create/Setup profile
├─ Fill name, bio, image
├─ Set visibility to Public
└─ Return: https://g.dev/john
```

### Stage 3: Hack2skill Registration
```
main.py
├─ Signup with email + OTP
├─ Fill 25+ registration fields
├─ Upload college ID
├─ Submit form
└─ Auto-update Google Sheet
```

---

## 📁 Complete File Structure

```
selenium/
├── 🎭 AUTOMATION SCRIPTS
│   ├── main.py                       # Hack2skill registration
│   ├── setup_pipeline.py             # Master orchestrator
│   ├── cockli_automation.py          # Email creation
│   ├── gdp_automation.py             # GDP profile setup
│   ├── browser_driver.py             # Selenium with stealth
│   ├── email_handler.py              # OTP from email
│   ├── sheets_handler.py             # Google Sheets
│   └── captcha_handler.py            # CAPTCHA solving
│
├── ⚙️  CONFIGURATION
│   ├── config.py                     # All settings
│   ├── requirements.txt              # Dependencies
│   └── .env.example                  # Env template
│
├── 📚 DOCUMENTATION
│   ├── README.md                     # This file
│   ├── COMPLETE_SETUP_SUMMARY.md     # Project overview
│   ├── SETUP_GUIDE.md               # Installation guide
│   ├── SETUP_PIPELINE_GUIDE.md      # 3-stage pipeline
│   ├── FORM_FIELDS_REFERENCE.md     # All form fields
│   ├── SELECTOR_GUIDE.md            # CSS selector guide
│   └── CHECKLIST.py                 # Pre-flight checks
│
└── 🛠️  UTILITIES
    ├── test_setup.py                # Validation script
    ├── .gitignore                   # Security
    └── CHECKLIST.py                 # Pre-run checklist
```

---

## 🚀 Quick Start (60 minutes)

### Installation (5 min)
```bash
cd c:\Users\preet\Downloads\selenium
pip install -r requirements.txt
```

### Get Credentials (10 min)
1. **Google Cloud** → Download Service Account JSON → Save as `credentials.json`
2. **Create cock.li accounts** → https://cock.li/ (or automate later)

### Setup Form Selectors (15 min)
1. Open registration page in browser
2. Right-click form field → Inspect (F12)
3. Copy selector → Update FORM_SELECTORS in config.py
4. Use SELECTOR_GUIDE.md for help

### Create Google Sheet (10 min)
**Sheet name:** `Hack2skill_Registrations`

Columns: Name, Email, Password, FullName, WhatsappNumber, DateOfBirth, ... [25+ fields]

### Run Setup Pipeline (20 min)

**Option A: Create email + GDP first**
```bash
python setup_pipeline.py --mode interactive
# Or batch: python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
```

**Option B: Use existing emails**
```bash
# Just fill Google Sheet with existing emails + GDP links
# Then run: python main.py
```

---

## 📊 3-Stage Workflow

### Stage 1: Cock.li Email + GDP Profile
```bash
python setup_pipeline.py --mode interactive

Prompts:
- Full Name: John Doe
- cock.li username: johndoe123
- cock.li password: Pass123!
- Google email: john@gmail.com
- Google password: (auto/manual login)

Output:
✅ Email: john@cock.li
✅ GDP Link: https://g.dev/johndoe
```

### Stage 2: (Optional) Batch Create Multiple Accounts
```bash
python setup_pipeline.py --mode batch --sheet "Setup_Accounts"

# Reads from Google Sheet:
# Name | CockliUsername | CockliPassword | GoogleEmail | ...
# 
# Creates all accounts automatically
# Updates Status column: Done / Failed / Error
```

### Stage 3: Auto-Register on Hack2skill
```bash
python main.py

# Reads from Hack2skill_Registrations sheet
# For each pending row:
# - Signup with email + OTP
# - Fill form (25+ fields)
# - Upload college ID
# - Submit registration
# - Update Status: Done / Failed / Error
```

---

## 🎯 Complete Data Flow

```
Setup_Accounts Sheet
├─ Input: Full Name, cock.li username, Google email
├─ Process: Create email + GDP profile
└─ Output: Email address + GDP link

        ↓ (Copy to registration sheet)

Hack2skill_Registrations Sheet
├─ Input: Email, Password, Full Name, ... (all form fields)
├─ Process: Auto-fill form + verify OTP
└─ Output: Registered account + Status: Done

        ↓

Hack2skill Platform
├─ Account: john@cock.li
├─ Name: John Doe
├─ GDP Link: https://g.dev/johndoe
└─ College ID: Verified
```

---

## 📝 Google Sheet Templates

### Sheet 1: Setup_Accounts (for Stage 1)
```
| Name | CockliUsername | CockliPassword | GoogleEmail | GooglePassword | ProfileImagePath | ProfileBio | Status |
|---|---|---|---|---|---|---|---|
| John Doe | johndoe123 | Pass123! | john@gmail.com | (opt) | /images/john.jpg | AI Dev | |
```

### Sheet 2: Hack2skill_Registrations (for Stage 3)
```
| Name | Email | Password | FullName | WhatsappNumber | DateOfBirth | ... | GDPProfileLink | ReferralAnswer | Status |
|---|---|---|---|---|---|---|---|---|---|
| John Doe | john@cock.li | Pass123! | John Doe | +91123... | 01.01.2000 | ... | https://g.dev/johndoe | no | |
```

---

## 🛡️ CAPTCHA Handling

### During cock.li Email Creation
- Script navigates to signup
- CAPTCHA appears
- Script **pauses and waits** (30 seconds)
- **You solve manually** in browser
- Script resumes automatically
- ✅ Account created

### During Hack2skill Registration
Configure in config.py:
```python
CAPTCHA_CONFIG = {
    "method": "manual",      # Or "2captcha", "capsolver"
    "manual_pause_time": 30,
}
```

---

## ⚠️ Important Features

### ✨ Clever Referral Field Handling
Form has "Yes" pre-selected by default.
Script automatically:
- If "no" → Clicks "No" radio button
- If "yes" → Fills referral code (no click needed)

### 🕵️ Anti-Bot Protection
- Undetected-ChromeDriver (bypasses detection)
- Selenium Stealth plugin
- Random 2-5 second delays
- User-agent spoofing

### 📊 Real-Time Status Tracking
- Reads from Google Sheet
- Updates Status column: Done / Failed / Error
- Resume support (skips completed)
- Detailed logging

### 🔐 Email OTP Auto-Fetch
- Connects via IMAP
- Extracts 4-6 digit code
- Auto-fills in form
- Fallback to manual if needed

---

## 🧪 Testing Workflow

### 1. Test Setup Pipeline
```bash
python setup_pipeline.py --mode interactive

# Create 1 test account
Name: Test User
cock.li: testuser123
Google: test@gmail.com
```

### 2. Test Hack2skill Registration
```bash
# Add test account to Hack2skill_Registrations sheet
# Update config.py with actual form selectors
# Run: python main.py
```

### 3. Validate Everything
```bash
python test_setup.py
# Checks: Python, packages, Chrome, credentials, selectors
```

---

## 🚀 Production Setup

### Local Automation
```bash
# Manual runs
python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
python main.py
```

### Scheduled Runs (Windows Task Scheduler)
```batch
# File: run_automation.bat
@echo off
cd C:\Users\preet\Downloads\selenium
python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
timeout /t 300
python main.py
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "setup_pipeline.py", "--mode", "batch"]
```

---

## 📚 Documentation Map

| File | Purpose |
|------|---------|
| **SETUP_PIPELINE_GUIDE.md** | ✅ START HERE - Complete 3-stage pipeline |
| **SETUP_GUIDE.md** | Detailed installation & configuration |
| **FORM_FIELDS_REFERENCE.md** | All 25+ Hack2skill form fields |
| **SELECTOR_GUIDE.md** | How to find CSS selectors |
| **COMPLETE_SETUP_SUMMARY.md** | Project overview & features |
| **README.md** | This file - Quick reference |

---

## 🎓 You'll Learn

✅ Automating multi-step form filling  
✅ Email account creation  
✅ Google OAuth/Login automation  
✅ CAPTCHA handling (pause + API methods)  
✅ Google Sheets API  
✅ Pipeline orchestration  
✅ Error recovery  
✅ Production deployment  

---

## ⚡ Next Steps

### 👉 Start Here
1. **Read:** SETUP_PIPELINE_GUIDE.md (10 min)
2. **Install:** `pip install -r requirements.txt`
3. **Test:** `python test_setup.py`
4. **Run:** `python setup_pipeline.py --mode interactive`

### 🎯 Then Register
5. **Inspect:** Find form selectors (SELECTOR_GUIDE.md)
6. **Configure:** Update FORM_SELECTORS in config.py
7. **Create Sheet:** Hack2skill_Registrations
8. **Register:** `python main.py`

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Chrome crashes | Update: `pip install --upgrade undetected-chromedriver` |
| Element not found | Inspect page, update selectors in config.py |
| CAPTCHA times out | Enter manually when script pauses |
| Email not received | Check IMAP enabled, use app password |
| Sheet not updating | Share with service account email |

See **SETUP_GUIDE.md** for detailed troubleshooting

---

## 💡 Pro Tips

1. **Test with 1-2 accounts first** before bulk run
2. **Save successful selectors** - don't need to update again
3. **Use environment variables** for passwords (not hardcoded)
4. **Check logs frequently** - they show exactly what happened
5. **Take screenshots** on errors (auto-saved)
6. **Spread registrations over time** to avoid detection

---

**Status:** ✅ Production Ready  
**Version:** 1.0 Complete  
**Location:** `c:\Users\preet\Downloads\selenium\`

---

## 🚀 Ready?

**Start with:** `python setup_pipeline.py --mode interactive`

Then: `python main.py` for Hack2skill registration

Good luck! 🎓
