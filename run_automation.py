#!/usr/bin/env python3
"""
Sequential automation workflow:
1. Tor Browser → cock.li registration
2. Thunderbird → add email account
3. Tor Browser → Hack2skill registration
"""

import subprocess
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User data
USER_DATA = {
    "full_name": "John Doe",
    "cockli_username": "piyalib140",
    "password": "preetb121106",
    "whatsapp": "7439163739",
    "dob": "15.03.1999",
    "gender": "Male"
}

def step_1_cockli_registration():
    """Step 1: Register cock.li email using Tor"""
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Opening Tor Browser for cock.li registration")
    logger.info("="*60)
    
    # Common Tor Browser paths on Windows
    tor_paths = [
        "C:\\Program Files\\Tor Browser\\Browser\\firefox.exe",
        "C:\\Program Files (x86)\\Tor Browser\\Browser\\firefox.exe",
        os.path.expanduser("~\\AppData\\Local\\Tor Browser\\Browser\\firefox.exe"),
        os.path.expanduser("~\\Tor Browser\\Browser\\firefox.exe"),
        "C:\\Users\\preet\\Tor\\Browser\\firefox.exe"
    ]
    
    tor_path = None
    for path in tor_paths:
        if os.path.exists(path):
            tor_path = path
            break
    
    if tor_path:
        try:
            subprocess.Popen([tor_path, "https://cock.li/register.php"])
            logger.info("✓ Tor opened at cock.li/register.php")
            logger.info("⏳ Waiting for Tor to connect... (30 seconds)")
            time.sleep(30)
        except Exception as e:
            logger.error(f"Failed to open Tor: {e}")
    else:
        logger.warning("⚠️  Tor Browser not found - opening in default browser instead")
        logger.warning("🔴 IMPORTANT: Open Tor Browser manually and navigate to: https://cock.li/register.php")
        import webbrowser
        webbrowser.open("https://cock.li/register.php")
    
    logger.info("\n📋 MANUALLY FILL IN cock.li FORM:")
    logger.info(f"  Email username: {USER_DATA['cockli_username']}")
    logger.info(f"  Password: {USER_DATA['password']}")
    logger.info(f"  Confirm Password: {USER_DATA['password']}")
    logger.info(f"  Select domain: @cock.li")
    logger.info(f"  CAPTCHA: Solve manually")
    logger.info(f"  ✅ Check: I agree to the Terms of Service and Privacy Policy")
    logger.info(f"  Click 'Register' button")
    logger.info("\n⏰ Press ENTER after successful registration...")
    input()
    
    return True

def step_2_thunderbird_setup():
    """Step 2: Add email to Thunderbird"""
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Setting up Thunderbird with cock.li email")
    logger.info("="*60)
    
    # Common Thunderbird paths
    tb_paths = [
        "C:\\Program Files\\Mozilla Thunderbird\\thunderbird.exe",
        "C:\\Program Files (x86)\\Mozilla Thunderbird\\thunderbird.exe",
        os.path.expanduser("~\\AppData\\Local\\Mozilla Thunderbird\\thunderbird.exe")
    ]
    
    tb_path = None
    for path in tb_paths:
        if os.path.exists(path):
            tb_path = path
            break
    
    if tb_path:
        try:
            subprocess.Popen([tb_path])
            logger.info("✓ Thunderbird opened")
            logger.info("⏳ Waiting for Thunderbird to start... (10 seconds)")
            time.sleep(10)
        except Exception as e:
            logger.error(f"Failed to open Thunderbird: {e}")
    else:
        logger.warning("⚠️  Thunderbird not found - opening it manually")
        logger.warning("🔴 Please open Mozilla Thunderbird manually")
    
    logger.info("\n📧 MANUALLY ADD EMAIL IN THUNDERBIRD:")
    logger.info(f"  1. Click 'Create a new account'")
    logger.info(f"  2. Select 'Email'")
    logger.info(f"  3. Enter Full name: {USER_DATA['full_name']}")
    logger.info(f"  4. Enter Email address: {USER_DATA['cockli_username']}@cock.li")
    logger.info(f"  5. Enter password: {USER_DATA['password']}")
    logger.info(f"  6. Click 'Continue'")
    logger.info(f"  7. Let it auto-detect cock.li IMAP settings")
    logger.info(f"     (IMAP: imap.cock.li, SMTP: smtp.cock.li)")
    logger.info(f"  8. Click 'Done'")
    logger.info(f"  9. Keep Thunderbird open for OTP code later")
    logger.info("\n⏰ Press ENTER after Thunderbird email setup is complete...")
    input()
    
    return True

def step_3_hack2skill_registration():
    """Step 3: Register on Hack2skill using Tor with new identity"""
    logger.info("\n" + "="*60)
    logger.info("STEP 3: Opening NEW Tor identity for Hack2skill registration")
    logger.info("="*60)
    
    # Request new Tor identity (in Tor Browser, press Ctrl+Shift+U)
    logger.info("\n🔄 IN TOR BROWSER:")
    logger.info("  1. Press Ctrl+Shift+U to get NEW Tor identity")
    logger.info("  2. Wait 10 seconds for new identity to establish")
    logger.info("  3. Go to: https://vision.hack2skill.com/event/solution-challenge-2026/registration")
    logger.info("\n📝 MANUALLY FILL HACK2SKILL FORM:")
    logger.info(f"  Full Name: {USER_DATA['full_name']}")
    logger.info(f"  Email: {USER_DATA['cockli_username']}@cock.li")
    logger.info(f"  Password: {USER_DATA['password']}")
    logger.info(f"  WhatsApp: {USER_DATA['whatsapp']}")
    logger.info(f"  DateOfBirth: {USER_DATA['dob']}")
    logger.info(f"  Gender: {USER_DATA['gender']}")
    logger.info(f"  Fill remaining fields as needed")
    logger.info(f"  Wait for OTP email from cock.li")
    logger.info(f"  Check Thunderbird for OTP code")
    logger.info(f"  Enter OTP and submit")
    logger.info("\n⏰ Press ENTER after Hack2skill registration done...")
    input()
    
    return True

def main():
    """Run the complete workflow"""
    logger.info("╔" + "="*58 + "╗")
    logger.info("║  COCK.LI + HACK2SKILL AUTOMATED REGISTRATION WORKFLOW  ║")
    logger.info("╚" + "="*58 + "╝")
    
    logger.info(f"\n👤 User: {USER_DATA['full_name']}")
    logger.info(f"📧 Email: {USER_DATA['cockli_username']}@cock.li")
    logger.info(f"📱 WhatsApp: {USER_DATA['whatsapp']}")
    
    # Run steps
    if not step_1_cockli_registration():
        logger.error("Step 1 failed!")
        return False
    
    time.sleep(2)
    
    if not step_2_thunderbird_setup():
        logger.error("Step 2 failed!")
        return False
    
    time.sleep(2)
    
    if not step_3_hack2skill_registration():
        logger.error("Step 3 failed!")
        return False
    
    logger.info("\n" + "="*60)
    logger.info("✅ REGISTRATION WORKFLOW COMPLETE!")
    logger.info("="*60)
    logger.info("\n📌 Next steps:")
    logger.info("  1. Close Tor Browser")
    logger.info("  2. Close Thunderbird")
    logger.info("  3. Edit registration link if needed")
    logger.info("  4. Share registration confirmation")

if __name__ == "__main__":
    main()
