"""Global hotkey support for AlfredPy using pynput."""

import threading
import time
from typing import Callable, Optional
import sys

try:
    from pynput import keyboard
    HAS_PYNPUT = True
except ImportError:
    HAS_PYNPUT = False
    print("⚠️  pynput not installed. Install with: pip install pynput")


class GlobalHotkeyManager:
    """Manage global hotkeys for launcher."""

    def __init__(self, hotkey: str = "<alt>+<space>"):
        self.hotkey = hotkey
        self.callback: Optional[Callable] = None
        self.listener: Optional[keyboard.Listener] = None
        self.active = False
        self._current_keys = set()

    def register(self, callback: Callable) -> bool:
        """Register callback for hotkey activation."""
        if not HAS_PYNPUT:
            return False

        self.callback = callback

        try:
            self.listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release,
                suppress=False,
            )
            self.listener.start()
            self.active = True
            print(f"✅ Hotkey registered: {self.hotkey}")
            return True
        except Exception as e:
            print(f"❌ Failed to register hotkey: {e}")
            return False

    def unregister(self):
        """Unregister hotkey."""
        if self.listener:
            self.listener.stop()
            self.listener = None
        self.active = False
        self._current_keys.clear()

    def _on_press(self, key):
        """Handle key press."""
        try:
            self._current_keys.add(key)

            # Check if hotkey combination is pressed
            if self._is_hotkey_pressed():
                if self.callback:
                    # Run callback in separate thread to avoid blocking
                    threading.Thread(target=self.callback, daemon=True).start()

                # Clear keys to prevent repeated triggering
                self._current_keys.clear()
        except AttributeError:
            pass

    def _on_release(self, key):
        """Handle key release."""
        try:
            self._current_keys.discard(key)
        except AttributeError:
            pass

    def _is_hotkey_pressed(self) -> bool:
        """Check if hotkey combination is currently pressed."""
        if not self.callback:
            return False

        # Parse hotkey string (e.g., "<alt>+<space>")
        hotkey_parts = self.hotkey.lower().replace("<", "").replace(">", "").split("+")

        key_map = {
            "ctrl": [keyboard.Key.ctrl, keyboard.Key.ctrl_l, keyboard.Key.ctrl_r],
            "alt": [keyboard.Key.alt, keyboard.Key.alt_l, keyboard.Key.alt_r],
            "shift": [keyboard.Key.shift, keyboard.Key.shift_l, keyboard.Key.shift_r],
            "cmd": [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r],
            "win": [keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r],
            "space": [keyboard.Key.space],
        }

        required_modifier_keys = []
        for part in hotkey_parts:
            if part in key_map:
                required_modifier_keys.extend(key_map[part])

        # Check if all modifier keys are pressed
        modifiers_pressed = any(k in self._current_keys for k in required_modifier_keys)

        # Check for space key
        if "space" in hotkey_parts:
            space_pressed = keyboard.Key.space in self._current_keys
            return modifiers_pressed and space_pressed

        return modifiers_pressed


def create_launcher_callback(launch_func, args=None):
    """Create a callback function for launching the app."""
    def callback():
        try:
            print("🚀 Launching AlfredPy...")
            launch_func(*(args or []))
        except Exception as e:
            print(f"❌ Launch failed: {e}")

    return callback


if __name__ == "__main__":
    # Test hotkey listener
    def test_callback():
        print("🔔 Hotkey activated! (Alt+Space)")

    manager = GlobalHotkeyManager("<alt>+<space>")
    if manager.register(test_callback):
        print("Listening for hotkeys... Press Alt+Space to test")
        print("Press Ctrl+C to exit")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            manager.unregister()
            print("\n✅ Hotkey listener stopped")
    else:
        print("Failed to start hotkey listener")
