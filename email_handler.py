import imaplib
import email
import time
import re
from email.header import decode_header
from config import EMAIL_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailOTPHandler:
    """Fetch OTP from email using IMAP"""
    
    def __init__(self, email_address, password):
        self.email_address = email_address
        self.password = password
        self.imap_server = EMAIL_CONFIG["imap_server"]
        self.imap_port = EMAIL_CONFIG["imap_port"]
    
    def connect(self):
        """Connect to IMAP server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.mail.login(self.email_address, self.password)
            logger.info(f"Connected to {self.imap_server}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to email: {e}")
            return False
    
    def get_latest_otp(self, timeout=60):
        """
        Wait for OTP email and extract code
        Retries for up to 'timeout' seconds
        """
        start_time = time.time()
        otp = None
        
        while (time.time() - start_time) < timeout:
            try:
                self.mail.select("INBOX")
                status, messages = self.mail.search(None, "ALL")
                
                if messages[0]:
                    # Get latest email
                    email_ids = messages[0].split()
                    latest_email_id = email_ids[-1]
                    
                    status, msg_data = self.mail.fetch(latest_email_id, "(RFC822)")
                    
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Get email body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode()
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode()
                            
                            # Extract OTP (look for 4-6 digit code)
                            otp_match = re.search(r'\b(\d{4,6})\b', body)
                            if otp_match:
                                otp = otp_match.group(1)
                                logger.info(f"OTP found: {otp}")
                                return otp
                
                logger.info("Waiting for OTP email...")
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error fetching OTP: {e}")
                time.sleep(5)
        
        logger.warning("OTP not found within timeout")
        return None
    
    def disconnect(self):
        """Disconnect from IMAP"""
        try:
            self.mail.close()
            self.mail.logout()
            logger.info("Disconnected from email")
        except:
            pass

class ManualOTPHandler:
    """Fallback: Manual OTP input (script pauses for user)"""
    
    @staticmethod
    def get_otp():
        """Ask user to input OTP manually"""
        otp = input("\n📧 Check your email and enter the OTP code: ")
        return otp.strip()
