"""
Configuration file for Hand Gesture Cursor Control
Adjust these parameters to customize the behavior of the application.
"""

# MediaPipe Hand Detection Settings
MIN_DETECTION_CONFIDENCE = 0.7  # Minimum confidence for initial hand detection (0.0 to 1.0)
MIN_TRACKING_CONFIDENCE = 0.7   # Minimum confidence for hand tracking (0.0 to 1.0)
MAX_NUM_HANDS = 1               # Maximum number of hands to detect

# Cursor Movement Settings
SMOOTH_FACTOR = 5               # Higher = smoother but slower response (1-10 recommended)

# Click Detection Settings
PINCH_THRESHOLD = 0.05          # Maximum distance for pinch detection (0.01-0.1 recommended)
CLICK_COOLDOWN = 0.3            # Minimum time between clicks in seconds

# Pause/Resume Settings
PAUSE_COOLDOWN = 0.5            # Minimum time between pause toggles in seconds

# Camera Settings
CAMERA_INDEX = 0                # Camera device index (0 for default camera)
CAMERA_WIDTH = None             # Camera capture width (None for default)
CAMERA_HEIGHT = None            # Camera capture height (None for default)

# Display Settings
SHOW_LANDMARKS = True           # Show hand landmark connections
WINDOW_NAME = "Hand Gesture Cursor Control"

# PyAutoGUI Settings
PYAUTOGUI_FAILSAFE = True       # Enable failsafe (move to corner to abort)
PYAUTOGUI_PAUSE = 0.001         # Pause between PyAutoGUI calls
