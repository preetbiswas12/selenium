# CLEAN: Registration Form Filling Function
# This is the properly synchronized version for Hack2Skill registration

def fill_registration_form(driver: webdriver.Firefox, account: Dict) -> bool:
    """
    Properly synchronized registration form filling with:
    - Structured sections (Personal, Location, College, Profiles, Terms)
    - Proper waits between sections (1s between major sections)
    - Proper dropdown handling (clear, type, wait, click)
    - Error tracking and retry logic
    """
    print_step(4, "════════════════════════════════════════════════════════════════")
    print_step(4, "REGISTRATION FORM FILLING - 20 AUTO-FILL FIELDS")
    print_step(4, "════════════════════════════════════════════════════════════════")
    
    MAX_RETRIES = 2
    retry_count = 0
    fields_filled = {}
    fields_not_found = []
    
    while retry_count < MAX_RETRIES:
        print_step(4, f"\n┌─ ATTEMPT {retry_count + 1}/{MAX_RETRIES} ─────────────────────────────────────┐", True)
        
        try:
            wait = WebDriverWait(driver, TIMEOUT_ELEMENT)
            
            # Load the registration form
            print_step(4, "Loading registration form...", True)
            driver.get(REGISTRATION_URL)
            time.sleep(3)
            
            # Wait for form to be fully interactive
            try:
                wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
            except TimeoutException:
                print_warning("Form timeout, retrying page load...", True)
                retry_count += 1
                time.sleep(2)
                continue
            
            time.sleep(2)
            remove_blocking_overlays(driver)
            print_success("Form ready", True)
            
            # ════════════════════════════════════════════════════════════════════
            # SECTION 1: PERSONAL INFORMATION (5 fields)
            # ════════════════════════════════════════════════════════════════════
            section = "PERSONAL INFO"
            print_step(4, f"\n├─ {section}", True)
            time.sleep(0.8)
            
            # Name & Email: Pre-filled from signup (SKIP)
            print_step(4, "  1. Full Name: Pre-filled from signup", True)
            print_step(4, "  2. Email: Pre-filled & disabled", True)
            fields_filled["FullName"] = "pre-filled"
            fields_filled["Email"] = "pre-filled"
            time.sleep(0.3)
            
            # WhatsApp Number
            print_step(4, "  3. WhatsApp field", True)
            whatsapp = find_input_by_label_or_placeholder(driver, ["whatsapp", "phone", "+91"], "WhatsApp", verbose=False)
            if whatsapp:
                safe_fill_field(driver, whatsapp, "+919876543210", "WhatsApp")
                fields_filled["WhatsApp"] = "+919876543210"
            else:
                fields_not_found.append("WhatsApp")
            time.sleep(0.5)
            
            # Alternate Number Checkbox
            print_step(4, "  4. Alternate Number checkbox", True)
            try:
                checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                if checkboxes:
                    if not checkboxes[0].is_selected():
                        checkboxes[0].click()
                    fields_filled["AltNumber"] = "checked"
                    print_success("    ✓ Checked", True)
            except:
                fields_not_found.append("AltNumber")
            time.sleep(0.5)
            
            # Date of Birth (2004-2007)
            print_step(4, "  5. Date of Birth field", True)
            try:
                dob_fields = driver.find_elements(By.XPATH, "//input[@type='date']")
                if dob_fields:
                    year = random.randint(2004, 2007)
                    month = random.randint(1, 12)
                    day = random.randint(1, 28)
                    dob = f"{year:04d}-{month:02d}-{day:02d}"
                    dob_fields[0].send_keys(dob)
                    fields_filled["DOB"] = dob
                    print_success(f"    ✓ {dob} (age {2026-year})", True)
            except:
                fields_not_found.append("DOB")
            time.sleep(0.5)
            
            # Gender (Male/Female random)
            print_step(4, "  6. Gender field", True)
            gender = random.choice(["Male", "Female"])
            try:
                # Try select first
                selects = driver.find_elements(By.XPATH, "//select")
                if selects:
                    Select(selects[0]).select_by_visible_text(gender)
                    fields_filled["Gender"] = gender
                    print_success(f"    ✓ {gender} (select)", True)
                else:
                    # Try radio
                    radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                    for radio in radios:
                        if gender.lower() in (radio.get_attribute('value') or "").lower():
                            radio.click()
                            fields_filled["Gender"] = gender
                            print_success(f"    ✓ {gender} (radio)", True)
                            break
            except:
                fields_not_found.append("Gender")
            time.sleep(0.5)
            
            # ════════════════════════════════════════════════════════════════════
            # SECTION 2: LOCATION (3 fields)
            # ════════════════════════════════════════════════════════════════════
            section = "LOCATION"
            print_step(4, f"\n├─ {section}", True)
            time.sleep(1)
            
            # Country
            print_step(4, "  7. Country field", True)
            country = find_input_by_label_or_placeholder(driver, ["country"], "Country", verbose=False)
            if country:
                country.click()
                time.sleep(0.2)
                country.clear()
                country.send_keys("India")
                time.sleep(0.8)
                ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                if ops:
                    ops[0].click()
                    fields_filled["Country"] = "India"
                    print_success("    ✓ India", True)
            else:
                fields_not_found.append("Country")
            time.sleep(0.8)
            
            # State
            print_step(4, "  8. State field", True)
            state = find_input_by_label_or_placeholder(driver, ["state", "province"], "State", verbose=False)
            if state:
                state.click()
                time.sleep(0.2)
                state.clear()
                state.send_keys("Uttar Pradesh")
                time.sleep(0.8)
                ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                if ops:
                    ops[0].click()
                    fields_filled["State"] = "Uttar Pradesh"
                    print_success("    ✓ Uttar Pradesh", True)
            else:
                fields_not_found.append("State")
            time.sleep(0.8)
            
            # City
            print_step(4, "  9. City field", True)
            city = find_input_by_label_or_placeholder(driver, ["city"], "City", verbose=False)
            if city:
                city.click()
                time.sleep(0.2)
                city.clear()
                city.send_keys("Greater Noida")
                time.sleep(0.8)
                ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                if ops:
                    ops[0].click()
                    fields_filled["City"] = "Greater Noida"
                    print_success("    ✓ Greater Noida", True)
            else:
                fields_not_found.append("City")
            time.sleep(0.8)
            
            # Occupation
            print_step(4, "  10. Occupation field", True)
            occ = find_input_by_label_or_placeholder(driver, ["occupation", "job", "student"], "Occupation", verbose=False)
            if occ:
                occ.click()
                time.sleep(0.2)
                occ.clear()
                occ.send_keys("College Student")
                time.sleep(0.5)
                ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                if ops:
                    ops[0].click()
                fields_filled["Occupation"] = "College Student"
                print_success("    ✓ College Student", True)
            else:
                fields_not_found.append("Occupation")
            time.sleep(0.8)
            
            # ════════════════════════════════════════════════════════════════════
            # SECTION 3: COLLEGE INFO (6 fields)
            # ════════════════════════════════════════════════════════════════════
            section = "COLLEGE INFO"
            print_step(4, f"\n├─ {section}", True)
            time.sleep(1)
            
            # College Name
            print_step(4, "  11. College Name field", True)
            college = find_input_by_label_or_placeholder(driver, ["college name"], "College", verbose=False)
            if college:
                safe_fill_field(driver, college, "Galgotias University", "College")  
                fields_filled["CollegeName"] = "Galgotias University"
            else:
                fields_not_found.append("CollegeName")
            time.sleep(0.6)
            
            # College Country
            print_step(4, "  12. College Country field", True)
            try:
                country_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'country') or contains(@aria-label, 'country')]")
                for inp in country_inputs:
                    parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form')]").text.lower()
                    if "college" in parent:
                        inp.click()
                        inp.clear()
                        inp.send_keys("India")
                        time.sleep(0.5)
                        ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if ops:
                            ops[0].click()
                        fields_filled["CollegeCountry"] = "India"
                        print_success("    ✓ India", True)
                        break
            except:
                pass
            time.sleep(0.6)
            
            # College State
            print_step(4, "  13. College State field", True)
            try:
                state_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'state') or contains(@aria-label, 'state')]")
                for inp in state_inputs:
                    parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form')]").text.lower()
                    if "college" in parent:
                        inp.click()
                        inp.clear()
                        inp.send_keys("Uttar Pradesh")
                        time.sleep(0.5)
                        ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if ops:
                            ops[0].click()
                        fields_filled["CollegeState"] = "Uttar Pradesh"
                        print_success("    ✓ Uttar Pradesh", True)
                        break
            except:
                pass
            time.sleep(0.6)
            
            # College City
            print_step(4, "  14. College City field", True)
            try:
                city_inputs = driver.find_elements(By.XPATH, "//input[contains(@placeholder, 'city') or contains(@aria-label, 'city')]")
                for inp in city_inputs:
                    parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form')]").text.lower()
                    if "college" in parent:
                        inp.click()
                        inp.clear()
                        inp.send_keys("Greater Noida")
                        time.sleep(0.5)
                        ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                        if ops:
                            ops[0].click()
                        fields_filled["CollegeCity"] = "Greater Noida"
                        print_success("    ✓ Greater Noida", True)
                        break
            except:
                pass
            time.sleep(0.6)
            
            # Degree
            print_step(4, "  15. Degree field", True)
            degree = find_input_by_label_or_placeholder(driver, ["degree"], "Degree", verbose=False)
            if degree:
                degree.click()
                degree.clear()
                degree.send_keys("B.Tech")
                time.sleep(0.5)
                ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                if ops:
                    ops[0].click()
                fields_filled["Degree"] = "B.Tech"
                print_success("    ✓ B.Tech", True)
            time.sleep(0.6)
            
            # Stream/Specialization
            print_step(4, "  16. Specialization field", True)
            stream = find_input_by_label_or_placeholder(driver, ["stream", "specialization", "branch"], "Stream", verbose=False)
            if stream:
                safe_fill_field(driver, stream, "CSE", "Stream")
                fields_filled["Specialization"] = "CSE"
            else:
                fields_not_found.append("Specialization")
            time.sleep(0.6)
            
            # Passout Year
            print_step(4, "  17. Passout Year field", True)
            passout = find_input_by_label_or_placeholder(driver, ["passout", "graduation", "year"], "Passout", verbose=False)
            if passout:
                passout.click()
                passout.clear()
                passout.send_keys("2028")
                time.sleep(0.5)
                ops = driver.find_elements(By.XPATH, "//div[@role='option']")
                if ops:
                    ops[0].click()
                fields_filled["PassoutYear"] = "2028"
                print_success("    ✓ 2028", True)
            else:
                fields_not_found.append("PassoutYear")
            time.sleep(0.8)
            
            # ════════════════════════════════════════════════════════════════════
            # SECTION 4: PROFILES (2 fields)
            # ════════════════════════════════════════════════════════════════════
            section = "PROFILES"
            print_step(4, f"\n├─ {section}", True)
            time.sleep(1)
            
            # LinkedIn
            print_step(4, "  18. LinkedIn Profile field", True)
            linkedin = find_input_by_label_or_placeholder(driver, ["linkedin"], "LinkedIn", verbose=False)
            if linkedin:
                safe_fill_field(driver, linkedin, "https://linkedin.com/in/aditya-kumar", "LinkedIn")
                fields_filled["LinkedIn"] = "added"
            else:
                fields_not_found.append("LinkedIn")
            time.sleep(0.6)
            
            # File Upload (College ID)
            print_step(4, "  19. College ID Upload field", True)
            try:
                uploads = driver.find_elements(By.XPATH, "//input[@type='file']")
                if uploads:
                    idcard = r"C:\Users\preet\Downloads\selenium\idcard.jpg"
                    if os.path.exists(idcard):
                        uploads[0].send_keys(idcard)
                        fields_filled["CollegeID"] = "uploaded"
                        time.sleep(10)
                        print_success("    ✓ Uploaded", True)
            except:
                pass
            time.sleep(0.6)
            
            # GDP Profile
            print_step(4, "  20. GDP Profile Link field", True)
            gdp = find_input_by_label_or_placeholder(driver, ["g.dev", "gdp"], "GDP", verbose=False)
            if gdp:
                safe_fill_field(driver, gdp, "https://g.dev/aditya-kumar", "GDP")
                fields_filled["GDP"] = "added"
            else:
                fields_not_found.append("GDP")
            time.sleep(0.8)
            
            # ════════════════════════════════════════════════════════════════════
            # SECTION 5: TERMS & SUBMIT
            # ════════════════════════════════════════════════════════════════════
            section = "TERMS & SUBMIT"
            print_step(4, f"\n├─ {section}", True)
            time.sleep(1)
            
            # Referral: NO
            print_step(4, "  21. Referral (NO) field", True)
            try:
                radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
                for radio in radios:
                    val = (radio.get_attribute('value') or "").lower()
                    if "no" in val:
                        if not radio.is_selected():
                            radio.click()
                        fields_filled["Referral"] = "No"
                        print_success("    ✓ No", True)
                        break
            except:
                pass
            time.sleep(0.6)
            
            # Terms & Conditions checkboxes
            print_step(4, "  22. Terms & Conditions checkboxes", True)
            try:
                all_checks = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                checked = 0
                for chk in all_checks:
                    if chk.get_attribute('id') != 'alt-checkbox':  # Skip alt number checkbox
                        try:
                            if not chk.is_selected():
                                driver.execute_script("arguments[0].scrollIntoView(true);", chk)
                                time.sleep(0.1)
                                chk.click()
                            checked += 1
                        except:
                            pass
                if checked > 0:
                    fields_filled["TermsCheckboxes"] = f"{checked} checked"
                    print_success(f"    ✓ {checked} box(es) checked", True)
            except:
                pass
            time.sleep(1)
            
            # ════════════════════════════════════════════════════════════════════
            # FORM SUBMISSION
            # ════════════════════════════════════════════════════════════════════
            print_step(4, "\n├─ FORM SUBMISSION", True)
            success, msg = click_button_with_validation(
                driver,
                "//button[contains(text(), 'Register')]",
                "Submit Registration",
                timeout=TIMEOUT_INTERACTION
            )
            
            if success:
                print_success("✓ FORM SUBMITTED SUCCESSFULLY", True)
                print_step(4, f"\n└─ FIELDS FILLED: {len(fields_filled)}/20", True)
                return True
            else:
                print_warning("Form submission validation failed, retrying...", True)
                retry_count += 1
                time.sleep(2)
                continue
                
        except Exception as e:
            print_error(f"Error in form filling: {str(e)[:60]}")
            retry_count += 1
            if retry_count < MAX_RETRIES:
                print_step(4, f"Retrying... ({retry_count}/{MAX_RETRIES})", True)
                time.sleep(2)
            continue
    
    print_error(f"Form filling failed after {MAX_RETRIES} attempts")
    return False
