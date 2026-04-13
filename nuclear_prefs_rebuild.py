#!/usr/bin/env python3
"""
NUCLEAR OPTION: Complete prefs.js rebuild with minimal dependencies
No user.js - everything goes directly into prefs.js
"""

import os
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

def load_accounts():
    with open(r"C:\Users\preet\Downloads\selenium\accounts_created.csv") as f:
        accounts = list(csv.DictReader(f))
    return accounts

def nuclear_prefs_rebuild():
    profile_dir = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
    prefs_path = os.path.join(profile_dir, "prefs.js")
    user_js_path = os.path.join(profile_dir, "user.js")
    
    logger.info("")
    logger.info("="*80)
    logger.info("NUCLEAR OPTION: Complete prefs.js rebuild")
    logger.info("="*80)
    
    # Step 1: Remove user.js (don't need it)
    logger.info("\n[STEP 1] Removing user.js...")
    if os.path.exists(user_js_path):
        os.remove(user_js_path)
        logger.info("  ✅ Deleted user.js")
    
    # Step 2: Delete old prefs.js completely
    logger.info("\n[STEP 2] Deleting old prefs.js...")
    if os.path.exists(prefs_path):
        os.remove(prefs_path)
        logger.info("  ✅ Deleted old prefs.js")
    
    # Step 3: Create FRESH prefs.js with ONLY essential settings + 15 accounts
    logger.info("\n[STEP 3] Creating fresh prefs.js...")
    accounts = load_accounts()
    
    # Start with ONLY essential Thunderbird settings
    prefs_content = """// Mozilla Thunderbird User Profile Configuration
// Auto-generated for 15 cock.li email accounts

// ===== Essential Thunderbird Settings =====
user_pref("browser.startup.homepage_override.mstone", "ignored");
user_pref("startup.homepage_welcome_url", "");
user_pref("startup.homepage_welcome_url.additional", "");
user_pref("mail.default_charsets.iso-2022-jp.enable_conversion", false);
user_pref("mail.default_charsets.shift_jis", "shift_jis");

// ===== 15 COCK.LI ACCOUNTS =====

"""
    
    # Build account configurations
    for idx, acc in enumerate(accounts):
        account_id = f"account{idx}"
        mail_dir = f"ImapMail/imap.cock-{idx}.li"
        full_path = os.path.join(profile_dir, mail_dir).replace("\\", "\\\\")
        
        # Account definition
        prefs_content += f'user_pref("mail.account.{account_id}.identities", "{account_id}_identity");\n'
        prefs_content += f'user_pref("mail.account.{account_id}.server", "{account_id}_server");\n'
        
        # Identity
        prefs_content += f'user_pref("mail.identity.{account_id}_identity.fullName", "");\n'
        prefs_content += f'user_pref("mail.identity.{account_id}_identity.reply_to", "{acc["email"]}");\n'
        prefs_content += f'user_pref("mail.identity.{account_id}_identity.smtpServer", "{account_id}_smtp");\n'
        prefs_content += f'user_pref("mail.identity.{account_id}_identity.useremail", "{acc["email"]}");\n'
        prefs_content += f'user_pref("mail.identity.{account_id}_identity.valid", true);\n'
        
        # IMAP Server
        prefs_content += f'user_pref("mail.server.{account_id}_server.directory", "{full_path}");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.directory-rel", "[ProfD]{mail_dir}");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.hostname", "imap.cock.li");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.port", 993);\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.secure_auth", "on");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.storeContractID", "@mozilla.org/msgstore/berkeleystore;1");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.type", "imap");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.username", "{acc["username"]}");\n'
        prefs_content += f'user_pref("mail.server.{account_id}_server.security_override", "STARTTLS");\n'
        
        # SMTP Server
        prefs_content += f'user_pref("mail.smtpServer.{account_id}_smtp.auth_method", 1);\n'
        prefs_content += f'user_pref("mail.smtpServer.{account_id}_smtp.hostname", "smtp.cock.li");\n'
        prefs_content += f'user_pref("mail.smtpServer.{account_id}_smtp.port", 587);\n'
        prefs_content += f'user_pref("mail.smtpServer.{account_id}_smtp.try_secure_auth_initially", true);\n'
        prefs_content += f'user_pref("mail.smtpServer.{account_id}_smtp.username", "{acc["username"]}");\n'
    
    # Account Manager - CRITICAL
    account_list = ",".join([f"account{i}" for i in range(len(accounts))])
    prefs_content += f'\n// ===== ACCOUNT MANAGER =====\n'
    prefs_content += f'user_pref("mail.accountmanager.accounts", "{account_list}");\n'
    prefs_content += f'user_pref("mail.accountmanager.defaultaccount", "account0");\n'
    prefs_content += f'user_pref("mail.accountmanager.localfoldersserver", "server1");\n'
    prefs_content += f'user_pref("mail.smtpservers", "{account_list}");\n'
    
    # Local Folders server (required by Thunderbird)
    prefs_content += f'\n// ===== LOCAL FOLDERS SERVER =====\n'
    prefs_content += f'user_pref("mail.server.server1.type", "none");\n'
    prefs_content += f'user_pref("mail.server.server1.hostname", "Local Folders");\n'
    prefs_content += f'user_pref("mail.server.server1.directory", "{os.path.join(profile_dir, "Mail", "Local Folders-4").replace(chr(92), chr(92)*2)}");\n'
    prefs_content += f'user_pref("mail.server.server1.directory-rel", "[ProfD]Mail/Local Folders-4");\n'
    prefs_content += f'user_pref("mail.server.server1.name", "Local Folders");\n'
    prefs_content += f'user_pref("mail.server.server1.storeContractID", "@mozilla.org/msgstore/berkeleystore;1");\n'
    prefs_content += f'user_pref("mail.server.server1.userName", "nobody");\n'
    
    # Write fresh prefs.js
    with open(prefs_path, 'w') as f:
        f.write(prefs_content)
    
    logger.info(f"  ✅ Created fresh prefs.js ({len(prefs_content)} bytes)")
    
    # Step 4: Create mail directories
    logger.info("\n[STEP 4] Creating mail directories...")
    imap_base = os.path.join(profile_dir, "ImapMail")
    os.makedirs(imap_base, exist_ok=True)
    
    for idx in range(len(accounts)):
        mail_dir = os.path.join(imap_base, f"imap.cock-{idx}.li")
        os.makedirs(mail_dir, exist_ok=True)
    
    logger.info(f"  ✅ Created {len(accounts)} mail directories")
    
    # Step 5: Delete cache files
    logger.info("\n[STEP 5] Deleting cache files...")
    cache_files = [
        'global-messages-db.sqlite',
        'global-messages-db.sqlite-shm',
        'global-messages-db.sqlite-wal',
        'folderTree.json'
    ]
    
    for cache_file in cache_files:
        file_path = os.path.join(profile_dir, cache_file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"  ✅ Deleted: {cache_file}")
            except:
                pass
    
    logger.info("")
    logger.info("="*80)
    logger.info("✅✅✅ NUCLEAR REBUILD COMPLETE!")
    logger.info("="*80)
    logger.info(f"\n✅ Created fresh prefs.js with 15 accounts")
    logger.info(f"✅ All mail directories created")
    logger.info(f"✅ Cache files deleted (force rebuild)")
    logger.info(f"\nAccounts: {account_list}")
    logger.info(f"\nNow open Thunderbird - all 15 accounts should appear!")
    logger.info("")
    
    return True

if __name__ == "__main__":
    import sys
    
    logger.info("\n⚠️  THUNDERBIRD MUST BE CLOSED!")
    response = input("Is Thunderbird closed? (yes/no): ").strip().lower()
    
    if response == "yes":
        nuclear_prefs_rebuild()
    else:
        logger.warning("Please close Thunderbird first!")
        sys.exit(1)
