"""
Hack2Skill Batch Registration Form Filler
Automatically logs in with CSV accounts and fills registration forms
"""

import time
import random
import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage&utm_campaign=&utm_term=&utm_content="
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"
LOG_FILE = r"C:\Users\preet\Downloads\selenium\registration_log.csv"

# Sample data generators
def generate_user_data_for_email(email):
    """Generate realistic Indian user data based on email"""
    first_names = ["Arjun", "Aditya", "Naman", "Raj", "Vikram", "Rohan", "Karan", "Rishi", "Aman", "Bhavesh"]
    last_names = ["Singh", "Sharma", "Kumar", "Patel", "Gupta", "Verma", "Yadav", "Joshi", "Desai", "Nair"]
    
    streams = [
        "Computer Science Engineering",
        "Information Technology",
        "Electronics and Communication",
        "Mechanical Engineering",
        "Civil Engineering",
        "Electrical Engineering",
        "Data Science",
        "Artificial Intelligence"
    ]
    
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    dob = f"{random.randint(2004, 2007)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    whatsapp = f"+91{random.randint(6000000000, 9999999999)}"
    stream = random.choice(streams)
    
    # Convert name to lowercase for URLs
    name_for_url = full_name.lower().replace(" ", "")
    
    return {
        "full_name": full_name,
        "dob": dob,
        "gender": "Male",
        "whatsapp": whatsapp,
        "country": "India",
        "state": "Uttar Pradesh",
        "city": "Noida",
        "college_name": "Galgotias University",
        "college_state": "Uttar Pradesh",
        "college_city": "Noida",
        "degree": "B.Tech",
        "stream": stream,
        "passout_year": str(random.randint(2025, 2028)),
        "linkedin_url": f"https://linkedin.com/in/{name_for_url}",
        "gdp_url": f"https://g.dev/{name_for_url}",
        "college_id_path": r"C:\Users\preet\Downloads\selenium\idcard.jpg",
        "gdg_referral": "Yes",
        "referral_code": "QZU6HH",
        "email": email
    }

def load_accounts_from_csv():
    """Load email accounts from CSV file"""
    accounts = []
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file not found: {CSV_FILE}")
        return accounts
    
    try:
        with open(CSV_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('email'):
                    accounts.append({
                        'username': row.get('username'),
                        'email': row.get('email'),
                        'password': row.get('password')
                    })
        print(f"✅ Loaded {len(accounts)} accounts from CSV")
        return accounts
    except Exception as e:
        print(f"❌ Error reading CSV: {str(e)}")
        return accounts

def log_progress(email, status, message=""):
    """Log the registration progress to a CSV file"""
    file_exists = os.path.exists(LOG_FILE)
    
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['timestamp', 'email', 'status', 'message'])
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), email, status, message])

def signup_and_verify_otp(driver, email_account):
    """Sign up and wait for OTP verification"""
    wait = WebDriverWait(driver, 25)
    
    try:
        print(f"   📝 Signing up with {email_account['email']}...")
        
        # Navigate to signup page
        driver.get(SIGNUP_PAGE_URL)
        time.sleep(3)
        
        # Generate a full name
        first_names = ["Arjun", "Aditya", "Naman", "Raj", "Vikram", "Rohan", "Karan", "Rishi", "Aman", "Bhavesh"]
        last_names = ["Singh", "Sharma", "Kumar", "Patel", "Gupta", "Verma", "Yadav", "Joshi", "Desai", "Nair"]
        full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        # Find and fill Full Name field
        print("   ✍️  Entering Full Name...")
        fullname_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter Full Name']")))
        fullname_field.clear()
        fullname_field.send_keys(full_name)
        print(f"   ✅ Full Name: {full_name}")
        time.sleep(1)
        
        # Find and fill Email field
        print("   📧 Entering Email...")
        email_field = driver.find_element(By.XPATH, "//input[@placeholder='Enter Email']")
        email_field.clear()
        email_field.send_keys(email_account['email'])
        print(f"   ✅ Email: {email_account['email']}")
        time.sleep(1)
        
        # Click Register button
        print("   🚀 Clicking Register...")
        register_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Register')]")
        register_button.click()
        print("   ✅ Register submitted")
        time.sleep(2)
        
        # Wait for OTP page to appear
        print("   ⏱️  OTP page loading...")
        otp_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='OTP' or @placeholder='Enter OTP' or contains(@placeholder, 'OTP')]")))
        print("   ✅ OTP field found")
        
        # Wait 30 seconds for user to enter OTP
        print("   ⏳ Waiting 30 seconds for OTP entry...")
        for i in range(30, 0, -1):
            print(f"      {i} seconds remaining...", end='\r')
            time.sleep(1)
        print("      ✅ 30 seconds passed, proceeding...")
        
        # Check if OTP is filled (user has 30 seconds to fill it)
        otp_value = otp_field.get_attribute('value')
        if not otp_value or len(otp_value) == 0:
            print("   ⚠️  OTP field appears empty - user may not have entered it")
        else:
            print(f"   ✅ OTP detected: {len(otp_value)} digits")
        
        time.sleep(1)
        
        # Click Verify button
        print("   🔐 Clicking Verify...")
        verify_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify')]")
        verify_button.click()
        print("   ✅ Verify submitted")
        time.sleep(3)
        
        return True
        
    except TimeoutException as e:
        print(f"   ❌ Timeout: {str(e)}")
        return False
    except Exception as e:
        print(f"   ❌ Signup error: {str(e)}")
        return False

def fill_form(driver, data, email_account):
    """Fill the registration form with provided data"""
    wait = WebDriverWait(driver, 15)
    
    try:
        print(f"   📝 Filling registration form...")
        
        # Navigate to registration form
        driver.get(REGISTRATION_URL)
        time.sleep(3)
        
        # 1. Full Name
        print("   ✍️  Full Name...")
        full_name_fields = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='name' i], input[type='text'][placeholder*='Name' i]")
        if full_name_fields:
            full_name_fields[0].clear()
            full_name_fields[0].send_keys(data["full_name"])
            time.sleep(0.3)
        else:
            print("   ⚠️  Could not find full name field")
        
        # 2. Date of Birth
        print("   📅 DOB...")
        dob_fields = driver.find_elements(By.CSS_SELECTOR, "input[type='date']")
        if dob_fields:
            dob_fields[0].send_keys(data["dob"].replace("-", ""))
            time.sleep(0.3)
        
        # 3. Gender (Dropdown)
        # 3. Gender
        print("   👤 Gender...")
        selects = driver.find_elements(By.TAG_NAME, "select")
        if selects:
            try:
                Select(selects[0]).select_by_visible_text(data["gender"])
            except:
                pass
            time.sleep(0.3)
        
        # 4. WhatsApp Number
        print("   📱 WhatsApp...")
        phone_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='tel']")
        if phone_inputs:
            phone_inputs[0].clear()
            phone_inputs[0].send_keys(data["whatsapp"])
            time.sleep(0.3)
        
        # 5. Alternate Number - Same as WhatsApp
        print("   ✅ Alternate same...")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkboxes:
            checkboxes[0].click()
            time.sleep(0.3)
        
        # 6. Country
        print("   🌍 Location...")
        country_selects = driver.find_elements(By.TAG_NAME, "select")
        if len(country_selects) > 0:
            try:
                Select(country_selects[0]).select_by_visible_text(data["country"])
            except:
                pass
            time.sleep(0.3)
        
        # 7. State/Province
        print("   📍 Location cont...")
        state_inputs = driver.find_elements(By.CSS_SELECTOR, "[placeholder*='state' i], [placeholder*='State' i]")
        if state_inputs:
            state_inputs[0].send_keys(data["state"])
            time.sleep(0.2)
            options = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            if options:
                options[0].click()
            time.sleep(0.3)
        
        # 8. City
        print("   🏙️  City...")
        city_inputs = driver.find_elements(By.CSS_SELECTOR, "[placeholder*='City' i], [placeholder*='city' i]")
        if city_inputs:
            city_inputs[0].send_keys(data["city"])
            time.sleep(0.2)
            options = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            if options:
                options[0].click()
            time.sleep(0.3)
        
        # 9. Occupation - Click "College Student"
        print("   🎓 College Student...")
        all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'College Student')]")
        if all_elements:
            all_elements[0].click()
            time.sleep(1)
        
        # 10. College Name
        print("   🏫 College info...")
        college_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='College' i]")
        if college_inputs:
            college_inputs[0].clear()
            college_inputs[0].send_keys(data["college_name"])
            time.sleep(0.3)
        
        # 11. College Country
        print("   🌍 College location...")
        selects = driver.find_elements(By.TAG_NAME, "select")
        if len(selects) >= 2:
            try:
                Select(selects[1]).select_by_visible_text(data["country"])
            except:
                pass
            time.sleep(0.3)
        
        # 12. College State
        print("   📍 College location cont...")
        state_inputs = driver.find_elements(By.CSS_SELECTOR, "[placeholder*='state' i], [placeholder*='State' i]")
        if len(state_inputs) > 1:
            state_inputs[1].send_keys(data["college_state"])
            time.sleep(0.2)
            options = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            if options:
                options[0].click()
            time.sleep(0.3)
        
        # 13. College City
        print("   🏙️  College location cont...")
        city_inputs = driver.find_elements(By.CSS_SELECTOR, "[placeholder*='City' i], [placeholder*='city' i]")
        if len(city_inputs) > 1:
            city_inputs[1].send_keys(data["college_city"])
            time.sleep(0.2)
            options = driver.find_elements(By.CSS_SELECTOR, "[role='option']")
            if options:
                options[0].click()
            time.sleep(0.3)
        
        # 14-16. Degree, Stream, Passout Year
        print("   📚 College details...")
        time.sleep(0.5)
        
        # 17. LinkedIn URL
        print("   🔗 LinkedIn...")
        linkedin_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='Linkedin' i]")
        if linkedin_inputs:
            linkedin_inputs[0].clear()
            linkedin_inputs[0].send_keys(data["linkedin_url"])
            time.sleep(0.3)
        
        # 18. College ID Card Upload
        print("   📄 College ID...")
        file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
        if file_inputs:
            file_inputs[0].send_keys(data["college_id_path"])
            time.sleep(1)
        
        # 19. GDP Public Profile Link
        print("   🔗 GDP Link...")
        gdp_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='g.dev' i]")
        if gdp_inputs:
            gdp_inputs[0].clear()
            gdp_inputs[0].send_keys(data["gdp_url"])
            time.sleep(0.3)
        
        # 20. GDG Referral Question
        print("   ❓ GDG Referral...")
        radio_buttons = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
        for radio in radio_buttons:
            try:
                if radio.get_attribute('value') == 'Yes':
                    if not radio.is_selected():
                        radio.click()
                    break
            except:
                pass
        time.sleep(1)
        
        # 21. Referral Code (appears when "Yes" is selected)
        print("   🔐 Referral Code...")
        referral_inputs = driver.find_elements(By.CSS_SELECTOR, "input[placeholder*='referral' i]")
        if referral_inputs:
            referral_inputs[0].clear()
            referral_inputs[0].send_keys(data["referral_code"])
            time.sleep(0.3)
        
        # 22. Terms & Conditions Checkbox
        print("   ✅ Terms...")
        all_checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if len(all_checkboxes) > 0:
            # Find the Terms & Conditions checkbox (usually the last or marked one)
            for cb in all_checkboxes:
                try:
                    if not cb.is_selected():
                        cb.click()
                        break
                except:
                    pass
        time.sleep(0.5)
        
        # 23. Submit Form
        print("   🚀 Submitting...")
        submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Register')]")
        if submit_buttons:
            submit_buttons[0].click()
            time.sleep(3)
            print(f"   ✅ Form submitted!")
            return True
        else:
            print(f"   ⚠️  Submit button not found")
            return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Form fill error: {error_msg}")
        return False

def main():
    """Main execution function"""
    # Load accounts
    accounts = load_accounts_from_csv()
    if not accounts:
        print("❌ No accounts to process!")
        return
    
    print(f"\n🚀 Starting batch registration for {len(accounts)} accounts...")
    print("=" * 60)
    
    # Initialize Firefox driver
    print("🔧 Initializing Firefox WebDriver...")
    options = webdriver.FirefoxOptions()
    # Uncomment to run headless (invisible)
    # options.add_argument("--headless")
    
    driver = webdriver.Firefox(options=options)
    
    completed = 0
    failed = 0
    
    try:
        for idx, account in enumerate(accounts, 1):
            print(f"\n\n{'='*60}")
            print(f"[{idx}/{len(accounts)}] Account: {account['email']}")
            print(f"{'='*60}")
            
            # Generate user data for this email
            user_data = generate_user_data_for_email(account['email'])
            user_data['email'] = account['email']
            
            # Step 1: Sign up with OTP verification
            signup_success = signup_and_verify_otp(driver, account)
            if not signup_success:
                print(f"❌ SIGNUP FAILED for {account['email']}")
                log_progress(account['email'], "FAILED", "Signup failed")
                failed += 1
                continue
            
            time.sleep(2)
            
            # Step 2: Fill form
            success = fill_form(driver, user_data, account)
            if success:
                completed += 1
                log_progress(account['email'], "SUCCESS", f"Registered as {user_data['full_name']}")
            else:
                failed += 1
                log_progress(account['email'], "PARTIAL", "Form fill incomplete")
            
            # Wait between accounts
            if idx < len(accounts):
                print(f"\n⏳ Waiting 5 seconds before next account...")
                time.sleep(5)
        
    finally:
        driver.quit()
    
    # Summary
    print(f"\n\n{'='*60}")
    print(f"✅ BATCH PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Total Accounts: {len(accounts)}")
    print(f"✅ Successful: {completed}")
    print(f"❌ Failed: {failed}")
    print(f"📋 Log File: {LOG_FILE}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
