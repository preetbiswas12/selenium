# Quick Selector Inspection Guide

## How to Find Form Field Selectors

This is a step-by-step guide to find the CSS/XPath selectors for each form field.

---

## 🎯 Step-by-Step Process

### 1. Open Registration Page
```
https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage
```

### 2. Open Browser DevTools
- **Windows/Linux**: Press `F12` or `Ctrl+Shift+I`
- **Mac**: Press `Cmd+Shift+I`

### 3. Use Inspector Tool
- Click the **Inspector** (mouse icon) in the top-left of DevTools
- Click on a form field on the page

### 4. Find the Selector

You'll see HTML like:
```html
<input id="fullName" type="text" name="fullName" class="form-control">
```

**Available selectors:**
- By ID: `#fullName`
- By Name: `input[name="fullName"]`
- By Class: `input.form-control`
- By Type: `input[type="text"]`

---

## 📝 Form Fields to Inspect

### Personal Information Fields

```python
# Full Name
<input ... id="fullName" name="fullName" ...>
SELECTOR = "input[id='fullName']"  or  "input[name='fullName']"

# Email
<input type="email" name="email" ...>
SELECTOR = "input[type='email']"  or  "input[name='email']"

# WhatsApp Number
<input type="tel" name="whatsapp" ...>
SELECTOR = "input[name*='whatsapp']"  or  "input[type='tel']"

# Date of Birth
<input type="date" name="dob" ...>
SELECTOR = "input[type='date']"  or  "input[name*='dob']"

# Gender
<select id="gender" name="gender">
  <option value="">--Select an Option--</option>
  <option value="male">Male</option>
  <option value="female">Female</option>
</select>
SELECTOR = "select[id='gender']"  or  "select[name='gender']"

# Alternate Number
<input type="tel" name="alternateNumber" ...>
SELECTOR = "input[name*='alternate']"

# Country
<select name="country">
  <option value="India">India</option>
</select>
SELECTOR = "select[name='country']"

# State/Province
<input type="text" name="state" placeholder="State...">
SELECTOR = "input[name*='state']"

# City
<input type="text" name="city" placeholder="City...">
SELECTOR = "input[name*='city']"
```

### Education Fields

```python
# Occupation
<select name="occupation">
  <option value="">--Select Occupation--</option>
  <option value="student">College Student</option>
</select>
SELECTOR = "select[name*='occupation']"

# College Name
<input name="collegeName" class="autocomplete" ...>
SELECTOR = "input[name*='college']"

# College State
<input name="collegeState" class="autocomplete" ...>
SELECTOR = "input[name*='collegeState']"

# Degree
<input name="degree" ...>
SELECTOR = "input[name*='degree']"

# Specialization
<textarea name="specialization" ...></textarea>
SELECTOR = "textarea[name*='specialization']"

# Passout Year
<select name="passoutYear">
  <option value="2026">2026</option>
</select>
SELECTOR = "select[name*='passout']"
```

### Profile & Links

```python
# LinkedIn URL
<input type="url" name="linkedinUrl" ...>
SELECTOR = "input[name*='linkedin']"

# College ID File Upload
<input type="file" name="collegeId" accept="image/*, .pdf" ...>
SELECTOR = "input[type='file'][name*='collegeId']"

# GDP Profile Link
<input type="url" name="gdpLink" placeholder="https://g.dev/username" ...>
SELECTOR = "input[name*='gdp']"
```

### Referral & Checkboxes

```python
# Referral - Yes Radio Button
<input type="radio" name="referral" value="yes" id="ref-yes">
SELECTOR = "input[type='radio'][value='yes'][name*='referral']"

# Referral - No Radio Button
<input type="radio" name="referral" value="no" id="ref-no">
SELECTOR = "input[type='radio'][value='no'][name*='referral']"

# Referral Code (appears if Yes selected)
<input type="text" name="referralCode" ...>
SELECTOR = "input[name*='referralCode']"

# Terms Checkbox
<input type="checkbox" name="terms" ...>
SELECTOR = "input[type='checkbox'][name*='terms']"

# Consent Checkbox
<input type="checkbox" name="consent" ..>
SELECTOR = "input[type='checkbox'][name*='consent']"

# Register Button
<button type="submit" class="btn-register">Register Now</button>
SELECTOR = "button[type='submit']"  or  "button:contains('Register Now')"
```

---

## ✅ Copy-Paste Template for config.py

Once you've inspected 2-3 fields and found the pattern, update your `config.py`:

```python
FORM_SELECTORS = {
    # Change these to match what you found
    "full_name": "input[name='fullName']",
    "email": "input[type='email']",
    "whatsapp_number": "input[name='whatsappNumber']",
    "date_of_birth": "input[type='date']",
    "gender": "select[name='gender']",
    "alternate_number": "input[name='alternateNumber']",
    "country": "select[name='country']",
    "state_province": "input[name='state']",
    "city": "input[name='city']",
    
    "occupation": "select[name='occupation']",
    "college_name": "input[name='collegeName']",
    "college_country": "select[name='collegeCountry']",
    "college_state": "input[name='collegeState']",
    "college_city": "input[name='collegeCity']",
    "degree": "input[name='degree']",
    "specialization": "textarea[name='specialization']",
    "passout_year": "select[name='passoutYear']",
    
    "linkedin_url": "input[name='linkedinUrl']",
    "college_id_file": "input[type='file'][name='collegeId']",
    "gdp_profile_link": "input[name='gdpLink']",
    
    "referral_yes_radio": "input[type='radio'][value='yes'][name='referral']",
    "referral_no_radio": "input[type='radio'][value='no'][name='referral']",
    "referral_code_input": "input[name='referralCode']",
    "terms_checkbox": "input[type='checkbox'][name='terms']",
    "consent_checkbox": "input[type='checkbox'][name='consent']",
    
    "register_btn": "button[type='submit']",
}
```

---

## 🔍 Selector Cheat Sheet

| Pattern | Meaning | Example |
|---------|---------|---------|
| `#id` | Find by ID | `#fullName` |
| `input[name='fullName']` | Find by name attribute | `input[name='fullName']` |
| `input[type='email']` | Find by input type | `input[type='email']` |
| `input[name*='college']` | Name contains 'college' | `input[name*='college']` |
| `:contains('text')` | Button text | `button:contains('Register')` |
| `.class` | Find by CSS class | `.form-control` |
| `select[name='gender']` | Dropdown selector | `select[name='gender']` |

---

## ❓ Troubleshooting

### "Script says element not found but I can see it"

**Solutions:**
1. The field might be inside an `<iframe>` - script can't access it
2. Field name might be different (inspect again)
3. Field might be dynamically loaded - wait for it with delays
4. Try a looser selector: `input[name*='name']` instead of `input[name='fullName']`

### "That selector breaks everything"

1. Clear the selector back to default
2. Inspect the element again carefully
3. Try a different selector (by type, contain, etc.)
4. Use browser console to test: `document.querySelector('your_selector')`

### "Can't find the exact ID"

Use partial matching with `*=`:
```python
"full_name": "input[name*='name']",  # matches 'fullName', 'first_name', etc.
```

---

## 🧪 Test Your Selectors

In browser console (F12 → Console):
```javascript
// This should return the element
document.querySelector('input[name="fullName"]')

// If you see an element, the selector works!
// If null, the selector is wrong
```

---

**Save your selectors once they work - you won't need to update them again!**
