"""
Manual GeckoDriver Setup
Downloads and installs GeckoDriver manually (more reliable than auto-installer)
"""

import os
import sys
import urllib.request
import zipfile
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

print("\n" + "="*70)
print("  GECKODRIVER MANUAL SETUP")
print("="*70 + "\n")

# Create webdrivers folder
webdrivers_dir = r"C:\webdrivers"
os.makedirs(webdrivers_dir, exist_ok=True)
logger.info(f"WebDrivers folder: {webdrivers_dir}")

# Check if already exists
geckodriver_path = os.path.join(webdrivers_dir, "geckodriver.exe")
if os.path.exists(geckodriver_path):
    logger.info(f"✓ GeckoDriver already exists: {geckodriver_path}")
    print("="*70)
    sys.exit(0)

print("\n[OPTION 1] Download Manually (Recommended)\n")
print("1. Go to: https://github.com/mozilla/geckodriver/releases")
print("2. Find the latest 'geckodriver-v*-win64.zip' (not win32)")
print("   These are typical versions:")
print("   - https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-win64.zip")
print("   - https://github.com/mozilla/geckodriver/releases/download/v0.33.3/geckodriver-v0.33.3-win64.zip")
print("3. Download the ZIP file")
print("4. Extract 'geckodriver.exe'")
print("5. Move to: C:\\webdrivers\\")
print("")

print("[OPTION 2] Use Alternative Download\n")
try:
    # Try alternative URL
    url = "https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-win64.zip"
    zip_path = os.path.join(webdrivers_dir, "geckodriver.zip")
    
    logger.info("Downloading GeckoDriver from alternative source...")
    logger.info(f"URL: {url}")
    
    urllib.request.urlretrieve(url, zip_path)
    logger.info(f"✓ Downloaded to: {zip_path}")
    
    logger.info("Extracting...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(webdrivers_dir)
    
    logger.info(f"✓ Extracted to: {webdrivers_dir}")
    
    # Clean up zip
    os.remove(zip_path)
    logger.info("✓ Cleanup complete")
    
    # Verify
    if os.path.exists(geckodriver_path):
        logger.info(f"✓ GeckoDriver ready: {geckodriver_path}")
        print("\n" + "="*70)
        logger.info("✓ SUCCESS! GeckoDriver installed.")
        print("="*70)
        sys.exit(0)
    else:
        raise FileNotFoundError("geckodriver.exe not found after extraction")

except Exception as e:
    logger.error(f"✗ Download failed: {e}")
    logger.error("\nManual Solution:")
    logger.error("1. Go to: https://github.com/mozilla/geckodriver/releases")
    logger.error("2. Download: geckodriver-v0.34.0-win64.zip (or latest)")
    logger.error("3. Extract to: C:\\webdrivers\\")
    logger.error("4. Run again: python run_complete_automation.py")
    print("\n" + "="*70)
    sys.exit(1)
