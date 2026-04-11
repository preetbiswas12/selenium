import logging
import time
import os
from browser_driver import BrowserDriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CockliEmailCreator:
    """Automate cock.li email account creation and add to Thunderbird"""
    
    COCK_LI_REGISTER_URL = "https://cock.li/register.php"
    
    def __init__(self):
        self.browser = BrowserDriver(headless=False)
        self.email_created = None
    
    def create_email_account(self, username, password):
        """
        Create a new cock.li email account
        
        Args:
            username: Desired username (without @cock.li)
            password: Account password
        
        Returns:
            email_address (e.g., username@cock.li) or None if failed
        """
        try:
            logger.info(f"Creating cock.li account: {username}@cock.li")
            
            if not self.browser.driver:
                self.browser.initialize()
            
            # Navigate directly to registration page
            self.browser.get(self.COCK_LI_REGISTER_URL)
            self.browser.random_delay(2, 4)
            
            # Fill username field (first text input on the form)
            logger.info("Filling username field...")
            username_input = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
            
            username_field = None
            if username_input:
                username_field = username_input[0]
            
            if username_field:
                self.browser.type_text(username_field, username)
                self.browser.random_delay(1, 2)
            else:
                logger.error("Username field not found")
                return None
            
            # Fill password fields
            logger.info("Filling password fields...")
            password_inputs = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
            
            if len(password_inputs) >= 2:
                # First password
                self.browser.type_text(password_inputs[0], password)
                self.browser.random_delay(1, 2)
                
                # Confirm password
                self.browser.type_text(password_inputs[1], password)
                self.browser.random_delay(1, 2)
            else:
                logger.error("Password fields not found")
                return None
            
            # Accept Terms checkbox
            logger.info("Accepting Terms of Service...")
            try:
                terms_checkbox = self.browser.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                if terms_checkbox:
                    self.browser.click(terms_checkbox[0])
                    self.browser.random_delay(1, 2)
            except:
                logger.warning("Could not find terms checkbox")
            
            # Handle CAPTCHA
            logger.info("⏸️ CAPTCHA detected - solve it manually in the browser")
            logger.info("Once solved, look for 'Register' button and click it")
            
            # Wait for user to complete CAPTCHA and click Register
            max_wait = 300  # 5 minutes
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                time.sleep(2)
                
                try:
                    current_url = self.browser.driver.current_url
                    page_text = self.browser.driver.page_source
                    
                    # Check for success indicators
                    if "successfully" in page_text.lower() or "created" in page_text.lower() or "confirmation" in page_text.lower():
                        logger.info("✅ Account creation successful!")
                        self.email_created = f"{username}@cock.li"
                        
                        # Add to Thunderbird
                        self._add_to_thunderbird(username, password)
                        return self.email_created
                    
                    # Check if page changed
                    if "register.php" not in current_url:
                        logger.info("✅ Account creation successful! (page redirected)")
                        self.email_created = f"{username}@cock.li"
                        
                        # Add to Thunderbird
                        self._add_to_thunderbird(username, password)
                        return self.email_created
                        
                except:
                    pass
            
            logger.error("❌ Timeout waiting for account creation")
            return None
        
        except Exception as e:
            logger.error(f"Account creation failed: {e}")
            self.browser.screenshot(f"cockli_error_{int(time.time())}.png")
            return None
    
    def _add_to_thunderbird(self, username, password):
        """
        Add the created email account to Mozilla Thunderbird
        
        Args:
            username: Email username
            password: Email password
        """
        try:
            email = f"{username}@cock.li"
            logger.info(f"📧 Adding {email} to Thunderbird...")
            
            # Thunderbird profile path
            thunderbird_profile_path = os.path.expanduser(
                "~\\AppData\\Roaming\\Thunderbird\\Profiles"
            )
            
            if not os.path.exists(thunderbird_profile_path):
                logger.warning("Thunderbird profiles directory not found")
                logger.info(f"Manual setup: Add {email} to Thunderbird")
                logger.info(f"  - IMAP Server: imap.cock.li (Port 993, SSL)")
                logger.info(f"  - SMTP Server: smtp.cock.li (Port 465, SSL)")
                logger.info(f"  - Username: {email}")
                logger.info(f"  - Password: {password}")
                return False
            
            # Find the default profile
            profiles = [d for d in os.listdir(thunderbird_profile_path) if d.endswith(".default") or d.endswith(".default-release")]
            
            if not profiles:
                logger.warning("No Thunderbird default profile found")
                return False
            
            profile_path = os.path.join(thunderbird_profile_path, profiles[0])
            prefs_file = os.path.join(profile_path, "prefs.js")
            
            # Add account configuration to prefs.js
            logger.info(f"Configuring Thunderbird account...")
            
            account_prefs = f'''
// Cock.li Account: {email}
user_pref("mail.accounts.account999.server", "server999");
user_pref("mail.accounts.account999.identities", "id999");
user_pref("mail.server.server999.hostname", "imap.cock.li");
user_pref("mail.server.server999.username", "{email}");
user_pref("mail.server.server999.port", 993);
user_pref("mail.server.server999.socketType", 3);
user_pref("mail.server.server999.type", "imap");
user_pref("mail.identity.id999.fullName", "{username}");
user_pref("mail.identity.id999.useremail", "{email}");
user_pref("mail.identity.id999.smtp_server", "smtp999");
user_pref("mail.smtpserver.smtp999.hostname", "smtp.cock.li");
user_pref("mail.smtpserver.smtp999.port", 465);
user_pref("mail.smtpserver.smtp999.socketType", 3);
user_pref("mail.smtpserver.smtp999.username", "{email}");
'''
            
            # Append to prefs.js
            if os.path.exists(prefs_file):
                try:
                    with open(prefs_file, 'a', encoding='utf-8') as f:
                        f.write(account_prefs)
                    logger.info("✅ Account configuration added to Thunderbird")
                except:
                    logger.warning("Could not write to Thunderbird config")
            
            # Save credentials manually for user reference
            logger.info(f"📝 Account credentials:")
            logger.info(f"  Email: {email}")
            logger.info(f"  Password: {password}")
            logger.info(f"  IMAP: imap.cock.li:993 (SSL/TLS)")
            logger.info(f"  SMTP: smtp.cock.li:465 (SSL/TLS)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding to Thunderbird: {e}")
            logger.info(f"Manual setup:")
            logger.info(f"  Email: {username}@cock.li")
            logger.info(f"  Password: {password}")
            logger.info(f"  IMAP: imap.cock.li:993")
            logger.info(f"  SMTP: smtp.cock.li:465")
            return False
    
    def close_browser(self):
        """Close the browser"""
        try:
            self.browser.close()
            logger.info("Browser closed")
        except:
            pass


class CockliEmailUpdater:
    """Update cock.li email account settings (recovery email, etc)"""
    
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.browser = BrowserDriver(headless=False)
    
    def login(self):
        """Login to cock.li account"""
        try:
            logger.info(f"Logging into: {self.email}")
            
            if not self.browser.driver:
                self.browser.initialize()
            
            self.browser.get("https://cock.li/")
            self.browser.random_delay(2, 3)
            
            logger.info("✅ Manual login required in browser")
            return True
        
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def close(self):
        """Close browser"""
        self.browser.close()
