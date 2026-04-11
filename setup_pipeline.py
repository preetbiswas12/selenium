#!/usr/bin/env python3
"""
Master Setup Script - Automate: cock.li email + GDP profile + Hack2skill registration
Complete automation pipeline for account creation
"""

import os
import sys
import logging
from cockli_automation import CockliEmailCreator
from gdp_automation import GoogleDeveloperProfileCreator, GoogleDeveloperProfileGetter
from sheets_handler import SheetsHandler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompleteSetupPipeline:
    """
    Complete automation: cock.li → Google Developer Profile → Hack2skill Registration
    """
    
    def __init__(self, sheets_credentials_path=None, use_tor=True):
        self.cockli = CockliEmailCreator(use_tor=use_tor)
        self.use_tor = use_tor
        self.sheets_handler = None
        
        if sheets_credentials_path and os.path.exists(sheets_credentials_path):
            try:
                self.sheets_handler = SheetsHandler(sheets_credentials_path)
            except Exception as e:
                logger.warning(f"Sheets not configured: {e}")
    
    def setup_single_account(self, person_data):
        """
        Complete setup for single person:
        1. Create cock.li email
        2. Create/get GDP profile
        3. Update Google Sheet
        
        person_data dict should contain:
        - name (for GDP profile)
        - cockli_username (desired username@cock.li)
        - cockli_password (password for email)
        - google_email (Google account for GDP)
        - google_password (optional, will prompt if not provided)
        - profile_image_path (optional)
        - profile_bio (optional)
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"Setting up account for: {person_data.get('name')}")
            logger.info(f"{'='*60}")
            
            # Step 1: Create cock.li email
            logger.info("\n📧 STEP 1: Creating cock.li email...")
            email_address = self._create_cockli_email(
                person_data.get("cockli_username"),
                person_data.get("cockli_password")
            )
            
            if not email_address:
                logger.error("❌ Failed to create cock.li email")
                return False
            
            person_data["email"] = email_address
            
            # Step 2: Create/Get GDP profile
            logger.info("\n🔗 STEP 2: Setting up Google Developer Profile...")
            gdp_link = self._create_gdp_profile(
                person_data.get("name"),
                person_data.get("google_email"),
                person_data.get("google_password"),
                person_data.get("profile_image_path"),
                person_data.get("profile_bio")
            )
            
            if not gdp_link:
                logger.error("❌ Failed to create/get GDP profile")
                return False
            
            person_data["gdp_profile_link"] = gdp_link
            
            # Step 3: Update Google Sheet
            if self.sheets_handler:
                logger.info("\n📊 STEP 3: Updating Google Sheet...")
                self._update_sheet_with_account_data(person_data)
            
            logger.info(f"\n✅ COMPLETE: Account setup finished!")
            logger.info(f"Email: {email_address}")
            logger.info(f"GDP Profile: {gdp_link}")
            return True
        
        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False
    
    def setup_batch_from_sheet(self, sheet_name, worksheet_name="Sheet1"):
        """
        Setup all pending accounts from Google Sheet
        
        Sheet columns needed:
        - Name
        - CockliUsername
        - CockliPassword
        - GoogleEmail
        - GooglePassword (optional)
        - ProfileImagePath (optional)
        - ProfileBio (optional)
        - Status
        """
        if not self.sheets_handler:
            logger.error("Sheets handler not configured")
            return
        
        try:
            spreadsheet = self.sheets_handler.get_sheet(sheet_name)
            records = self.sheets_handler.get_pending_records(spreadsheet, 0, "Status")
            
            logger.info(f"Setting up {len(records)} accounts...")
            
            successful = 0
            failed = 0
            
            for idx, record in enumerate(records, 1):
                logger.info(f"\n{'#'*60}")
                logger.info(f"Account {idx}/{len(records)}")
                logger.info(f"{'#'*60}")
                
                try:
                    person_data = {
                        "name": record.get("Name", ""),
                        "cockli_username": record.get("CockliUsername", ""),
                        "cockli_password": record.get("CockliPassword", ""),
                        "google_email": record.get("GoogleEmail", ""),
                        "google_password": record.get("GooglePassword", ""),
                        "profile_image_path": record.get("ProfileImagePath", ""),
                        "profile_bio": record.get("ProfileBio", ""),
                    }
                    
                    if self.setup_single_account(person_data):
                        self.sheets_handler.update_status(spreadsheet, idx - 1, "Email & GDP Created")
                        successful += 1
                    else:
                        self.sheets_handler.update_status(spreadsheet, idx - 1, "Setup Failed")
                        failed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing row {idx}: {e}")
                    try:
                        self.sheets_handler.update_status(spreadsheet, idx - 1, f"Error: {str(e)[:20]}")
                    except:
                        pass
                    failed += 1
            
            logger.info(f"\n{'='*60}")
            logger.info(f"SETUP COMPLETE: {successful} successful, {failed} failed")
            logger.info(f"{'='*60}")
        
        except Exception as e:
            logger.error(f"Batch setup failed: {e}")
    
    def _create_cockli_email(self, username, password):
        """Create cock.li email account"""
        try:
            email = self.cockli.create_email_account(username, password)
            if email:
                logger.info(f"✅ Cock.li email created: {email}")
                # Refresh tabs for fresh state
                self.cockli.browser.close_all_tabs_and_refresh()
            return email
        except Exception as e:
            logger.error(f"Cock.li creation failed: {e}")
            return None
    
    def _create_gdp_profile(self, name, google_email, google_password=None, image_path=None, bio=""):
        """Create or get Google Developer Profile"""
        try:
            # Try to get existing profile first
            getter = GoogleDeveloperProfileGetter(google_email, use_tor=self.use_tor)
            existing_profile = getter.get_profile_link()
            
            if existing_profile:
                logger.info(f"✅ Existing GDP profile found: {existing_profile}")
                getter.close()
                return existing_profile
            
            getter.close()
            
            # Create new profile if doesn't exist
            logger.info("Creating new GDP profile...")
            creator = GoogleDeveloperProfileCreator(google_email, google_password, use_tor=self.use_tor)
            profile_url = creator.create_or_setup_profile(name, bio, image_path)
            
            if profile_url:
                logger.info(f"✅ GDP profile created: {profile_url}")
                # Refresh tabs for fresh state
                creator.browser.close_all_tabs_and_refresh()
            
            creator.close()
            return profile_url
        
        except Exception as e:
            logger.error(f"GDP setup failed: {e}")
            return None
    
    def _update_sheet_with_account_data(self, person_data):
        """Update sheet with created account details"""
        try:
            # This would integrate with your actual sheet update logic
            logger.info(f"Updating sheet with:")
            logger.info(f"  Email: {person_data.get('email')}")
            logger.info(f"  GDP Link: {person_data.get('gdp_profile_link')}")
        except Exception as e:
            logger.warning(f"Sheet update failed: {e}")
    
    def cleanup(self):
        """Close all browsers/connections"""
        try:
            self.cockli.close()
        except:
            pass


def interactive_setup():
    """Interactive setup for single account"""
    print("\n" + "="*60)
    print("  COMPLETE ACCOUNT SETUP - Interactive Mode")
    print("="*60 + "\n")
    
    pipeline = CompleteSetupPipeline("credentials.json")
    
    person_data = {
        "name": input("Full Name: "),
        "cockli_username": input("Desired cock.li username (without @cock.li): "),
        "cockli_password": input("Cock.li password: "),
        "google_email": input("Google account email: "),
        "google_password": input("Google password (press Enter to enter manually): ") or None,
        "profile_image_path": input("Profile image path (optional, press Enter to skip): ") or None,
        "profile_bio": input("Profile bio (optional): ") or None,
    }
    
    if pipeline.setup_single_account(person_data):
        print("\n✅ Setup complete!")
        print(f"Email: {person_data.get('email')}")
        print(f"GDP Profile: {person_data.get('gdp_profile_link')}")
    else:
        print("\n❌ Setup failed - check logs above")
    
    pipeline.cleanup()


def batch_setup():
    """Setup from Google Sheet"""
    sheet_name = input("Enter Google Sheet name (default: Setup_Accounts): ") or "Setup_Accounts"
    
    pipeline = CompleteSetupPipeline("credentials.json")
    pipeline.setup_batch_from_sheet(sheet_name)
    pipeline.cleanup()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Complete account setup automation")
    parser.add_argument("--mode", choices=["interactive", "batch"], default="interactive",
                       help="Setup mode: interactive (single) or batch (from sheet)")
    parser.add_argument("--sheet", type=str, help="Google Sheet name (for batch mode)")
    
    args = parser.parse_args()
    
    if args.mode == "batch":
        sheet_name = args.sheet or "Setup_Accounts"
        pipeline = CompleteSetupPipeline("credentials.json")
        pipeline.setup_batch_from_sheet(sheet_name)
        pipeline.cleanup()
    else:
        interactive_setup()
