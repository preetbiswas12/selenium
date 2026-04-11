import logging
import time
from config import CAPTCHA_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CaptchaHandler:
    """Handle various CAPTCHA solving methods"""
    
    def __init__(self, method="manual"):
        self.method = method
        self.api_key = None
        
        if method == "2captcha":
            self.api_key = CAPTCHA_CONFIG.get("2captcha_api_key")
        elif method == "capsolver":
            self.api_key = CAPTCHA_CONFIG.get("capsolver_api_key")
    
    def handle_captcha(self, driver, captcha_site_key=None):
        """
        Handle CAPTCHA based on configured method
        
        Args:
            driver: Selenium WebDriver
            captcha_site_key: Site key for reCAPTCHA (if applicable)
        
        Returns:
            True if CAPTCHA solved, False if failed
        """
        if self.method == "manual":
            return self._manual_solve(driver)
        elif self.method == "2captcha":
            return self._solve_with_2captcha(captcha_site_key)
        elif self.method == "capsolver":
            return self._solve_with_capsolver(driver, captcha_site_key)
        else:
            logger.warning("Unknown CAPTCHA method")
            return False
    
    def _manual_solve(self, driver):
        """
        Pause automation and wait for manual CAPTCHA solve
        """
        try:
            pause_time = CAPTCHA_CONFIG.get("manual_pause_time", 30)
            logger.warning(f"\n⚠️  CAPTCHA DETECTED!")
            logger.warning(f"Please solve the CAPTCHA manually in the browser.")
            logger.info(f"Waiting {pause_time} seconds for you to solve it...")
            
            # Show visual countdown
            for i in range(pause_time, 0, -5):
                print(f"⏳ {i} seconds remaining...", end='\r')
                time.sleep(5)
            
            logger.info("✅ Proceeding with form submission...")
            return True
            
        except Exception as e:
            logger.error(f"Manual CAPTCHA handling failed: {e}")
            return False
    
    def _solve_with_2captcha(self, site_key):
        """
        Solve reCAPTCHA using 2Captcha API
        Requires: site_key from the page
        """
        if not self.api_key:
            logger.error("2Captcha API key not configured")
            return False
        
        try:
            import requests
            
            # Submit CAPTCHA to 2Captcha
            logger.info("Submitting CAPTCHA to 2Captcha...")
            
            payload = {
                'method': 'userrecaptcha',
                'googlekey': site_key,
                'key': self.api_key,
                'json': 1,
            }
            
            response = requests.post('http://2captcha.com/api/upload', data=payload)
            result = response.json()
            
            if result['status'] != 1:
                logger.error(f"2Captcha submission failed: {result}")
                return False
            
            captcha_id = result['captcha_id']
            logger.info(f"CAPTCHA submitted with ID: {captcha_id}")
            
            # Poll for result
            logger.info("Waiting for 2Captcha to solve...")
            timeout = CAPTCHA_CONFIG.get("captcha_timeout", 120)
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                time.sleep(5)  # Wait 5 seconds before checking
                
                check_payload = {
                    'method': 'res',
                    'captcha_id': captcha_id,
                    'key': self.api_key,
                    'json': 1,
                }
                
                check_response = requests.get('http://2captcha.com/api/res', params=check_payload)
                check_result = check_response.json()
                
                if check_result['status'] == 1:
                    token = check_result['request']
                    logger.info(f"✅ CAPTCHA solved! Token: {token[:20]}...")
                    return token
            
            logger.error("CAPTCHA solving timed out")
            return False
            
        except Exception as e:
            logger.error(f"2Captcha solving failed: {e}")
            return False
    
    def _solve_with_capsolver(self, driver, site_key):
        """
        Solve reCAPTCHA using CapSolver API
        """
        if not self.api_key:
            logger.error("CapSolver API key not configured")
            return False
        
        try:
            import requests
            
            # Get current page URL
            page_url = driver.current_url
            
            logger.info("Submitting CAPTCHA to CapSolver...")
            
            payload = {
                'clientKey': self.api_key,
                'task': {
                    'type': 'NoCaptchaTaskProxyless',
                    'websiteURL': page_url,
                    'websiteKey': site_key,
                }
            }
            
            response = requests.post(
                'https://api.capsolver.com/createTask',
                json=payload
            )
            result = response.json()
            
            if result['errorId'] != 0:
                logger.error(f"CapSolver submission failed: {result}")
                return False
            
            task_id = result['taskId']
            logger.info(f"CAPTCHA submitted with task ID: {task_id}")
            
            # Poll for result
            logger.info("Waiting for CapSolver to solve...")
            timeout = CAPTCHA_CONFIG.get("captcha_timeout", 120)
            start_time = time.time()
            
            while (time.time() - start_time) < timeout:
                time.sleep(5)
                
                check_payload = {
                    'clientKey': self.api_key,
                    'taskId': task_id,
                }
                
                check_response = requests.post(
                    'https://api.capsolver.com/getTaskResult',
                    json=check_payload
                )
                check_result = check_response.json()
                
                if check_result['status'] == 'ready':
                    token = check_result['solution']['gRecaptchaToken']
                    logger.info(f"✅ CAPTCHA solved! Token: {token[:20]}...")
                    return token
            
            logger.error("CAPTCHA solving timed out")
            return False
            
        except Exception as e:
            logger.error(f"CapSolver solving failed: {e}")
            return False
    
    @staticmethod
    def inject_recaptcha_token(driver, token):
        """
        Inject reCAPTCHA token into page after solving
        """
        try:
            # Try common reCAPTCHA response field names
            script = f"""
                document.getElementById('g-recaptcha-response').innerHTML = '{token}';
                if (window.___grecaptcha_cfg) {{
                    Object.entries(window.___grecaptcha_cfg.clients).forEach(([key, client]) => {{
                        if (client.callback) {{
                            client.callback('{token}');
                        }}
                    }});
                }}
            """
            driver.execute_script(script)
            logger.info("✅ CAPTCHA token injected successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to inject CAPTCHA token: {e}")
            return False
