#!/usr/bin/env python3
"""
CORRECTED: Inject all 15 accounts using the WORKING configuration from cubic4355@cock.li
Key differences from previous attempt:
1. Use mail.cock.li instead of imap.cock.li
2. Add all missing settings: check_new_mail, login_at_startup, timeout, trash_folder_name, clientid, namespace.personal
3. Match the exact structure from the manually-created working account
"""

import csv
import os
import subprocess
import uuid
from pathlib import Path

# Paths
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
PROFILE_DIR = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
PREFS_FILE = os.path.join(PROFILE_DIR, "prefs.js")
IMAP_HOSTNAME = "mail.cock.li"  # ← CORRECT HOSTNAME!
SMTP_HOSTNAME = "mail.cock.li"  # ← ALSO USE mail.cock.li!

def kill_thunderbird():
    """Kill any running Thunderbird processes"""
    try:
        subprocess.run(["taskkill", "/F", "/IM", "thunderbird.exe"], capture_output=True)
        print("✅ Thunderbird killed")
    except:
        pass

def read_accounts_from_csv():
    """Read email accounts from CSV file"""
    accounts = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append({
                'email': row['email'],
                'password': row['password'],
                'username': row['username']
            })
    return accounts

def generate_corrected_prefs(accounts):
    """Generate prefs.js lines using the EXACT working configuration"""
    lines = []
    account_ids = []
    
    print("\n[STEP 1] Generating CORRECTED configuration (mail.cock.li, not imap.cock.li)...")
    
    for i, account in enumerate(accounts):
        email = account['email']
        account_id = f"account{i}"
        server_id = f"server{i+3}"  # Start at server3 (server1=local, server2=blank, server3-17 for email)
        identity_id = f"id{i}"
        smtp_id = f"smtp{i}"
        
        # Generate unique clientid UUID
        clientid = str(uuid.uuid4())
        
        account_ids.append(account_id)
        
        # ===== SERVER CONFIGURATION (IMAP) - MATCHING WORKING ACCOUNT =====
        lines.append(f'user_pref("mail.server.{server_id}.auth_mechanism", "plain");')
        lines.append(f'user_pref("mail.server.{server_id}.check_new_mail", true);')
        lines.append(f'user_pref("mail.server.{server_id}.clientid", "{clientid}");')
        lines.append(f'user_pref("mail.server.{server_id}.directory", "[ProfD]ImapMail/mail.cock-{i+1}.li");')
        lines.append(f'user_pref("mail.server.{server_id}.directory-rel", "[ProfD]ImapMail/mail.cock-{i+1}.li");')
        lines.append(f'user_pref("mail.server.{server_id}.hostname", "{IMAP_HOSTNAME}");')
        lines.append(f'user_pref("mail.server.{server_id}.lastFilterTime", 0);')
        lines.append(f'user_pref("mail.server.{server_id}.login_at_startup", true);')
        lines.append(f'user_pref("mail.server.{server_id}.max_cached_connections", 5);')
        lines.append(f'user_pref("mail.server.{server_id}.namespace.personal", "\\\"\\\"");')
        lines.append(f'user_pref("mail.server.{server_id}.nextFilterTime", 0);')
        lines.append(f'user_pref("mail.server.{server_id}.port", 993);')
        lines.append(f'user_pref("mail.server.{server_id}.socketType", 3);')
        lines.append(f'user_pref("mail.server.{server_id}.spamActionTargetAccount", "imap://{email.replace("@", "%40")}@{IMAP_HOSTNAME}");')
        lines.append(f'user_pref("mail.server.{server_id}.storeContractID", "@mozilla.org/msgstore/berkeleystore;1");')
        lines.append(f'user_pref("mail.server.{server_id}.timeout", 29);')
        lines.append(f'user_pref("mail.server.{server_id}.trash_folder_name", "Trash");')
        lines.append(f'user_pref("mail.server.{server_id}.type", "imap");')
        lines.append(f'user_pref("mail.server.{server_id}.userName", "{email}");')
        lines.append(f'user_pref("mail.server.{server_id}.name", "{email}");')
        lines.append('')
        
        # ===== IDENTITY CONFIGURATION =====
        lines.append(f'user_pref("mail.identity.{identity_id}.bccAddr", "");')
        lines.append(f'user_pref("mail.identity.{identity_id}.bccSelf", false);')
        lines.append(f'user_pref("mail.identity.{identity_id}.doBcc", false);')
        lines.append(f'user_pref("mail.identity.{identity_id}.fullName", "{email}");')
        lines.append(f'user_pref("mail.identity.{identity_id}.mail.signature_file", "");')
        lines.append(f'user_pref("mail.identity.{identity_id}.replyTo", "");')
        lines.append(f'user_pref("mail.identity.{identity_id}.useremail", "{email}");')
        lines.append('')
        
        # ===== SMTP CONFIGURATION (MATCHING WORKING ACCOUNT STYLE) =====
        lines.append(f'user_pref("mail.smtpServer.smtp{i}.auth_method", 1);')
        lines.append(f'user_pref("mail.smtpServer.smtp{i}.hostname", "{SMTP_HOSTNAME}");')
        lines.append(f'user_pref("mail.smtpServer.smtp{i}.port", 465);')
        lines.append(f'user_pref("mail.smtpServer.smtp{i}.try_secure_auth_initially", true);')
        lines.append(f'user_pref("mail.smtpServer.smtp{i}.username", "{email}");')
        lines.append('')
        
        # ===== ACCOUNT-TO-SERVER/IDENTITY LINKAGE =====
        lines.append(f'user_pref("mail.account.{account_id}.identities", "{identity_id}");')
        lines.append(f'user_pref("mail.account.{account_id}.server", "{server_id}");')
        lines.append(f'user_pref("mail.account.{account_id}.smtp_server", "smtp{i}");')
        lines.append('')
        
        print(f"  [{i+1:2d}/15] {email} -> {account_id} -> {server_id} (mail.cock.li)")
    
    # The CRITICAL line: Global account registry
    account_list = ",".join(account_ids)
    lines.append(f'user_pref("mail.accountmanager.accounts", "{account_list}");')
    
    return "\n".join(lines), account_list

def remove_old_account_entries(prefs_content):
    """Remove old account entries from prefs.js"""
    new_lines = []
    
    for line in prefs_content.split('\n'):
        # Skip old account/server/identity/smtp lines (but keep non-email ones)
        if any(x in line for x in ['mail.account.account', 'mail.server.server', 'mail.identity.id', 'mail.smtpServer', 'mail.accountmanager.accounts', 'mail.smtpserver']):
            if 'mail.smtpserver.smtp15' not in line and 'mail.server.server1' not in line:  # Keep system ones
                continue
        new_lines.append(line)
    
    return '\n'.join(new_lines).rstrip() + '\n'

def inject_accounts():
    """Main function to inject all accounts with CORRECTED configuration"""
    print("\n" + "="*80)
    print("CORRECTED 15-ACCOUNT INJECTION (mail.cock.li)")
    print("="*80)
    
    # Kill Thunderbird
    kill_thunderbird()
    
    # Read accounts
    accounts = read_accounts_from_csv()
    print(f"\n✅ Read {len(accounts)} accounts from CSV")
    
    # Generate corrected configuration
    new_prefs_lines, account_list = generate_corrected_prefs(accounts)
    
    # Read current prefs.js
    print("\n[STEP 2] Reading current prefs.js...")
    with open(PREFS_FILE, 'r', encoding='utf-8') as f:
        prefs_content = f.read()
    print(f"  ✅ Read {len(prefs_content)} bytes")
    
    # Remove old account entries
    print("\n[STEP 3] Removing old broken account entries...")
    clean_prefs = remove_old_account_entries(prefs_content)
    print(f"  ✅ Cleaned prefs.js")
    
    # Append new corrected account entries
    print("\n[STEP 4] Appending CORRECTED account configuration...")
    final_prefs = clean_prefs + "\n// ===== 15 EMAIL ACCOUNTS (CORRECTED - mail.cock.li) =====\n" + new_prefs_lines
    
    # Write back
    print("\n[STEP 5] Writing updated prefs.js...")
    with open(PREFS_FILE, 'w', encoding='utf-8') as f:
        f.write(final_prefs)
    print(f"  ✅ Wrote {len(final_prefs)} bytes")
    
    # Verify
    print("\n[STEP 6] Verifying account registration...")
    with open(PREFS_FILE, 'r', encoding='utf-8') as f:
        verify_content = f.read()
        if f'user_pref("mail.accountmanager.accounts", "{account_list}");' in verify_content:
            print(f"  ✅ Account registry verified")
        else:
            print("  ❌ Account registry NOT found!")
            return False
    
    # Create mail directories with correct names
    print("\n[STEP 7] Creating mail directories (mail.cock-N.li naming)...")
    for i in range(len(accounts)):
        mail_dir = os.path.join(PROFILE_DIR, "ImapMail", f"mail.cock-{i+1}.li")
        os.makedirs(mail_dir, exist_ok=True)
        print(f"  ✅ mail.cock-{i+1}.li")
    
    # Summary
    print("\n" + "="*80)
    print("✅✅✅ CORRECTED INJECTION COMPLETE!")
    print("="*80)
    print(f"\nKey Fix: Using mail.cock.li instead of imap.cock.li")
    print(f"Account Registry: {account_list[:50]}...")
    print(f"\nTotal accounts: {len(accounts)}")
    print(f"\nNow open Thunderbird - all 15 accounts should show with Inbox, Junk, Trash!")
    print("="*80 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        inject_accounts()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
