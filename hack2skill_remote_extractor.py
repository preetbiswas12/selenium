"""
Hack2Skill - Remote Control & Page Content Extraction

Workflow:
1. Open signup page
2. You manually login and fill in some fields
3. Tell script when done
4. Script extracts full page HTML content
5. Save to file for analysis
"""

import time
from selenium import webdriver

def main():
    """Main workflow"""
    print("\n" + "="*70)
    print("HACK2SKILL: Remote Control Mode")
    print("="*70)
    
    # Initialize Firefox
    print("\n→ Step 1: Initializing Firefox...")
    options = webdriver.FirefoxOptions()
    options.add_argument("-private")  # Private browsing mode
    
    try:
        driver = webdriver.Firefox(options=options)
        print("✓ Firefox initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize Firefox: {str(e)}")
        return
    
    try:
        # Open signup page
        print("→ Step 2: Opening signup page...")
        signup_url = "https://vision.hack2skill.com/signup?utm_source=hack2skill&utm_medium=homepage&utm_campaign=&utm_term=&utm_content="
        driver.get(signup_url)
        time.sleep(2)
        print("✓ Signup page opened in Firefox\n")
        
        # Wait for user action
        print("→ Step 3: Waiting for you to complete actions...")
        print("")
        print("   Instructions:")
        print("   1. Fill in Full Name")
        print("   2. Fill in Email")
        print("   3. Click Register")
        print("   4. Complete OTP verification")
        print("   5. Fill in any registration form fields as needed")
        print("")
        
        input("Press Enter when you've completed all actions... ")
        
        # Wait a bit for page to settle
        time.sleep(2)
        print("\n✓ Extracting page content...\n")
        
        # Get page HTML
        page_html = driver.page_source
        
        # Get current URL
        current_url = driver.current_url
        print(f"Current URL: {current_url}\n")
        
        # Save to file
        output_file = r"C:\Users\preet\Downloads\selenium\page_content.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page_html)
        
        print(f"✓ Page HTML saved to: {output_file}")
        print(f"✓ File size: {len(page_html)} bytes\n")
        
        # Also print first 2000 characters to console
        print("="*70)
        print("PAGE CONTENT (First 2000 characters):")
        print("="*70)
        print(page_html[:2000])
        print("\n... (rest saved to file) ...\n")
        
        print("="*70)
        print("✓ Extraction complete!")
        print("="*70)
        
        # Keep browser open for inspection
        print("\nBrowser will stay open for 30 seconds for inspection...")
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n\n✗ Cancelled by user")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
    finally:
        print("\nClosing Firefox...")
        driver.quit()
        print("✓ Done!")


if __name__ == "__main__":
    main()
