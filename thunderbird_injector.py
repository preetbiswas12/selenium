"""
Thunderbird Account Injector
Directly adds email accounts to Thunderbird config without UI
"""

import os
import csv
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ThunderbirdAccountInjector:
    """Inject email accounts directly into Thunderbird profile"""
    
    def __init__(self):
        self.thunderbird_profile = self._find_thunderbird_profile()
        logger.info(f"Thunderbird profile: {self.thunderbird_profile}")
    
    def _find_thunderbird_profile(self):
        """Find Thunderbird profile directory"""
        # Windows default location
        appdata = os.path.expanduser("~\\AppData\\Roaming\\Thunderbird\\Profiles")
        
        if os.path.exists(appdata):
            profiles = [d for d in os.listdir(appdata) if os.path.isdir(os.path.join(appdata, d))]
            if profiles:
                profile_path = os.path.join(appdata, profiles[0])
                logger.info(f"✓ Found Thunderbird profile: {profile_path}")
                return profile_path
        
        logger.error("❌ Thunderbird profile not found. Install Thunderbird first.")
        return None
    
    def add_account(self, email, password, first_name="", last_name=""):
        """
        Add IMAP account to Thunderbird
        
        Args:
            email: Full email address (e.g., user@cock.li)
            password: Account password
            first_name: User's first name
            last_name: User's last name
        """
        if not self.thunderbird_profile:
            logger.error("Profile not found")
            return False
        
        try:
            # Detect email provider (cock.li, gmail, etc.)
            domain = email.split('@')[1]
            
            # IMAP/SMTP settings by provider
            settings = self._get_email_settings(domain)
            
            if not settings:
                logger.warning(f"Unknown provider: {domain}")
                return False
            
            logger.info(f"Adding account: {email}")
            
            # Read current prefs.js
            prefs_path = os.path.join(self.thunderbird_profile, "prefs.js")
            accounts_file = os.path.join(self.thunderbird_profile, "ImapMail", domain)
            
            # Create account folder if needed
            if domain not in ["cock.li", "gmail.com"]:
                os.makedirs(accounts_file, exist_ok=True)
            
            # Add account entry to prefs.js
            self._write_account_prefs(prefs_path, email, settings, first_name, last_name)
            
            logger.info(f"✅ Account added: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add account {email}: {e}")
            return False
    
    def _get_email_settings(self, domain):
        """Get IMAP/SMTP settings for email provider"""
        settings_map = {
            "cock.li": {
                "imap_server": "imap.cock.li",
                "imap_port": 993,
                "smtp_server": "smtp.cock.li",
                "smtp_port": 587,
                "security": "STARTTLS"
            },
            "gmail.com": {
                "imap_server": "imap.gmail.com",
                "imap_port": 993,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "security": "SSL/TLS"
            },
            "outlook.com": {
                "imap_server": "imap-mail.outlook.com",
                "imap_port": 993,
                "smtp_server": "smtp-mail.outlook.com",
                "smtp_port": 587,
                "security": "STARTTLS"
            }
        }
        return settings_map.get(domain)
    
    def _write_account_prefs(self, prefs_path, email, settings, first_name, last_name):
        """Write account preferences to prefs.js"""
        try:
            # Read existing prefs to preserve all accounts
            prefs_content = ""
            existing_accounts = ""
            
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r') as f:
                    prefs_content = f.read()
                
                # Extract existing account list
                for line in prefs_content.split('\n'):
                    if 'mail.accountmanager.accounts' in line:
                        # Parse existing accounts: user_pref("mail.accountmanager.accounts", "account1,account2");
                        if '", "' in line:
                            existing_accounts = line.split('", "')[1].rstrip('");')
                        break
            
            # Create account ID
            account_id = f"account_{email.replace('@', '_').replace('.', '_')}"
            username = email.split('@')[0]
            
            # Build new account list (append to existing)
            if existing_accounts:
                new_account_list = f"{existing_accounts},{account_id}"
            else:
                new_account_list = account_id
            
            # Build account config
            account_config = f'''
// Account: {email}
user_pref("mail.account.{account_id}.server", "{account_id}_server");
user_pref("mail.account.{account_id}.identities", "{account_id}_identity");

// Identity
user_pref("mail.identity.{account_id}_identity.fullName", "{first_name} {last_name}");
user_pref("mail.identity.{account_id}_identity.useremail", "{email}");
user_pref("mail.identity.{account_id}_identity.reply_to", "{email}");

// IMAP Server Settings
user_pref("mail.server.{account_id}_server.type", "imap");
user_pref("mail.server.{account_id}_server.hostname", "{settings['imap_server']}");
user_pref("mail.server.{account_id}_server.port", {settings['imap_port']});
user_pref("mail.server.{account_id}_server.username", "{username}");
user_pref("mail.server.{account_id}_server.secure_auth", "on");
user_pref("mail.server.{account_id}_server.security_override", "{settings['security']}");

// SMTP Server Settings
user_pref("mail.smtpServer.{account_id}_smtp.hostname", "{settings['smtp_server']}");
user_pref("mail.smtpServer.{account_id}_smtp.port", {settings['smtp_port']});
user_pref("mail.smtpServer.{account_id}_smtp.username", "{username}");
user_pref("mail.smtpServer.{account_id}_smtp.auth_method", 1);
user_pref("mail.smtpServer.{account_id}_smtp.try_secure_auth_initially", true);
user_pref("mail.identity.{account_id}_identity.smtpServer", "{account_id}_smtp");
'''
            
            # If file exists, remove old accountmanager line and append new one with updated list
            if os.path.exists(prefs_path):
                # Read all lines except the old accountmanager.accounts line
                new_content = ""
                with open(prefs_path, 'r') as f:
                    for line in f:
                        if 'mail.accountmanager.accounts' not in line:
                            new_content += line
                
                # Write updated content without old accountmanager line
                with open(prefs_path, 'w') as f:
                    f.write(new_content)
                    # Add the new account config
                    f.write(account_config)
                    # Add updated accountmanager list with all accounts
                    f.write(f'\nuser_pref("mail.accountmanager.accounts", "{new_account_list}");\n')
            else:
                # File doesn't exist, create it
                with open(prefs_path, 'w') as f:
                    f.write(account_config)
                    f.write(f'user_pref("mail.accountmanager.accounts", "{new_account_list}");\n')
            
            logger.info(f"✓ Added account: {email}")
            logger.info(f"  Account list now: {new_account_list}")
            
        except Exception as e:
            logger.error(f"Failed to write prefs: {e}")
    
    def batch_add_accounts(self, csv_file):
        """
        Add multiple accounts from CSV file
        
        CSV format:
        username,password,email,firstname,lastname
        """
        if not os.path.exists(csv_file):
            logger.error(f"CSV file not found: {csv_file}")
            return []
        
        added_accounts = []
        
        try:
            # First, find the next account number (to avoid conflicts)
            prefs_path = os.path.join(self.thunderbird_profile, "prefs.js")
            next_account_num = 0
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r') as f:
                    for line in f:
                        if 'mail.account.account' in line:
                            # Extract account number
                            import re
                            match = re.search(r'mail\.account\.account(\d+)', line)
                            if match:
                                num = int(match.group(1))
                                next_account_num = max(next_account_num, num + 1)
            
            logger.info(f"Starting from account number: {next_account_num}")
            
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    username = row.get('username')
                    password = row.get('password')
                    firstname = row.get('firstname', '')
                    lastname = row.get('lastname', '')
                    
                    email = f"{username}@cock.li"
                    
                    # Use sequential numbering: account0, account1, account2...
                    account_id = f"account{next_account_num}"
                    if self._add_account_with_id(email, password, firstname, lastname, account_id):
                        added_accounts.append(email)
                        next_account_num += 1
        
        except Exception as e:
            logger.error(f"Failed to batch add accounts: {e}")
        
        logger.info(f"\n✅ Successfully added {len(added_accounts)} accounts")
        return added_accounts
    
    def _add_account_with_id(self, email, password, first_name="", last_name="", account_id="account0"):
        """
        Add account with specific account ID (for sequential numbering)
        
        Args:
            email: Full email address
            password: Account password
            first_name: User's first name
            last_name: User's last name
            account_id: Specific account ID (account0, account1, etc.)
        """
        if not self.thunderbird_profile:
            logger.error("Profile not found")
            return False
        
        try:
            domain = email.split('@')[1]
            settings = self._get_email_settings(domain)
            
            if not settings:
                logger.warning(f"Unknown provider: {domain}")
                return False
            
            logger.info(f"Adding account: {email} as {account_id}")
            
            prefs_path = os.path.join(self.thunderbird_profile, "prefs.js")
            self._write_account_prefs_with_id(prefs_path, email, settings, first_name, last_name, account_id)
            
            logger.info(f"✅ Account added: {email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add account {email}: {e}")
            return False
    
    def _write_account_prefs_with_id(self, prefs_path, email, settings, first_name, last_name, account_id):
        """Write account preferences with specific account ID"""
        try:
            # Read existing prefs to preserve all accounts
            prefs_content = ""
            existing_accounts = ""
            
            if os.path.exists(prefs_path):
                with open(prefs_path, 'r') as f:
                    prefs_content = f.read()
                
                # Extract existing account list
                for line in prefs_content.split('\n'):
                    if 'mail.accountmanager.accounts' in line:
                        if '", "' in line:
                            existing_accounts = line.split('", "')[1].rstrip('");')
                        break
            
            username = email.split('@')[0]
            
            # Build new account list
            if existing_accounts:
                # Add only if not already there
                if account_id not in existing_accounts:
                    new_account_list = f"{existing_accounts},{account_id}"
                else:
                    new_account_list = existing_accounts
            else:
                new_account_list = account_id
            
            # Build account config
            account_config = f'''
// Account: {email} ({account_id})
user_pref("mail.account.{account_id}.server", "{account_id}_server");
user_pref("mail.account.{account_id}.identities", "{account_id}_identity");

// Identity
user_pref("mail.identity.{account_id}_identity.fullName", "{first_name} {last_name}");
user_pref("mail.identity.{account_id}_identity.useremail", "{email}");
user_pref("mail.identity.{account_id}_identity.reply_to", "{email}");
user_pref("mail.identity.{account_id}_identity.smtpServer", "{account_id}_smtp");

// IMAP Server Settings
user_pref("mail.server.{account_id}_server.type", "imap");
user_pref("mail.server.{account_id}_server.hostname", "{settings['imap_server']}");
user_pref("mail.server.{account_id}_server.port", {settings['imap_port']});
user_pref("mail.server.{account_id}_server.username", "{username}");
user_pref("mail.server.{account_id}_server.secure_auth", "on");
user_pref("mail.server.{account_id}_server.security_override", "{settings['security']}");
user_pref("mail.server.{account_id}_server.directory", "");

// SMTP Server Settings  
user_pref("mail.smtpServer.{account_id}_smtp.hostname", "{settings['smtp_server']}");
user_pref("mail.smtpServer.{account_id}_smtp.port", {settings['smtp_port']});
user_pref("mail.smtpServer.{account_id}_smtp.username", "{username}");
user_pref("mail.smtpServer.{account_id}_smtp.auth_method", 1);
user_pref("mail.smtpServer.{account_id}_smtp.try_secure_auth_initially", true);
'''
            
            # Write file: remove old accountmanager line and add new config + updated list
            if os.path.exists(prefs_path):
                new_content = ""
                with open(prefs_path, 'r') as f:
                    for line in f:
                        if 'mail.accountmanager.accounts' not in line:
                            new_content += line
                
                with open(prefs_path, 'w') as f:
                    f.write(new_content)
                    f.write(account_config)
                    f.write(f'user_pref("mail.accountmanager.accounts", "{new_account_list}");\n')
            else:
                with open(prefs_path, 'w') as f:
                    f.write(account_config)
                    f.write(f'user_pref("mail.accountmanager.accounts", "{new_account_list}");\n')
            
            logger.info(f"✓ Added {email} as {account_id}")
            logger.info(f"  Full account list: {new_account_list}")
            
        except Exception as e:
            logger.error(f"Failed to write prefs: {e}")


if __name__ == "__main__":
    import sys
    
    # Usage: python thunderbird_injector.py accounts.csv
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "accounts.csv"
    
    injector = ThunderbirdAccountInjector()
    injector.batch_add_accounts(csv_file)
    
    logger.info("\n📧 Restart Thunderbird to see accounts!")
    logger.info("All accounts are now configured in Thunderbird.")
