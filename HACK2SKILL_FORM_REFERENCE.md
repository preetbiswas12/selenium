# Hack2Skill Signup Form Field Reference

## Form URL
- **Signup Page**: `https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage`

## Form Fields

### 1. Full Name Field
- **Label**: Full Name (Required - marked with *)
- **Placeholder**: Enter Full Name
- **Type**: Text Input
- **Max Length**: 256 characters
- **Character Counter**: Shows as "0/256"
- **HTML Reference**: 
  - Input element class/id: Look for `input` with placeholder "Enter Full Name"
  - XPath: `//input[@placeholder='Enter Full Name']`
  - CSS Selector: `input[placeholder='Enter Full Name']`

### 2. Email Field
- **Label**: Email (Required - marked with *)
- **Placeholder**: Enter Email
- **Type**: Text Input (email type)
- **HTML Reference**:
  - Input element: Look for `input` with placeholder "Enter Email"
  - XPath: `//input[@placeholder='Enter Email']`
  - CSS Selector: `input[placeholder='Enter Email']`

### 3. Register Button
- **Label**: Register
- **Type**: Submit Button (blue button)
- **Color**: Blue (#2E5CB8 or similar)
- **HTML Reference**:
  - XPath: `//button[contains(text(), 'Register')]`
  - CSS Selector: `button:contains('Register')`

## Social Login Options
- **Google Login**: Present (Google logo icon)
- **GitHub Login**: Present (GitHub logo icon)
- **Note**: These are optional, we'll use email-based registration

## Form Submission
- After clicking Register, the form will validate:
  - Full Name: Required, must not be empty
  - Email: Required, must be valid email format
- The form likely sends a POST request to register the account

## Additional Elements
- **Login Link**: "Already have an account? Login" at the bottom
  - Directs to `/login` page
- **Cookie Banner**: May appear on first load (accept and close)

## Strategy for Automation
1. Accept cookie banner (if visible)
2. Fill in Full Name with a consistent name pattern
3. Fill in Email with each address from `accounts_created.csv`
4. Click Register button
5. Wait for success confirmation or page redirect
6. Repeat for all 15 emails

## Notes
- Form appears to be a React/Vue component (single-page app structure)
- No CAPTCHA detected on signup form
- Fields use placeholder text, not separate labels for better UX
