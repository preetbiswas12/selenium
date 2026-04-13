#!/usr/bin/env python3
"""
Add passwords to all 15 accounts in prefs.js
This will store the passwords so Thunderbird doesn't ask for them on login
"""

import csv
import os
import subprocess

CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
PROFILE_DIR = r"C:\Users\preet\AppData\Roaming\Thunderbird\Profiles\ckq7joll.default-esr-1"
PREFS_FILE = os.path.join(PROFILE_DIR, "prefs.js")

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

def add_passwords_to_prefs():
    """Add password preferences to prefs.js"""
    print("\n" + "="*80)
    print("ADDING PASSWORDS TO ALL 15 ACCOUNTS")
    print("="*80)
    
    kill_thunderbird()
    
    # Read accounts
    accounts = read_accounts_from_csv()
    print(f"\n✅ Read {len(accounts)} accounts from CSV")
    
    # Read current prefs.js
    print("\n[STEP 1] Reading prefs.js...")
    with open(PREFS_FILE, 'r', encoding='utf-8') as f:
        prefs_content = f.read()
    print(f"  ✅ Read {len(prefs_content)} bytes")
    
    # Remove old password lines
    print("\n[STEP 2] Removing old password entries...")
    new_lines = []
    for line in prefs_content.split('\n'):
        if 'signon.rememberSignons' not in line and 'password' not in line.lower():
            new_lines.append(line)
    
    clean_prefs = '\n'.join(new_lines)
    print(f"  ✅ Cleaned old password entries")
    
    # Generate password configuration
    print("\n[STEP 3] Generating password configuration...")
    password_lines = []
    
    # Enable password remembering
    password_lines.append('user_pref("signon.rememberSignons", true);')
    password_lines.append('')
    
    for i, account in enumerate(accounts):
        email = account['email']
        password = account['password']
        
        # Store password for each server and SMTP account
        # IMAP password (server3-17)
        server_id = f"server{i+3}"
        password_lines.append(f'user_pref("mail.server.{server_id}.auth_mechanism", "plain");')
        password_lines.append(f'user_pref("mail.server.{server_id}.logonFailure", false);')
        password_lines.append('')
        
        # SMTP password  
        smtp_id = f"smtp{i}"
        password_lines.append(f'user_pref("mail.smtpServer.smtp{i}.auth_method", 1);')
        password_lines.append(f'user_pref("mail.smtpserver.smtp{i}.auth_mechanism", "plain");')
        password_lines.append('')
        
        print(f"  [{i+1:2d}/15] {email}")
    
    password_config = '\n'.join(password_lines)
    
    # Write back
    print("\n[STEP 4] Writing updated prefs.js with password support...")
    final_prefs = clean_prefs + "\n\n// ===== PASSWORD CONFIGURATION =====\n" + password_config
    
    with open(PREFS_FILE, 'w', encoding='utf-8') as f:
        f.write(final_prefs)
    print(f"  ✅ Wrote {len(final_prefs)} bytes")
    
    # Now we need to store passwords in logins.json
    print("\n[STEP 5] Creating logins.json with encrypted passwords...")
    create_logins_json(PROFILE_DIR, accounts)
    print(f"  ✅ Passwords stored in logins.json")
    
    print("\n" + "="*80)
    print("✅✅✅ PASSWORDS ADDED!")
    print("="*80)
    print(f"\nTotal accounts with passwords: {len(accounts)}")
    print(f"\nNow open Thunderbird - it should NOT ask for passwords!")
    print("="*80 + "\n")

def create_logins_json(profile_dir, accounts):
    """Create logins.json with password entries"""
    import json
    import base64
    from datetime import datetime
    
    logins_file = os.path.join(profile_dir, "logins.json")
    
    # If logins.json exists, read it; otherwise create new
    if os.path.exists(logins_file):
        with open(logins_file, 'r') as f:
            logins_data = json.load(f)
    else:
        logins_data = {
            "nextId": 1,
            "logins": [],
            "potentiallyVulnerablePasswords": [],
            "dismissedBreachAlertsByLoginGUID": {},
            "dismissedUnmonitoredLoginsByLoginGUID": {},
            "version": 3
        }
    
    # Add login entries for each account
    for i, account in enumerate(accounts):
        email = account['email']
        password = account['password']
        server_id = f"server{i+3}"
        
        # IMAP login
        imap_login = {
            "id": logins_data["nextId"],
            "hostname": "imap://mail.cock.li:993",
            "httpRealm": None,
            "formSubmitURL": None,
            "usernameField": "",
            "passwordField": "",
            "encUsername": base64.b64encode(email.encode()).decode(),
            "encPassword": base64.b64encode(password.encode()).decode(),
            "guid": "",
            "encType": 1,
            "timeCreated": int(datetime.now().timestamp() * 1000),
            "timeLastUsed": int(datetime.now().timestamp() * 1000),
            "timePasswordChanged": int(datetime.now().timestamp() * 1000),
            "timesUsed": 1
        }
        logins_data["logins"].append(imap_login)
        logins_data["nextId"] += 1
        
        # SMTP login
        smtp_login = {
            "id": logins_data["nextId"],
            "hostname": "smtp://mail.cock.li:465",
            "httpRealm": None,
            "formSubmitURL": None,
            "usernameField": "",
            "passwordField": "",
            "encUsername": base64.b64encode(email.encode()).decode(),
            "encPassword": base64.b64encode(password.encode()).decode(),
            "guid": "",
            "encType": 1,
            "timeCreated": int(datetime.now().timestamp() * 1000),
            "timeLastUsed": int(datetime.now().timestamp() * 1000),
            "timePasswordChanged": int(datetime.now().timestamp() * 1000),
            "timesUsed": 1
        }
        logins_data["logins"].append(smtp_login)
        logins_data["nextId"] += 1
    
    # Write logins.json
    with open(logins_file, 'w') as f:
        json.dump(logins_data, f, indent=2)

if __name__ == "__main__":
    try:
        add_passwords_to_prefs()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
