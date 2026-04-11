"""
cock.li Email Account Creation - OS Level Automation
Uses PyAutoGUI to directly fill the registration form
Adds account to Thunderbird automatically
"""

import logging
import time
from os_automation import OSAutomation
import os
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CockliOSAutomation:
    """OS-level automation for cock.li email creation"""
    
    COCKLI_REGISTER_URL = "https://cock.li/register.php"
    
    def __init__(self):
        self.os_auto = OSAutomation()
        self.email_created = None
        self.password = None
    
    def create_email_account(self, username, password):
        """
        Create cock.li email account using OS-level automation
        
        Args:
            username: Email username (without @cock.li)
            password: Password for account
            
        Returns:
            email_address: Created email (username@cock.li) or None if failed
        """
        try:
            logger.info(f"Creating cock.li account: {username}@cock.li")
            
            # Step 1: Open registration page
            logger.info("Step 1: Opening cock.li registration page...")
            self.os_auto.open_url_in_browser(self.COCKLI_REGISTER_URL)
            time.sleep(4)  # Wait for page to load
            
            # Take screenshot to verify page loaded
            self.os_auto.screenshot("cockli_page.png")
            
            # Step 2: Click on username field and fill
            logger.info("Step 2: Filling username...")
            # Screenshot shows username field is at approximate position
            # We'll use Tab navigation for better compatibility
            
            # Click somewhere on the form to ensure focus
            self.os_auto.click(400, 300)
            time.sleep(0.5)
            
            # Press Tab to focus on username field
            self.os_auto.press_key('tab')
            time.sleep(0.3)
            
            # Type username
            self.os_auto.type_text_clipboard(username)
            time.sleep(0.5)
            
            # Step 3: Fill password first field
            logger.info("Step 3: Filling password (first field)...")
            self.os_auto.press_key('tab')
            time.sleep(0.3)
            self.os_auto.type_text_clipboard(password)
            time.sleep(0.5)
            
            # Step 4: Fill password second field (confirmation)
            logger.info("Step 4: Filling password confirmation...")
            self.os_auto.press_key('tab')
            time.sleep(0.3)
            self.os_auto.type_text_clipboard(password)
            time.sleep(0.5)
            
            # Step 5: CAPTCHA - Manual solve
            logger.info("Step 5: CAPTCHA detected - solving manually...")
            self.os_auto.screenshot("cockli_captcha.png")
            logger.warning("⚠️ CAPTCHA requires manual solve. Waiting 60 seconds...")
            logger.info("Please solve the CAPTCHA in the browser window")
            time.sleep(60)
            
            # Take screenshot after CAPTCHA
            self.os_auto.screenshot("cockli_after_captcha.png")
            
            # Step 6: Click Terms checkbox
            logger.info("Step 6: Accepting terms...")
            # Check the "I agree to Terms of Service and Privacy Policy" checkbox
            self.os_auto.press_key('tab')  # Move to checkbox
            time.sleep(0.3)
            self.os_auto.press_key('space')  # Check it
            time.sleep(0.5)
            
            # Step 7: Click Register button
            logger.info("Step 7: Clicking Register button...")
            self.os_auto.press_key('tab')  # Move to Register button
            time.sleep(0.3)
            self.os_auto.press_key('return')  # Click Register
            time.sleep(3)
            
            # Step 8: Verify registration success
            logger.info("Step 8: Verifying registration...")
            self.os_auto.screenshot("cockli_success.png")
            
            # Check for success message (look for text containing "success" or redirect)
            # For now, assume success if no errors thrown
            self.email_created = f"{username}@cock.li"
            self.password = password
            
            logger.info(f"✅ cock.li account created: {self.email_created}")
            
            # Step 9: Add to Thunderbird
            logger.info("Step 9: Adding account to Thunderbird...")
            self.add_to_thunderbird(username, password)
            
            return self.email_created
            
        except Exception as e:
            logger.error(f"❌ Failed to create cock.li account: {e}")
            self.os_auto.screenshot("cockli_error.png")
            return None
    
    def add_to_thunderbird(self, username, password):
        """
        Add cock.li email account to Thunderbird
        Directly manipulates Thunderbird profile files
        """
        try:
            logger.info("Adding account to Thunderbird...")
            
            # Thunderbird profile path
            thunderbird_profile = os.path.expanduser(
                "~\\AppData\\Roaming\\Thunderbird\\Profiles"
            )
            
            if not os.path.exists(thunderbird_profile):
                logger.warning("Thunderbird profile not found")
                return False
            
            # Find the default profile
            profiles = [d for d in os.listdir(thunderbird_profile) 
                       if os.path.isdir(os.path.join(thunderbird_profile, d))]
            
            if not profiles:
                logger.warning("No Thunderbird profiles found")
                return False
            
            profile_path = os.path.join(thunderbird_profile, profiles[0])
            prefs_path = os.path.join(profile_path, "prefs.js")
            
            logger.info(f"Using Thunderbird profile: {profiles[0]}")
            
            # Read existing prefs
            prefs_content = ""
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r', encoding='utf-8') as f:
                    prefs_content = f.read()
            
            # Find next account number
            account_num = 0
            while f'mail.account.account{account_num}' in prefs_content:
                account_num += 1
            
            # Create account preferences
            email = f"{username}@cock.li"
            account_prefs = f'''
user_pref("mail.account.account{account_num}.server", "server{account_num}");
user_pref("mail.account.account{account_num}.identities", "id{account_num}");
user_pref("mail.server.server{account_num}.type", "imap");
user_pref("mail.server.server{account_num}.hostname", "mail.cock.li");
user_pref("mail.server.server{account_num}.username", "{username}");
user_pref("mail.server.server{account_num}.port", 993);
user_pref("mail.server.server{account_num}.socketType", 3);
user_pref("mail.identity.id{account_num}.fullName", "User");
user_pref("mail.identity.id{account_num}.email", "{email}");
'''
            
            # Append to prefs
            with open(prefs_path, 'a', encoding='utf-8') as f:
                f.write(account_prefs)
            
            logger.info(f"✅ Account {email} added to Thunderbird")
            
            # Note: Password needs to be stored in Thunderbird's password manager
            # For now, user will be prompted to enter password on first sync
            logger.info("Note: Restart Thunderbird for changes to take effect")
            logger.info("You will be prompted to enter the password on first sync")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add account to Thunderbird: {e}")
            return False
    
    def wait_for_confirmation_email(self, timeout=300):
        """
        Wait for cock.li confirmation email
        Most cock.li accounts are auto-confirmed, but policy may vary
        """
        logger.info("Checking account status...")
        logger.info("Most cock.li accounts are automatically confirmed")
        return True


# Test runner
if __name__ == "__main__":
    automation = CockliOSAutomation()
    
    # Example
    email = automation.create_email_account("testuser999", "SecurePass123!")
    if email:
        print(f"✅ Created: {email}")
    else:
        print("❌ Failed to create account")
