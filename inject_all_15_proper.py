#!/usr/bin/env python3
"""
PROPER INJECTION: Create complete Thunderbird config for all 15 accounts
Copies exact format from the working cubic4355 account
"""

import os
import csv
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def load_csv():
    """Load all accounts from CSV"""
    accounts = []
    csv_path = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append(row['username'])
    
    return accounts

def inject_all_15():
    """Inject all 15 accounts into prefs.js"""
    
    profile = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
    prefs_path = os.path.join(profile, "prefs.js")
    
    logger.info("")
    logger.info("="*80)
    logger.info("PROPER INJECTION: All 15 Cock.li Accounts")
    logger.info("="*80)
    
    # Load accounts from CSV
    accounts = load_csv()
    logger.info(f"✅ Loaded {len(accounts)} accounts from CSV")
    
    # Read current prefs.js
    with open(prefs_path, 'r') as f:
        all_lines = f.readlines()
    
    # Remove ALL mail-related config (clean slate)
    clean_lines = []
    for line in all_lines:
        if any(x in line for x in [
            'mail.account.',
            'mail.server.',
            'mail.identity.',
            'mail.smtpServer.',
            'mail.smtpserver.',
            'mail.accountmanager.'
        ]):
            continue
        clean_lines.append(line)
    
    logger.info(f"✅ Cleaned old configuration")
    
    # Build complete config
    config_lines = []
    config_lines.append("\n")
    config_lines.append("// ========== ACCOUNT DEFINITIONS ==========\n")
    
    # Account definitions first
    for idx, username in enumerate(accounts):
        account_id = f"account{idx}"
        config_lines.append(f'user_pref("mail.account.{account_id}.identities", "{account_id}_identity");\n')
        config_lines.append(f'user_pref("mail.account.{account_id}.server", "{account_id}_server");\n')
    
    # Identity definitions
    config_lines.append("\n// ========== IDENTITY DEFINITIONS ==========\n")
    for idx, username in enumerate(accounts):
        email = f"{username}@cock.li"
        account_id = f"account{idx}"
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.fullName", "");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.reply_to", "{email}");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.smtpServer", "{account_id}_smtp");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.useremail", "{email}");\n')
        config_lines.append(f'user_pref("mail.identity.{account_id}_identity.valid", true);\n')
    
    # IMAP Server definitions
    config_lines.append("\n// ========== IMAP SERVER DEFINITIONS ==========\n")
    for idx, username in enumerate(accounts):
        account_id = f"account{idx}"
        mail_dir = f"ImapMail/imap.cock-{idx}.li"
        full_path = f"C:\\\\Users\\\\preet\\\\AppData\\\\Roaming\\\\Thunderbird\\\\Profiles\\\\ckq7joll.default-esr-1\\\\{mail_dir}"
        
        config_lines.append(f'user_pref("mail.server.{account_id}_server.directory", "{full_path}");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.directory-rel", "[ProfD]{mail_dir}");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.hostname", "imap.cock.li");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.port", 993);\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.secure_auth", "on");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.security_override", "STARTTLS");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.type", "imap");\n')
        config_lines.append(f'user_pref("mail.server.{account_id}_server.username", "{username}");\n')
    
    # SMTP Server definitions
    config_lines.append("\n// ========== SMTP SERVER DEFINITIONS ==========\n")
    for idx, username in enumerate(accounts):
        account_id = f"account{idx}"
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.auth_method", 1);\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.hostname", "smtp.cock.li");\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.port", 587);\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.try_secure_auth_initially", true);\n')
        config_lines.append(f'user_pref("mail.smtpServer.{account_id}_smtp.username", "{username}");\n')
    
    # Account manager
    config_lines.append("\n// ========== ACCOUNT MANAGER ==========\n")
    all_accounts = ",".join([f"account{i}" for i in range(len(accounts))])
    config_lines.append(f'user_pref("mail.accountmanager.accounts", "{all_accounts}");\n')
    config_lines.append(f'user_pref("mail.accountmanager.defaultaccount", "account0");\n')
    config_lines.append(f'user_pref("mail.accountmanager.localfoldersserver", "server1");\n')
    
    # Write everything back
    with open(prefs_path, 'w') as f:
        f.writelines(clean_lines)
        f.writelines(config_lines)
    
    logger.info("")
    logger.info("="*80)
    logger.info(f"✅✅✅ SUCCESS! Configured {len(accounts)} accounts")
    logger.info("="*80)
    logger.info("")
    logger.info("Account manager list:")
    logger.info(f"  {all_accounts}")
    logger.info("")
    logger.info("Each account configured with:")
    logger.info("  ✅ Identity (email, reply-to, SMTP server)")
    logger.info("  ✅ IMAP Server (imap.cock.li:993, STARTTLS)")
    logger.info("  ✅ SMTP Server (smtp.cock.li:587)")
    logger.info("")
    logger.info("Now open Thunderbird - you should see all 15 accounts!")
    logger.info("")
    
    return True

if __name__ == "__main__":
    import sys
    
    logger.info("")
    logger.info("⚠️  THUNDERBIRD MUST BE COMPLETELY CLOSED!")
    logger.info("")
    response = input("Is Thunderbird closed? (yes/no): ").strip().lower()
    
    if response == "yes":
        inject_all_15()
        logger.info("✅ Injection complete! Open Thunderbird now.")
    else:
        logger.warning("Please close Thunderbird first!")
        sys.exit(1)
