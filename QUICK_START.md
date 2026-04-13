# ⚡ QUICK REFERENCE - 5 Minutes to Success

## 📋 What You Need

- Python (you have it)
- Tor Browser (you have it)
- Thunderbird (you have it)
- Selenium (`pip install selenium`)
- GeckoDriver (Firefox WebDriver)

---

## 🔧 Installation (2 Minutes)

### Quick Auto-Setup:
```powershell
.\setup.bat
```

### Or Manual:
```powershell
pip install selenium
pip install geckodriver-autoinstaller
```

---

## 🚀 Run It (30 Seconds)

```powershell
python run_complete_automation.py
```

Answer the prompts:
1. How many accounts? (1-200)
2. Ready? (yes)
3. Thunderbird closed? (yes)

---

## 🎯 What It Will Do

1. Opens browser automatically
2. For each account:
   - Fills form with random username
   - Auto-fills password (gdgocgu12)
   - **Alerts you when CAPTCHA appears**
   - You solve it in the browser
   - Script detects completion
   - Moves to next account
3. Saves all accounts
4. Adds to Thunderbird automatically

---

## ⏱️ Time Estimate

- 5 accounts: 10 minutes
- 10 accounts: 20 minutes
- 50 accounts: 90 minutes (~1.5 hours)
- 100 accounts: 3 hours
- 200 accounts: 5-6 hours

(Depends on CAPTCHA solving speed)

---

## ✅ When It's Done

- ✅ `accounts_created.csv` has all details
- ✅ Thunderbird configured automatically
- ✅ Open Thunderbird → All accounts ready!

---

## ❓ If Something Fails

1. **Selenium not found**: `pip install selenium`
2. **GeckoDriver not found**: Download from GitHub or run setup.bat
3. **Browser doesn't load**: Check internet, wait for retry
4. **CAPTCHA not detected**: Still works! Wait for you to solve it
5. **Accounts missing in Thunderbird**: Close & reopen Thunderbird

---

## 💡 Pro Tips

- Start with 5 accounts to test
- Keep browser visible during CAPTCHA solving
- Monitor the terminal for any errors
- Passwords are all the same (gdgocgu12)
- Usernames are unique (no duplicates)

---

## 🎬 Start Now

```powershell
# Install
.\setup.bat

# Run
python run_complete_automation.py
```

**That's all you need!** 🚀

No more time-based guessing. Script watches browser. You solve CAPTCHA. Done!
