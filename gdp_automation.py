import logging
import time
from browser_driver import BrowserDriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleDeveloperProfileCreator:
    """Automate Google Developer Profile creation and setup"""
    
    DEVELOPERS_URL = "https://developers.google.com/"
    GDP_CREATE_URL = "https://g.dev/"
    
    def __init__(self, google_email, google_password=None):
        self.google_email = google_email
        self.google_password = google_password
        self.browser = BrowserDriver(headless=False)
        self.profile_link = None
    
    def create_or_setup_profile(self, full_name, bio="", profile_image_path=None):
        """
        Create or setup Google Developer Profile
        
        Args:
            full_name: Full name for profile
            bio: Short bio for profile
            profile_image_path: Path to profile picture
        
        Returns:
            profile_url (e.g., https://g.dev/username) or None if failed
        """
        try:
            logger.info(f"Setting up Google Developer Profile for: {full_name}")
            
            if not self.browser.driver:
                self.browser.initialize()
            
            # Step 1: Navigate to developers.google.com
            self.browser.get(self.DEVELOPERS_URL)
            self.browser.random_delay(3, 5)
            
            # Step 2: Check if already signed in or need to login
            if not self._check_signed_in():
                if not self._login_google(self.google_email, self.google_password):
                    logger.error("Failed to login to Google")
                    return None
            
            self.browser.random_delay(2, 3)
            
            # Step 3: Navigate to profile setup (g.dev or developers page)
            self.browser.get(self.GDP_CREATE_URL)
            self.browser.random_delay(3, 4)
            
            # Step 4: Fill profile details
            if not self._fill_profile_details(full_name, bio, profile_image_path):
                logger.error("Failed to fill profile details")
                return None
            
            # Step 5: Make profile public
            if not self._make_profile_public():
                logger.warning("Could not verify if profile is public")
            
            # Step 6: Get profile link
            self.profile_link = self._extract_profile_link()
            
            if self.profile_link:
                logger.info(f"✅ Profile created: {self.profile_link}")
                return self.profile_link
            else:
                logger.error("Could not extract profile link")
                return None
        
        except Exception as e:
            logger.error(f"Profile creation failed: {e}")
            self.browser.screenshot(f"gdp_error_{int(time.time())}.png")
            return None
    
    def _check_signed_in(self):
        """Check if already signed into Google"""
        try:
            # Look for sign out button or profile icon
            profile_selectors = [
                "button[aria-label*='account']",
                "button[aria-label*='profile']",
                "div[aria-label*='account']",
            ]
            
            for selector in profile_selectors:
                try:
                    element = self.browser.driver.find_elements("css selector", selector)
                    if element:
                        logger.info("Already signed into Google")
                        return True
                except:
                    pass
            
            # Look for sign in button
            signin_selector = "a:contains('Sign in')"
            try:
                signin = self.browser.find_element(signin_selector)
                if signin:
                    logger.info("Not signed in - will login")
                    return False
            except:
                pass
            
            # Assume signed in if no sign out found
            return True
        
        except Exception as e:
            logger.warning(f"Could not determine login status: {e}")
            return False
    
    def _login_google(self, email, password=None):
        """Login to Google account"""
        try:
            logger.info(f"Logging into Google: {email}")
            
            # Find login button
            signin_btn = self.browser.find_element("a:contains('Sign in')")
            if signin_btn:
                self.browser.click(signin_btn)
                self.browser.random_delay(3, 4)
            
            # Fill email
            email_field = self._find_element_by_multiple_selectors([
                "input[type='email']",
                "input[name='username']",
                "input[id='identifierId']",
            ])
            
            if email_field:
                self.browser.type_text(email_field, email)
                self.browser.random_delay(1, 2)
                
                # Click Next
                next_btn = self._find_element_by_multiple_selectors([
                    "button:contains('Next')",
                    "button[aria-label='Next']",
                ])
                
                if next_btn:
                    self.browser.click(next_btn)
                    self.browser.random_delay(2, 3)
            
            # Fill password if provided
            if password:
                pwd_field = self._find_element_by_multiple_selectors([
                    "input[type='password']",
                    "input[name='password']",
                ])
                
                if pwd_field:
                    self.browser.type_text(pwd_field, password)
                    self.browser.random_delay(1, 2)
                    
                    # Click Next
                    next_btn = self._find_element_by_multiple_selectors([
                        "button:contains('Next')",
                        "button[aria-label='Next']",
                    ])
                    
                    if next_btn:
                        self.browser.click(next_btn)
                        self.browser.random_delay(3, 4)
            else:
                logger.warning("⚠️  Password not provided - please login manually")
                self.browser.random_delay(10, 15)
            
            logger.info("✅ Logged into Google")
            return True
        
        except Exception as e:
            logger.error(f"Google login failed: {e}")
            return False
    
    def _fill_profile_details(self, full_name, bio, image_path):
        """Fill profile details (name, bio, image)"""
        try:
            logger.info("Filling profile details...")
            
            # Fill full name
            name_field = self._find_element_by_multiple_selectors([
                "input[name='fullName']",
                "input[id='fullName']",
                "input[placeholder*='name']",
            ])
            
            if name_field:
                self.browser.type_text(name_field, full_name)
                self.browser.random_delay(1, 2)
            
            # Fill bio
            if bio:
                bio_field = self._find_element_by_multiple_selectors([
                    "textarea[name='bio']",
                    "textarea[id='bio']",
                    "textarea[placeholder*='bio']",
                    "textarea[placeholder*='about']",
                ])
                
                if bio_field:
                    self.browser.type_text(bio_field, bio)
                    self.browser.random_delay(1, 2)
            
            # Upload profile image
            if image_path:
                file_input = self._find_element_by_multiple_selectors([
                    "input[type='file'][name='photo']",
                    "input[type='file'][id='photo']",
                    "input[type='file'][accept*='image']",
                ])
                
                if file_input:
                    self.browser.upload_file(file_input, image_path)
                    self.browser.random_delay(2, 3)
            
            logger.info("✅ Profile details filled")
            return True
        
        except Exception as e:
            logger.error(f"Failed to fill profile details: {e}")
            return False
    
    def _make_profile_public(self):
        """Make profile public/visible"""
        try:
            logger.info("Setting profile visibility to public...")
            
            # Look for visibility toggle/dropdown
            visibility_selectors = [
                "select[name='visibility']",
                "select[name='privacy']",
                "button[aria-label*='visibility']",
                "button[aria-label*='public']",
            ]
            
            for selector in visibility_selectors:
                try:
                    element = self.browser.find_element(selector)
                    if element:
                        if "SELECT" in element.tag_name.upper():
                            self.browser.select_dropdown(element, "public")
                        else:
                            self.browser.click(element)
                        
                        # Click public option if dropdown
                        public_option = self._find_element_by_multiple_selectors([
                            "option[value='public']",
                            "button:contains('Public')",
                        ])
                        
                        if public_option:
                            self.browser.click(public_option)
                        
                        logger.info("✅ Profile set to public")
                        return True
                except:
                    pass
            
            logger.warning("Could not find visibility settings")
            return False
        
        except Exception as e:
            logger.error(f"Failed to set profile visibility: {e}")
            return False
    
    def _extract_profile_link(self):
        """Extract profile link from page"""
        try:
            # Look for profile link display
            link_selectors = [
                "input[value^='https://g.dev']",
                "a[href^='https://g.dev']",
                "div:contains('https://g.dev')",
                "span:contains('https://g.dev')",
            ]
            
            for selector in link_selectors:
                try:
                    element = self.browser.driver.find_elements("css selector", selector)
                    if element:
                        if "INPUT" in element[0].tag_name.upper():
                            return element[0].get_attribute("value")
                        elif "A" in element[0].tag_name.upper():
                            return element[0].get_attribute("href")
                        else:
                            text = element[0].text
                            if text.startswith("https://g.dev"):
                                return text
                except:
                    pass
            
            # Try extracting from URL
            current_url = self.browser.driver.current_url
            if "g.dev" in current_url:
                logger.info(f"Profile URL from current page: {current_url}")
                return current_url
            
            logger.warning("Could not extract profile link")
            return None
        
        except Exception as e:
            logger.warning(f"Error extracting profile link: {e}")
            return None
    
    def _find_element_by_multiple_selectors(self, selectors):
        """Try multiple selectors until one works"""
        for selector in selectors:
            try:
                element = self.browser.find_element(selector)
                if element:
                    return element
            except:
                pass
        return None
    
    def close(self):
        """Close browser"""
        self.browser.close()


class GoogleDeveloperProfileGetter:
    """Get existing Google Developer Profile link"""
    
    def __init__(self, google_email, use_tor=True):
        self.google_email = google_email
        self.browser = BrowserDriver(headless=False, use_tor=use_tor)
    
    def get_profile_link(self):
        """
        Get existing GDP profile link
        
        Args:
            google_email: Google email address
        
        Returns:
            Profile URL or None
        """
        try:
            logger.info(f"Retrieving GDP profile for: {self.google_email}")
            
            if not self.browser.driver:
                self.browser.initialize()
            
            # Navigate to g.dev
            self.browser.get("https://g.dev/")
            self.browser.random_delay(2, 3)
            
            # Extract username from email (before @)
            username = self.google_email.split("@")[0]
            
            # Check if profile exists at g.dev/username
            profile_url = f"https://g.dev/{username}"
            self.browser.get(profile_url)
            self.browser.random_delay(2, 3)
            
            # Check if profile page loaded (not 404)
            if "404" not in self.browser.driver.page_source.lower():
                logger.info(f"✅ Profile found: {profile_url}")
                return profile_url
            else:
                logger.warning(f"Profile not found at: {profile_url}")
                return None
        
        except Exception as e:
            logger.error(f"Failed to get profile link: {e}")
            return None
        
        finally:
            self.browser.close()
