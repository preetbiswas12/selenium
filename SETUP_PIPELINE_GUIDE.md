# Complete Setup Pipeline - Cock.li + GDP + Hack2skill

## 📋 Overview

This is a **3-stage automation pipeline** that handles the complete account creation process:

1. **Stage 1:** Create cock.li email account
2. **Stage 2:** Create/Setup Google Developer Profile (GDP)
3. **Stage 3:** Auto-fill Hack2skill registration (already handled in main.py)

---

## 🎯 What Gets Automated

### Stage 1: cock.li Email Creation
✅ Visit cock.li signup page  
✅ Fill username, password, confirm password  
✅ Complete CAPTCHA (manual pause)  
✅ Submit form  
✅ Return email address: `username@cock.li`

### Stage 2: Google Developer Profile
✅ Login to Google account  
✅ Navigate to developers.google.com  
✅ Fill profile info (name, bio, image)  
✅ Set profile visibility to Public  
✅ Return profile link: `https://g.dev/username`

### Stage 3: Hack2skill Registration
✅ Use email & GDP link from Stages 1-2  
✅ Auto-fill all form fields  
✅ Verify OTP from email  
✅ Submit registration

---

## 🚀 Quick Start

### Single Account (Interactive)

```bash
python setup_pipeline.py --mode interactive
```

**Prompts you for:**
- Full Name
- Desired cock.li username
- Cock.li password
- Google email
- Google password (optional)
- Profile image path (optional)
- Profile bio (optional)

**Output:**
- Created email: `user@cock.li`
- Created GDP link: `https://g.dev/user`

### Batch from Google Sheet

```bash
python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
```

**Reads from sheet and creates all accounts**

---

## 📊 Google Sheet Format

For batch mode, create a sheet with these columns:

| Name | CockliUsername | CockliPassword | GoogleEmail | GooglePassword | ProfileImagePath | ProfileBio | Status |
|------|---|---|---|---|---|---|---|
| John Doe | johndoe123 | Pass123!Secure | john@gmail.com | (optional) | C:\images\john.jpg | AI Enthusiast | |
| Jane Smith | janesmith456 | Pass456!Secure | jane@gmail.com | (optional) | C:\images\jane.jpg | Data Scientist | |

**Columns needed:**
- `Name` - Full name for GDP profile
- `CockliUsername` - Desired username (without @cock.li)
- `CockliPassword` - Password for email account
- `GoogleEmail` - Your Google account email
- `GooglePassword` - (Optional) Your Google password
- `ProfileImagePath` - (Optional) Path to profile picture
- `ProfileBio` - (Optional) Short bio for profile
- `Status` - Auto-updated by script (Done/Failed/Error)

---

## 📁 Files Involved

### New Files (3)
- `cockli_automation.py` - Cock.li email creation
- `gdp_automation.py` - Google Developer Profile setup
- `setup_pipeline.py` - Master orchestrator

### Existing Files Used
- `browser_driver.py` - Selenium automation
- `sheets_handler.py` - Google Sheets integration
- config.py - Configuration
- requirements.txt - Dependencies

---

## ⚙️ Step-by-Step Workflow

### Interactive Mode

```
1. User runs: python setup_pipeline.py --mode interactive
2. Prompts for account details (name, emails, passwords)
3. Creates cock.li account
   └─ Fills username, password
   └─ Completes CAPTCHA (user pauses during this)
   └─ Returns: john@cock.li
4. Creates/Gets GDP profile
   └─ Logs into Google
   └─ Fills profile details
   └─ Sets visibility to Public
   └─ Returns: https://g.dev/john
5. Displays results
6. (Optional) Can integrate into Hack2skill registration
```

### Batch Mode

```
1. User runs: python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
2. Reads all pending rows from Google Sheet
3. For each row:
   ├─ Creates cock.li email
   ├─ Creates/gets GDP profile
   ├─ Updates sheet Status column
   ├─ Waits 5-10 seconds
   └─ Moves to next row
4. Displays summary (✅ 10 created, ❌ 2 failed)
```

---

## 🔐 Security Considerations

### Never Commit These:
- Google passwords in code
- cock.li passwords in code
- credentials.json file

### Use Environment Variables:
```python
import os
google_password = os.getenv("GOOGLE_PASSWORD")
cockli_password = os.getenv("COCKLI_PASSWORD")
```

### Use .env File:
```bash
# Create .env file
GOOGLE_PASSWORD=your_password
COCKLI_PASSWORD=your_password

# Load in Python
from dotenv import load_dotenv
load_dotenv()
password = os.getenv("GOOGLE_PASSWORD")
```

---

## ⚠️ Important Notes

### Manual CAPTCHA Solving
When cock.li CAPTCHA appears:
1. Script pauses automatically
2. You solve the CAPTCHA manually in browser
3. Script resumes after 3-5 seconds
4. Signup completes

### Google Login
If you don't provide Google password:
1. Script navigates to login page
2. You login manually
3. Script continues with profile creation

### Profile Image Upload
Optional - if path not provided, script skips this step

---

## 🧪 Testing

### Test Single Account
```bash
python setup_pipeline.py --mode interactive

# Prompts:
# Full Name: Test User
# cock.li username: testuser123
# cock.li password: TestPass123!
# Google email: testuser@gmail.com
# Google password: (press Enter for manual login)
```

### Test Batch Mode
1. Create Google Sheet: `Setup_Accounts`
2. Add 2 test rows
3. Run: `python setup_pipeline.py --mode batch`

---

## 🔄 Integration with main.py

After accounts are created via setup_pipeline.py:

**Option 1: Manual Integration**
```bash
# Stage 1-2: Create emails & GDP profiles
python setup_pipeline.py --mode batch --sheet "Setup_Accounts"

# Stage 3: Register on Hack2skill
python main.py
```

**Option 2: One-Line Integration**
Create new script that calls setup_pipeline → main() sequentially

---

## 📊 Output & Status Tracking

### Interactive Mode Output
```
✅ Cock.li email created: john@cock.li
✅ GDP profile created: https://g.dev/johndoe
```

### Batch Mode Output
```
==============================================================
  Account 1/10
  Setting up account for: John Doe
==============================================================

📧 STEP 1: Creating cock.li email...
✅ Cock.li email created: john@cock.li

🔗 STEP 2: Setting up Google Developer Profile...
✅ GDP profile created: https://g.dev/johndoe

📊 STEP 3: Updating Google Sheet...
✅ Sheet updated

==============================================================
SETUP COMPLETE: 10 successful, 0 failed
==============================================================
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "CAPTCHA timeout" | Enter CAPTCHA manually when script pauses |
| "Google login fails" | Don't provide password, login manually instead |
| "Email already exists" | Use different username |
| "GDP profile not found" | Create it manually first at developers.google.com |
| "Sheet not updating" | Share sheet with service account email |

---

## 📝 Example Usage

### Create 5 Email Accounts + GDP Profiles
```bash
# Method 1: Interactive (one at a time)
python setup_pipeline.py --mode interactive  # Run 5 times

# Method 2: Batch (all at once)
# 1. Create sheet "Setup_Accounts" with 5 rows
# 2. Run: python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
```

### Then Register on Hack2skill
```bash
# Add email + GDP link from setup_pipeline output to Hack2skill sheet
# Run: python main.py
```

---

## 🎓 What You'll Learn

✅ Automating email account creation  
✅ Multi-step form filling  
✅ Conditional element handling (CAPTCHA pause)  
✅ Browser-based authentication  
✅ Pipeline orchestration  
✅ Error recovery & status tracking  

---

## 🚀 Production Deployment

### Docker Container
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "setup_pipeline.py", "--mode", "batch", "--sheet", "Setup_Accounts"]
```

### Scheduled Runs (Task Scheduler)
```cmd
# Create batch file: run_setup.bat
cd C:\Users\preet\Downloads\selenium
python setup_pipeline.py --mode batch --sheet "Setup_Accounts"
```

Then schedule via Task Scheduler to run daily/weekly

---

**Version:** 1.0  
**Status:** Production Ready ✅  
**Created:** April 2026
