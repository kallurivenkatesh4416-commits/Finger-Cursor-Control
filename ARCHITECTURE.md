# Architecture and Data Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Hand Gesture Cursor Control                   │
└─────────────────────────────────────────────────────────────────┘

                              ┌──────────┐
                              │  Webcam  │
                              └────┬─────┘
                                   │ Video Frames
                                   ▼
                         ┌──────────────────┐
                         │   OpenCV         │
                         │   (cv2.VideoCapture)│
                         └────────┬─────────┘
                                  │ BGR Frame
                                  ▼
                         ┌──────────────────┐
                         │  Frame Processing│
                         │  - Flip horizontal│
                         │  - BGR to RGB     │
                         └────────┬─────────┘
                                  │ RGB Frame
                                  ▼
                         ┌──────────────────┐
                         │    MediaPipe     │
                         │  Hand Detection  │
                         └────────┬─────────┘
                                  │ Hand Landmarks
                                  │ (21 points)
                                  ▼
                    ┌─────────────────────────┐
                    │  Gesture Recognition    │
                    │  HandCursorController   │
                    └─────────┬───────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                 │                 │
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Cursor     │  │    Click     │  │    Pause     │
    │   Movement   │  │   Detection  │  │   Detection  │
    │              │  │              │  │              │
    │ Index finger │  │ Pinch gesture│  │ Fist gesture │
    │ tracking     │  │ (thumb+index)│  │ (all folded) │
    └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
           │                 │                 │
           │                 │                 │
           ▼                 ▼                 ▼
    ┌──────────────────────────────────────────────┐
    │              PyAutoGUI                        │
    │         System Mouse Control                  │
    └───────────────────┬──────────────────────────┘
                        │
                        ▼
                ┌────────────────┐
                │   User Screen  │
                │   Cursor moves │
                │   Clicks occur │
                └────────────────┘
```

## Component Details

### 1. Video Input Layer
- **Component**: OpenCV VideoCapture
- **Input**: Webcam video stream
- **Output**: BGR image frames
- **Frame Rate**: 30 FPS typical

### 2. Pre-processing Layer
- **Operations**:
  - Horizontal flip (mirror effect)
  - Color space conversion (BGR → RGB)
- **Purpose**: Prepare frames for MediaPipe

### 3. Hand Detection Layer
- **Component**: MediaPipe Hands
- **Input**: RGB frames
- **Output**: 21 hand landmarks per hand
- **Landmarks Used**:
  - Landmark 4: Thumb tip
  - Landmark 8: Index finger tip
  - Landmarks 5,9,13,17: Knuckles (MCP)
  - Landmarks 12,16,20: Other finger tips

### 4. Gesture Recognition Layer
- **Component**: HandCursorController class
- **Processes**:

#### A. Cursor Movement
```
Index Finger Position → Normalize to Screen → Apply Smoothing → Move Cursor
     (camera space)        (screen space)      (exp. avg.)    (PyAutoGUI)
```

#### B. Click Detection
```
Thumb & Index Position → Calculate Distance → Check Threshold → Perform Click
     (landmarks 4,8)     (Euclidean dist.)   (< 0.05)        (with cooldown)
```

#### C. Pause Detection
```
All Fingers → Count Folded → Check Count → Toggle Pause
 (tips+MCP)   (Y position)   (>= 4)      (with cooldown)
```

### 5. Output Layer
- **Component**: PyAutoGUI
- **Actions**:
  - `moveTo(x, y)`: Move cursor
  - `click()`: Perform left-click
- **Failsafe**: Move to corner to abort

## Data Flow Sequence

```
1. Capture Frame
   │
2. Preprocess (flip, convert color)
   │
3. Detect Hand (MediaPipe)
   │
4. Extract Landmarks
   │
5. Check Pause Gesture
   ├─ If fist: Toggle pause state
   │
6. If not paused:
   │
   ├─ Get Index Finger Position
   │  ├─ Map to screen coordinates
   │  ├─ Apply smoothing
   │  └─ Move cursor
   │
   └─ Check Pinch Gesture
      ├─ Calculate thumb-index distance
      ├─ If distance < threshold
      └─ Perform click (with cooldown)
   │
7. Draw Visualizations
   │
8. Display Frame
   │
9. Check for quit command
   │
10. Repeat from step 1
```

## State Management

### Controller State Variables
```python
self.prev_x, self.prev_y         # Previous cursor position (smoothing)
self.click_performed             # Current click state
self.last_click_time             # Time of last click (cooldown)
self.paused                      # Pause state
self.last_pause_toggle           # Time of last pause toggle (cooldown)
```

### State Transitions
```
┌──────────┐  close fist   ┌──────────┐
│  ACTIVE  │ ────────────> │  PAUSED  │
│          │ <──────────── │          │
└──────────┘  open fist    └──────────┘

┌───────────────┐  pinch     ┌───────────────┐
│ CLICK_READY   │ ────────> │ CLICK_ACTIVE  │
│               │           │               │
└───────────────┘           └───────┬───────┘
        ▲                           │
        │      cooldown expires     │
        └───────────────────────────┘
```

## Configuration Flow

```
config.py
   │
   ├─ MIN_DETECTION_CONFIDENCE → MediaPipe initialization
   ├─ MIN_TRACKING_CONFIDENCE  → MediaPipe initialization
   ├─ SMOOTH_FACTOR           → Cursor smoothing calculation
   ├─ PINCH_THRESHOLD         → Click detection
   ├─ CLICK_COOLDOWN          → Click timing
   ├─ PAUSE_COOLDOWN          → Pause timing
   └─ CAMERA_INDEX            → Video capture device
```

## Performance Optimization

### Smoothing Algorithm
```python
# Exponential Moving Average
smooth_x = prev_x + (x - prev_x) / smooth_factor
smooth_y = prev_y + (y - prev_y) / smooth_factor

# Higher smooth_factor = more smoothing, slower response
# Lower smooth_factor = less smoothing, faster response
```

### Cooldown Mechanism
```python
current_time = time.time()
time_since_last = current_time - last_action_time

if time_since_last > cooldown_threshold:
    # Allow action
    perform_action()
    last_action_time = current_time
```

## Error Handling

```
VideoCapture Failure
    ↓
Print Error + Exit

MediaPipe Processing
    ↓
No Hands Detected
    ↓
Continue (no action)

Keyboard Interrupt
    ↓
Cleanup + Exit
```

## Threading Model

- **Single-threaded**: All processing in main thread
- **Blocking I/O**: cv2.waitKey() for frame display
- **No async operations**: Sequential processing

## Memory Management

- **Frame Buffer**: Single frame in memory
- **Landmark Data**: 21 points × 3 coordinates per hand
- **State Variables**: Minimal memory footprint
- **No caching**: Frames processed and discarded

## Integration Points

### External Dependencies
1. **OpenCV**: Frame capture and display
2. **MediaPipe**: Hand detection (Google's ML model)
3. **PyAutoGUI**: OS-level mouse control

### OS Integration
- **Windows**: Win32 API via PyAutoGUI
- **macOS**: Quartz via PyAutoGUI
- **Linux**: X11 via PyAutoGUI

## Extensibility

### Adding New Gestures
```python
def detect_new_gesture(self, hand_landmarks):
    # Extract required landmarks
    # Calculate distances/angles
    # Apply threshold
    # Return True/False
    pass
```

### Supporting Multiple Hands
```python
# Change in config.py
MAX_NUM_HANDS = 2

# Handle in process_frame
for hand_landmarks in results.multi_hand_landmarks:
    # Process each hand
    pass
```
