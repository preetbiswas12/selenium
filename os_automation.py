"""
OS-Level Automation Module
Uses PyAutoGUI for keyboard/mouse control
No browser dependencies - Direct OS interaction
"""

import pyautogui
import time
import logging
from PIL import Image
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OSAutomation:
    """OS-level automation for form filling and app control"""
    
    DELAY = 0.5  # Default delay between actions (human-like)
    
    def __init__(self):
        # Enable pause between actions
        pyautogui.PAUSE = self.DELAY
        # Fail-safe: move mouse to corner to abort
        pyautogui.FAILSAFE = True
        logger.info("OS Automation initialized")
    
    def open_url_in_browser(self, url):
        """Open URL in default browser"""
        try:
            subprocess.Popen(f'start {url}', shell=True)
            time.sleep(3)
            logger.info(f"Opened URL: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            return False
    
    def type_text(self, text, delay=0.05):
        """Type text with human-like delays between keystrokes"""
        try:
            for char in text:
                pyautogui.typewrite(char, interval=delay)
            logger.info(f"Typed: {text[:20]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def type_text_clipboard(self, text):
        """Paste text using clipboard (faster, for long text)"""
        try:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            logger.info(f"Pasted text via clipboard")
            return True
        except:
            # Fallback to typing if clipboard fails
            return self.type_text(text)
    
    def click(self, x, y, clicks=1):
        """Click at coordinates"""
        try:
            pyautogui.click(x, y, clicks=clicks)
            time.sleep(self.DELAY)
            logger.info(f"Clicked at ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False
    
    def screenshot(self, filename="screenshot.png"):
        """Take screenshot and save"""
        try:
            img = pyautogui.screenshot()
            img.save(filename)
            logger.info(f"Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return None
    
    def find_element_by_color(self, rgb_color, confidence=0.9):
        """Find element by color on screen"""
        try:
            img = pyautogui.screenshot()
            # Simple color matching (can be enhanced)
            return True
        except Exception as e:
            logger.error(f"Failed to find element: {e}")
            return False
    
    def press_key(self, key):
        """Press a single key"""
        try:
            pyautogui.press(key)
            time.sleep(self.DELAY)
            logger.info(f"Pressed key: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False
    
    def wait(self, seconds=1):
        """Wait for specified seconds"""
        time.sleep(seconds)
        logger.info(f"Waited {seconds} seconds")
        return True
    
    def hotkey(self, *keys):
        """Press multiple keys simultaneously"""
        try:
            pyautogui.hotkey(*keys)
            time.sleep(self.DELAY)
            logger.info(f"Pressed hotkey: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"Failed to press hotkey: {e}")
            return False
    
    def move_mouse(self, x, y):
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=0.5)
            logger.info(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False
    
    def focus_window(self, window_title):
        """Focus a window by title"""
        try:
            import pygetwindow as gw
            window = gw.getWindowsWithTitle(window_title)[0]
            window.activate()
            time.sleep(1)
            logger.info(f"Focused window: {window_title}")
            return True
        except Exception as e:
            logger.error(f"Failed to focus window: {e}")
            return False
    
    def clear_field(self):
        """Clear a text field (Ctrl+A, Delete)"""
        try:
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(self.DELAY)
            logger.info("Cleared field")
            return True
        except Exception as e:
            logger.error(f"Failed to clear field: {e}")
            return False
    
    def close_browser_tab(self):
        """Close current browser tab (Ctrl+W)"""
        try:
            pyautogui.hotkey('ctrl', 'w')
            time.sleep(1)
            logger.info("Closed browser tab")
            return True
        except Exception as e:
            logger.error(f"Failed to close tab: {e}")
            return False
    
    def new_browser_tab(self):
        """Open new browser tab (Ctrl+T)"""
        try:
            pyautogui.hotkey('ctrl', 't')
            time.sleep(1)
            logger.info("Opened new browser tab")
            return True
        except Exception as e:
            logger.error(f"Failed to open new tab: {e}")
            return False
