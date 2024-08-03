# SOCD cleaner v1.0.0 (snap tap) script for python as Autohotkey wasn't reliable enough.
# This version adds a tray icon with context menu for toggling of the SOCD cleaning function.
#
# setup instructions
# pip install interception-python==1.5.2 / ref:https://github.com/kennyhml/pyinterception
# pip install pywin32
# install driver as instructed -> https://github.com/oblitum/Interception
# reboot

# SOCD cleaner v1 (snap tap) script for python as Autohotkey wasn't reliable enough.
#
# setup instructions
# pip install interception-python==1.5.2 / ref:https://github.com/kennyhml/pyinterception
# pip install pywin32
# install driver as instructed -> https://github.com/oblitum/Interception
# reboot

import interception
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item, Menu
import threading
import os


def initialize_interception():
    """
    Initializes the interception context and sets up device filters.
    
    Returns:
        context (Interception): The interception context object.
    """
    interception.auto_capture_devices(keyboard=True)  # Automatically captures keyboard devices
    context = interception.Interception()
    context.set_filter(interception.is_keyboard, interception.FilterKeyFlag.FILTER_KEY_ALL)  # Filter to capture all keyboard events
    return context

def create_key_mappings():
    """
    Creates the key state dictionary and opposite key mappings.
    
    Returns:
        key_state (dict): Dictionary to track the state of keys (True if pressed, False if released).
        opposite_keys (dict): Dictionary to map each key to its opposite direction.
    """
    key_map = interception.KEYBOARD_MAPPING  # Mapping from characters to key codes
    key_state = {key_map[char]: False for char in 'wasd'}  # Initialize key state for 'W', 'A', 'S', 'D' keys
    opposite_keys = {
        key_map['w']: key_map['s'],
        key_map['a']: key_map['d'],
        key_map['s']: key_map['w'],
        key_map['d']: key_map['a'],
    }
    return key_state, opposite_keys

def handle_key_stroke(context, device, stroke, key_state, opposite_keys, intercepting):
    """
    Handles the key stroke event by managing opposite key presses.
    
    Args:
        context (Interception): The interception context.
        device (int): The device ID from which the event was captured.
        stroke (KeyStroke): The key stroke event.
        key_state (dict): Dictionary to track the state of keys.
        opposite_keys (dict): Dictionary to map each key to its opposite direction.
        intercepting (bool): Whether the script is currently intercepting key presses.
    """
    KeyStroke = interception.KeyStroke
    KeyFlag = interception.KeyFlag

    if intercepting and isinstance(stroke, KeyStroke):  # Ensure the stroke is a keyboard event and interception is active
        key = stroke.code
        state = stroke.flags

        if key in key_state:  # Check if the key is one we're tracking (WASD keys)
            opposite_key = opposite_keys.get(key)  # Get the opposite key

            if state == KeyFlag.KEY_DOWN and not key_state[key]:  # Handle key press
                if key_state.get(opposite_key, False):  # Release the opposite key if it's held down
                    context.send(device, KeyStroke(opposite_key, KeyFlag.KEY_UP))
                key_state[key] = True  # Mark the key as held down

            elif state == KeyFlag.KEY_UP and key_state[key]:  # Handle key release
                key_state[key] = False  # Mark the key as released
                if key_state.get(opposite_key, False):  # Re-press the opposite key if it's held down
                    context.send(device, KeyStroke(opposite_key, KeyFlag.KEY_DOWN))

    context.send(device, stroke)  # Pass through the stroke as it was received

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Keyboard Interception")
        self.root.geometry("300x200")

        # State to track if the main loop is running
        self.is_running = False
        self.main_thread = None

        # State to track if interception is enabled
        self.intercepting = True

        # Create images for active and inactive states
        self.image_active = Image.new('RGB', (64, 64), color=(73, 109, 137))
        self.image_inactive = Image.new('RGB', (64, 64), color=(137, 101, 73))

        # Start the app minimized to tray
        self.root.withdraw()

        # Create the system tray icon
        self.create_tray_icon()

        # Immediately start the main loop in background
        self.start_main_loop()

    def create_tray_icon(self):
        # Create an icon for the tray
        draw = ImageDraw.Draw(self.image_active)

        # Define the tray menu with quit and pause options
        self.menu = Menu(
            item('Pause', self.toggle_socd),
            item('Quit', self.quit_app)
        )

        # Create the tray icon
        self.icon = pystray.Icon("icon", self.image_active, "SOCD cleaner", self.menu)

        # Start the icon in a separate thread
        self.icon.run_detached()

    def main_loop(self):
        """
        Main function to initialize interception and handle key strokes in an infinite loop.
        """
        context = initialize_interception()
        key_state, opposite_keys = create_key_mappings()

        while self.is_running:
            try:
                device = context.await_input()  # Wait for a key event from any device
                if device is None:  # Unlikely case: No device event detected, skip to the next loop iteration
                    continue

                stroke = context.devices[device].receive()  # Receive the key stroke event
                if stroke is None:  # Unlikely case: No key stroke data received, skip to the next loop iteration
                    continue

                handle_key_stroke(context, device, stroke, key_state, opposite_keys, self.intercepting)
            except Exception as e:
                print(f"Error: {e}")    # Print any error that occurs during the loop

    def update_icon(self, condition):
        # Update the icon and menu based on the condition
        self.icon.icon = self.image_active if condition else self.image_inactive
        self.icon.menu = Menu(
            item('Pause' if condition else 'Resume', self.toggle_socd),
            item('Quit', self.quit_app)
        )
        self.icon.update_menu()

    def start_main_loop(self):
        if not self.is_running:
            self.is_running = True  # Set the flag to indicate the loop should run
            self.main_thread = threading.Thread(target=self.main_loop)  # Create a new thread for the main loop
            self.main_thread.start()

    def stop_main_loop(self):
        if self.is_running:
            self.is_running = False # Set the flag to indicate the loop should stop
            self.main_thread.join() # Wait for the main loop thread to finish

    def toggle_socd(self):
        self.intercepting = not self.intercepting
        self.update_icon(self.intercepting)
        state = "enabled" if self.intercepting else "disabled"

    def quit_app(self, *args):
        self.icon.stop()
        self.icon.visible = False
        
        os._exit(0)

if __name__ == "__main__":
    app = App()
    app.root.mainloop()
