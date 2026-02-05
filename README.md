# Finger-Cursor-Control

A real-time Python application that uses MediaPipe and OpenCV to control the system mouse cursor via hand gestures. Features include smooth cursor tracking, pinch-to-click, and gesture-based pause/resume.

## Features

- **Smooth Cursor Tracking**: Control your mouse cursor by moving your index finger in front of the webcam
- **Pinch-to-Click**: Perform left-clicks by pinching your thumb and index finger together
- **Gesture-Based Pause/Resume**: Close your fist to pause cursor control, and open it to resume
- **Real-time Hand Detection**: Uses MediaPipe for accurate and fast hand landmark detection
- **Visual Feedback**: See your hand landmarks and gesture status in real-time

## Requirements

- Python 3.7 or higher
- Webcam
- Operating System: Windows, macOS, or Linux

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kallurivenkatesh4416-commits/Finger-Cursor-Control.git
cd Finger-Cursor-Control
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python hand_cursor_control.py
```

### Controls

- **Move Cursor**: Move your index finger to control the cursor position
- **Left Click**: Pinch your thumb and index finger together
- **Pause/Resume**: Close your fist (all fingers down) to toggle pause state
- **Quit**: Press 'q' key in the application window

## How It Works

1. **Hand Detection**: The application uses MediaPipe's hand tracking solution to detect hand landmarks in real-time
2. **Cursor Control**: The index finger tip position is mapped to screen coordinates with smoothing applied for stable movement
3. **Click Detection**: The distance between thumb tip and index finger tip is calculated. When below a threshold, a click is performed
4. **Pause Detection**: The application checks if fingers are folded to detect a closed fist gesture for pausing

## Configuration

You can adjust the following parameters in `hand_cursor_control.py`:

- `smooth_factor`: Controls cursor movement smoothness (default: 5)
- `click_cooldown`: Minimum time between clicks in seconds (default: 0.3)
- `pause_cooldown`: Minimum time between pause toggles in seconds (default: 0.5)
- `pinch_threshold`: Distance threshold for pinch detection (default: 0.05)
- `min_detection_confidence`: Minimum confidence for hand detection (default: 0.7)
- `min_tracking_confidence`: Minimum confidence for hand tracking (default: 0.7)

## Troubleshooting

- **Webcam not detected**: Ensure your webcam is properly connected and not being used by another application
- **Cursor movement is jittery**: Increase the `smooth_factor` value for more smoothing
- **Clicks are too sensitive**: Increase the `click_cooldown` value
- **Hand not detected**: Ensure good lighting and try adjusting the `min_detection_confidence` value

## Dependencies

- `opencv-python`: For video capture and display
- `mediapipe`: For hand detection and landmark tracking
- `pyautogui`: For controlling the mouse cursor

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Feel free to submit issues and pull requests.

## Acknowledgments

- Google's MediaPipe team for the excellent hand tracking solution
- OpenCV community for the computer vision library
