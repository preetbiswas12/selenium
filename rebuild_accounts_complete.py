#!/usr/bin/env python3
"""
COMPLETE REBUILD: Restore all 15 accounts with FULL configuration
"""

import os
import csv
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def rebuild_accounts():
    """Completely rebuild all 15 accounts from scratch"""
    
    profile = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
    prefs_path = os.path.join(profile, "prefs.js")
    csv_path = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
    
    logger.info("")
    logger.info("="*70)
    logger.info("COMPLETE REBUILD: Loading all 15 accounts from CSV")
    logger.info("="*70)
    logger.info("")
    
    # Read CSV
    accounts = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append({
                    'username': row.get('username'),
                    'email': f"{row.get('username')}@cock.li",
                    'password': row.get('password')
                })
        logger.info(f"✓ Loaded {len(accounts)} accounts from CSV")
    else:
        logger.error(f"CSV not found: {csv_path}")
        return False
    
    # Read prefs and keep only non-account lines
    with open(prefs_path, 'r') as f:
        lines = f.readlines()
    
    clean_lines = []
    for line in lines:
        if any(x in line for x in [
            'mail.account.',
            'mail.server.',
            'mail.identity.',
            'mail.smtpServer.',
            'mail.smtpserver.',
            'mail.accountmanager.accounts',
            'mail.accountmanager.localfoldersserver',
            'mail.accountmanager.defaultaccount'
        ]):
            continue
        clean_lines.append(line)
    
    logger.info(f"Cleaned old account configuration")
    
    # Build complete account configuration
    config_lines = []
    config_lines.append('\n// ===== COMPLETE ACCOUNT CONFIGURATION (15 accounts) =====\n')
    
    # Add each account
    for idx, acc in enumerate(accounts):
        account_id = f"account{idx}"
        username = acc['username']
        email = acc['email']
        
        logger.info(f"  [{idx+1}/15] Configuring {email}...")
        
        # Account definition
        config_lines.append(f'user_pref("mail.account.{account_id}.identities", "{account_id}_identity");\n')
        config_lines.append(f'user_pref("mail.account.{account_id}.server", "{account_id}_server");\n')
        
        # Identity settings
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.fullName", " ");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.useremail", "{email}");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.reply_to", "{email}");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.smtpServer", "{account_id}_smtp");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.valid", true);\n')
        
        # IMAP Server settings
        config_lines.append(f'user_pref("mail.server.{account_id}_server.type", "imap");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.hostname", "imap.cock.li");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.port", 993);\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.username", "{username}");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.password", "{acc['password']}");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.secure_auth", "on");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.security_override", "STARTTLS");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.directory", "");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.storeContractID", "@mozilla.org/msgstore/berkeleystore;1");\n')
        
        # SMTP Server settings
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.hostname", "smtp.cock.li");\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.port", 587);\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.username", "{username}");\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.auth_method", 1);\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.try_secure_auth_initially", true);\n')
    
    # Add account manager settings
    all_accounts = ",".join([f"account{i}" for i in range(len(accounts))])
    config_lines.append(f'\nuser_pref("mail.accountmanager.accounts", "{all_accounts}");\n')
    config_lines.append(f'user_pref("mail.accountmanager.defaultaccount", "account0");\n')
    config_lines.append(f'user_pref("mail.accountmanager.localfoldersserver", "server1");\n')
    
    # Write complete file
    with open(prefs_path, 'w') as f:
        f.writelines(clean_lines)
        f.writelines(config_lines)
    
    logger.info("")
    logger.info("="*70)
    logger.info(f"✅ REBUILT! All {len(accounts)} accounts fully configured")
    logger.info("="*70)
    logger.info("")
    logger.info(f"Account list: {all_accounts}")
    logger.info("")
    logger.info("Close and reopen Thunderbird now!")
    logger.info("")
    
    return True

if __name__ == "__main__":
    import sys
    
    logger.info("")
    logger.info("⚠️  CLOSE THUNDERBIRD FIRST!")
    logger.info("")
    response = input("Is Thunderbird closed? (yes/no): ").strip().lower()
    
    if response == "yes":
        rebuild_accounts()
    else:
        logger.warning("Please close Thunderbird!")
        sys.exit(1)
