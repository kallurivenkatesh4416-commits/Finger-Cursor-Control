#!/usr/bin/env python3
"""
Hand Gesture Cursor Control
A real-time application using MediaPipe and OpenCV to control the system mouse cursor.
Features:
- Smooth cursor tracking using index finger
- Pinch-to-click gesture (thumb and index finger)
- Gesture-based pause/resume (closed fist)
"""

import cv2
import mediapipe as mp
import pyautogui
import math
import time
try:
    import config
except ImportError:
    # Use default config if config.py not found
    class config:
        MIN_DETECTION_CONFIDENCE = 0.7
        MIN_TRACKING_CONFIDENCE = 0.7
        MAX_NUM_HANDS = 1
        SMOOTH_FACTOR = 5
        PINCH_THRESHOLD = 0.05
        CLICK_COOLDOWN = 0.3
        PAUSE_COOLDOWN = 0.5
        CAMERA_INDEX = 0
        SHOW_LANDMARKS = True
        PYAUTOGUI_FAILSAFE = True
        PYAUTOGUI_PAUSE = 0.001

# Configure PyAutoGUI
pyautogui.FAILSAFE = config.PYAUTOGUI_FAILSAFE
pyautogui.PAUSE = config.PYAUTOGUI_PAUSE

class HandCursorController:
    def __init__(self):
        # Initialize MediaPipe Hand solution
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=config.MAX_NUM_HANDS,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Get screen dimensions
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Smoothing parameters
        self.smooth_factor = config.SMOOTH_FACTOR
        self.prev_x, self.prev_y = 0, 0
        
        # Click state
        self.click_performed = False
        self.click_cooldown = config.CLICK_COOLDOWN
        self.last_click_time = 0
        
        # Pause state
        self.paused = False
        self.pause_cooldown = config.PAUSE_COOLDOWN
        self.last_pause_toggle = 0
        
        # Other settings
        self.pinch_threshold = config.PINCH_THRESHOLD
        self.show_landmarks = config.SHOW_LANDMARKS
        
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)
    
    def is_fist_closed(self, hand_landmarks):
        """Detect if hand is in a closed fist (all fingers folded)"""
        # Get finger tips and their corresponding base points
        finger_tips = [8, 12, 16, 20]  # Index, middle, ring, pinky tips
        finger_mcp = [5, 9, 13, 17]    # Corresponding knuckles
        
        # Count folded fingers
        folded_count = 0
        for tip, mcp in zip(finger_tips, finger_mcp):
            tip_y = hand_landmarks.landmark[tip].y
            mcp_y = hand_landmarks.landmark[mcp].y
            # Finger is folded if tip is below (higher y value) the knuckle
            if tip_y > mcp_y:
                folded_count += 1
        
        # Also check thumb
        thumb_tip = hand_landmarks.landmark[4]
        thumb_mcp = hand_landmarks.landmark[2]
        if thumb_tip.x < thumb_mcp.x:  # For right hand
            folded_count += 1
        
        # Consider it a fist if at least 4 fingers are folded
        return folded_count >= 4
    
    def smooth_coordinates(self, x, y):
        """Apply smoothing to cursor movement"""
        smooth_x = self.prev_x + (x - self.prev_x) / self.smooth_factor
        smooth_y = self.prev_y + (y - self.prev_y) / self.smooth_factor
        
        self.prev_x = smooth_x
        self.prev_y = smooth_y
        
        return int(smooth_x), int(smooth_y)
    
    def process_frame(self, frame):
        """Process a single frame for hand detection and gesture recognition"""
        # Flip the frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame with MediaPipe
        results = self.hands.process(rgb_frame)
        
        # Check for hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks if enabled
                if self.show_landmarks:
                    self.mp_draw.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS
                    )
                
                # Check for fist gesture (pause/resume)
                current_time = time.time()
                if self.is_fist_closed(hand_landmarks):
                    if current_time - self.last_pause_toggle > self.pause_cooldown:
                        self.paused = not self.paused
                        self.last_pause_toggle = current_time
                        status = "PAUSED" if self.paused else "ACTIVE"
                        print(f"Gesture Control: {status}")
                
                # If paused, skip cursor control
                if self.paused:
                    cv2.putText(frame, "PAUSED", (10, 70), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    continue
                
                # Get index finger tip (landmark 8) for cursor control
                index_finger_tip = hand_landmarks.landmark[8]
                
                # Convert normalized coordinates to screen coordinates
                x = int(index_finger_tip.x * self.screen_width)
                y = int(index_finger_tip.y * self.screen_height)
                
                # Apply smoothing
                smooth_x, smooth_y = self.smooth_coordinates(x, y)
                
                # Move cursor
                pyautogui.moveTo(smooth_x, smooth_y, duration=0)
                
                # Draw index finger position on frame
                index_x = int(index_finger_tip.x * w)
                index_y = int(index_finger_tip.y * h)
                cv2.circle(frame, (index_x, index_y), 10, (0, 255, 0), -1)
                
                # Check for pinch gesture (click)
                thumb_tip = hand_landmarks.landmark[4]
                distance = self.calculate_distance(thumb_tip, index_finger_tip)
                
                # Use configured pinch threshold
                if distance < self.pinch_threshold:
                    # Draw line between thumb and index finger
                    thumb_x = int(thumb_tip.x * w)
                    thumb_y = int(thumb_tip.y * h)
                    cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), 
                            (0, 255, 255), 3)
                    
                    # Perform click with cooldown
                    if not self.click_performed and (current_time - self.last_click_time > self.click_cooldown):
                        pyautogui.click()
                        self.click_performed = True
                        self.last_click_time = current_time
                        print("Click performed!")
                        
                    cv2.putText(frame, "CLICK", (10, 110), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                else:
                    self.click_performed = False
        
        # Display status
        status_text = "PAUSED" if self.paused else "ACTIVE"
        status_color = (0, 0, 255) if self.paused else (0, 255, 0)
        cv2.putText(frame, f"Status: {status_text}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
        
        return frame
    
    def run(self):
        """Main loop to capture video and process gestures"""
        cap = cv2.VideoCapture(config.CAMERA_INDEX)
        
        if not cap.isOpened():
            print("Error: Could not open webcam")
            return
        
        print("Hand Gesture Cursor Control Started")
        print("Controls:")
        print("  - Move index finger to control cursor")
        print("  - Pinch thumb and index finger to click")
        print("  - Close fist to pause/resume")
        print("  - Press 'q' to quit")
        print("-" * 50)
        
        try:
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    print("Error: Failed to capture frame")
                    break
                
                # Process the frame
                processed_frame = self.process_frame(frame)
                
                # Display the frame
                cv2.imshow("Hand Gesture Cursor Control", processed_frame)
                
                # Exit on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            self.hands.close()
            print("Application closed")

def main():
    controller = HandCursorController()
    controller.run()

if __name__ == "__main__":
    main()
