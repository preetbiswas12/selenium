#!/usr/bin/env python3
"""
QUICK REFERENCE - Run inspect_form.py FIRST to get actual selectors
Then update THIS script with correct field identifiers

For now, using simplified selectors...
"""

# After running inspect_form.py, you'll see output like:
# [1] Type: text, Placeholder: 'Full Name', >>> Use: By.XPATH, "//input[@placeholder='Full Name']"
# [2] Type: email, Name: 'email', >>> Use: By.NAME, 'email'
# etc.

# COPY THE CORRECT SELECTORS FROM INSPECT OUTPUT AND PASTE THEM HERE:

FIELD_SELECTORS = {
    "full_name": {
        "type": "xpath",
        "value": "//input[@placeholder='Full Name' or @placeholder='Enter Full Name']",
        "fill_value": "Aditya Kumar"  # Will be auto-generated
    },
    "email": {
        "type": "xpath",
        "value": "//input[@placeholder='Email' or @type='email']",
        "fill_value": "user@cock.li"  # Will be from CSV
    },
    "whatsapp": {
        "type": "xpath",
        "value": "//input[@placeholder='WhatsApp' or @type='tel']",
        "fill_value": "+919876543210"
    },
    "dob": {
        "type": "xpath",
        "value": "//input[@type='date']",
        "fill_value": "1999-05-15"
    },
    "gender": {
        "type": "xpath",
        "value": "//select[contains(@name, 'gender') or contains(@id, 'gender')]",
        "fill_value": "Male"
    },
    "country": {
        "type": "xpath",
        "value": "//input[contains(@placeholder, 'Country')]",
        "fill_value": "India"
    },
    "state": {
        "type": "xpath",
        "value": "//input[contains(@placeholder, 'State')]",
        "fill_value": "Uttar Pradesh"
    },
    "city": {
        "type": "xpath",
        "value": "//input[contains(@placeholder, 'City')]",
        "fill_value": "Greater Noida"
    },
}

# INSTRUCTIONS:
# 1. Run: python inspect_form.py
# 2. Screenshot or copy the output
# 3. Reply with the ACTUAL selectors for each field
# 4. I'll update the main script with correct selectors

print(__doc__)
