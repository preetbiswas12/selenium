"""
COMPLETE FIELD MAPPING FOR HACK2SKILL REGISTRATION FORM
Based on extracted page_structure_analysis.txt

FIELD POSITIONS & SELECTORS - ALL 58 INPUTS EXTRACTED
"""

# ═══════════════════════════════════════════════════════════════
# FORM FIELD MAPPING (by visible position on form)
# ═══════════════════════════════════════════════════════════════

FORM_FIELDS = {
    # PERSONAL INFORMATION SECTION
    "Full Name": {
        "index": 0,
        "type": "text",
        "id": "547369a30a85acee6c3069c28883_0_69a30a85acee6c3069c28883",
        "placeholder": "Full Name",
        "visible": True,
        "status": "pre-filled from signup"
    },
    
    "Email": {
        "index": 1,
        "type": "email",
        "id": "547369a30a85acee6c3069c28884_1_69a30a85acee6c3069c28884",
        "placeholder": "Email",
        "visible": True,
        "status": "pre-filled from signup"
    },
    
    "WhatsApp Number": {
        "index": 2,
        "type": "tel",
        "id": "NO ID",
        "placeholder": "1 (702) 123-4567",
        "visible": True,
        "status": "FILL THIS - Phone number with country code",
        "example": "+919876543210"
    },
    
    "Alternate Number Checkbox": {
        "index": 3,
        "type": "checkbox",
        "id": "5473sameField_3_sameField",
        "label": "Alternate number is same as WhatsApp number",
        "visible": True,
        "status": "Optional - check if same as WhatsApp"
    },
    
    "Date of Birth": {
        "index": 4,
        "type": "date",
        "id": "547369a30a85acee6c3069c2888a_4_69a30a85acee6c3069c2888a",
        "placeholder": "Date of Birth",
        "visible": True,
        "status": "FILL THIS - Format: YYYY-MM-DD",
        "example": "2005-05-28"
    },
    
    "Gender": {
        "index": 5,
        "type": "text/radio",
        "id": "5473otherGender_6_otherGender",
        "placeholder": "Specify your gender here...",
        "visible": False,
        "status": "Hidden - may be radio buttons on page",
        "options": ["Male", "Female", "Other"]
    },
    
    "Alternate Number": {
        "index": 6,
        "type": "tel",
        "id": "NO ID",
        "placeholder": "1 (702) 123-4567",
        "visible": True,
        "status": "FILL ONLY IF NOT SAME AS WHATSAPP"
    },
    
    # LOCATION INFORMATION SECTION
    "Country": {
        "index": 7,
        "type": "react-select",
        "id": "react-select-2-input",
        "hidden_id": "69a30a85acee6c3069c28887",
        "label": "Country",
        "visible": True,
        "status": "FILL THIS - Autocomplete dropdown",
        "example": "India"
    },
    
    "State/Province": {
        "index": 10,
        "type": "react-select",
        "id": "react-select-3-input",
        "hidden_id": "69a30a85acee6c3069c28888",
        "label": "State/Province",
        "visible": True,
        "status": "FILL THIS - Autocomplete dropdown",
        "example": "Uttar Pradesh"
    },
    
    "City": {
        "index": 12,
        "type": "react-select",
        "id": "react-select-4-input",
        "label": "City",
        "visible": True,
        "status": "FILL THIS - Autocomplete dropdown",
        "example": "Greater Noida"
    },
    
    "Occupation": {
        "index": 21,
        "type": "react-select",
        "id": "react-select-8-input",
        "hidden_id": "69a30a85acee6c3069c2888f",
        "label": "Occupation",
        "visible": True,
        "status": "FILL THIS or SELECT RADIO",
        "note": "May appear as radio buttons - select role (SCHOOL_STUDENT, COLLEGE_STUDENT, PROFESSIONAL, etc)"
    },
    
    # COLLEGE INFORMATION SECTION (if COLLEGE_STUDENT selected)
    "College Name": {
        "index": 13,
        "type": "text",
        "id": "5473SCHOOL_STUDENT_12_name",
        "placeholder": "Write here...",
        "visible": False,
        "status": "FILL THIS when role = COLLEGE/SCHOOL",
        "example": "Galgotias University"
    },
    
    "College Country": {
        "index": 14,
        "type": "react-select",
        "id": "react-select-5-input",
        "hidden_id": "country",
        "visible": False,
        "status": "FILL THIS when role = COLLEGE/SCHOOL",
        "example": "India"
    },
    
    "College State": {
        "index": 17,
        "type": "react-select/text",
        "id": "react-select-6-input",
        "hidden_id": "state",
        "visible": False,
        "status": "FILL THIS when role = COLLEGE/SCHOOL",
        "example": "Uttar Pradesh"
    },
    
    "College City": {
        "index": 20,
        "type": "react-select",
        "id": "react-select-7-input",
        "hidden_id": "city",
        "visible": False,
        "status": "FILL THIS when role = COLLEGE/SCHOOL"
    },
    
    "Degree": {
        "index": 30,
        "type": "text",
        "id": "5473COLLEGE_STUDENT_13_otherDegree",
        "placeholder": "specify your degree here...",
        "visible": True,
        "status": "FILL THIS or SELECT from dropdown",
        "example": "B.Tech"
    },
    
    "Specialization/Stream": {
        "index": 31,
        "type": "text",
        "id": "5473COLLEGE_STUDENT_13_specialization",
        "placeholder": "Write here...",
        "visible": False,
        "status": "FILL THIS when role = COLLEGE",
        "example": "Computer Science Engineering"
    },
    
    "Passout Year": {
        "index": None,
        "type": "select",
        "id": "passoutYear",
        "label": "Passout Year",
        "visible": True,
        "status": "SELECT from dropdown",
        "example": "2028"
    },
    
    # PROFILES SECTION
    "LinkedIn Profile": {
        "index": 46,
        "type": "text",
        "id": "547369a30a85acee6c3069c2888e_17_69a30a85acee6c3069c2888e",
        "placeholder": "[EMPTY]",
        "visible": True,
        "status": "OPTIONAL - LinkedIn URL",
        "example": "https://linkedin.com/in/aditya-kumar"
    },
    
    "College ID Card": {
        "index": 47,
        "type": "file",
        "id": "69a3ec31acee6c3069e3f0ea",
        "label": "College ID Card",
        "visible": True,
        "status": "UPLOAD FILE - JPG/PNG"
    },
    
    "GDP Profile Link": {
        "index": 48,
        "type": "text",
        "id": "547369a3ec31acee6c3069e3f11b_19_69a3ec31acee6c3069e3f11b",
        "placeholder": "https://g.dev/username",
        "visible": True,
        "status": "OPTIONAL - G.DEV Profile URL"
    },
    
    # REFERRAL SECTION
    "Referral - Yes": {
        "index": 49,
        "type": "radio",
        "id": "5473_69a65a52acee6c30695f4345_20_69a65a52acee6c30695f4345_0",
        "visible": True,
        "status": "SELECT ONE - Yes/No"
    },
    
    "Referral - No": {
        "index": 50,
        "type": "radio",
        "id": "5473_69a65a52acee6c30695f4345_20_69a65a52acee6c30695f4345_1",
        "visible": True,
        "status": "SELECT ONE - Yes/No"
    },
    
    # TERMS & CONDITIONS
    "Terms & Conditions": {
        "index": 51,
        "type": "checkbox",
        "id": "672369df16fd99413d2b46215e70_0_69df16fd99413d2b46215e70",
        "label": "By registering you accept the Terms & Conditions",
        "visible": True,
        "status": "MUST CHECK"
    },
    
    "Communication Consent": {
        "index": 52,
        "type": "checkbox",
        "id": "672369df16fd99413d2b46215e71_1_69df16fd99413d2b46215e71",
        "label": "By registering, you consent to receive updates and communications",
        "visible": True,
        "status": "MUST CHECK"
    },
}

# ═══════════════════════════════════════════════════════════════
# SELECT DROPDOWNS (3 found)
# ═══════════════════════════════════════════════════════════════

SELECT_DROPDOWNS = {
    "Class/Gender Dropdown": {
        "id": "class",
        "visible": True,
        "status": "May be used for gender or class selection"
    },
    
    "Passout Year Dropdown": {
        "id": "passoutYear",
        "visible": True,
        "status": "Select graduation year",
        "example": "2028"
    },
}

# ═══════════════════════════════════════════════════════════════
# SUBMIT BUTTON
# ═══════════════════════════════════════════════════════════════

SUBMIT_BUTTON = {
    "text": "Register Now",
    "type": "submit",
    "index": 4,  # 5th button found on page
    "xpath": "//button[text()='Register Now']"
}

# ═══════════════════════════════════════════════════════════════
# IMPORTANT NOTES
# ═══════════════════════════════════════════════════════════════

"""
FORM BEHAVIOR NOTES:

1. OCCUPATION/ROLE SELECTION:
   - After selecting occupation, different form fields appear
   - COLLEGE_STUDENT shows: College Name, Country, State, City, Degree, Specialization, Passout Year
   - SCHOOL_STUDENT shows: School Name, Class
   - PROFESSIONAL shows: Designation, Years of Experience
   - STARTUP shows: Founded Date, Size, Designation
   - FREELANCER shows: Portfolio Link

2. REACT-SELECT FIELDS:
   - These are autocomplete dropdowns
   - Type in the field (e.g., "India") and wait for options
   - Click the matching option to select
   - Not standard HTML selects

3. VISIBLE vs HIDDEN FIELDS:
   - Some fields are hidden initially and appear based on selections
   - Must detect current page state before filling

4. FIELD IDS ARE DYNAMIC:
   - IDs change but pattern is consistent:
     "547369a30a85acee6c3069c28883_0_69a30a85acee6c3069c28883"
   - Position-based selection is more reliable than ID-based

5. APPROACH FOR FILLING:
   - Get all input fields by index/position
   - Fill in order: Personal → Location → Occupation → Role-specific → Profiles → Terms
   - Wait between fields for React to re-render
   - Handle both visible and hidden fields properly

6. TOTAL VISIBLE FIELDS TO FILL:
   - WhatsApp: [2]
   - DOB: [4]
   - Country: [7]
   - State: [10]
   - City: [12]
   - Occupation: [21]
   - LinkedIn: [46]
   - GDP: [48]
   - Referral: [49] or [50]
   - Terms: [51] and [52]
   + College fields (if role = COLLEGE_STUDENT)
"""
