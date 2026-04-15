"""
Diagnostic script to inspect the actual OTP verification page
Run this to see what buttons and fields exist
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

# Config
SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"

def main():
    # Load first account
    with open(CSV_FILE, 'r') as f:
        reader = csv.DictReader(f)
        account = next(reader)
    
    print("="*70)
    print(f"Testing OTP with: {account['email']}")
    print("="*70)
    
    driver = webdriver.Firefox()
    try:
        # Go to signup
        print("\n1. Navigating to signup...")
        driver.get(SIGNUP_PAGE_URL)
        time.sleep(3)
        
        # Fill and submit
        print("2. Filling signup form...")
        name_field = driver.find_element(By.XPATH, "//input[@type='text']")
        name_field.send_keys("Test User")
        time.sleep(0.5)
        
        email_field = driver.find_element(By.XPATH, "//input[@type='email']")
        email_field.send_keys(account['email'])
        time.sleep(0.5)
        
        # Click Register
        register_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        register_btn.click()
        print("   ✓ Register clicked")
        time.sleep(3)
        
        # Wait for OTP page
        print("3. Waiting for OTP page to load...")
        wait = WebDriverWait(driver, 30)
        
        # Wait for any OTP-related field
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text']")))
            print("   ✓ OTP page loaded")
        except:
            print("   ✗ OTP page didn't load")
            print(f"   Current URL: {driver.current_url}")
            print(f"   Page title: {driver.title}")
        
        time.sleep(1)
        
        # Inspect all elements on the page
        print("\n" + "="*70)
        print("PAGE INSPECTION - ALL BUTTONS")
        print("="*70)
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:\n")
        for idx, btn in enumerate(buttons, 1):
            text = btn.text.strip()
            btn_type = btn.get_attribute("type") or "button"
            disabled = btn.get_attribute("disabled")
            print(f"[{idx}] Type: {btn_type:8} | Text: '{text}' | Disabled: {disabled}")
        
        # Inspect all input fields
        print("\n" + "="*70)
        print("PAGE INSPECTION - ALL INPUT FIELDS")
        print("="*70)
        
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Found {len(inputs)} input fields:\n")
        for idx, inp in enumerate(inputs, 1):
            inp_type = inp.get_attribute("type") or "text"
            placeholder = inp.get_attribute("placeholder") or "[NO PLACEHOLDER]"
            inp_id = inp.get_attribute("id") or "[NO ID]"
            inp_name = inp.get_attribute("name") or "[NO NAME]"
            print(f"[{idx}] Type: {inp_type:10} | ID: {inp_id:20}")
            print(f"     Placeholder: {placeholder}")
            print(f"     Name: {inp_name}\n")
        
        # Inspect all text content
        print("\n" + "="*70)
        print("PAGE TEXT CONTENT")
        print("="*70)
        body_text = driver.find_element(By.TAG_NAME, "body").text
        print(body_text[:500])
        
        # WAIT FOR USER
        print("\n" + "="*70)
        print("⏳ MANUAL STEP: Enter OTP in the browser window above")
        print("   Once you've entered it, press ENTER here...")
        print("="*70)
        input()
        
        # Check what OTP field looks like after user enters it
        print("\n" + "="*70)
        print("AFTER OTP ENTRY - BUTTON INSPECTION")
        print("="*70)
        
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Found {len(buttons)} buttons:\n")
        for idx, btn in enumerate(buttons, 1):
            text = btn.text.strip()
            btn_type = btn.get_attribute("type") or "button"
            disabled = btn.get_attribute("disabled")
            print(f"[{idx}] Type: {btn_type:8} | Text: '{text}' | Disabled: {disabled}")
        
        # Show correct selector
        if buttons:
            verify_btn = buttons[0]  # Usually first/second button
            print(f"\n✓ VERIFY BUTTON FOUND: '{verify_btn.text}'")
            print(f"  Exact selector: //button[text()='{verify_btn.text}']")
            print(f"  Contains selector: //button[contains(text(), '{verify_btn.text[:10]}')]")
        
        print("\nPress ENTER to close browser...")
        input()
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
