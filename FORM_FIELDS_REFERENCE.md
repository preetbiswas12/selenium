# Hack2skill Registration - Form Fields Reference

## Complete Form Structure

This document lists all form fields from the actual Hack2skill registration page.

---

## 📋 Signup Section (Before Verification)

**Note:** Users first sign up with just name and email, receive OTP, then fill the full registration form.

| Field | Type | HTML Selector To Find |
|-------|------|----------------------|
| Full Name | Text Input | Look for input with `name*='name'` or placeholder "Full Name" |
| Email | Email Input | `input[type='email']` |
| Register Now Button | Button | `button:contains('Register Now')` or `button[type='submit']` |

---

## 📝 Registration Form Fields (After OTP Verification)

### Personal Information

| Field | Type | Selector | Max Length | Required |
|-------|------|----------|------------|----------|
| Full Name | Text | `input[name*='fullName']` | 255 | ✅ |
| Email | Email | `input[type='email']` | - | ✅ |
| WhatsApp Number | Phone | `input[name*='whatsapp']` | - | ✅ |
| Date of Birth | Date | `input[type='date']` | - | ✅ |
| Gender | Dropdown | `select[name*='gender']` | - | ✅ |
| Alternate Number | Phone | `input[name*='alternate']` | - | ✅ |
| Country | Dropdown | `select[name*='country']` | - | ✅ |
| State/Province | Text | `input[name*='state']` | - | ✅ |
| City | Text | `input[name*='city']` | - | ✅ |

**Age Requirement:** Must be between 18-30 years old

---

### Education Information

| Field | Type | Selector | Max Length | Required |
|-------|------|----------|------------|----------|
| Occupation | Dropdown | `select[name*='occupation']` | - | ✅ |
| College Name | Text (Autocomplete) | `input[name*='college']` | 128 | ✅ |
| College Country | Dropdown | `select[name*='collegeCountry']` | - | ✅ |
| College State | Text (Autocomplete) | `input[name*='collegeState']` | - | ✅ |
| College City | Text (Autocomplete) | `input[name*='collegeCity']` | - | ✅ |
| Degree | Text | `input[name*='degree']` | - | ✅ |
| Stream/Specialization | Textarea | `textarea[name*='specialization']` | - | ✅ |
| Passout Year | Dropdown | `select[name*='passout']` | - | ✅ |

---

### Profile & Links

| Field | Type | Selector | Format | Required |
|-------|------|----------|--------|----------|
| LinkedIn URL | URL | `input[name*='linkedin']` | Must include `https://` or `http://` | ✅ |
| College ID Card | File Upload | `input[type='file'][name*='collegeId']` | Image/PDF, Max 5MB | ✅ |
| GDP Profile Link | URL | `input[name*='gdp']` | Format: `https://g.dev/username` | ✅ |

**Important:** 
- Create Google Developer Profile: https://developers.google.com/
- Make profile **PUBLIC**
- Copy your profile link

---

### Referral & Settings

| Field | Type | Selector | Options | Required |
|-------|------|----------|---------|----------|
| Referred by GDG Organizer? | Radio Buttons | `input[type='radio'][name*='referral']` | Yes / No | ✅ |
| Referral Code | Text | `input[name*='referralCode']` | Only shows if "Yes" selected | ✅* |
| Terms & Conditions | Checkbox | `input[type='checkbox'][name*='terms']` | Accept/Decline | ✅ |
| Consent for Communications | Checkbox | `input[type='checkbox'][name*='consent']` | Accept/Decline | ✅ |

**⚠️ SPECIAL NOTE:** 
- **"Yes" is pre-selected by default** for the referral question
- If you select "No", you must click the "No" radio button
- Only provide referral code if selecting "Yes"

---

## 🎯 How to Find Exact Selectors

### Step 1: Open Registration Page
```
https://vision.hack2skill.com/event/solution-challenge-2026/registration
```

### Step 2: Inspect an Input Field
1. Right-click the form field
2. Select "Inspect Element" (or F12)
3. You'll see HTML like:
```html
<input id="fullName" type="text" name="fullName" placeholder="Full Name">
<select id="gender" name="genderSelect">
  <option value="">--Select an Option--</option>
</select>
```

### Step 3: Copy the Selector
- **By ID:** `#fullName`
- **By Name:** `input[name="fullName"]`
- **By Type:** `input[type="email"]`
- **Combination:** `input[name*="fullName"][type="text"]`

---

## 📊 Data Formats Expected

### Phone Numbers
- Format: `+91XXXXXXXXXX` (India)
- Example: `+911234567890`

### Date of Birth
- Format: `dd.mm.yyyy` (dot separator)
- Example: `01.01.2000`

### LinkedIn URL
- Format: `https://linkedin.com/in/username`
- Must include `https://` or `http://`

### Google Developer Profile
- Format: `https://g.dev/username`
- Example: `https://g.dev/john_doe

`
- Create at: https://developers.google.com/

### College ID Upload
- Accepted: Image files (jpg, png, etc.) or PDF
- Max size: 5 MB
- Required for verification

---

## ✅ Form Validation Rules

### Full Name
- Required
- Max 255 characters

### Email
- Required
- Valid email format

### Phone Numbers
- Required
- Must start with +91 (for India)

### Date of Birth
- Required
- Format: dd.mm.yyyy
- Age must be 18-30

### College ID
- Required
- File type: Image or PDF
- Max size: 5 MB

### Checkboxes
- Both "Terms & Conditions" and "Consent for Communication" MUST be checked

### Referral Code
- Only required if "Yes" is selected for referral question
- Provided by GDG on Campus Organizer

---

## 🔴 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Referral code field doesn't appear" | Form is set to "Yes" by default | Click "No" radio button if not referred |
| "Can't upload college ID" | File > 5MB or wrong format | Use image/PDF under 5MB |
| "LinkedIn URL invalid" | Missing https:// | Add `https://` to the beginning |
| "GDP link rejected" | Wrong format | Use `https://g.dev/username` format |
| "CAPTCHA appears" | Anti-bot protection | Solve manually or use solver API |

---

## 📝 Google Sheet Column Template

Your Google Sheet should have these columns:

```
Name | Email | Password | FullName | Email | WhatsappNumber | DateOfBirth | Gender | AlternateNumber | Country | StateProvince | City | Occupation | CollegeName | CollegeCountry | CollegeState | CollegeCity | Degree | Specialization | PassoutYear | LinkedinURL | CollegeIDPath | GDPProfileLink | ReferralAnswer | ReferralCode | Status
```

**Example Row:**
```
John Doe | john@cock.li | Pass123!Test | John Doe | john@cock.li | +911234567890 | 01.01.2000 | Male | +911234567890 | India | Maharashtra | Mumbai | College Student | University of Mumbai | India | Maharashtra | Mumbai | B.Tech | Computer Science | 2026 | https://linkedin.com/in/johndoe | C:\images\john_id.jpg | https://g.dev/johndoe | no | | 
```

---

**Last Updated:** April 2026  
**Form Version:** Hack2skill Solution Challenge 2026
