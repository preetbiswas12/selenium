#!/usr/bin/env python3
"""
Pre-run Checklist
Run through this before executing main.py
"""

import os
import sys

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def check_item(item, done=False):
    status = "✅" if done else "⏳"
    return f"{status} {item}"

def main():
    print_header("HACK2SKILL AUTOMATION - PRE-RUN CHECKLIST")
    
    checklist = {
        "Environment Setup": [
            ("Python 3.8+ installed", os.system("python --version") == 0),
            ("pip installed", os.system("pip --version") == 0),
            ("All requirements installed", os.path.exists("requirements.txt")),
        ],
        "Credentials & Keys": [
            ("credentials.json exists", os.path.exists("credentials.json")),
            ("Google Sheet created", False),  # Manual check
            ("cock.li email accounts created", False),  # Manual check
            ("CAPTCHA API key (if using auto)", False),  # Manual check
        ],
        "Configuration": [
            ("config.py updated with form selectors", False),  # Manual check
            ("CAPTCHA_CONFIG method selected", False),  # Manual check
            ("Email credentials configured", False),  # Manual check
            ("main.py has correct sheet name", False),  # Manual check
        ],
        "Google Sheet": [
            ("Sheet name: Hack2skill_Registrations", False),  # Manual check
            ("All columns added (see FORM_FIELDS_REFERENCE.md)", False),  # Manual check
            ("Test data in 1-2 rows", False),  # Manual check
            ("Sheet shared with service account", False),  # Manual check
        ],
        "Form Inspection": [
            ("Inspected all form fields (F12)", False),  # Manual check
            ("Updated FORM_SELECTORS in config.py", False),  # Manual check
            ("Tested selectors in browser console", False),  # Manual check
        ],
        "Testing": [
            ("Ran: python test_setup.py", False),  # Manual check
            ("No errors in test_setup.py output", False),  # Manual check
            ("Browser launches successfully", False),  # Manual check
            ("Single registration test (optional)", False),  # Manual check
        ],
        "Final Verification": [
            ("All form selectors are correct", False),  # Manual check
            ("Email OTP fetching works", False),  # Manual check
            ("Google Sheet updates properly", False),  # Manual check
            ("Ready to run main.py", False),  # Manual check
        ],
    }
    
    total_checked = 0
    total_items = 0
    
    for category, items in checklist.items():
        print(f"\n📋 {category}")
        print("-" * 60)
        
        for item, status in items:
            total_items += 1
            if status:
                total_checked += 1
                print(check_item(item, True))
            else:
                print(check_item(item, False))
    
    print_header("SUMMARY")
    print(f"Progress: {total_checked}/{total_items} items complete")
    
    if total_checked == total_items:
        print("✅ All items checked! You're ready to run: python main.py\n")
        return True
    else:
        remaining = total_items - total_checked
        print(f"⏳ {remaining} item(s) remaining\n")
        print("Next steps:")
        print("1. Complete unchecked items above")
        print("2. Use SETUP_GUIDE.md for detailed instructions")
        print("3. Use SELECTOR_GUIDE.md to find form selectors")
        print("4. Use FORM_FIELDS_REFERENCE.md for field mappings")
        print("5. Run test_setup.py to diagnose issues")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
