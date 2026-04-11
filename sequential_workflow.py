"""
Sequential Automation Workflow:
1. Tor Browser → cock.li registration
2. Thunderbird → add email account
3. Tor Browser (new identity) → Hack2skill registration
4. User → manual editing
"""

import subprocess
import time
import pyautogui
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SequentialWorkflow:
    """Complete automation workflow with manual hand-offs"""
    
    def __init__(self):
        pyautogui.PAUSE = 0.5
        pyautogui.FAILSAFE = True
    
    # ============ STAGE 1: TOR + cock.li ============
    
    def stage1_cockli_email(self, username, password):
        """
        Stage 1: Create cock.li email account
        1. Open Tor Browser
        2. Navigate to cock.li/register.php
        3. User fills form (with some automation help)
        4. Close Tor
        """
        logger.info("="*60)
        logger.info("STAGE 1: Creating cock.li EMAIL")
        logger.info("="*60)
        
        try:
            # Step 1: Open Tor Browser
            logger.info("\n📱 Step 1: Opening Tor Browser...")
            tor_paths = [
                r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
                r"C:\Program Files\Tor Browser\Browser\firefox.exe",
            ]
            
            tor_path = None
            for path in tor_paths:
                if os.path.exists(path):
                    tor_path = path
                    break
            
            if not tor_path:
                logger.error("❌ Tor Browser not found. Install from: https://www.torproject.org")
                return False
            
            subprocess.Popen([tor_path])
            logger.info("✅ Tor Browser starting... (waiting 8 seconds)")
            time.sleep(8)
            
            # Step 2: Navigate to cock.li register
            logger.info("\n🌐 Step 2: Opening cock.li registration...")
            pyautogui.hotkey('ctrl', 'l')  # Focus address bar
            time.sleep(0.5)
            pyautogui.typewrite('https://cock.li/register.php', interval=0.02)
            pyautogui.press('enter')
            time.sleep(4)
            logger.info("✅ cock.li registration page loaded")
            
            # Step 3: User fills form (manual with UI help)
            logger.info("\n✏️  Step 3: MANUAL - Fill cock.li form")
            logger.info(f"   Username: {username}")
            logger.info(f"   Password: {password}")
            logger.info(f"   Domain: cock.li (pre-selected)")
            logger.info("")
            logger.info("MANUAL STEPS:")
            logger.info("1. Click on username field")
            logger.info(f"2. Type: {username}")
            logger.info("3. Confirm domain is 'cock.li'")
            logger.info(f"4. Type password: {password} (twice)")
            logger.info("5. Solve CAPTCHA")
            logger.info("6. Check Terms & Conditions")
            logger.info("7. Click Register")
            logger.info("")
            input("➡️  Press ENTER when email registration is COMPLETE...")
            
            logger.info("✅ cock.li email created: {email}@cock.li")
            
            # Step 4: Close Tor
            logger.info("\n❌ Step 4: Closing Tor Browser...")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2)
            logger.info("✅ Tor Browser closed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 1 failed: {e}")
            return False
    
    # ============ STAGE 2: THUNDERBIRD ============
    
    def stage2_thunderbird_email(self, email, password):
        """
        Stage 2: Add email to Thunderbird
        1. Open Thunderbird
        2. User adds email account manually
        3. Close Thunderbird
        """
        logger.info("\n" + "="*60)
        logger.info("STAGE 2: Setting up EMAIL in Thunderbird")
        logger.info("="*60)
        
        try:
            # Step 1: Open Thunderbird
            logger.info("\n📧 Step 1: Opening Thunderbird...")
            thunderbird_paths = [
                r"C:\Program Files\Mozilla Thunderbird\thunderbird.exe",
                r"C:\Program Files (x86)\Mozilla Thunderbird\thunderbird.exe",
            ]
            
            tb_path = None
            for path in thunderbird_paths:
                if os.path.exists(path):
                    tb_path = path
                    break
            
            if not tb_path:
                logger.warning("⚠️  Thunderbird not found at standard locations")
                logger.info("Install from: https://www.thunderbird.net")
                return False
            
            subprocess.Popen([tb_path])
            logger.info("✅ Thunderbird starting... (waiting 8 seconds)")
            time.sleep(8)
            
            # Step 2: User adds account
            logger.info("\n⚙️ Step 2: MANUAL - Add email account")
            logger.info("")
            logger.info("MANUAL STEPS IN THUNDERBIRD:")
            logger.info("1. Click 'Create New Account' (or Menu → New Account)")
            logger.info("2. Select 'Email'")
            logger.info(f"3. Fill: Your name (any), Email: {email}, Password: {password}")
            logger.info("4. Click 'Continue'")
            logger.info("5. Select IMAP server (should auto-detect cock.li)")
            logger.info("6. Click 'Done'")
            logger.info("7. Account should now be syncing")
            logger.info("")
            input("➡️  Press ENTER when email account is ADDED to Thunderbird...")
            
            logger.info("✅ Email account added to Thunderbird")
            
            # Step 3: Close Thunderbird
            logger.info("\n❌ Step 3: Closing Thunderbird...")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2)
            logger.info("✅ Thunderbird closed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 2 failed: {e}")
            return False
    
    # ============ STAGE 3: TOR (NEW IDENTITY) + HACK2SKILL ============
    
    def stage3_hack2skill_registration(self, full_name, email, whatsapp, dob, gender):
        """
        Stage 3: Register on Hack2skill with NEW Tor identity
        1. Open Tor Browser (fresh)
        2. Get NEW Tor identity
        3. Navigate to Hack2skill registration
        4. Auto-fill some fields, user completes rest
        5. Close Tor
        """
        logger.info("\n" + "="*60)
        logger.info("STAGE 3: Hack2skill REGISTRATION (NEW TOR IDENTITY)")
        logger.info("="*60)
        
        try:
            # Step 1: Open Tor (fresh)
            logger.info("\n📱 Step 1: Opening Tor Browser (fresh session)...")
            tor_paths = [
                r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
                r"C:\Program Files\Tor Browser\Browser\firefox.exe",
            ]
            
            tor_path = None
            for path in tor_paths:
                if os.path.exists(path):
                    tor_path = path
                    break
            
            if not tor_path:
                logger.error("❌ Tor Browser not found")
                return False
            
            subprocess.Popen([tor_path])
            logger.info("✅ Tor Browser starting... (waiting 8 seconds)")
            time.sleep(8)
            
            # Step 2: Get new Tor identity
            logger.info("\n🔄 Step 2: Getting NEW Tor identity...")
            try:
                pyautogui.hotkey('ctrl', 'shift', 'l')  # Request new identity
                logger.info("✅ New Tor identity request sent (wait 3-5 seconds)")
                time.sleep(5)
            except:
                logger.warning("⚠️  Hotkey method didn't work, identity will change on new session")
                logger.info("   You have a fresh Tor identity already")
            
            # Step 3: Navigate to Hack2skill
            logger.info("\n🌐 Step 3: Opening Hack2skill registration...")
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.5)
            hack2skill_url = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
            pyautogui.typewrite(hack2skill_url, interval=0.01)
            pyautogui.press('enter')
            time.sleep(5)
            logger.info("✅ Hack2skill registration page loaded")
            
            # Step 4: Fill form (mix of auto and manual)
            logger.info("\n✏️  Step 4: SEMI-AUTO - Filling registration form")
            logger.info(f"   Full Name: {full_name}")
            logger.info(f"   Email: {email}")
            logger.info(f"   WhatsApp: {whatsapp}")
            logger.info(f"   DOB: {dob}")
            logger.info(f"   Gender: {gender}")
            logger.info("")
            
            logger.info("AUTO-FILLING BASIC FIELDS...")
            time.sleep(1)
            
            # Try to auto-fill first field
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # Full Name
            logger.info("  • Typing Full Name...")
            pyautogui.typewrite(full_name, interval=0.02)
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # Email
            logger.info("  • Typing Email...")
            # For email, use clipboard paste (faster)
            import pyperclip
            pyperclip.copy(email)
            pyautogui.hotkey('ctrl', 'v')
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # WhatsApp
            logger.info("  • Typing WhatsApp...")
            pyautogui.typewrite(whatsapp, interval=0.02)
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # DOB
            logger.info("  • Typing DOB...")
            pyautogui.typewrite(dob, interval=0.02)
            pyautogui.press('tab')
            time.sleep(0.3)
            
            # Gender (select dropdown)
            logger.info("  • Selecting Gender...")
            if gender.lower() == 'male':
                pyautogui.press('down')
            elif gender.lower() == 'female':
                pyautogui .press('down')
                pyautogui.press('down')
            pyautogui.press('tab')
            time.sleep(0.3)
            
            logger.info("✅ Basic fields auto-filled!")
            logger.info("")
            logger.info("MANUAL STEPS REMAINING:")
            logger.info("1. Scroll down and fill remaining fields:")
            logger.info("   - Alternate Phone")
            logger.info("   - Country, State, City")
            logger.info("   - Occupation")
            logger.info("   - College details (name, country, state, city)")
            logger.info("   - Degree, Specialization, Passout Year")
            logger.info("   - LinkedIn URL")
            logger.info("   - College ID (file upload)")
            logger.info("   - GDP Profile Link (from earlier)")
            logger.info("   - Referral Question & Code (if applicable)")
            logger.info("2. Check Terms & Conditions")
            logger.info("3. Review all fields")
            logger.info("4. Click SUBMIT")
            logger.info("")
            input("➡️  Press ENTER when form is COMPLETE and SUBMITTED...")
            
            logger.info("✅ Hack2skill registration submitted!")
            
            # Step 5: Close Tor
            logger.info("\n❌ Step 5: Closing Tor Browser...")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2)
            logger.info("✅ Tor Browser closed")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Stage 3 failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    # ============ MAIN ORCHESTRATOR ============
    
    def run_complete_workflow(self):
        """Run the complete 3-stage workflow"""
        logger.info("\n\n")
        logger.info("╔" + "="*58 + "╗")
        logger.info("║" + " COMPLETE AUTOMATION WORKFLOW ".center(58) + "║")
        logger.info("║" + "Stage 1: cock.li Email → Stage 2: Thunderbird → Stage 3: Hack2skill".center(58) + "║")
        logger.info("╚" + "="*58 + "╝")
        
        # Get user input for email
        logger.info("\n📋 SETUP INFORMATION")
        logger.info("="*60)
        
        full_name = input("Enter Full Name: ").strip()
        username = input("Enter desired cock.li username (without @cock.li): ").strip()
        password = input("Enter password (for cock.li and Google): ").strip()
        whatsapp = input("Enter WhatsApp number (with country code, e.g. +91...): ").strip()
        dob = input("Enter Date of Birth (DD.MM.YYYY): ").strip()
        gender = input("Enter Gender (Male/Female/Other): ").strip()
        
        email = f"{username}@cock.li"
        
        logger.info("\n✅ Configuration Summary:")
        logger.info(f"   Full Name: {full_name}")
        logger.info(f"   Email (cock.li): {email}")
        logger.info(f"   WhatsApp: {whatsapp}")
        logger.info(f"   DOB: {dob}")
        logger.info(f"   Gender: {gender}")
        logger.info("")
        
        confirm = input("❓ Start automation? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("❌ Cancelled by user")
            return False
        
        # Run Stage 1
        if not self.stage1_cockli_email(username, password):
            logger.error("❌ Stage 1 failed. Cannot continue.")
            return False
        
        logger.info("\n⏸️  Pausing between stages... (10 seconds)")
        time.sleep(10)
        
        # Run Stage 2
        if not self.stage2_thunderbird_email(email, password):
            logger.error("⚠️  Stage 2 failed. Continuing to Stage 3...")
        
        logger.info("\n⏸️  Pausing between stages... (10 seconds)")
        time.sleep(10)
        
        # Run Stage 3
        if not self.stage3_hack2skill_registration(full_name, email, whatsapp, dob, gender):
            logger.error("❌ Stage 3 failed.")
            return False
        
        logger.info("\n\n" + "="*60)
        logger.info("✅ ALL STAGES COMPLETE!")
        logger.info("="*60)
        logger.info("Summary:")
        logger.info(f"  1. ✅ cock.li email created: {email}")
        logger.info(f"  2. ✅ Email added to Thunderbird")
        logger.info(f"  3. ✅ Hack2skill registration submitted")
        logger.info("")
        logger.info("Next Steps:")
        logger.info("  • Check Thunderbird for confirmation emails")
        logger.info("  • Check registration email for any issues")
        logger.info("  • Complete any additional requirements from organizers")
        logger.info("="*60)
        
        return True


if __name__ == "__main__":
    # Install dependencies if needed
    try:
        import pyautogui
        import pyperclip
    except ImportError:
        logger.info("Installing required packages...")
        subprocess.run(["pip", "install", "pyautogui", "pyperclip", "-q"])
    
    # Run workflow
    workflow = SequentialWorkflow()
    workflow.run_complete_workflow()
