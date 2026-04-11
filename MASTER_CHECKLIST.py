#!/usr/bin/env python3
"""
MASTER EXECUTION CHECKLIST
Complete setup validation before running automation
"""

import os
import sys
import subprocess

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check(item, done=False):
    return f"{'✅' if done else '⏳'} {item}"

def main():
    print_section("HACK2SKILL AUTOMATION - MASTER EXECUTION CHECKLIST")
    
    items = {
        "Stage 1: Environment & Dependencies": {
            "Python 3.8+ installed": os.system("python --version 2>&1") == 0,
            "requirements.txt exists": os.path.exists("requirements.txt"),
            "All packages installed": False,  # Check manually
        },
        "Stage 2: Google Cloud Setup": {
            "credentials.json exists": os.path.exists("credentials.json"),
            "Google Cloud project created": False,
            "Sheets API enabled": False,
            "Service account configured": False,
        },
        "Stage 3: Form Configuration": {
            "Registration page inspected": False,
            "FORM_SELECTORS updated in config.py": False,
            "Selectors tested in browser": False,
        },
        "Stage 4: Email Setup": {
            "cock.li accounts ready": False,
            "Gmail IMAP enabled": False,
            "Email credentials configured": False,
        },
        "Stage 5: Google Developer Profile": {
            "Google accounts created (optional)": False,
            "Developer profiles created (optional)": False,
        },
        "Stage 6: Google Sheets": {
            "Setup_Accounts sheet created": False,
            "Hack2skill_Registrations sheet created": False,
            "All columns added": False,
            "Test data added": False,
            "Sheets shared with service account": False,
        },
        "Stage 7: CAPTCHA Configuration": {
            "CAPTCHA_CONFIG method selected": False,
            "API keys configured (if using auto)": False,
        },
        "Stage 8: Validation": {
            "test_setup.py ran successfully": False,
            "Browser launches correctly": False,
            "Single account test passed": False,
        },
    }
    
    total_items = sum(len(v) for v in items.values())
    checked = sum(1 for stage in items.values() for item in stage.values() if item)
    
    # Display checklist
    for stage, stage_items in items.items():
        print(f"\n📋 {stage}")
        print("-" * 70)
        for item, done in stage_items.items():
            print(check(item, done))
        print()
    
    # Summary
    print_section("PROGRESS SUMMARY")
    print(f"Progress: {checked}/{total_items} items complete\n")
    
    if checked >= total_items * 0.7:  # 70% complete
        print("✅ You can start with setup_pipeline.py for basic testing\n")
    
    if checked >= total_items * 0.9:  # 90% complete
        print("✅ You're ready to run production automation!\n")
    else:
        print(f"⏳ {total_items - checked} items remaining\n")
        print("Next steps:")
        print("1. Check items above")
        print("2. Follow SETUP_PIPELINE_GUIDE.md")
        print("3. Use SELECTOR_GUIDE.md to find form selectors")
        print("4. Run: python test_setup.py")
        print("5. Run: python setup_pipeline.py --mode interactive")
        print("6. Run: python main.py")
    
    print_section("QUICK COMMAND REFERENCE")
    
    print("Installation:")
    print("  pip install -r requirements.txt\n")
    
    print("Testing:")
    print("  python test_setup.py\n")
    
    print("Create Email + GDP Profile:")
    print("  python setup_pipeline.py --mode interactive\n")
    
    print("Batch Create Multiple Accounts:")
    print("  python setup_pipeline.py --mode batch --sheet 'Setup_Accounts'\n")
    
    print("Register on Hack2skill:")
    print("  python main.py\n")
    
    print_section("DOCUMENTATION QUICK ACCESS")
    print("""
👉 START HERE:
   SETUP_PIPELINE_GUIDE.md    - Complete 3-stage pipeline guide
   
📚 INSTALLATION & CONFIG:
   SETUP_GUIDE.md             - Detailed installation steps
   SELECTOR_GUIDE.md          - Find CSS form selectors
   FORM_FIELDS_REFERENCE.md   - All 25+ form fields
   
📊 SYSTEM OVERVIEW:
   README_COMPLETE.md         - Complete project overview
   COMPLETE_SETUP_SUMMARY.md  - Feature summary
   
🔧 UTILITIES:
   test_setup.py              - Validation script
   CHECKLIST.py               - This file
""")
    
    print_section("FINAL CHECKLIST")
    
    ready_to_go = input("\n✅ Are you ready to start? (yes/no): ").strip().lower()
    
    if ready_to_go == 'yes':
        print("\n🚀 Let's begin!\n")
        print("1. First, prepare accounts:")
        print("   python setup_pipeline.py --mode interactive\n")
        print("2. Then register on Hack2skill:")
        print("   python main.py\n")
        return True
    else:
        print("\n⏳ Complete the checklist items above and come back!\n")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
