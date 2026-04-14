#!/usr/bin/env python3
"""
DIRECT FIX: Re-write the critical account configuration lines
"""

import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def direct_fix():
    """Directly fix the prefs.js file"""
    
    profile = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
    prefs_path = os.path.join(profile, "prefs.js")
    
    logger.info("")
    logger.info("="*70)
    logger.info("DIRECT FIX: Re-writing account configuration")
    logger.info("="*70)
    logger.info("")
    
    if not os.path.exists(prefs_path):
        logger.error(f"prefs.js not found: {prefs_path}")
        return False
    
    # Read entire file
    with open(prefs_path, 'r') as f:
        lines = f.readlines()
    
    # Remove all lines that contain account/server/identity/smtp configuration
    clean_lines = []
    removed = 0
    
    for line in lines:
        # Skip lines about accounts, servers, identities, smtp
        if any(x in line for x in [
            'mail.account.',
            'mail.server.',
            'mail.identity.',
            'mail.smtpServer.',
            'mail.accountmanager.accounts',
            'mail.accountmanager.localfoldersserver',
            'mail.accountmanager.defaultaccount'
        ]):
            removed += 1
            continue
        
        clean_lines.append(line)
    
    logger.info(f"Removed {removed} old account-related lines")
    
    # Prepare all account configuration lines
    account_config = []
    
    # Add mail.account lines for all 15 accounts
    for i in range(15):
        account_config.append(f'user_pref("mail.account.account{i}.identities", "account{i}_identity");\n')
        account_config.append(f'user_pref("mail.account.account{i}.server", "account{i}_server");\n')
    
    # Add the accountmanager lines
    all_accounts = ",".join([f"account{i}" for i in range(15)])
    account_config.append(f'user_pref("mail.accountmanager.accounts", "{all_accounts}");\n')
    account_config.append(f'user_pref("mail.accountmanager.defaultaccount", "account0");\n')
    account_config.append(f'user_pref("mail.accountmanager.localfoldersserver", "server1");\n')
    
    # Write back: clean lines + account config
    with open(prefs_path, 'w') as f:
        f.writelines(clean_lines)
        f.write('\n// ===== ACCOUNT CONFIGURATION (15 cock.li accounts) =====\n')
        f.writelines(account_config)
    
    logger.info("")
    logger.info("="*70)
    logger.info("✅ FIXED! Account list:")
    logger.info(all_accounts)
    logger.info("="*70)
    logger.info("")
    logger.info("Close and reopen Thunderbird to see all 15 accounts")
    logger.info("")
    
    return True

if __name__ == "__main__":
    import sys
    
    logger.info("")
    logger.info("⚠️  CLOSE THUNDERBIRD FIRST!")
    logger.info("")
    response = input("Is Thunderbird closed? (yes/no): ").strip().lower()
    
    if response == "yes":
        direct_fix()
    else:
        logger.warning("Please close Thunderbird!")
        sys.exit(1)
