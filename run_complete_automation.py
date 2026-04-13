"""
COMPLETE AUTOMATION MASTER SCRIPT
Create 100-200 cock.li accounts + Add to Thunderbird
With Tor restart, CAPTCHA handling, and batch scaling
"""

import os
import sys
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def print_banner(text):
    """Print pretty banner"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def get_number_of_accounts():
    """Ask user how many accounts to create"""
    print_banner("Step 1: How Many Accounts?")
    
    while True:
        try:
            num = int(input("Enter number of accounts to create (1-200): ").strip())
            if 1 <= num <= 200:
                return num
            else:
                print("❌ Please enter a number between 1 and 200")
        except ValueError:
            print("❌ Please enter a valid number")


def get_anonymity_mode():
    """Ask user which anonymity mode"""
    print_banner("Step 2: Anonymity Mode?")
    
    print("Choose your privacy level:")
    print("")
    print("[1] Firefox Incognito (local privacy, same IP)")
    print("    ✓ Cleaning after each account")
    print("    ✓ No cookies/cache shared")
    print("    ✓ Faster")
    print("")
    print("[2] Tor Browser (new IP per account)")
    print("    ✓ Completely anonymous")
    print("    ✓ New IP for each account")
    print("    ✓ Maximum privacy")
    print("    ⚠ Slower (Tor startup per account)")
    print("")
    
    while True:
        choice = input("Choose [1] or [2]: ").strip()
        if choice == "1":
            return False  # Don't use Tor
        elif choice == "2":
            return True   # Use Tor
        else:
            print("❌ Please enter 1 or 2")


def main():
    """Main automation flow"""
    
    print_banner("🚀 COMPLETE EMAIL AUTOMATION SYSTEM")
    print("Features:")
    print("  ✓ Creates 1-200 cock.li accounts at scale")
    print("  ✓ Unique random usernames")
    print("  ✓ Smart browser detection")
    print("  ✓ Automatic form filling")
    print("  ✓ CAPTCHA handling (you solve manually)")
    print("  ✓ Auto-inject into Thunderbird")
    print("")
    
    # Check if GeckoDriver exists
    print("Checking dependencies...")
    geckodriver_exists = os.path.exists(r"C:\webdrivers\geckodriver.exe")
    
    if not geckodriver_exists:
        print("")
        print("⚠️  GeckoDriver not found!")
        print("")
        print("Fix this with ONE command:")
        print("  python setup_geckodriver.py")
        print("")
        print("Then run this script again.")
        return False
    
    print("✓ All dependencies found\n")
    
    # Step 1: Get number of accounts
    num_accounts = get_number_of_accounts()
    
    # Step 2: Get anonymity mode
    use_tor = get_anonymity_mode()
    
    # Step 2: Create cock.li accounts
    print_banner("Step 3: Creating cock.li Accounts")
    
    logger.info(f"Will create {num_accounts} accounts...")
    logger.info("")
    logger.info("IMPORTANT:")
    if use_tor:
        logger.info(f"  1. Tor Browser will open/close {num_accounts} times")
        logger.info(f"  2. Wait 20 seconds for Tor to connect EACH TIME")
        logger.info("  3. For each account, you'll have 20 seconds to solve CAPTCHA")
        logger.info("  4. Each account takes ~2-3 minutes (Tor + CAPTCHA)")
        total_time = num_accounts * 2.5
    else:
        logger.info(f"  1. Firefox Incognito will open/close {num_accounts} times")
        logger.info("  2. For each account, you'll have 20 seconds to solve CAPTCHA")
        logger.info("  3. Each account takes ~1-2 minutes")
        total_time = num_accounts * 1.5
    
    logger.info("")
    logger.info(f"Estimated total time: {total_time:.0f} minutes (~{total_time/60:.1f} hours)")
    logger.info("")
    
    response = input("Ready to start? (yes/no): ").strip().lower()
    if response != "yes":
        logger.info("❌ Cancelled.")
        return False
    
    try:
        from cockli_batch_creator import CockliBatchCreator
        
        logger.info("")
        logger.info("="*70)
        mode = "TOR BROWSER (New IP per account)" if use_tor else "INCOGNITO FIREFOX (Same IP)"
        logger.info(f"STARTING ACCOUNT CREATION: {mode}")
        logger.info("="*70)
        logger.info("")
        
        batch = CockliBatchCreator(use_tor=use_tor, use_incognito=True, fixed_password="gdgocgu12")
        accounts = batch.create_batch_accounts(num_accounts)
        
        if not accounts:
            logger.error("")
            logger.error("="*70)
            logger.error("NO ACCOUNTS CREATED - STOPPING")
            logger.error("="*70)
            return False
        
        logger.info("")
        logger.info("="*70)
        logger.info(f"SUCCESS! CREATED {len(accounts)} ACCOUNTS")
        logger.info("="*70)
        logger.info("")
        
        created_csv = "accounts_created.csv"
        
        if not os.path.exists(created_csv):
            logger.error(f"❌ {created_csv} not found!")
            return False
        
    except Exception as e:
        logger.error(f"❌ Failed to create accounts: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Prepare to inject into Thunderbird
    print_banner("Step 4: Preparing Thunderbird")
    
    logger.info("⚠️  IMPORTANT: Please close Thunderbird completely")
    logger.info("This is required before injecting accounts.")
    logger.info("")
    
    response = input("Is Thunderbird closed? (yes/no): ").strip().lower()
    if response != "yes":
        logger.info("Please close Thunderbird and try again.")
        return False
    
    # Step 4: Inject accounts into Thunderbird
    print_banner("Step 5: Injecting Accounts into Thunderbird")
    
    try:
        from thunderbird_injector import ThunderbirdAccountInjector
        
        injector = ThunderbirdAccountInjector()
        injector.batch_add_accounts(created_csv)
        
        logger.info("✅ All accounts injected into Thunderbird!")
        
    except Exception as e:
        logger.error(f"❌ Failed to inject accounts: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 5: Done!
    print_banner("AUTOMATION COMPLETE!")
    
    logger.info(f"Summary:")
    logger.info(f"  Total accounts created: {len(accounts)}")
    logger.info(f"  Saved to: accounts_created.csv")
    logger.info(f"  Injected into Thunderbird: YES")
    logger.info(f"  Fixed password: gdgocgu12")
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Open Thunderbird")
    logger.info("  2. All accounts should appear automatically")
    logger.info("  3. Test sending/receiving email from one account")
    logger.info("")
    
    if len(accounts) > 10:
        logger.info(f"Pro tip: You have {len(accounts)} accounts!")
        logger.info("  - Create filters for auto-sorting")
        logger.info("  - Set up signatures per account")
        logger.info("  - Consider email forwarding rules")
    
    logger.info("")
    logger.info("="*70)
    logger.info("SUCCESS! All accounts are ready to use!")
    logger.info("="*70)
    logger.info("")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

