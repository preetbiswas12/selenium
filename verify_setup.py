"""
Quick verification script
Checks if all dependencies are installed and configured correctly
"""

import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("  DEPENDENCY CHECK")
print("="*70 + "\n")

# Check 1: Python version
print("[1/5] Checking Python...")
try:
    import sys
    version = sys.version_info
    logger.info(f"✓ Python {version.major}.{version.minor}.{version.micro}")
except:
    logger.error("✗ Python not found")
    sys.exit(1)

# Check 2: Selenium
print("\n[2/5] Checking Selenium...")
try:
    import selenium
    logger.info(f"✓ Selenium {selenium.__version__}")
except ImportError:
    logger.error("✗ Selenium not installed")
    logger.error("  Fix: pip install selenium")
    sys.exit(1)

# Check 3: GeckoDriver
print("\n[3/5] Checking GeckoDriver...")
geckodriver_found = False

# Check if exists in standard location
if os.path.exists(r"C:\webdrivers\geckodriver.exe"):
    logger.info("✓ GeckoDriver found at C:\\webdrivers\\geckodriver.exe")
    geckodriver_found = True
else:
    try:
        import geckodriver_autoinstaller
        logger.info("✓ geckodriver-autoinstaller found")
        logger.info("  (Will auto-download on first use)")
        geckodriver_found = True
    except ImportError:
        logger.warning("⚠ GeckoDriver not yet installed")
        logger.info("  Fix options:")
        logger.info("  1. Run: python setup_geckodriver.py")
        logger.info("  2. Or: pip install geckodriver-autoinstaller")
        logger.info("  3. Or: Download from https://github.com/mozilla/geckodriver/releases")

# Check 4: Tor Browser
print("\n[4/5] Checking Tor Browser...")
tor_paths = [
    r"C:\Users\preet\OneDrive\Documents\Tor Browser\Browser\firefox.exe",
    r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
    r"C:\Program Files\Tor Browser\Browser\firefox.exe",
    r"C:\Users\preet\Desktop\Tor Browser\firefox.exe",
    r"C:\Users\preet\Downloads\Tor Browser\firefox.exe",
]

tor_found = False
for path in tor_paths:
    if os.path.exists(path):
        logger.info(f"✓ Tor Browser found: {path}")
        tor_found = True
        break

if not tor_found:
    logger.warning("⚠ Tor Browser not found in default locations")
    logger.info("  Fix: Download from https://www.torproject.org/download")
    logger.info("  Or: Install to C:\\Program Files\\Tor Browser")

# Check 5: Thunderbird
print("\n[5/5] Checking Thunderbird...")
tb_paths = [
    r"C:\Program Files\Mozilla Thunderbird\thunderbird.exe",
    r"C:\Program Files (x86)\Mozilla Thunderbird\thunderbird.exe",
]

tb_found = False
for path in tb_paths:
    if os.path.exists(path):
        logger.info(f"✓ Thunderbird found: {path}")
        tb_found = True
        break

if not tb_found:
    logger.warning("⚠ Thunderbird not found in default locations")
    logger.info("  Fix: Download from https://www.thunderbird.net")

# Summary
print("\n" + "="*70)
if tor_found and tb_found:
    if geckodriver_found:
        logger.info("✓ ALL CHECKS PASSED - Ready to run!")
        print("="*70)
        print("\nNext step:")
        print("  python run_complete_automation.py")
        sys.exit(0)
    else:
        logger.warning("⚠ Missing GeckoDriver (see above)")
        print("="*70)
        print("\nFix:")
        print("  python setup_geckodriver.py")
        sys.exit(1)
else:
    logger.warning("⚠ Some components missing (see above)")
    print("="*70)
    print("\nFix the missing components and try again")
    sys.exit(1)
