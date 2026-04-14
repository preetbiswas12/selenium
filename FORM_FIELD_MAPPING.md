# Hack2Skill Registration Form - Field Mapping (UPDATED)

## Form Structure & Field Types

### Section 1: Personal Information

| # | Field | Type | Value | Notes |
|---|-------|------|-------|-------|
| 1 | Full Name | Text | Pre-filled from signup | SKIP (already filled) |
| 2 | Email | Email | Pre-filled from signup | SKIP (disabled) |
| 3 | WhatsApp Number | Phone | +919876543210 | Regular text input |
| 4 | Alternate = WhatsApp | Checkbox | Checked | Auto-checks when same |
| 5 | Date of Birth | Date | YYYY-MM-DD (age 18-30) | Date input, random between 1996-2006 |
| 6 | Gender | Select | Male | HTML `<select>` dropdown |

### Section 2: Location

| # | Field | Type | Value | Notes |
|---|-------|------|-------|-------|
| 7 | Country | React Select | India | Type + click option from `//div[@role='option']` |
| 8 | State/Province | React Select | Uttar Pradesh | Type + click option (2nd react-select-container) |
| 9 | City | React Select | Noida | Type + click option (3rd react-select-container) |
| 10 | Occupation | Radio | College Student | Must select to show college fields |

### Section 3: Education

| # | Field | Type | Value | Notes |
|---|-------|------|-------|-------|
| 11 | College Name | React Select | Galgotias University | Type + click option (6th react-select-container) |
| 12 | College Country | React Select | India | Type + click option (7th react-select-container) |
| 13 | College State | React Select | Uttar Pradesh | Type + click option (8th react-select-container) |
| 14 | College City | React Select | Noida | Type + click option (9th react-select-container) |
| 15 | Degree | React Select | Bachelor of Technology (B.Tech) | Type + click option (10th react-select-container) |
| 16 | Stream | Text INPUT | Computer Science Engineering | ⚠️ **TEXT FIELD** (NOT autocomplete) |
| 17 | Passout Year | HTML `<select>` | 2026 | **⚠️ DROPDOWN ONLY** - Use `Select().select_by_value("2026")` |

### Section 4: Profiles & Documents

| # | Field | Type | Value | Notes |
|---|-------|------|-------|-------|
| 18 | LinkedIn Profile | Text URL | https://linkedin.com/in/username | Must include https:// or http:// |
| 19 | College ID Card | File Upload | idcard.jpg | Image or PDF, max 5MB |
| 20 | GDP Profile Link | Text URL | https://g.dev/username | **⚠️ STRICT FORMAT: Must be `https://g.dev/username`** |

### Section 5: Referral (CONDITIONAL)

| # | Field | Type | Value | Notes |
|---|-------|------|-------|-------|
| 21 | Were you referred? | Radio | **YES** ✅ | **MUST SELECT YES** to unlock referral code field |
| 22 | Referral Code | Text | GDG2026REF | **ONLY APPEARS after selecting YES** |

### Section 6: Terms & Agreements

| # | Field | Type | Value | Notes |
|---|-------|------|-------|-------|
| 23 | Terms & Conditions | Checkboxes | CHECKED | Check all consent checkboxes |

---

## Critical Implementation Notes

### ✅ React Select Components (Typing Dropdowns)

Fields: Country, State, City, College Name, College Country, College State, City, Degree

**Pattern:**
```python
# Find the container
containers = driver.find_elements(By.XPATH, "//div[contains(@class, 'react-select-container')]")
# Get the nth container (indexed 0+)
input_field = containers[n].find_element(By.XPATH, ".//input[@type='text']")
# Click, type, wait for options, click option
input_field.click()
time.sleep(0.3)
input_field.send_keys("value")
time.sleep(1)
options = driver.find_elements(By.XPATH, "//div[@role='option']")
if options:
    options[0].click()
```

### ⚠️ HTML `<select>` Dropdowns

Fields: Gender, Passout Year

**Pattern:**
```python
selects = driver.find_elements(By.TAG_NAME, "select")
for select_elem in selects:
    try:
        Select(select_elem).select_by_value("value")
        break
    except:
        pass
```

### 📝 Text Inputs (NOT Autocomplete)

Fields: WhatsApp, DOB, Stream, LinkedIn, GDP Profile

**Pattern:**
```python
element.click()
time.sleep(0.2)
element.send_keys("value")
```

### 🔴 Critical Fixes Applied

1. **Passout Year** ❌ Was trying to type in a `<select>` dropdown
   - ✅ Now uses `Select().select_by_value()`

2. **Stream/Specialization** ❌ Was trying to autocomplete
   - ✅ Now treats as plain text input

3. **Referral** ❌ Was selecting "No"
   - ✅ Now selects "YES" to unlock referral code field

4. **React Select Containers** ❌ Was using by-placeholder selectors
   - ✅ Now uses container indexing for precise field selection

5. **GDP Profile** ❌ Was accepting any format
   - ✅ Now enforces strict format: `https://g.dev/username`

---

## Test Values

Use these values to test the form filling:

```
Full Name: Generated (Arjun Singh, Aditya Kumar, etc.)
Email: cubic4355@cock.li (from CSV)
WhatsApp: +919876543210
DOB: 2003-11-12 (randomly generated, 18-30 age)
Gender: Male
Country: India
State: Uttar Pradesh
City: Noida
Occupation: College Student
College Name: Galgotias University
College Country: India
College State: Uttar Pradesh
College City: Noida
Degree: Bachelor of Technology (B.Tech)
Stream: Computer Science Engineering
Passout Year: 2026
LinkedIn: https://linkedin.com/in/aditya-kumar
College ID: idcard.jpg (file upload)
GDP Profile: https://g.dev/aditya-kumar
Referral: YES (important!)
Referral Code: GDG2026REF
Terms: All checkboxes checked
```

---

**Last Updated:** April 14, 2026
**Status:** ✅ Based on actual HTML extraction from successful manual fill
