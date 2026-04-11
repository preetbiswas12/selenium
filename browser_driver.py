from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.keys import Keys
import time
import random
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrowserDriver:
    """Selenium browser with Tor support"""
    
    def __init__(self, headless=False, use_tor=True):
        self.headless = headless
        self.use_tor = use_tor
        self.driver = None
    
    def initialize(self):
        """Start browser - Tor Browser or Chrome"""
        try:
            if self.use_tor:
                return self._initialize_tor()
            else:
                return self._initialize_chrome()
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def _initialize_tor(self):
        """Initialize Tor Browser (Firefox with Tor)"""
        try:
            # Tor Browser path (typical installation)
            tor_paths = [
                r"C:\Program Files\Tor Browser\Browser\firefox.exe",
                r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
                os.path.expanduser(r"~\AppData\Local\Tor Browser\Browser\firefox.exe"),
            ]
            
            tor_path = None
            for path in tor_paths:
                if os.path.exists(path):
                    tor_path = path
                    break
            
            if not tor_path:
                logger.warning("Tor Browser not found, falling back to Chrome")
                return self._initialize_chrome()
            
            options = FirefoxOptions()
            options.binary_location = tor_path
            
            # Socks proxy for Tor
            options.set_preference("network.proxy.type", 1)  # Manual proxy
            options.set_preference("network.proxy.socks", "127.0.0.1")
            options.set_preference("network.proxy.socks_port", 9050)
            options.set_preference("network.proxy.socks_remote_dns", True)
            
            # Privacy settings
            options.set_preference("dom.webdriver.enabled", False)
            options.set_preference("useAutomationExtension", False)
            
            self.driver = webdriver.Firefox(options=options)
            time.sleep(random.uniform(2, 4))
            logger.info("✅ Tor Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Tor Browser: {e}")
            return self._initialize_chrome()
    
    def _initialize_chrome(self):
        """Initialize standard Chrome"""
        try:
            options = Options()
            
            if self.headless:
                options.add_argument("--headless=new")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            time.sleep(random.uniform(1, 3))
            logger.info("✅ Chrome initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Chrome: {e}")
            return False
    
    def get(self, url):
        """Navigate to URL"""
        try:
            self.driver.get(url)
            self.random_delay()
            logger.info(f"Navigated to: {url}")
        except Exception as e:
            logger.error(f"Failed to navigate: {e}")
    
    def find_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        """Find element with wait"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            self.random_delay(0.5, 1.5)
            return element
        except Exception as e:
            logger.error(f"Element not found: {selector} ({e})")
            return None
    
    def click(self, element):
        """Click element safely"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", element)
            self.random_delay(0.5, 1)
            element.click()
            logger.info(f"Clicked element")
        except Exception as e:
            logger.error(f"Failed to click: {e}")
    
    def type_text(self, element, text, speed=0.05):
        """Type text with human-like speed"""
        try:
            element.clear()
            self.random_delay(0.3, 0.7)
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(speed - 0.02, speed + 0.02))
            logger.info(f"Typed text (length: {len(text)})")
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
    
    def upload_file(self, file_input_element, file_path):
        """Upload file"""
        try:
            file_input_element.send_keys(file_path)
            logger.info(f"Uploaded file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
    
    def select_dropdown(self, element, value):
        """Select from dropdown by value"""
        try:
            from selenium.webdriver.support.select import Select
            Select(element).select_by_value(value)
            logger.info(f"Selected dropdown value: {value}")
        except Exception as e:
            logger.error(f"Failed to select dropdown: {e}")
    
    def random_delay(self, min_sec=2, max_sec=5):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def screenshot(self, filename):
        """Take screenshot"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
    
    def close_all_tabs_and_refresh(self):
        """Close all tabs except first one and open a fresh tab"""
        try:
            # Close all tabs except the first one
            tabs = self.driver.window_handles
            for tab in tabs[1:]:
                self.driver.switch_to.window(tab)
                self.driver.close()
            
            # Back to first tab
            if self.driver.window_handles:
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.delete_all_cookies()  # Clear cookies for fresh state
                logger.info("✅ Closed all tabs, opened fresh tab")
            
            time.sleep(random.uniform(1, 2))
            return True
        except Exception as e:
            logger.error(f"Failed to refresh tabs: {e}")
            return False
    
    def close(self):
        """Close browser"""
        try:
            self.driver.quit()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")
