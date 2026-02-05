#!/usr/bin/env python3
"""
Demo script for Hand Gesture Cursor Control
This script demonstrates basic usage of the hand cursor controller.
"""

from hand_cursor_control import HandCursorController

def main():
    print("=" * 60)
    print("Hand Gesture Cursor Control - Demo")
    print("=" * 60)
    print()
    print("This demo will start the hand gesture cursor control.")
    print()
    print("Instructions:")
    print("  1. Position yourself in front of your webcam")
    print("  2. Show your hand to the camera")
    print("  3. Move your index finger to move the cursor")
    print("  4. Pinch thumb and index finger together to click")
    print("  5. Close your fist to pause/resume cursor control")
    print("  6. Press 'q' to exit the application")
    print()
    print("Tips for best results:")
    print("  - Ensure good lighting")
    print("  - Keep your hand at a comfortable distance from camera")
    print("  - Make clear, deliberate gestures")
    print("=" * 60)
    print()
    
    input("Press Enter to start...")
    
    # Create and run the controller
    controller = HandCursorController()
    controller.run()

if __name__ == "__main__":
    main()
