# SOCD cleaner v1.0.1 (snap tap) script for python as Autohotkey wasn't reliable enough.
#
# setup instructions
# pip install interception-python==1.5.2 / ref:https://github.com/kennyhml/pyinterception
# pip install pywin32
# install driver as instructed -> https://github.com/oblitum/Interception
# reboot

import interception

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

def handle_key_stroke(context, device, stroke, key_state, opposite_keys):
    """
    Handles the key stroke event by managing opposite key presses.
    
    Args:
        context (Interception): The interception context.
        device (int): The device ID from which the event was captured.
        stroke (KeyStroke): The key stroke event.
        key_state (dict): Dictionary to track the state of keys.
        opposite_keys (dict): Dictionary to map each key to its opposite direction.
    """
    KeyStroke = interception.KeyStroke
    KeyFlag = interception.KeyFlag

    if isinstance(stroke, KeyStroke):  # Ensure the stroke is a keyboard event
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

def main():
    """
    Main function to initialize interception and handle key strokes in an infinite loop.
    """
    context = initialize_interception()
    key_state, opposite_keys = create_key_mappings()

    while True:
        try:
            device = context.await_input()  # Wait for a key event from any device
            if device is None:  # Unlikely case: No device event detected, skip to the next loop iteration
                continue

            stroke = context.devices[device].receive()  # Receive the key stroke event
            if stroke is None:  # Unlikely case: No key stroke data received, skip to the next loop iteration
                continue

            handle_key_stroke(context, device, stroke, key_state, opposite_keys)
        except Exception as e:
            print(f"Error: {e}")  # Print any error that occurs during the loop

if __name__ == "__main__":
    main()
