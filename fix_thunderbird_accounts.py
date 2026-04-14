#!/usr/bin/env python3
"""
FIX Thunderbird account list - Add all 15 accounts properly
"""

import os
import re
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def fix_thunderbird():
    """Fix the mail.accountmanager.accounts line"""
    
    profile = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
    prefs_path = os.path.join(profile, "prefs.js")
    
    logger.info("")
    logger.info("="*70)
    logger.info("FIXING THUNDERBIRD ACCOUNT LIST")
    logger.info("="*70)
    logger.info("")
    
    if not os.path.exists(prefs_path):
        logger.error(f"prefs.js not found: {prefs_path}")
        return False
    
    # Read file
    with open(prefs_path, 'r') as f:
        content = f.read()
    
    # Build the correct account list (all 15)
    all_accounts = ",".join([f"account{i}" for i in range(15)])
    
    logger.info(f"Setting account list to: {all_accounts}")
    logger.info("")
    
    # Replace the accountmanager.accounts line
    old_pattern = r'user_pref\("mail\.accountmanager\.accounts".*?\);'
    new_line = f'user_pref("mail.accountmanager.accounts", "{all_accounts}");'
    
    content = re.sub(old_pattern, new_line, content)
    
    # Now add the missing mail.account.accountX.identities and mail.account.accountX.server lines
    # These need to be added after the accountmanager.accounts line
    
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        new_lines.append(line)
        
        # After accountmanager.accounts line, add the missing account definitions
        if 'mail.accountmanager.accounts' in line and 'account0,account1' not in line:
            # Add all missing account.accountX.identities and account.accountX.server
            logger.info("Adding account.identities and account.server entries...")
            
            for i in range(15):
                # Check if this account definition already exists
                account_def_identity = f'mail.account.account{i}.identities'
                account_def_server = f'mail.account.account{i}.server'
                
                identity_exists = any(account_def_identity in l for l in lines)
                server_exists = any(account_def_server in l for l in lines)
                
                if not identity_exists:
                    new_lines.append(f'user_pref("mail.account.account{i}.identities", "account{i}_identity");')
                
                if not server_exists:
                    new_lines.append(f'user_pref("mail.account.account{i}.server", "account{i}_server");')
    
    # Write back
    with open(prefs_path, 'w') as f:
        f.write('\n'.join(new_lines))
    
    logger.info("")
    logger.info("="*70)
    logger.info("✅ FIXED! All 15 accounts configured")
    logger.info("="*70)
    logger.info("")
    logger.info("Account list: " + all_accounts)
    logger.info("")
    logger.info("Next: Close and reopen Thunderbird to see all 15 accounts!")
    logger.info("")
    
    return True

if __name__ == "__main__":
    import sys
    
    logger.info("")
    logger.info("⚠️  IMPORTANT: Close Thunderbird completely before running!")
    logger.info("")
    response = input("Is Thunderbird closed? (yes/no): ").strip().lower()
    
    if response == "yes":
        success = fix_thunderbird()
        if success:
            logger.info("✓ Ready! Open Thunderbird now")
    else:
        logger.warning("Please close Thunderbird first!")
        sys.exit(1)
