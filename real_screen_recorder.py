"""
Real Screen Recording & Automated Form Filling System
- Records mouse clicks while interacting with forms
- Replays clicks automatically in incognito Chrome
- Perfect for bulk account registrations
"""

import json
import time
import os
from datetime import datetime
from PIL import Image
import logging
from pynput import mouse
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChromeIncognitoLauncher:
    """Launch Chrome in incognito mode with no cache"""
    
    def __init__(self):
        self.driver = None
    
    def launch(self, url="https://cock.li/register.php"):
        """Launch Chrome incognito and navigate to URL"""
        try:
            options = Options()
            options.add_argument("--incognito")
            options.add_argument("--disable-cache")
            options.add_argument("--disable-application-cache")
            options.add_argument("--disable-offline-load")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            self.driver = webdriver.Chrome(options=options)
            time.sleep(2)
            self.driver.get(url)
            time.sleep(2)
            
            logger.info(f"✅ Chrome opened in incognito mode: {url}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to launch Chrome: {e}")
            return False
    
    def close(self):
        """Close Chrome"""
        if self.driver:
            self.driver.quit()

class RealScreenRecorder:
    """Records REAL mouse clicks only"""
    
    def __init__(self, session_name="cockli"):
        self.session_name = session_name
        self.actions = []
        self.recordings_dir = "action_recordings"
        self.screenshots_dir = os.path.join(self.recordings_dir, session_name, "screenshots")
        
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.is_recording = False
        self.start_time = None
        
        logger.info(f"✅ Recorder initialized for session: {session_name}")
    
    def _relative_time(self):
        """Get time relative to recording start"""
        if self.start_time:
            return time.time() - self.start_time
        return 0
    
    def record_action(self, action_type, **kwargs):
        """Record an action with relative timestamp"""
        relative_time = self._relative_time()
        action = {
            "timestamp": relative_time,
            "type": action_type,
            "data": kwargs
        }
        self.actions.append(action)
        logger.info(f"  [{relative_time:.2f}s] ✓ {action_type}: {str(kwargs)[:60]}")
    
    def on_move(self, x, y):
        """Mouse movement handler"""
        pass
    
    def on_click(self, x, y, button, pressed):
        """Mouse click handler - records clicks only"""
        if self.is_recording and pressed:
            button_name = str(button).split('.')[-1]
            self.record_action("click", x=x, y=y, button=button_name)
    
    def on_scroll(self, x, y, dx, dy):
        """Mouse scroll handler"""
        if self.is_recording:
            self.record_action("scroll", x=x, y=y, dx=dx, dy=dy)
    
    def start_recording(self, chrome_launcher):
        """Start recording user actions with Chrome open"""
        logger.info("\n" + "="*70)
        logger.info("🔴 RECORDING STARTED - CLICK ON FORM FIELDS NOW".center(70))
        logger.info("="*70)
        
        logger.info("\n📌 WHAT TO DO:")
        logger.info("  1. Click on form fields in Chrome")
        logger.info("  2. Type your username, password, etc. (typing NOT recorded)")
        logger.info("  3. When finished, press Ctrl+C in terminal to stop")
        logger.info(f"\n⏱ Recording for session: {self.session_name}\n")
        
        self.is_recording = True
        self.start_time = time.time()
        self.actions = []
        
        # Set up mouse listener
        listener_mouse = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
        logger.info("🔴 RECORDING IN PROGRESS - Click fields in Chrome browser now...\n")
        
        try:
            with listener_mouse:
                listener_mouse.join()
        except KeyboardInterrupt:
            self.is_recording = False
            logger.info("\n\n⛔ RECORDING STOPPED")
    
    def stop_recording(self):
        """Stop and save recording"""
        self.is_recording = False
        
        logger.info("\n" + "="*70)
        logger.info("🟢 RECORDING COMPLETED".center(70))
        logger.info(f"Total actions: {len(self.actions)}".center(70))
        logger.info("="*70)
        
        return self.save_recording()
    
    def save_recording(self):
        """Save to JSON"""
        try:
            recording_file = os.path.join(self.recordings_dir, f"{self.session_name}_recording.json")
            
            with open(recording_file, 'w') as f:
                json.dump(self.actions, f, indent=2)
            
            logger.info(f"\n✅ Recording saved: {recording_file}")
            logger.info(f"   Actions: {len(self.actions)}")
            
            action_summary = {}
            for action in self.actions:
                action_type = action['type']
                action_summary[action_type] = action_summary.get(action_type, 0) + 1
            
            logger.info(f"\n📊 Actions:")
            for action_type, count in sorted(action_summary.items()):
                logger.info(f"   {action_type}: {count}")
            
            return recording_file
        except Exception as e:
            logger.error(f"Failed to save: {e}")
            return None


class RealScreenPlayback:
    """Replays recorded clicks automatically"""
    
    def __init__(self, session_name="cockli"):
        self.session_name = session_name
        self.actions = []
        self.recordings_dir = "action_recordings"
        self.load_recording()
    
    def load_recording(self):
        """Load recording from JSON"""
        try:
            recording_file = os.path.join(self.recordings_dir, f"{self.session_name}_recording.json")
            
            if not os.path.exists(recording_file):
                logger.error(f"❌ Recording not found: {recording_file}")
                logger.info("   Run Mode 1 (RECORD) first to create a recording")
                return False
            
            with open(recording_file, 'r') as f:
                self.actions = json.load(f)
            
            logger.info(f"✅ Recording loaded: {recording_file}")
            logger.info(f"   Actions to replay: {len(self.actions)}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load: {e}")
            return False
    
    def replay(self, speed=1.0, chrome_launcher=None):
        """Replay clicks automatically"""
        if not self.actions:
            logger.error("No actions to replay!")
            return False
        
        logger.info("\n" + "="*70)
        logger.info("▶️  PLAYBACK STARTED - AUTO-CLICKING FIELDS".center(70))
        logger.info("="*70)
        logger.info(f"\nSpeed: {speed}x")
        logger.info("🤖 Playing back recorded clicks...\n")
        
        from pynput import mouse, keyboard as kb
        
        try:
            mouse_controller = mouse.Controller()
            
            prev_timestamp = 0
            
            for idx, action in enumerate(self.actions):
                action_type = action['type']
                timestamp = action['timestamp']
                data = action['data']
                
                # Calculate delay
                delay = (timestamp - prev_timestamp) / speed
                if delay > 0:
                    time.sleep(delay)
                
                progress = f"[{idx+1}/{len(self.actions)}]"
                
                if action_type == "click":
                    x = data['x']
                    y = data['y']
                    button = data['button']
                    
                    button_map = {
                        'left': mouse.Button.left,
                        'right': mouse.Button.right,
                        'middle': mouse.Button.middle
                    }
                    button_obj = button_map.get(button, mouse.Button.left)
                    
                    logger.info(f"{progress} Click at ({x}, {y})")
                    mouse_controller.position = (x, y)
                    mouse_controller.click(button=button_obj)
                    time.sleep(0.3)
                
                elif action_type == "scroll":
                    x = data['x']
                    y = data['y']
                    dy = data.get('dy', 0)
                    
                    logger.info(f"{progress} Scroll at ({x}, {y})")
                    mouse_controller.position = (x, y)
                    mouse_controller.scroll(0, 3 if dy > 0 else -3)
                
                prev_timestamp = timestamp
            
            logger.info("\n" + "="*70)
            logger.info("✅ PLAYBACK COMPLETED - NOW TYPE YOUR INFO".center(70))
            logger.info("="*70)
            logger.info("\n💡 Chrome is ready! Type your username, password, and complete the form.\n")
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Playback error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    logger.info("\n" + "="*70)
    logger.info("CHROME INCOGNITO RECORDING & PLAYBACK SYSTEM".center(70))
    logger.info("="*70)
    
    print("\n🎬 Choose mode:")
    print("━" * 50)
    print("1️⃣  RECORD  - Open Chrome, click fields → saves clicks")
    print("2️⃣  PLAYBACK - Replay clicks, you type new inputs")
    print("3️⃣  EXIT")
    print("━" * 50)
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        logger.info("\n🚀 STARTING RECORD MODE...\n")
        
        chrome = ChromeIncognitoLauncher()
        if chrome.launch("https://cock.li/register.php"):
            recorder = RealScreenRecorder("cockli")
            try:
                recorder.start_recording(chrome)
                recorder.stop_recording()
                logger.info("\n✅ Next time, run this and choose PLAYBACK mode!")
            except KeyboardInterrupt:
                logger.info("\n⛔ Recording stopped by user")
                recorder.stop_recording()
            finally:
                time.sleep(2)
                chrome.close()
        else:
            logger.error("❌ Failed to launch Chrome")
    
    elif choice == "2":
        logger.info("\n🚀 STARTING PLAYBACK MODE...\n")
        
        chrome = ChromeIncognitoLauncher()
        if chrome.launch("https://cock.li/register.php"):
            player = RealScreenPlayback("cockli")
            player.replay(speed=1.0, chrome_launcher=chrome)
            
            logger.info("\n⏳ Chrome will stay open for 60 seconds for you to type...")
            logger.info("   When done, close Chrome to exit.\n")
            
            try:
                time.sleep(60)
            except KeyboardInterrupt:
                pass
            finally:
                chrome.close()
        else:
            logger.error("❌ Failed to launch Chrome")
    
    elif choice == "3":
        logger.info("👋 Exiting... Goodbye!")
        sys.exit(0)
    
    else:
        logger.error("❌ Invalid choice")
        sys.exit(1)
