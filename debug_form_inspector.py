"""
Debug script to inspect the actual form structure and help fix field detection
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage"
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"

def inspect_form(driver, url, title):
    """Inspect and print form structure"""
    print(f"\n{'='*80}")
    print(f"INSPECTING: {title}")
    print(f"URL: {url}")
    print(f"{'='*80}\n")
    
    driver.get(url)
    time.sleep(4)
    
    # Get all input fields
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Found {len(inputs)} input elements:\n")
    
    for idx, inp in enumerate(inputs, 1):
        input_type = inp.get_attribute("type") or "text"
        input_id = inp.get_attribute("id") or "[NO ID]"
        input_name = inp.get_attribute("name") or "[NO NAME]"
        input_placeholder = inp.get_attribute("placeholder") or "[NO PLACEHOLDER]"
        input_value = inp.get_attribute("value") or "[EMPTY]"
        
        # Try to find associated label
        label_text = "[NO LABEL]"
        try:
            if input_id and input_id != "[NO ID]":
                label = driver.find_element(By.XPATH, f"//label[@for='{input_id}']")
                label_text = label.text
        except:
            pass
        
        print(f"[{idx}] TYPE={input_type:8} | LABEL: {label_text:25} | ID: {input_id:20}")
        print(f"     NAME: {input_name:25} | PLACEHOLDER: {input_placeholder}")
        print()
    
    # Get all labels
    labels = driver.find_elements(By.TAG_NAME, "label")
    print(f"\n--- LABELS ({len(labels)} found) ---\n")
    for idx, label in enumerate(labels, 1):
        label_text = label.text
        label_for = label.get_attribute("for") or "[NO FOR]"
        print(f"[{idx}] FOR={label_for:20} TEXT: {label_text}")
    
    # Get all selects
    selects = driver.find_elements(By.TAG_NAME, "select")
    if selects:
        print(f"\n--- SELECT DROPDOWNS ({len(selects)} found) ---\n")
        for idx, sel in enumerate(selects, 1):
            sel_id = sel.get_attribute("id") or "[NO ID]"
            sel_name = sel.get_attribute("name") or "[NO NAME]"
            print(f"[{idx}] ID={sel_id:20} NAME={sel_name}")
    
    # Get all buttons
    buttons = driver.find_elements(By.TAG_NAME, "button")
    print(f"\n--- BUTTONS ({len(buttons)} found) ---\n")
    for idx, btn in enumerate(buttons, 1):
        btn_text = btn.text.strip() or "[NO TEXT]"
        btn_class = btn.get_attribute("class") or "[NO CLASS]"
        btn_type = btn.get_attribute("type") or "button"
        print(f"[{idx}] TYPE={btn_type:8} TEXT: {btn_text:30} CLASS: {btn_class}")

def main():
    options = webdriver.FirefoxOptions()
    # options.add_argument("--headless")  # Comment to see browser
    driver = webdriver.Firefox(options=options)
    
    try:
        # Inspect signup page
        inspect_form(driver, SIGNUP_PAGE_URL, "SIGNUP PAGE")
        
        input("\nPress ENTER to inspect registration page...")
        
        # Inspect registration page
        inspect_form(driver, REGISTRATION_URL, "REGISTRATION PAGE")
        
        print("\n" + "="*80)
        print("INSPECTION COMPLETE")
        print("="*80)
        print("\nUse this information to update find_input_by_label_or_placeholder()")
        print("Keywords to search for should match the LABEL, PLACEHOLDER, NAME, or ID found above")
        
        input("\nPress ENTER to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
