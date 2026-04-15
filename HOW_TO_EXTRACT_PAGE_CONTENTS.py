"""
QUICK REFERENCE: HOW TO EXTRACT & USE PAGE STRUCTURE

There are 4 ways to find input fields in Selenium:
"""

# ═══════════════════════════════════════════════════════════════
# METHOD 1: GET BY ID (if IDs exist)
# ═══════════════════════════════════════════════════════════════

from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Firefox()
driver.get("https://vision.hack2skill.com/event/solution-challenge-2026/registration")

# If you know the ID:
element = driver.find_element(By.ID, "whatsapp_field")
element.send_keys("+919876543210")

print("✓ Found by ID")


# ═══════════════════════════════════════════════════════════════
# METHOD 2: GET BY NAME (if names exist)
# ═══════════════════════════════════════════════════════════════

# If you know the name:
element = driver.find_element(By.NAME, "whatsapp_number")
element.send_keys("+919876543210")

print("✓ Found by NAME")


# ═══════════════════════════════════════════════════════════════
# METHOD 3: GET BY XPATH (most flexible)
# ═══════════════════════════════════════════════════════════════

# If ID or name don't work, use XPath:
element = driver.find_element(By.XPATH, "//input[@placeholder='WhatsApp']")
element.send_keys("+919876543210")

print("✓ Found by XPATH")

# Or by label text:
element = driver.find_element(By.XPATH, "//label[text()='WhatsApp']/following-sibling::input")
element.send_keys("+919876543210")

print("✓ Found by XPATH + Label")


# ═══════════════════════════════════════════════════════════════
# METHOD 4: GET BY POSITION (what we use in simple_working.py)
# ═══════════════════════════════════════════════════════════════

# Get ALL inputs in order:
all_inputs = driver.find_elements(By.TAG_NAME, "input")

# Fill by position (0-indexed):
all_inputs[0].send_keys("Full Name")      # Position 0
all_inputs[1].send_keys("email@test.com") # Position 1
all_inputs[2].send_keys("+919876543210")  # Position 2 = WhatsApp
all_inputs[3].send_keys("2005-05-28")     # Position 3 = DOB

print("✓ Found by POSITION")


# ═══════════════════════════════════════════════════════════════
# HOW TO EXTRACT INPUT ATTRIBUTES
# ═══════════════════════════════════════════════════════════════

# Get the ID:
input_id = element.get_attribute("id")
print(f"ID: {input_id}")  # e.g., "whatsapp_429469a30a85acee6c3069c28883"

# Get the name:
input_name = element.get_attribute("name")
print(f"NAME: {input_name}")  # e.g., "whatsapp_number"

# Get the placeholder:
input_placeholder = element.get_attribute("placeholder")
print(f"PLACEHOLDER: {input_placeholder}")  # e.g., "WhatsApp"

# Get the type:
input_type = element.get_attribute("type")
print(f"TYPE: {input_type}")  # e.g., "text", "email", "date"

# Get the class:
input_class = element.get_attribute("class")
print(f"CLASS: {input_class}")  # e.g., "form-control input-field"


# ═══════════════════════════════════════════════════════════════
# HOW TO INSPECT A PAGE IN YOUR BROWSER (Developer Tools)
# ═══════════════════════════════════════════════════════════════

"""
1. Open Firefox
2. Navigate to: https://vision.hack2skill.com/event/solution-challenge-2026/registration
3. Press F12 to open Developer Tools
4. Press Ctrl+Shift+C to enable Element Inspector
5. Click on any form field to see its HTML:

   <input 
     type="text" 
     id="whatsapp_429469a30a85acee6c3069c28883"
     name="whatsapp_number"
     placeholder="WhatsApp Number"
     class="form-control"
   />

6. Copy the attributes you need (ID, name, placeholder, xpath)

You can then use these in Selenium scripts:
   element = driver.find_element(By.ID, "whatsapp_429469a30a85acee6c3069c28883")
"""


# ═══════════════════════════════════════════════════════════════
# WHAT THE EXTRACTION SCRIPT DOES
# ═══════════════════════════════════════════════════════════════

"""
Run: python extract_page_contents.py

This will:
1. Open Firefox
2. Navigate to signup page
3. Extract ALL inputs, buttons, labels
4. Fill signup and submit
5. Extract OTP page contents
6. Navigate to registration form
7. Extract ALL form fields with:
   - ID
   - Name  
   - Placeholder
   - Type
   - Position number
   - Associated label text
8. Save everything to: page_structure_analysis.txt

Then you just open the file and see:
   [1] TYPE: text | PLACEHOLDER: Full Name | ID: full_name_xyz
   [2] TYPE: email | PLACEHOLDER: Email | ID: email_field_abc
   [3] TYPE: text | PLACEHOLDER: WhatsApp | ID: whatsapp_429469a30a85acee6c3069c28883
   ...etc

This tells you:
- Position 3 is WhatsApp (use: all_inputs[3])
- ID is "whatsapp_429469a30a85acee6c3069c28883"
- Name is (shown in output)
- Placeholder is "WhatsApp"

You can then choose ANY method to fill:
   all_inputs[3].send_keys(value)  # By position
   element = driver.find_element(By.ID, "whatsapp_429469a30a85acee6c3069c28883")
   element = driver.find_element(By.XPATH, "//input[@placeholder='WhatsApp']")
"""


# ═══════════════════════════════════════════════════════════════
# EXAMPLE: Using Both Methods
# ═══════════════════════════════════════════════════════════════

# Once you run extract_page_contents.py and read the output:

# Option A: Get by position (simple, always works)
all_inputs = driver.find_elements(By.TAG_NAME, "input")
all_inputs[2].send_keys("+919876543210")  # WhatsApp at position 2

# Option B: Get by ID (requires exact ID from extraction)
element = driver.find_element(By.ID, "whatsapp_429469a30a85acee6c3069c28883")
element.send_keys("+919876543210")

# Option C: Get by placeholder (if placeholder is consistent)
element = driver.find_element(By.XPATH, "//input[@placeholder='WhatsApp Number']")
element.send_keys("+919876543210")

# All three do the same thing - pick whichever works!
