# 🛠️ SETUP GUIDE - Smart Browser Automation

## What Changed

**OLD**: Time-based waits (unreliable with internet issues)  
**NEW**: Smart element detection using Selenium (watches browser)

---

## What You Need to Install

### **1. Selenium (Python package)**
```powershell
pip install selenium
```

### **2. GeckoDriver (Firefox WebDriver)**

**Option A: Download manually** (Recommended)
```
1. Go to: https://github.com/mozilla/geckodriver/releases
2. Download: geckodriver-v0.33.1-win64.zip (latest version)
3. Extract geckodriver.exe
4. Put in: C:\webdrivers\
5. Done!
```

**Option B: Auto-install via pip**
```powershell
pip install geckodriver-autoinstaller
```

### **3. Tor Browser** (You already have this)
- Should be at: `C:\Program Files\Tor Browser`

---

## Verify Installation

```powershell
# Check Selenium
python -c "import selenium; print(selenium.__version__)"

# Check GeckoDriver
geckodriver --version
```

---

## How the Smart System Works

Instead of fixed waits:

```
OLD WAY (Broken with internet issues):
- Wait 30 seconds
- Wait 10 seconds for CAPTCHA
- Hope everything works

NEW WAY (Smart & Resilient):
- Load page → Wait for form element to APPEAR
- Type username → Wait for field to be READY
- Type password → Wait for field to be READY
- Accept terms → Wait for checkbox to exist
- Wait for CAPTCHA to VISUALLY APPEAR
- Stop waiting when registration succeeds
- Detect success by checking page content
```

---

## What It Actually Does

### Per Account:
1. **Start fresh browser** (new Tor instance)
2. **Load registration page** (waits for actual page load)
3. **Find username field** (waits for it to appear, smart timeout)
4. **Type username** (waits for field to be ready)
5. **Find password fields** (waits for them)
6. **Type password 1 & 2** (both auto-filled)
7. **Click terms checkbox** (if it exists)
8. **Detect CAPTCHA** (checks if it appears on page)
9. **Alert you** (pauses for manual solving)
10. **Wait for success** (watches page for completion)
11. **Close browser** (fresh start for next account)

---

## Installation Steps

### **Step 1: Install Python Packages**
```powershell
pip install selenium
```

### **Step 2: Get GeckoDriver**

**Option A: Manual (Recommended)**
```powershell
# Create folder
mkdir C:\webdrivers

# Download from: https://github.com/mozilla/geckodriver/releases
# Extract geckodriver.exe into C:\webdrivers\

# Verify
geckodriver --version
```

**Option B: Auto-install**
```powershell
pip install geckodriver-autoinstaller
```

---

## Now Run It

```powershell
python run_complete_automation.py
```

---

## Troubleshooting

### **"No module named 'selenium'"**
```powershell
pip install selenium
```

### **"geckodriver not found"**
- Download from: https://github.com/mozilla/geckodriver/releases
- Put in: `C:\webdrivers\geckodriver.exe`
- Or: `pip install geckodriver-autoinstaller`

### **"Firefox not found"**
- Script will try to find Tor Browser automatically
- If not found, install Tor: https://www.torproject.org/download

### **Browser opens but doesn't load page**
- Check internet connection
- Try running again (script retries automatically)

### **CAPTCHA not detected**
- It should wait forever for you to solve it
- The script will detect success automatically
- No fixed 10-second wait anymore!

---

## Key Differences from Old Version

| Aspect | OLD | NEW |
|--------|-----|-----|
| Waits | Fixed times (10s, 30s) | Adaptive (waits for elements) |
| Page Load | Assumes page loaded | Waits for form to appear |
| CAPTCHA | Fixed 10 sec pause | Waits until solved |
| Success Check | Hopes for best | Checks page content |
| Internet Issues | Fails | Retries intelligently |
| Speed | Slow (many unnecessary waits) | Fast (no wasted time) |

---

## You're Ready!

```powershell
python run_complete_automation.py
```

Then:
1. Enter how many accounts (1-200)
2. Confirm you're ready
3. **Browser opens automatically**
4. **For each account:**
   - Form fills automatically
   - Waits for CAPTCHA to appear
   - Alerts you to solve it
   - Detects when done
   - Moves to next account
5. **All accounts injected into Thunderbird**

**No more time-based guessing!** ✨
