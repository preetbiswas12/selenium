#!/usr/bin/env python3
"""
Read email contents from all 15 cock.li accounts via IMAP.
Connects directly to imap.cock.li and retrieves emails.
"""

import csv
import imaplib
import email
from email.header import decode_header
import ssl

# Configuration
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts_created.csv"
IMAP_SERVER = "imap.cock.li"
IMAP_PORT = 993

def decode_email_subject(subject):
    """Decode email subject (handles encoded characters)"""
    decoded_parts = []
    for text, encoding in decode_header(subject):
        if isinstance(text, bytes):
            text = text.decode(encoding or 'utf-8', errors='ignore')
        decoded_parts.append(text)
    return ''.join(decoded_parts)

def get_email_body(msg):
    """Extract email body (text version preferred)"""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                break
            elif part.get_content_type() == "text/html" and not body:
                body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
    else:
        body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
    
    return body[:500] if len(body) > 500 else body  # Truncate long emails

def check_account(email_addr, password):
    """Connect to IMAP and check for emails"""
    try:
        # Create SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # Ignore cert issues (for local testing)
        
        # Connect to IMAP server
        print(f"\n{'='*70}")
        print(f"📧 Connecting to {email_addr}...")
        print(f"{'='*70}")
        
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=ssl_context)
        mail.login(email_addr, password)
        
        # Select INBOX
        status, mailbox_data = mail.select("INBOX")
        if status != "OK":
            print(f"  ❌ Cannot select INBOX")
            mail.close()
            mail.logout()
            return
        
        # Get email count
        email_count = int(mailbox_data[0])
        print(f"  ✅ Connected! Found {email_count} emails in INBOX")
        
        if email_count == 0:
            print(f"     (No emails yet)")
            mail.close()
            mail.logout()
            return
        
        # Fetch recent emails (last 5 or all if less than 5)
        fetch_count = min(5, email_count)
        status, messages = mail.search(None, 'ALL')
        
        if status != "OK":
            print(f"  ❌ Cannot search emails")
            mail.close()
            mail.logout()
            return
        
        email_ids = messages[0].split()
        
        # Get the last N emails
        for i, email_id in enumerate(email_ids[-fetch_count:], 1):
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            if status != "OK":
                continue
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            subject = decode_email_subject(msg.get("Subject", "(No Subject)"))
            from_addr = msg.get("From", "(Unknown)")
            date = msg.get("Date", "(Unknown)")
            
            print(f"\n  📨 Email {i}/{fetch_count}:")
            print(f"     From:    {from_addr}")
            print(f"     Subject: {subject}")
            print(f"     Date:    {date}")
            
            body = get_email_body(msg)
            if body:
                print(f"     Body:    {body[:150]}...")
        
        mail.close()
        mail.logout()
        print(f"\n  ✅ Closed connection")
        
    except imaplib.IMAP4.error as e:
        print(f"  ❌ IMAP Error: {e}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    """Read emails from all accounts"""
    print("\n" + "="*70)
    print("READING EMAIL CONTENTS FROM ALL 15 COCK.LI ACCOUNTS")
    print("="*70)
    
    # Read accounts from CSV
    accounts = []
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            accounts.append({
                'email': row['email'],
                'password': row['password']
            })
    
    print(f"\n✅ Loaded {len(accounts)} accounts from CSV")
    
    # Check each account
    for i, account in enumerate(accounts, 1):
        email_addr = account['email']
        password = account['password']
        
        print(f"\n[{i:2d}/15]", end=" ")
        check_account(email_addr, password)
    
    print("\n" + "="*70)
    print("✅ EMAIL CHECK COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
