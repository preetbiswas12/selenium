# Form field selectors for Hack2skill Registration
FORM_SELECTORS = {
    # ==================== SIGNUP SECTION ====================
    "signup_name_input": "input[placeholder*='Full Name'], input[name*='name'], input[id*='name']",
    "signup_email_input": "input[type='email'], input[name*='email'], input[id*='email']",
    "register_now_btn": "button:contains('Register Now'), button:contains('REGISTER'), input[value='Register Now']",
    
    # ==================== OTP VERIFICATION ====================
    "otp_input": "input[name*='otp'], input[id*='otp'], input[placeholder*='OTP']",
    "verify_otp_btn": "button:contains('Verify'), button:contains('Submit'), button:contains('Signup')",
    
    # ==================== REGISTRATION FORM ====================
    # Personal Information
    "full_name": "input[name*='fullName'], input[name*='full_name'], input[placeholder*='Full Name']",
    "email": "input[type='email']",
    "whatsapp_number": "input[name*='whatsapp'], input[placeholder*='WhatsApp']",
    "date_of_birth": "input[type='date'], input[name*='dob'], input[name*='birth']",
    "gender": "select[name*='gender'], select[id*='gender']",
    "alternate_number": "input[name*='alternate'], input[placeholder*='Alternate']",
    "country": "select[name*='country'], input[name*='country']",
    "state_province": "input[name*='state'], input[name*='province'], input[placeholder*='State']",
    "city": "input[name*='city']",
    
    # Education & Occupation
    "occupation": "select[name*='occupation'], input[name*='occupation']",
    "college_name": "input[name*='college'], input[placeholder*='college']",
    "college_country": "select[name*='collegeCountry'], input[name*='collegeCountry']",
    "college_state": "input[name*='collegeState'], input[placeholder*='College State']",
    "college_city": "input[name*='collegeCity'], input[placeholder*='College City']",
    "degree": "input[name*='degree'], input[placeholder*='Degree']",
    "specialization": "input[name*='specialization'], input[name*='stream'], textarea[name*='specialization']",
    "passout_year": "select[name*='passout'], select[name*='year']",
    
    # Profile Links & Documents
    "linkedin_url": "input[name*='linkedin'], input[type='url'][placeholder*='linkedin']",
    "college_id_file": "input[type='file'][name*='collegeId'], input[type='file'][name*='college_id']",
    "gdp_profile_link": "input[name*='gdp'], input[placeholder*='g.dev']",
    
    # Referral & Consent
    "referral_yes_radio": "input[type='radio'][value='yes'][name*='referral']",
    "referral_no_radio": "input[type='radio'][value='no'][name*='referral']",
    "referral_code_input": "input[name*='referralCode'], input[placeholder*='referral code']",
    "terms_checkbox": "input[type='checkbox'][name*='terms']",
    "consent_checkbox": "input[type='checkbox'][name*='consent']",
    
    # Submit Button
    "register_btn": "button:contains('Register Now'), button[type='submit']",
    "submit_btn": "button:contains('Register'), button[type='submit']:last",
}

# Email configuration
EMAIL_CONFIG = {
    "email_provider": "cock.li",
    "imap_server": "mail.cock.li",
    "imap_port": 993,
    "thunderbird_profile": "C:\\Users\\preet\\AppData\\Roaming\\Thunderbird\\Profiles\\",
}

# CAPTCHA Handling
CAPTCHA_CONFIG = {
    "method": "manual",  # Options: "manual", "2captcha", "capsolver"
    "manual_pause_time": 30,  # Seconds to wait for manual solve
    
    # For 2Captcha API
    "2captcha_api_key": "",  # Get from https://2captcha.com/
    
    # For CapSolver API
    "capsolver_api_key": "",  # Get from https://www.capsolver.com/
    
    # Timeout settings
    "captcha_timeout": 120,  # Total time to wait for CAPTCHA solve (seconds)
}

# Selenium settings
SELENIUM_CONFIG = {
    "headless": False,  # Set to True to run in background
    "stealth": True,  # Hide bot detection
    "implicit_wait": 10,
    "page_load_timeout": 30,
    "random_delay_min": 2,  # seconds
    "random_delay_max": 5,
}

# URLs
URLS = {
    "registration": "https://vision.hack2skill.com/event/solution-challenge-2026/registration?isExternalLinkRedirection=true",
}

# Google Sheets
SHEET_CONFIG = {
    "spreadsheet_name": "Hack2skill_Registrations",  # or ID
    "worksheet_name": "Sheet1",
}
