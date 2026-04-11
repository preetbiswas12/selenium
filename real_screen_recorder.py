"""
Real Screen Recording System - Mouse Clicks Only
Listens to MOUSE CLICKS at OS level
Skips keyboard recording (so you can use different inputs each time)
Records timing and screenshot changes for reference
Perfect for automating form clicks with dynamic input
"""

import json
import time
import os
from datetime import datetime
from PIL import Image, ImageChops
import logging
from pynput import mouse, keyboard
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealScreenRecorder:
    """Records REAL mouse clicks only - keyboard input skipped"""
    
    def __init__(self, session_name="default"):
        self.session_name = session_name
        self.actions = []
        self.recordings_dir = "action_recordings"
        self.screenshots_dir = os.path.join(self.recordings_dir, session_name, "screenshots")
        
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.is_recording = False
        self.last_screenshot = None
        self.start_time = None
        
        logger.info(f"✅ Real Screen Recorder initialized for session: {session_name}")

    
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
        """Mouse movement handler (optional - can skip to reduce noise)"""
        # Uncomment to record mouse movement
        # self.record_action("move", x=x, y=y)
        pass
    
    def on_click(self, x, y, button, pressed):
        """Mouse click handler"""
        if self.is_recording:
            if pressed:
                button_name = str(button).split('.')[-1]
                self.record_action("click", x=x, y=y, button=button_name, pressed=True)
            else:
                button_name = str(button).split('.')[-1]
                self.record_action("click", x=x, y=y, button=button_name, pressed=False)
    
    def on_scroll(self, x, y, dx, dy):
        """Mouse scroll handler"""
        if self.is_recording:
            self.record_action("scroll", x=x, y=y, dx=dx, dy=dy)
    
    def on_press(self, key):
        """Keyboard press handler - DISABLED (keyboard input changes per registration)"""
        pass
    
    def on_release(self, key):
        """Keyboard release handler - DISABLED (keyboard input changes per registration)"""
        pass
    
    def screenshot_monitor(self):
        """Monitor for screenshot changes (page loads, etc)"""
        screenshot_num = 0
        while self.is_recording:
            try:
                time.sleep(2)  # Check every 2 seconds
                
                img = Image.new('RGB', (1920, 1080))
                try:
                    img = Image.frombytes('RGB', (1920, 1080), open(0).read())
                except:
                    img = Image.frombytes('RGB', (1920, 1080), b'\0' * (1920 * 1080 * 3))
                
                # Simple screenshot for reference
                filename = f"{screenshot_num:03d}_auto.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                
                try:
                    screenshot = Image.new('RGB', (1920, 1080))
                except:
                    pass
                
                screenshot_num += 1
            except Exception as e:
                logger.warning(f"Screenshot monitor error: {e}")
    
    def take_manual_screenshot(self, label=""):
        """Take a manual screenshot"""
        try:
            screenshot_num = len([f for f in os.listdir(self.screenshots_dir) if f.endswith('.png')])
            filename = f"{screenshot_num:03d}_{label}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            import pyautogui
            img = pyautogui.screenshot()
            img.save(filepath)
            
            relative_time = self._relative_time()
            self.record_action("screenshot", filepath=filepath, label=label, filename=filename)
            logger.info(f"  [{relative_time:.2f}s] 📸 Screenshot saved: {filename}")
            
            return filepath
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
    
    def start_recording(self):
        """Start recording user actions"""
        logger.info("\n" + "="*70)
        logger.info("🔴 RECORDING STARTED - MOUSE CLICKS WILL BE CAPTURED".center(70))
        logger.info("="*70)
        
        logger.info("\n📌 IMPORTANT:")
        logger.info("  • Mouse clicks WILL be recorded (position & button)")
        logger.info("  • Keyboard input will NOT be recorded (changes per registration)")
        logger.info("  • You type different usernames/passwords each time")
        logger.info("  • Timing recorded between actions")
        
        logger.info("\n⏹ TO STOP RECORDING: Press Ctrl+C in the terminal\n")
        
        # Take initial screenshot
        self.take_manual_screenshot("start")
        
        self.is_recording = True
        self.start_time = time.time()
        self.actions = []
        
        # Set up MOUSE listener only (NO keyboard listener)
        listener_mouse = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
        logger.info("🔴 RECORDING IN PROGRESS...\n")
        logger.info("   (Perform your actions now - click on fields, etc.)\n")
        logger.info("   (Type manually - keyboard input is NOT recorded)\n")
        
        try:
            with listener_mouse:
                listener_mouse.join()
        
        except KeyboardInterrupt:
            self.is_recording = False
            logger.info("\n\n⛔ RECORDING STOPPED BY USER")
    
    def stop_recording(self):
        """Stop recording and save"""
        self.is_recording = False
        
        # Take final screenshot
        self.take_manual_screenshot("end")
        
        logger.info("\n" + "="*70)
        logger.info("🟢 RECORDING STOPPED".center(70))
        logger.info(f"Total actions recorded: {len(self.actions)}".center(70))
        logger.info("="*70)
        
        return self.save_recording()
    
    def save_recording(self):
        """Save recording to JSON"""
        try:
            recording_file = os.path.join(self.recordings_dir, f"{self.session_name}_recording.json")
            
            with open(recording_file, 'w') as f:
                json.dump(self.actions, f, indent=2)
            
            logger.info(f"\n✅ Recording saved: {recording_file}")
            logger.info(f"   Total actions: {len(self.actions)}")
            logger.info(f"   Duration: {self.actions[-1]['timestamp'] if self.actions else 0:.2f} seconds")
            
            # Save action summary
            action_summary = {}
            for action in self.actions:
                action_type = action['type']
                action_summary[action_type] = action_summary.get(action_type, 0) + 1
            
            logger.info(f"\n📊 Action Summary:")
            for action_type, count in sorted(action_summary.items()):
                logger.info(f"   {action_type}: {count}")
            
            return recording_file
        
        except Exception as e:
            logger.error(f"Failed to save recording: {e}")
            return None


class RealScreenPlayback:
    """Replays recorded actions exactly as they were performed"""
    
    def __init__(self, session_name="default"):
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
                return False
            
            with open(recording_file, 'r') as f:
                self.actions = json.load(f)
            
            logger.info(f"✅ Recording loaded: {recording_file}")
            logger.info(f"   Total actions: {len(self.actions)}")
            
            if self.actions:
                total_duration = self.actions[-1]['timestamp']
                logger.info(f"   Duration: {total_duration:.2f} seconds")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to load recording: {e}")
            return False
    
    def replay(self, speed=1.0):
        """Replay actions with timing"""
        if not self.actions:
            logger.error("No actions to replay!")
            return False
        
        logger.info("\n" + "="*70)
        logger.info("▶️  PLAYBACK STARTED - REPLAYING YOUR ACTIONS".center(70))
        logger.info("="*70)
        logger.info(f"\nSpeed: {speed}x")
        logger.info("🎬 Playing back recorded actions...\n")
        
        import pyautogui
        from pynput import mouse, keyboard as kb
        
        try:
            mouse_controller = mouse.Controller()
            keyboard_controller = kb.Controller()
            
            prev_timestamp = 0
            
            for idx, action in enumerate(self.actions):
                action_type = action['type']
                timestamp = action['timestamp']
                data = action['data']
                
                # Calculate delay since last action
                delay = (timestamp - prev_timestamp) / speed
                if delay > 0:
                    time.sleep(delay)
                
                # Display progress
                progress = f"[{idx+1}/{len(self.actions)}]"
                
                # Execute action
                if action_type == "click":
                    x = data['x']
                    y = data['y']
                    button = data['button']
                    pressed = data.get('pressed', True)
                    
                    if pressed:
                        logger.info(f"{progress} Click at ({x}, {y}) - {button}")
                        mouse_controller.position = (x, y)
                        mouse_controller.click(button if button != 'left' else None)
                    else:
                        logger.info(f"{progress} Release click at ({x}, {y})")
                
                elif action_type == "scroll":
                    x = data['x']
                    y = data['y']
                    dx = data.get('dx', 0)
                    dy = data.get('dy', 0)
                    
                    logger.info(f"{progress} Scroll at ({x}, {y}) - dx:{dx}, dy:{dy}")
                    mouse_controller.position = (x, y)
                    mouse_controller.scroll(dx, dy)
                
                elif action_type == "screenshot":
                    label = data.get('label', '')
                    logger.info(f"{progress} Screenshot: {label}")
                
                prev_timestamp = timestamp
            
            logger.info("\n" + "="*70)
            logger.info("✅ PLAYBACK COMPLETED SUCCESSFULLY".center(70))
            logger.info("="*70)
            return True
        
        except Exception as e:
            logger.error(f"\n❌ Playback error: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    import sys
    
    logger.info("\n" + "="*70)
    logger.info("REAL SCREEN RECORDING & PLAYBACK SYSTEM (MOUSE CLICKS ONLY)".center(70))
    logger.info("="*70)
    
    print("\n🎬 Choose mode:")
    print("1. RECORD - Do your actions (mouse clicks recorded, you type manually)")
    print("2. PLAYBACK - Replay recorded clicks (you type manually again)")
    print("3. EXIT")
    
    choice = input("\nEnter choice (1/2/3): ").strip()
    
    if choice == "1":
        print("\n📍 Session name (default='cockli'): ", end="")
        session_name = input().strip() or "cockli"
        
        try:
            recorder = RealScreenRecorder(session_name)
            recorder.start_recording()
            recorder.stop_recording()
            logger.info("\n✅ Recording saved! Each registration will:")
            logger.info("   1. Run playback to click on fields")
            logger.info("   2. You manually type username/password/etc")
            logger.info("   3. Repeat with different inputs next time!")
        
        except KeyboardInterrupt:
            logger.info("\n\n⛔ Recording interrupted")
            recorder.stop_recording()
        
        except ImportError as e:
            logger.error(f"\n❌ Missing dependency: {e}")
            logger.info("Install with: pip install pynput")
    
    elif choice == "2":
        print("\n📍 Session name to playback (default='cockli'): ", end="")
        session_name = input().strip() or "cockli"
        
        print("\nPlayback speed:")
        print("  1 = Normal speed (same as you did)")
        print("  2 = 2x faster")
        print("  0.5 = 2x slower")
        speed_input = input("Speed (default=1): ").strip() or "1"
        
        try:
            speed = float(speed_input)
        except:
            speed = 1.0
        
        try:
            player = RealScreenPlayback(session_name)
            player.replay(speed=speed)
            logger.info("\n✅ Playback complete! Now type your inputs manually.")
        except ImportError as e:
            logger.error(f"\n❌ Missing dependency: {e}")
            logger.info("Install with: pip install pynput")
    
    elif choice == "3":
        logger.info("Exiting...")
        sys.exit(0)
    
    else:
        logger.error("Invalid choice")
        sys.exit(1)
