#!/usr/bin/env python3
"""Fix indentation in hack2skill_batch_form_filler_v2.py"""

# Read the file
with open('hack2skill_batch_form_filler_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the main try block and the matching except
main_try_line = None
main_except_line = None

for i, line in enumerate(lines):
    # Find the main try block start (looking in form fill function - around line 469)
    if 460 < i < 500:
        if line.strip() == 'try:' and len(line) - len(line.lstrip()) == 8:
            # Check next few lines to confirm this is our main try (should have WebDriverWait)
            if any('WebDriverWait' in lines[j] for j in range(i, min(i+5, len(lines)))):
                main_try_line = i
                break

# Find the matching except
if main_try_line:
    for i in range(main_try_line + 1, len(lines)):
        line = lines[i]
        # Look for the main except: "except Exception as e:" with 8 spaces indentation
        if (line.strip().startswith('except Exception as e:') and 
            len(line) - len(line.lstrip()) == 8):
            # Check if "Form fill error" is in the next few lines
            if any('Form fill error' in lines[j] for j in range(i, min(i+3, len(lines)))):
                main_except_line = i
                break

print(f"Main try block at line {main_try_line + 1}" if main_try_line else "Could not find main try")
print(f"Main except block at line {main_except_line + 1}" if main_except_line else "Could not find main except")

# Fix indentation: lines with 8 spaces between main_try and main_except should have 12 spaces
if main_try_line and main_except_line:
    fixed_count = 0
    for i in range(main_try_line + 1, main_except_line):
        line = lines[i]
        # Count leading spaces
        leading_spaces = len(line) - len(line.lstrip())
        
        # If this line has exactly 8 spaces (not empty, not already indented more), fix it
        if leading_spaces == 8 and line.strip() and not line.strip().startswith('except') and not line.strip().startswith('finally'):
            lines[i] = '    ' + line  # Add 4 spaces
            fixed_count += 1
    
    print(f"Fixed {fixed_count} lines")
    
    # Write back
    with open('hack2skill_batch_form_filler_v2.py', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("File saved successfully")
else:
    print("Could not find main try/except blocks")
