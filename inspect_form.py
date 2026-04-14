#!/usr/bin/env python3
"""
Inspect the registration form and output all field selectors
Run this to understand the actual form structure
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize driver
options = webdriver.FirefoxOptions()
options.add_argument("--private")

driver = webdriver.Firefox(options=options)

try:
    # Navigate to form
    print("\n" + "="*70)
    print("FORM INSPECTION - Finding all input fields...")
    print("="*70 + "\n")
    
    REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
    driver.get(REGISTRATION_URL)
    time.sleep(5)  # Wait for page to load
    
    # Find ALL input fields
    all_inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"\n📝 Found {len(all_inputs)} INPUT FIELDS:\n")
    
    for i, inp in enumerate(all_inputs, 1):
        field_type = inp.get_attribute('type')
        field_name = inp.get_attribute('name')
        field_id = inp.get_attribute('id')
        placeholder = inp.get_attribute('placeholder')
        value = inp.get_attribute('value')
        
        print(f"\n[{i}] Type: {field_type}")
        if field_name:
            print(f"    Name: {field_name}")
        if field_id:
            print(f"    ID: {field_id}")
        if placeholder:
            print(f"    Placeholder: {placeholder}")
        if value:
            print(f"    Value: {value}")
        
        # Show XPath options for this field
        if field_id:
            print(f"    >>> Use: By.ID, '{field_id}'")
        if field_name:
            print(f"    >>> Use: By.NAME, '{field_name}'")
        if placeholder:
            print(f"    >>> Use: By.XPATH, \"//input[@placeholder='{placeholder}']\"")
    
    # Find ALL select dropdowns
    all_selects = driver.find_elements(By.TAG_NAME, "select")
    print(f"\n\n📋 Found {len(all_selects)} SELECT DROPDOWNS:\n")
    
    for i, select in enumerate(all_selects, 1):
        select_name = select.get_attribute('name')
        select_id = select.get_attribute('id')
        
        print(f"\n[SELECT-{i}]")
        if select_name:
            print(f"    Name: {select_name}")
        if select_id:
            print(f"    ID: {select_id}")
        
        # Show options
        options_list = select.find_elements(By.TAG_NAME, "option")
        print(f"    Options: {', '.join([opt.text for opt in options_list[:5]])}")
        
        if select_id:
            print(f"    >>> Use: By.ID, '{select_id}'")
        if select_name:
            print(f"    >>> Use: By.NAME, '{select_name}'")
    
    # Find ALL radio buttons
    all_radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
    print(f"\n\n🔘 Found {len(all_radios)} RADIO BUTTONS:\n")
    
    for i, radio in enumerate(all_radios, 1):
        radio_name = radio.get_attribute('name')
        radio_value = radio.get_attribute('value')
        radio_id = radio.get_attribute('id')
        
        print(f"\n[RADIO-{i}] Name: {radio_name}")
        if radio_value:
            print(f"    Value: {radio_value}")
        if radio_id:
            print(f"    ID: {radio_id}")
        print(f"    >>> Use: By.XPATH, \"//input[@type='radio'][@value='{radio_value}']\"")
    
    # Find ALL textareas and custom components
    all_textareas = driver.find_elements(By.TAG_NAME, "textarea")
    print(f"\n\n📄 Found {len(all_textareas)} TEXTAREAS:\n")
    for i, ta in enumerate(all_textareas, 1):
        ta_name = ta.get_attribute('name')
        ta_id = ta.get_attribute('id')
        print(f"\n[TEXTAREA-{i}] Name: {ta_name}, ID: {ta_id}")
    
    print("\n" + "="*70)
    print("INSPECTION COMPLETE - Use the selectors above to identify fields")
    print("="*70 + "\n")
    
finally:
    input("Press Enter to close browser...")
    driver.quit()
