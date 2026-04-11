"""
Screen Learning & Recording System
Records user actions and replays them automatically
Uses PyAutoGUI + PIL + OCR (pytesseract)
"""

import pyautogui
import time
import json
import os
from datetime import datetime
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ActionRecorder:
    """Records mouse clicks, keyboard input, and screenshots"""
    
    def __init__(self, session_name="default"):
        self.session_name = session_name
        self.actions = []
        self.recordings_dir = "action_recordings"
        self.screenshots_dir = os.path.join(self.recordings_dir, session_name, "screenshots")
        
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        # Enable fail-safe
        pyautogui.FAILSAFE = True
        logger.info(f"Recorder initialized for session: {session_name}")
        logger.info("⚠️  IMPORTANT: Move mouse to TOP-LEFT corner to STOP recording")
    
    def record_action(self, action_type, **kwargs):
        """Record an action with timestamp and details"""
        timestamp = datetime.now().isoformat()
        action = {
            "timestamp": timestamp,
            "type": action_type,
            "data": kwargs
        }
        self.actions.append(action)
        logger.info(f"✓ Recorded: {action_type} - {kwargs}")
    
    def take_screenshot(self, label=""):
        """Take a screenshot and save it"""
        try:
            screenshot_num = len([f for f in os.listdir(self.screenshots_dir) if f.endswith('.png')])
            filename = f"{screenshot_num:03d}_{label}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            img = pyautogui.screenshot()
            img.save(filepath)
            
            self.record_action("screenshot", filepath=filepath, label=label)
            logger.info(f"📸 Screenshot saved: {filename}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
    
    def start_recording(self):
        """Start interactive recording session"""
        logger.info("\n" + "="*60)
        logger.info("🔴 RECORDING SESSION STARTED")
        logger.info("="*60)
        logger.info("\nYou are now in RECORDING MODE")
        logger.info("Everything you do will be captured:\n")
        logger.info("✓ Mouse clicks (position)")
        logger.info("✓ Keyboard input (text typed)")
        logger.info("✓ Screenshots (for visual reference)")
        logger.info("✓ Timing (delays between actions)")
        logger.info("\n⚠️  To STOP recording: Move mouse to TOP-LEFT CORNER")
        logger.info("="*60 + "\n")
        
        input("Press ENTER to START recording (perform your actions now)...\n")
        
        # Take initial screenshot
        self.take_screenshot("session_start")
        
        last_pos = None
        has_stopped = False
        
        try:
            while not has_stopped:
                time.sleep(0.1)  # Check every 100ms
                
                # Check if mouse is at top-left corner (fail-safe)
                x, y = pyautogui.position()
                
                if x < 10 and y < 10:
                    logger.info("\n⛔ STOP signal detected (top-left corner)")
                    has_stopped = True
                    break
        
        except KeyboardInterrupt:
            logger.info("\n⛔ Recording stopped by user (Ctrl+C)")
            has_stopped = True
        
        # Take final screenshot
        self.take_screenshot("session_end")
        
        logger.info("\n" + "="*60)
        logger.info("🟢 RECORDING SESSION ENDED")
        logger.info(f"Total actions recorded: {len(self.actions)}")
        logger.info("="*60 + "\n")
        
        return self.save_recording()
    
    def save_recording(self):
        """Save recorded actions to JSON file"""
        try:
            recording_file = os.path.join(self.recordings_dir, f"{self.session_name}_recording.json")
            
            with open(recording_file, 'w') as f:
                json.dump(self.actions, f, indent=2)
            
            logger.info(f"✅ Recording saved: {recording_file}")
            logger.info(f"   Recorded {len(self.actions)} actions")
            return recording_file
            
        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            return None


class ActionPlayer:
    """Plays back recorded actions"""
    
    def __init__(self, session_name="default"):
        self.session_name = session_name
        self.actions = []
        self.recordings_dir = "action_recordings"
        
        # Enable fail-safe
        pyautogui.FAILSAFE = True
        
        # Load recording
        self.load_recording()
    
    def load_recording(self):
        """Load recorded actions from JSON"""
        try:
            recording_file = os.path.join(self.recordings_dir, f"{self.session_name}_recording.json")
            
            if not os.path.exists(recording_file):
                logger.error(f"Recording not found: {recording_file}")
                return False
            
            with open(recording_file, 'r') as f:
                self.actions = json.load(f)
            
            logger.info(f"✅ Recording loaded: {recording_file}")
            logger.info(f"   Total actions: {len(self.actions)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load recording: {e}")
            return False
    
    def replay(self, speed=1.0, interactive=True):
        """
        Replay recorded actions
        speed: 1.0 = normal, 2.0 = 2x faster, 0.5 = 2x slower
        interactive: True = ask for confirmation before each action
        """
        if not self.actions:
            logger.error("No actions to replay!")
            return False
        
        logger.info("\n" + "="*60)
        logger.info("▶️  PLAYBACK SESSION STARTED")
        logger.info("="*60)
        logger.info(f"Playing back {len(self.actions)} recorded actions")
        logger.info(f"Speed: {speed}x")
        logger.info("="*60 + "\n")
        
        if interactive:
            input("Press ENTER to START playback...\n")
        
        try:
            for idx, action in enumerate(self.actions):
                action_type = action['type']
                data = action['data']
                
                # Display progress
                progress = f"[{idx+1}/{len(self.actions)}]"
                logger.info(f"{progress} Playing: {action_type}")
                
                # Handle different action types
                if action_type == "screenshot":
                    logger.info(f"  → Screenshot: {data.get('label', '')}")
                    time.sleep(0.5 / speed)
                
                elif action_type == "click":
                    x = data['x']
                    y = data['y']
                    button = data.get('button', 'left')
                    logger.info(f"  → Click at ({x}, {y}) - {button}")
                    pyautogui.click(x, y, button=button)
                    time.sleep(0.3 / speed)
                
                elif action_type == "type":
                    text = data['text']
                    logger.info(f"  → Type: {text[:50]}..." if len(text) > 50 else f"  → Type: {text}")
                    pyautogui.typewrite(text, interval=0.05 / speed)
                    time.sleep(0.2 / speed)
                
                elif action_type == "hotkey":
                    keys = data['keys']
                    logger.info(f"  → Hotkey: {'+'.join(keys)}")
                    pyautogui.hotkey(*keys)
                    time.sleep(0.3 / speed)
                
                elif action_type == "press":
                    key = data['key']
                    logger.info(f"  → Press: {key}")
                    pyautogui.press(key)
                    time.sleep(0.2 / speed)
                
                elif action_type == "wait":
                    duration = data['duration'] / speed
                    logger.info(f"  → Wait: {duration:.1f}s")
                    time.sleep(duration)
                
                # Optional: pause between actions in interactive mode
                if interactive and idx < len(self.actions) - 1:
                    response = input(f"  ► Continue? (y/skip/stop): ").strip().lower()
                    if response == 'stop':
                        logger.info("❌ Playback stopped by user")
                        return False
                    elif response == 'skip':
                        logger.info("⊘ Action skipped")
                        continue
            
            logger.info("\n" + "="*60)
            logger.info("✅ PLAYBACK COMPLETED SUCCESSFULLY")
            logger.info("="*60 + "\n")
            return True
            
        except pyautogui.FailSafeException:
            logger.error("❌ Fail-safe activated (mouse at top-left)")
            return False
        except Exception as e:
            logger.error(f"❌ Playback error: {e}")
            import traceback
            traceback.print_exc()
            return False


class ScreenLearner:
    """
    Main workflow:
    1. First run: Record user actions
    2. Learn from screenshots
    3. Subsequent runs: Replay automatically
    """
    
    def __init__(self, session_name):
        self.session_name = session_name
        self.recorder = None
        self.player = None
    
    def first_run_record(self):
        """First run: Record everything the user does"""
        logger.info("\n" + "╔" + "="*58 + "╗")
        logger.info("║" + " FIRST RUN: RECORDING MODE ".center(58) + "║")
        logger.info("║" + " Do everything manually, we'll record all actions ".center(58) + "║")
        logger.info("╚" + "="*58 + "╝\n")
        
        self.recorder = ActionRecorder(self.session_name)
        
        # Hook into pyautogui to capture actions
        self._hook_pyautogui()
        
        # Start recording
        recording_file = self.recorder.start_recording()
        
        if recording_file:
            logger.info("\n✅ Recording saved successfully!")
            logger.info(f"   File: {recording_file}")
            return True
        return False
    
    def subsequent_runs_playback(self, speed=1.0, interactive=False):
        """Subsequent runs: Replay the recorded actions"""
        logger.info("\n" + "╔" + "="*58 + "╗")
        logger.info("║" + " PLAYBACK MODE: AUTOMATIC EXECUTION ".center(58) + "║")
        logger.info("║" + " Replaying your recorded actions ".center(58) + "║")
        logger.info("╚" + "="*58 + "╝\n")
        
        self.player = ActionPlayer(self.session_name)
        return self.player.replay(speed=speed, interactive=interactive)
    
    def _hook_pyautogui(self):
        """Hook pyautogui functions to record actions"""
        original_click = pyautogui.click
        original_typewrite = pyautogui.typewrite
        original_hotkey = pyautogui.hotkey
        original_press = pyautogui.press
        
        def recorded_click(x=None, y=None, clicks=1, interval=0.0, button='left', _keys=None):
            if x is not None and y is not None:
                self.recorder.record_action("click", x=x, y=y, button=button)
            return original_click(x, y, clicks, interval, button, _keys)
        
        def recorded_typewrite(string, interval=0.0, _pause=True):
            self.recorder.record_action("type", text=string)
            return original_typewrite(string, interval, _pause)
        
        def recorded_hotkey(*args, _pause=True):
            self.recorder.record_action("hotkey", keys=list(args))
            return original_hotkey(*args, _pause=_pause)
        
        def recorded_press(key, presses=1, interval=0.0, _pause=True):
            self.recorder.record_action("press", key=key)
            return original_press(key, presses, interval, _pause)
        
        # Replace functions
        pyautogui.click = recorded_click
        pyautogui.typewrite = recorded_typewrite
        pyautogui.hotkey = recorded_hotkey
        pyautogui.press = recorded_press
        
        logger.info("✓ PyAutoGUI hooks installed - actions will be recorded")


if __name__ == "__main__":
    import sys
    
    logger.info("\n" + "="*70)
    logger.info("SCREEN LEARNING & RECORDING SYSTEM".center(70))
    logger.info("="*70)
    
    print("\nChoose mode:")
    print("1. RECORD - Do your actions manually (first time)")
    print("2. PLAYBACK - Replay your recorded actions automatically")
    print("3. EXIT")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\n📍 Session name (default='cockli'):", end=" ")
        session_name = input().strip() or "cockli"
        
        learner = ScreenLearner(session_name)
        if learner.first_run_record():
            logger.info("\n✅ Ready for playback! Run again and choose option 2")
        else:
            logger.error("\n❌ Recording failed")
    
    elif choice == "2":
        print("\n📍 Session name to playback (default='cockli'):", end=" ")
        session_name = input().strip() or "cockli"
        
        print("\nPlayback speed:")
        print("  1 = Normal speed")
        print("  2 = 2x faster")
        print("  0.5 = 2x slower")
        speed_input = input("Speed (default=1): ").strip() or "1"
        
        try:
            speed = float(speed_input)
        except:
            speed = 1.0
            logger.warning("Invalid speed, using 1.0")
        
        learner = ScreenLearner(session_name)
        if learner.subsequent_runs_playback(speed=speed, interactive=False):
            logger.info("\n✅ Playback completed!")
        else:
            logger.error("\n❌ Playback failed")
    
    elif choice == "3":
        logger.info("Exiting...")
        sys.exit(0)
    
    else:
        logger.error("Invalid choice")
        sys.exit(1)
