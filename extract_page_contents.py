"""
PAGE CONTENT EXTRACTION & INSPECTION TOOL
Extract all form fields, buttons, and page structure from the registration form
This shows you EXACTLY what's on the page so you can map fields correctly
"""

import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ═══════════════════════════════════════════════════════════════
# URLS & CONFIG
# ═══════════════════════════════════════════════════════════════

SIGNUP_PAGE_URL = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage"
REGISTRATION_URL = "https://vision.hack2skill.com/event/solution-challenge-2026/registration"
CSV_FILE = r"C:\Users\preet\Downloads\selenium\accounts.csv"
OUTPUT_FILE = r"C:\Users\preet\Downloads\selenium\page_structure_analysis.txt"


# ═══════════════════════════════════════════════════════════════
# EXTRACTION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def extract_all_inputs(driver, page_name=""):
    """Extract all input fields from the page"""
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"INPUT FIELDS - {page_name}")
    output.append("="*80 + "\n")
    
    # Get all inputs
    all_inputs = driver.find_elements(By.TAG_NAME, "input")
    output.append(f"Total inputs found: {len(all_inputs)}\n")
    
    for idx, inp in enumerate(all_inputs, 1):
        # Get all attributes
        inp_type = inp.get_attribute("type") or "text"
        inp_id = inp.get_attribute("id") or "[NO ID]"
        inp_name = inp.get_attribute("name") or "[NO NAME]"
        inp_placeholder = inp.get_attribute("placeholder") or "[NO PLACEHOLDER]"
        inp_class = inp.get_attribute("class") or "[NO CLASS]"
        inp_value = inp.get_attribute("value") or "[EMPTY]"
        
        # Try to find associated label
        label_text = "[NO LABEL]"
        try:
            if inp_id and inp_id != "[NO ID]":
                label = driver.find_element(By.XPATH, f"//label[@for='{inp_id}']")
                label_text = label.text or "[EMPTY LABEL]"
        except:
            try:
                # Try finding label by proximity
                parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'form-group') or contains(@class, 'mb-')]")
                labels = parent.find_elements(By.TAG_NAME, "label")
                if labels:
                    label_text = labels[0].text
            except:
                pass
        
        # Check if visible
        is_visible = inp.is_displayed()
        
        output.append(f"[{idx}] TYPE: {inp_type:10} | VISIBLE: {str(is_visible):5}")
        output.append(f"     ID:          {inp_id}")
        output.append(f"     NAME:        {inp_name}")
        output.append(f"     PLACEHOLDER: {inp_placeholder}")
        output.append(f"     LABEL:       {label_text}")
        output.append(f"     CLASS:       {inp_class}")
        output.append(f"     VALUE:       {inp_value}")
        output.append("")
    
    return "\n".join(output)

def extract_all_selects(driver, page_name=""):
    """Extract all select dropdowns"""
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"SELECT DROPDOWNS - {page_name}")
    output.append("="*80 + "\n")
    
    all_selects = driver.find_elements(By.TAG_NAME, "select")
    output.append(f"Total selects found: {len(all_selects)}\n")
    
    for idx, sel in enumerate(all_selects, 1):
        sel_id = sel.get_attribute("id") or "[NO ID]"
        sel_name = sel.get_attribute("name") or "[NO NAME]"
        sel_class = sel.get_attribute("class") or "[NO CLASS]"
        
        # Try to find label
        label_text = "[NO LABEL]"
        try:
            if sel_id and sel_id != "[NO ID]":
                label = driver.find_element(By.XPATH, f"//label[@for='{sel_id}']")
                label_text = label.text
        except:
            pass
        
        # Get options
        options = sel.find_elements(By.TAG_NAME, "option")
        option_texts = [opt.text for opt in options[:5]]  # First 5
        
        output.append(f"[{idx}] ID: {sel_id}")
        output.append(f"     NAME: {sel_name}")
        output.append(f"     LABEL: {label_text}")
        output.append(f"     CLASS: {sel_class}")
        output.append(f"     OPTIONS ({len(options)} total): {', '.join(option_texts)}")
        output.append("")
    
    return "\n".join(output)

def extract_all_buttons(driver, page_name=""):
    """Extract all buttons"""
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"BUTTONS - {page_name}")
    output.append("="*80 + "\n")
    
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    output.append(f"Total buttons found: {len(all_buttons)}\n")
    
    for idx, btn in enumerate(all_buttons, 1):
        btn_text = btn.text.strip() or "[NO TEXT]"
        btn_type = btn.get_attribute("type") or "button"
        btn_id = btn.get_attribute("id") or "[NO ID]"
        btn_class = btn.get_attribute("class") or "[NO CLASS]"
        disabled = btn.get_attribute("disabled") or "False"
        
        output.append(f"[{idx}] TYPE: {btn_type:8} | TEXT: '{btn_text}'")
        output.append(f"     ID: {btn_id}")
        output.append(f"     CLASS: {btn_class}")
        output.append(f"     DISABLED: {disabled}")
        output.append("")
    
    return "\n".join(output)

def extract_all_labels(driver, page_name=""):
    """Extract all labels"""
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"LABELS - {page_name}")
    output.append("="*80 + "\n")
    
    all_labels = driver.find_elements(By.TAG_NAME, "label")
    output.append(f"Total labels found: {len(all_labels)}\n")
    
    for idx, label in enumerate(all_labels, 1):
        label_text = label.text or "[EMPTY]"
        label_for = label.get_attribute("for") or "[NO FOR]"
        label_class = label.get_attribute("class") or "[NO CLASS]"
        
        output.append(f"[{idx}] TEXT: {label_text}")
        output.append(f"     FOR: {label_for}")
        output.append(f"     CLASS: {label_class}")
        output.append("")
    
    return "\n".join(output)

def extract_page_html(driver, page_name=""):
    """Extract and save full page HTML"""
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"FULL PAGE HTML - {page_name}")
    output.append("="*80 + "\n")
    
    html = driver.page_source
    output.append(html)
    
    return "\n".join(output)

def extract_form_structure(driver, page_name=""):
    """Extract form structure using JavaScript"""
    
    output = []
    output.append("\n" + "="*80)
    output.append(f"PAGE STRUCTURE ANALYSIS - {page_name}")
    output.append("="*80 + "\n")
    
    # Use JavaScript to get form structure
    script = """
    var info = {
        url: window.location.href,
        title: document.title,
        forms: [],
        allInputs: []
    };
    
    // Get all forms
    var forms = document.querySelectorAll('form');
    forms.forEach((form, idx) => {
        info.forms.push({
            index: idx,
            id: form.id || 'NO ID',
            class: form.className || 'NO CLASS',
            method: form.method || 'NO METHOD',
            action: form.action || 'NO ACTION',
            inputs: form.querySelectorAll('input').length
        });
    });
    
    // Get all inputs
    var inputs = document.querySelectorAll('input');
    inputs.forEach((inp, idx) => {
        info.allInputs.push({
            index: idx,
            type: inp.type || 'NO TYPE',
            id: inp.id || 'NO ID',
            name: inp.name || 'NO NAME',
            placeholder: inp.placeholder || 'NO PLACEHOLDER',
            value: inp.value || 'EMPTY',
            visible: !!(inp.offsetParent !== null),
            required: inp.required || false
        });
    });
    
    return info;
    """
    
    result = driver.execute_script(script)
    
    output.append(f"URL: {result['url']}")
    output.append(f"Title: {result['title']}\n")
    
    output.append(f"FORMS: {len(result['forms'])}\n")
    for form in result['forms']:
        output.append(f"  Form {form['index']}: ID={form['id']}, Method={form['method']}, Inputs={form['inputs']}")
    
    output.append(f"\nALL INPUTS: {len(result['allInputs'])}\n")
    for inp in result['allInputs']:
        output.append(f"  [{inp['index']}] {inp['type']:10} | {inp['placeholder']:25} | ID={inp['id']}")
    
    return "\n".join(output)


# ═══════════════════════════════════════════════════════════════
# MAIN EXTRACTION WORKFLOW
# ═══════════════════════════════════════════════════════════════

def main():
    print("="*80)
    print("PAGE CONTENT EXTRACTION TOOL (MANUAL MODE)")
    print("="*80)
    print("\nThis will:")
    print("  1. Open Firefox (blank)")
    print("  2. Wait for YOU to navigate & login")
    print("  3. Extract page contents when you're ready")
    print("  4. Save to file:")
    print(f"     {OUTPUT_FILE}\n")
    
    driver = None
    all_output = []
    
    try:
        print("Initializing Firefox...")
        driver = webdriver.Firefox()
        print("✓ Firefox opened (blank window)\n")
        
        print("="*80)
        print("WAITING FOR YOUR INPUT")
        print("="*80)
        print("\n📋 INSTRUCTIONS:")
        print("  1. Firefox window is now open")
        print("  2. Manually navigate to your page (or any URL you want)")
        print("  3. Login if needed")
        print("  4. Fill out any fields manually")
        print("  5. Once you're on the page you want to analyze...")
        print("  6. Come back to this terminal window")
        print("  7. Press ENTER to extract the current page")
        print("\n" + "="*80)
        input("→ Press ENTER once you're ready to extract the page contents...\n")
        
        print("Extracting page contents...")
        print("="*80 + "\n")
        
        # Get current URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}\n")
        
        # ═══════════════════════════════════════════════════════════════
        # EXTRACT CURRENT PAGE
        # ═══════════════════════════════════════════════════════════════
        all_output.append("\n" + "#"*80)
        all_output.append("# PAGE CONTENT ANALYSIS")
        all_output.append("#"*80)
        
        all_output.append(extract_form_structure(driver, "CURRENT PAGE"))
        all_output.append(extract_all_inputs(driver, "CURRENT PAGE"))
        all_output.append(extract_all_selects(driver, "CURRENT PAGE"))
        all_output.append(extract_all_buttons(driver, "CURRENT PAGE"))
        all_output.append(extract_all_labels(driver, "CURRENT PAGE"))
        
        print("✓ Extraction complete\n")
        
        # ═══════════════════════════════════════════════════════════════
        # SAVE OUTPUT
        # ═══════════════════════════════════════════════════════════════
        print(f"Saving extraction to: {OUTPUT_FILE}")
        
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(all_output))
        
        print("✓ File saved!")
        print("\nYou can now:")
        print(f"  1. Open the file: {OUTPUT_FILE}")
        print("  2. Find field positions by counting [N] numbers")
        print("  3. Map field names to positions in your script")
        print("  4. Use exact selectors (ID, name, placeholder shown)")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n" + "="*80)
        print("Press ENTER to close browser...")
        input()
        
        if driver:
            try:
                driver.quit()
                print("✓ Firefox closed")
            except:
                pass

if __name__ == "__main__":
    main()
