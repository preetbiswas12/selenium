#!/usr/bin/env python3
"""Comprehensive fix for indentation in hack2skill_batch_form_filler_v2.py"""

with open('hack2skill_batch_form_filler_v2.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the main try block (line 470) and main except (line 1009)
main_try_line = 469  # Line 470 (0-indexed is 469)
main_except_line = 1008  # Line 1009 (0-indexed is 1008)

fixed_count = 0

# From line 470 to main except, all lines should be indented inside the try
for i in range(main_try_line + 1, main_except_line):
    line = lines[i]
    stripped = line.lstrip()
    
    # Skip empty lines, comments that start at column 0
    if not stripped or (stripped.startswith('#') and line[0] == '#'):
        continue
    
    # Get current indentation
    current_indent = len(line) - len(stripped)
    
    # Lines with 8 spaces should become 12 spaces
    # Lines with any other indentation should stay as-is (they're probably correct)
    # But we need special handling for try/except/finally blocks
    
    if current_indent == 8:
        # This is inside the main try block, should be 12 spaces
        lines[i] = '    ' + line
        fixed_count += 1
    elif current_indent == 4:
        # This is probably a try/except at wrong level - should be 8
        if stripped.startswith(('try:', 'except', 'finally')):
            lines[i] = '    ' + line
            fixed_count += 1

print(f"Fixed {fixed_count} indentation errors")

# Write back
with open('hack2skill_batch_form_filler_v2.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("File saved. Now checking syntax...")

# Quick syntax check
import py_compile
try:
    py_compile.compile('hack2skill_batch_form_filler_v2.py', doraise=True)
    print("✓ Syntax OK!")
except py_compile.PyCompileError as e:
    print(f"✗ Syntax Error: {e}")
