"""
Finger Cursor Control
=====================
Control your mouse cursor using hand gestures!

GESTURES:
- Index finger up: Move cursor
- Pinch (index + thumb together): Left click
- Two fingers up (index + middle): Right click
- Fist: Pause/stop tracking
- Open palm: Start/resume tracking

Press Q to quit.
"""

import cv2
import numpy as np
import urllib.request
from pathlib import Path
import time

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import pyautogui

# Disable pyautogui fail-safe (corner trips were closing app)
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0  # No delay between actions

# -----------------------------
# Settings
# -----------------------------
HAND_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
HAND_MODEL_PATH = Path("hand_landmarker.task")

# Cursor control settings
SMOOTHING = 6              # Higher = smoother but slower cursor (1-10)
SPEED_GAIN = 2.1           # Increase amplification for larger on-screen travel
SAFE_EDGE = 0.02           # Allow closer to edges for more area
MAX_STEP = 180             # Allow larger per-frame travel (still clamped)
DEADZONE = 8               # Ignore tiny jitter (pixels)
CLICK_THRESHOLD = 0.05     # Distance threshold for pinch detection
FRAME_MARGIN = 0.05        # Margin from frame edges (0.0-0.5)

# Screen size
SCREEN_W, SCREEN_H = pyautogui.size()

# Landmark indices
INDEX_TIP = 8
THUMB_TIP = 4
MIDDLE_TIP = 12
INDEX_PIP = 6
MIDDLE_PIP = 10


def ensure_hand_model():
    """Download hand landmarker model if not present."""
    if HAND_MODEL_PATH.exists():
        return
    print("Downloading hand_landmarker.task ...")
    urllib.request.urlretrieve(HAND_MODEL_URL, HAND_MODEL_PATH.as_posix())
    print("Downloaded:", HAND_MODEL_PATH.resolve())


class FingerCursor:
    def __init__(self):
        self.prev_x, self.prev_y = SCREEN_W // 2, SCREEN_H // 2
        self.smooth_x, self.smooth_y = SCREEN_W // 2, SCREEN_H // 2
        self.first_move = True  # Align cursor to first detected hand position
        self.is_clicking = False
        self.is_right_clicking = False
        self.tracking_active = True
        self.last_click_time = 0
        
    def get_finger_states(self, landmarks, handedness):
        """Determine which fingers are up."""
        states = {}
        
        # Get landmark positions
        def lm(i):
            return landmarks[i].x, landmarks[i].y
        
        # Thumb: compare x positions based on handedness
        thumb_tip_x, _ = lm(THUMB_TIP)
        thumb_ip_x, _ = lm(3)
        if handedness == "Right":
            states["thumb"] = thumb_tip_x > thumb_ip_x
        else:
            states["thumb"] = thumb_tip_x < thumb_ip_x
        
        # Other fingers: tip y < pip y means finger is up
        for finger, tip, pip in [
            ("index", INDEX_TIP, INDEX_PIP),
            ("middle", MIDDLE_TIP, MIDDLE_PIP),
            ("ring", 16, 14),
            ("pinky", 20, 18)
        ]:
            _, tip_y = lm(tip)
            _, pip_y = lm(pip)
            states[finger] = tip_y < pip_y
            
        return states
    
    def get_pinch_distance(self, landmarks):
        """Get distance between index tip and thumb tip."""
        index_x, index_y = landmarks[INDEX_TIP].x, landmarks[INDEX_TIP].y
        thumb_x, thumb_y = landmarks[THUMB_TIP].x, landmarks[THUMB_TIP].y
        return np.sqrt((index_x - thumb_x)**2 + (index_y - thumb_y)**2)
    
    def map_to_screen(self, x, y, frame_w, frame_h):
        """Map camera coordinates to screen coordinates with margin and safety edge."""
        # Apply margin
        x_min, x_max = FRAME_MARGIN, 1 - FRAME_MARGIN
        y_min, y_max = FRAME_MARGIN, 1 - FRAME_MARGIN
        
        # Clamp to margins
        x = max(x_min, min(x_max, x))
        y = max(y_min, min(y_max, y))
        
        # Map to screen with safety edge to avoid exact corners
        screen_x = np.interp(x, [x_min, x_max], [SAFE_EDGE * SCREEN_W, (1 - SAFE_EDGE) * SCREEN_W])
        screen_y = np.interp(y, [y_min, y_max], [SAFE_EDGE * SCREEN_H, (1 - SAFE_EDGE) * SCREEN_H])
        
        return int(screen_x), int(screen_y)
    
    def smooth_cursor(self, x, y):
        """Apply smoothing to cursor movement."""
        self.smooth_x += (x - self.smooth_x) / SMOOTHING
        self.smooth_y += (y - self.smooth_y) / SMOOTHING
        return int(self.smooth_x), int(self.smooth_y)
    
    def process_hand(self, landmarks, handedness, frame_w, frame_h):
        """Process hand landmarks and control cursor."""
        states = self.get_finger_states(landmarks, handedness)
        num_fingers_up = sum(states.values())
        
        # Detect gestures
        index_up = states["index"]
        middle_up = states["middle"]
        thumb_up = states["thumb"]
        
        # FIST: Pause tracking
        if num_fingers_up <= 1 and not index_up:
            if self.tracking_active:
                print("[GESTURE] Fist - Tracking PAUSED")
            self.tracking_active = False
            return "PAUSED", None
        
        # OPEN PALM: Resume tracking
        if num_fingers_up >= 4:
            if not self.tracking_active:
                print("[GESTURE] Open Palm - Tracking RESUMED")
            self.tracking_active = True
            return "READY", None
        
        if not self.tracking_active:
            return "PAUSED", None
        
        # Get index finger position for cursor
        index_x = landmarks[INDEX_TIP].x
        index_y = landmarks[INDEX_TIP].y
        
        # Map to screen
        screen_x, screen_y = self.map_to_screen(index_x, index_y, frame_w, frame_h)

        # On first move, align cursor to hand to avoid jump to corner
        if self.first_move:
            self.prev_x = self.smooth_x = screen_x
            self.prev_y = self.smooth_y = screen_y
            self.first_move = False

        # Amplify small finger movement to cover more screen area
        amp_x = self.prev_x + (screen_x - self.prev_x) * SPEED_GAIN
        amp_y = self.prev_y + (screen_y - self.prev_y) * SPEED_GAIN

        # Deadzone to kill jitter
        if abs(amp_x - self.prev_x) < DEADZONE:
            amp_x = self.prev_x
        if abs(amp_y - self.prev_y) < DEADZONE:
            amp_y = self.prev_y

        # Clamp step to avoid big jumps per frame
        amp_dx = np.clip(amp_x - self.prev_x, -MAX_STEP, MAX_STEP)
        amp_dy = np.clip(amp_y - self.prev_y, -MAX_STEP, MAX_STEP)
        amp_x = self.prev_x + amp_dx
        amp_y = self.prev_y + amp_dy

        self.prev_x, self.prev_y = amp_x, amp_y

        # Smooth and move cursor
        smooth_x, smooth_y = self.smooth_cursor(amp_x, amp_y)
        
        # Move cursor
        pyautogui.moveTo(smooth_x, smooth_y)
        
        # PINCH: Left click
        pinch_dist = self.get_pinch_distance(landmarks)
        if pinch_dist < CLICK_THRESHOLD:
            if not self.is_clicking:
                now = time.time()
                if now - self.last_click_time > 0.3:  # Debounce
                    pyautogui.click()
                    print("[GESTURE] Pinch - LEFT CLICK")
                    self.last_click_time = now
                self.is_clicking = True
            return "CLICK", (smooth_x, smooth_y)
        else:
            self.is_clicking = False
        
        # TWO FINGERS (index + middle): Right click
        if index_up and middle_up and not states["ring"] and not states["pinky"]:
            if not self.is_right_clicking:
                now = time.time()
                if now - self.last_click_time > 0.5:  # Debounce
                    pyautogui.rightClick()
                    print("[GESTURE] Two Fingers - RIGHT CLICK")
                    self.last_click_time = now
                self.is_right_clicking = True
            return "RIGHT CLICK", (smooth_x, smooth_y)
        else:
            self.is_right_clicking = False
        
        # Just moving
        return "MOVING", (smooth_x, smooth_y)


def main():
    ensure_hand_model()
    
    # Setup hand landmarker
    base_options = python.BaseOptions(model_asset_path=HAND_MODEL_PATH.as_posix())
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,  # Track only one hand for cursor
        min_hand_detection_confidence=0.7,
        min_hand_presence_confidence=0.7,
        min_tracking_confidence=0.7,
    )
    hand_landmarker = vision.HandLandmarker.create_from_options(options)
    
    # Initialize cursor controller
    cursor = FingerCursor()
    
    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")
    
    print("=" * 50)
    print("FINGER CURSOR CONTROL")
    print("=" * 50)
    print("GESTURES:")
    print("  - Point (index up): Move cursor")
    print("  - Pinch (index + thumb): Left click")
    print("  - Two fingers (index + middle): Right click")
    print("  - Fist: Pause tracking")
    print("  - Open palm: Resume tracking")
    print("")
    print("Press Q to quit")
    print("Move mouse to screen corner = emergency stop")
    print("=" * 50)
    
    timestamp_ms = 0
    
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Process with MediaPipe
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms += 33
        
        result = hand_landmarker.detect_for_video(mp_image, timestamp_ms)
        
        status = "No hand detected"
        
        if result.hand_landmarks:
            hand_lms = result.hand_landmarks[0]
            handedness = "Right"
            if result.handedness and len(result.handedness) > 0:
                handedness = result.handedness[0][0].category_name
            
            # Process hand and control cursor
            status, pos = cursor.process_hand(hand_lms, handedness, w, h)
            
            # Draw landmarks
            for i, lm in enumerate(hand_lms):
                x, y = int(lm.x * w), int(lm.y * h)
                color = (0, 255, 0) if i == INDEX_TIP else (0, 200, 200)
                radius = 8 if i == INDEX_TIP else 4
                cv2.circle(frame, (x, y), radius, color, -1)
            
            # Draw connections
            connections = [
                (0, 1), (1, 2), (2, 3), (3, 4),  # thumb
                (0, 5), (5, 6), (6, 7), (7, 8),  # index
                (0, 9), (9, 10), (10, 11), (11, 12),  # middle
                (0, 13), (13, 14), (14, 15), (15, 16),  # ring
                (0, 17), (17, 18), (18, 19), (19, 20),  # pinky
                (5, 9), (9, 13), (13, 17)  # palm
            ]
            for c1, c2 in connections:
                x1, y1 = int(hand_lms[c1].x * w), int(hand_lms[c1].y * h)
                x2, y2 = int(hand_lms[c2].x * w), int(hand_lms[c2].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 200, 200), 2)
            
            # Draw pinch indicator
            thumb_x, thumb_y = int(hand_lms[THUMB_TIP].x * w), int(hand_lms[THUMB_TIP].y * h)
            index_x, index_y = int(hand_lms[INDEX_TIP].x * w), int(hand_lms[INDEX_TIP].y * h)
            pinch_dist = cursor.get_pinch_distance(hand_lms)
            pinch_color = (0, 255, 0) if pinch_dist < CLICK_THRESHOLD else (0, 0, 255)
            cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), pinch_color, 3)
        
        # Draw status
        color = (0, 255, 0) if "MOVING" in status or "CLICK" in status else (0, 165, 255)
        cv2.putText(frame, f"Status: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        cv2.putText(frame, "Finger Cursor Control | Q to quit", (10, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Show frame
        cv2.imshow("Finger Cursor", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in [ord('q'), ord('Q')]:
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("Finger cursor stopped.")


if __name__ == "__main__":
    main()
