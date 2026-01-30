#!/usr/bin/env python3
"""Test pyqt5_wrapper API fixes."""

import sys
from modules.pyqt5_wrapper import SharpWindow

# Test the fixed add_label() API
print("Testing pyqt5_wrapper API fixes")
print("=" * 50)

# Create a window
win = SharpWindow("Test Window", 400, 300)

# Test 1: add_label with just text (primary parameter)
print("\nTest 1: add_label() with text only")
try:
    win.add_label("Welcome to Sharp GUI!")
    print("✓ add_label('Welcome to Sharp GUI!') works!")
except TypeError as e:
    print(f"✗ Error: {e}")

# Test 2: add_label with text and name
print("\nTest 2: add_label() with text and name")
try:
    win.add_label("Status: Ready", name="status_label")
    print("✓ add_label('Status: Ready', name='status_label') works!")
except TypeError as e:
    print(f"✗ Error: {e}")

# Test 3: add_button with callback
print("\nTest 3: add_button() with text and callback")
try:
    def on_click():
        print("Button clicked!")
    win.add_button("Click me!", callback=on_click)
    print("✓ add_button('Click me!', callback=on_click) works!")
except TypeError as e:
    print(f"✗ Error: {e}")

# Test 4: add_textbox
print("\nTest 4: add_textbox() with placeholder")
try:
    win.add_textbox(placeholder="Enter your name")
    print("✓ add_textbox(placeholder='Enter your name') works!")
except TypeError as e:
    print(f"✗ Error: {e}")

# Test 5: add_textarea
print("\nTest 5: add_textarea() with text")
try:
    win.add_textarea(text="Hello World!\nThis is a text area.")
    print("✓ add_textarea(text='...') works!")
except TypeError as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 50)
print("All tests completed!")

# Exit without showing GUI
sys.exit(0)
