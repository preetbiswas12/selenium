"""
Integrated Workflow with Screen Learning
First Run: RECORD user actions with Tor + cock.li + Thunderbird + Hack2skill
Subsequent Runs: PLAYBACK automatically
"""

import os
import subprocess
import time
import pyautogui
import logging
from screen_learner import ScreenLearner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TorWorkflow:
    """Workflow with Tor Browser and Screen Learning"""
    
    def __init__(self):
        # Find Tor Browser (firefox.exe in Tor installation)
        self.tor_path = self._find_tor()
        self.tor_process = None
        
        logger.info(f"Tor path: {self.tor_path if self.tor_path else 'NOT FOUND'}")
    
    def _find_tor(self):
        """Find Tor Browser (firefox.exe)"""
        paths = [
            r"C:\Users\preet\OneDrive\Documents\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files (x86)\Tor Browser\Browser\firefox.exe",
            r"C:\Program Files\Tor Browser\Browser\firefox.exe",
            r"C:\Users\preet\Desktop\Tor Browser\firefox.exe",
            r"C:\Users\preet\Downloads\Tor Browser\firefox.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                logger.info(f"✓ Found Tor at: {path}")
                return path
        
        # Try to find in PATH
        try:
            result = subprocess.run(['where', 'firefox.exe'], capture_output=True, text=True)
            if result.returncode == 0:
                tor_path = result.stdout.strip().split('\n')[0]
                if 'Tor' in tor_path or 'tor' in tor_path.lower():
                    logger.info(f"✓ Found Tor in PATH: {tor_path}")
                    return tor_path
        except:
            pass
        
        logger.warning("⚠️  Tor Browser not found. Install it or provide path.")
        return None
    
    def open_tor(self):
        """Open Tor Browser"""
        if not self.tor_path:
            logger.error("❌ Tor path not found. Please install Tor Browser.")
            logger.info("Download from: https://www.torproject.org/download")
            return False
        
        try:
            logger.info("📱 Opening Tor Browser...")
            self.tor_process = subprocess.Popen([self.tor_path])
            logger.info("✓ Tor starting (waiting 8 seconds for full load)...")
            time.sleep(8)
            return True
        except Exception as e:
            logger.error(f"Failed to open Tor: {e}")
            return False
    
    def close_tor(self):
        """Close Tor Browser"""
        try:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2)
            logger.info("✓ Tor Browser closed")
            return True
        except:
            if self.tor_process:
                self.tor_process.terminate()
            return True
    
    def open_thunderbird(self):
        """Open Thunderbird"""
        paths = [
            r"C:\Program Files\Mozilla Thunderbird\thunderbird.exe",
            r"C:\Program Files (x86)\Mozilla Thunderbird\thunderbird.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                try:
                    logger.info("📧 Opening Thunderbird...")
                    subprocess.Popen([path])
                    logger.info("✓ Thunderbird starting (waiting 8 seconds)...")
                    time.sleep(8)
                    return True
                except Exception as e:
                    logger.error(f"Failed to open Thunderbird: {e}")
                    return False
        
        logger.error("❌ Thunderbird not found")
        logger.info("Install from: https://www.thunderbird.net")
        return False
    
    def close_thunderbird(self):
        """Close Thunderbird"""
        try:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(2)
            logger.info("✓ Thunderbird closed")
            return True
        except:
            return True
    
    def stage1_cockli_recording(self):
        """Stage 1: Record cock.li email creation"""
        logger.info("\n" + "="*70)
        logger.info("STAGE 1: COCK.LI EMAIL REGISTRATION (LEARNING MODE)")
        logger.info("="*70)
        
        if not self.open_tor():
            return False
        
        learner = ScreenLearner("cock_li_registration")
        
        logger.info("\n➡️  INSTRUCTIONS:")
        logger.info("1. Tor Browser is now open")
        logger.info("2. Navigate to: https://cock.li/register.php")
        logger.info("3. Fill the registration form:")
        logger.info("   - Username: (your choice)")
        logger.info("   - Password: (your choice, twice)")
        logger.info("   - Solve CAPTCHA when prompted")
        logger.info("   - Check Terms & Conditions")
        logger.info("   - Click Register")
        logger.info("4. After registration, MOVE MOUSE TO TOP-LEFT CORNER to stop recording")
        logger.info("")
        
        # Start recording
        if not learner.first_run_record():
            logger.error("❌ Recording failed")
            return False
        
        self.close_tor()
        logger.info("✅ Stage 1 complete!\n")
        return True
    
    def stage1_cockli_playback(self):
        """Stage 1: Replay cock.li email creation"""
        logger.info("\n" + "="*70)
        logger.info("STAGE 1: COCK.LI EMAIL REGISTRATION (AUTOMATIC)")
        logger.info("="*70)
        
        if not self.open_tor():
            return False
        
        learner = ScreenLearner("cock_li_registration")
        
        logger.info("▶️  Replaying cock.li registration...")
        logger.info("(Watch the screen - actions will be performed automatically)")
        logger.info("")
        
        time.sleep(2)
        success = learner.subsequent_runs_playback(speed=1.0, interactive=False)
        
        self.close_tor()
        
        if success:
            logger.info("✅ Stage 1 complete!\n")
        return success
    
    def stage2_thunderbird_recording(self):
        """Stage 2: Record Thunderbird email setup"""
        logger.info("\n" + "="*70)
        logger.info("STAGE 2: THUNDERBIRD EMAIL SETUP (LEARNING MODE)")
        logger.info("="*70)
        
        if not self.open_thunderbird():
            return False
        
        learner = ScreenLearner("thunderbird_setup")
        
        logger.info("\n➡️  INSTRUCTIONS:")
        logger.info("1. Thunderbird is now open")
        logger.info("2. Click 'Create New Account' or Menu → New → Mail Account")
        logger.info("3. Fill in:")
        logger.info("   - Your name: (any name)")
        logger.info("   - Email: (the cock.li email you just created)")
        logger.info("   - Password: (same as cock.li)")
        logger.info("4. Click Continue")
        logger.info("5. Select IMAP server (auto-detect cock.li)")
        logger.info("6. Click Done")
        logger.info("7. Account syncing will start")
        logger.info("8. When complete, MOVE MOUSE TO TOP-LEFT CORNER to stop recording")
        logger.info("")
        
        if not learner.first_run_record():
            logger.error("❌ Recording failed")
            return False
        
        self.close_thunderbird()
        logger.info("✅ Stage 2 complete!\n")
        return True
    
    def stage2_thunderbird_playback(self):
        """Stage 2: Replay Thunderbird setup"""
        logger.info("\n" + "="*70)
        logger.info("STAGE 2: THUNDERBIRD EMAIL SETUP (AUTOMATIC)")
        logger.info("="*70)
        
        if not self.open_thunderbird():
            return False
        
        learner = ScreenLearner("thunderbird_setup")
        
        logger.info("▶️  Replaying Thunderbird setup...")
        logger.info("")
        
        time.sleep(2)
        success = learner.subsequent_runs_playback(speed=1.0, interactive=False)
        
        self.close_thunderbird()
        
        if success:
            logger.info("✅ Stage 2 complete!\n")
        return success
    
    def stage3_hack2skill_recording(self):
        """Stage 3: Record Hack2skill registration"""
        logger.info("\n" + "="*70)
        logger.info("STAGE 3: HACK2SKILL REGISTRATION (LEARNING MODE)")
        logger.info("="*70)
        
        if not self.open_tor():
            return False
        
        learner = ScreenLearner("hack2skill_registration")
        
        logger.info("\n➡️  INSTRUCTIONS:")
        logger.info("1. Tor Browser is now open with NEW Tor identity")
        logger.info("2. Navigate to: https://vision.hack2skill.com/event/solution-challenge-2026/registration")
        logger.info("3. Fill the registration form with your details:")
        logger.info("   - Full Name")
        logger.info("   - Email (your cock.li email)")
        logger.info("   - WhatsApp number")
        logger.info("   - Date of Birth")
        logger.info("   - Gender, Country, State, City")
        logger.info("   - College information")
        logger.info("   - LinkedIn, GDP profile")
        logger.info("   - Check terms & conditions")
        logger.info("4. Click Submit")
        logger.info("5. When complete, MOVE MOUSE TO TOP-LEFT CORNER to stop recording")
        logger.info("")
        
        if not learner.first_run_record():
            logger.error("❌ Recording failed")
            return False
        
        self.close_tor()
        logger.info("✅ Stage 3 complete!\n")
        return True
    
    def stage3_hack2skill_playback(self):
        """Stage 3: Replay Hack2skill registration"""
        logger.info("\n" + "="*70)
        logger.info("STAGE 3: HACK2SKILL REGISTRATION (AUTOMATIC)")
        logger.info("="*70)
        
        if not self.open_tor():
            return False
        
        learner = ScreenLearner("hack2skill_registration")
        
        logger.info("▶️  Replaying Hack2skill registration...")
        logger.info("")
        
        time.sleep(2)
        success = learner.subsequent_runs_playback(speed=1.0, interactive=False)
        
        self.close_tor()
        
        if success:
            logger.info("✅ Stage 3 complete!\n")
        return success
    
    def run_full_workflow_first_time(self):
        """First time: Record all 3 stages"""
        logger.info("\n\n")
        logger.info("╔" + "="*68 + "╗")
        logger.info("║" + " FIRST RUN: LEARNING MODE ".center(68) + "║")
        logger.info("║" + " You will perform actions, we will record everything ".center(68) + "║")
        logger.info("║" + " This creates a blueprint for future automatic runs ".center(68) + "║")
        logger.info("╚" + "="*68 + "╝")
        
        if not self.stage1_cockli_recording():
            logger.error("❌ Stage 1 failed")
            return False
        
        time.sleep(5)
        
        if not self.stage2_thunderbird_recording():
            logger.error("⚠️  Stage 2 failed (continuing to Stage 3)")
        
        time.sleep(5)
        
        if not self.stage3_hack2skill_recording():
            logger.error("❌ Stage 3 failed")
            return False
        
        logger.info("\n" + "="*70)
        logger.info("✅ ALL STAGES RECORDED SUCCESSFULLY!")
        logger.info("="*70)
        logger.info("\nYour actions have been saved. Next time you run this script,")
        logger.info("it will replay everything automatically!\n")
        
        return True
    
    def run_full_workflow_auto(self):
        """Subsequent times: Playback all 3 stages"""
        logger.info("\n\n")
        logger.info("╔" + "="*68 + "╗")
        logger.info("║" + " AUTOMATIC MODE: PLAYBACK ".center(68) + "║")
        logger.info("║" + " Replaying your recorded actions ".center(68) + "║")
        logger.info("╚" + "="*68 + "╝")
        
        if not self.stage1_cockli_playback():
            logger.error("❌ Stage 1 failed")
            return False
        
        time.sleep(5)
        
        if not self.stage2_thunderbird_playback():
            logger.error("⚠️  Stage 2 failed (continuing to Stage 3)")
        
        time.sleep(5)
        
        if not self.stage3_hack2skill_playback():
            logger.error("❌ Stage 3 failed")
            return False
        
        logger.info("\n" + "="*70)
        logger.info("✅ ALL STAGES COMPLETED AUTOMATICALLY!")
        logger.info("="*70 + "\n")
        
        return True


def main():
    # Install dependencies
    try:
        import pyautogui
        import PIL
    except ImportError:
        logger.info("Installing dependencies...")
        subprocess.run(["pip", "install", "pyautogui", "pillow", "-q"])
    
    workflow = TorWorkflow()
    
    # Check if recordings exist
    recordings_exist = (
        os.path.exists("action_recordings/cock_li_registration_recording.json") and
        os.path.exists("action_recordings/hack2skill_registration_recording.json")
    )
    
    if not recordings_exist:
        logger.info("\n⚡ FIRST TIME SETUP DETECTED")
        logger.info("You will record your actions for future automation\n")
        
        confirm = input("Ready to START LEARNING MODE? (yes/no): ").strip().lower()
        if confirm != 'yes':
            logger.info("Cancelled")
            return False
        
        return workflow.run_full_workflow_first_time()
    else:
        logger.info("\n⚡ RECORDINGS DETECTED")
        logger.info("Running in AUTOMATIC PLAYBACK mode\n")
        
        return workflow.run_full_workflow_auto()


if __name__ == "__main__":
    main()
