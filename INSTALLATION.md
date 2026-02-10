# Installation and Setup Guide

## Prerequisites

Before installing the application, ensure you have:

1. **Python 3.7 or higher**
   ```bash
   python3 --version
   ```

2. **pip (Python package installer)**
   ```bash
   pip3 --version
   ```

3. **Webcam** - Built-in or external USB webcam

4. **Operating System**
   - Windows 10/11
   - macOS 10.13+
   - Linux (Ubuntu 18.04+, Fedora, etc.)

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/kallurivenkatesh4416-commits/Finger-Cursor-Control.git
cd Finger-Cursor-Control
```

### 2. Create Virtual Environment (Recommended)

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `opencv-python` - For video capture and image processing
- `mediapipe` - For hand detection and tracking
- `pyautogui` - For mouse control

### 4. Verify Installation

Run the test suite to verify everything is installed correctly:

```bash
python test_hand_cursor_control.py
```

You should see all tests passing.

## Running the Application

### Basic Usage

```bash
python hand_cursor_control.py
```

### Using the Demo Script

```bash
python demo.py
```

The demo script provides a more guided experience with instructions.

## Platform-Specific Notes

### Linux

On Linux, you may need to install additional dependencies:

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk python3-dev

# For PyAutoGUI on X11
sudo apt-get install scrot python3-tk python3-dev
```

### macOS

Grant camera permissions when prompted. You may also need to grant accessibility permissions for mouse control:
- System Preferences → Security & Privacy → Privacy → Accessibility

### Windows

No additional setup required. The application should work out of the box.

## Troubleshooting Installation

### Issue: OpenCV fails to install

**Solution:**
```bash
pip install --upgrade pip
pip install opencv-python-headless
```

### Issue: MediaPipe fails to install

**Solution:**
Ensure you're using a compatible Python version (3.7-3.11):
```bash
python --version
```

If using Python 3.12+, downgrade to 3.11:
```bash
# Install Python 3.11 from python.org
# Then create a new virtual environment with Python 3.11
```

### Issue: PyAutoGUI doesn't control mouse

**Solution on Linux:**
```bash
pip install python3-xlib
```

**Solution on macOS:**
Grant accessibility permissions in System Preferences

### Issue: Webcam not detected

**Solution:**
1. Check if camera is working in other applications
2. Try different camera index in `config.py`:
   ```python
   CAMERA_INDEX = 1  # Try 0, 1, 2, etc.
   ```

## Updating the Application

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

## Uninstalling

To remove the application and its dependencies:

```bash
# Deactivate virtual environment
deactivate

# Remove the directory
cd ..
rm -rf Finger-Cursor-Control

# Or on Windows
# rmdir /s Finger-Cursor-Control
```

## Next Steps

After successful installation:
1. Read the [README.md](README.md) for usage instructions
2. Check [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for gesture guide
3. Customize settings in [config.py](config.py)
4. Run the application and have fun!

## Getting Help

If you encounter issues:
1. Check the troubleshooting sections in README.md
2. Ensure all dependencies are correctly installed
3. Verify webcam is working
4. Check that you have sufficient lighting
5. Open an issue on GitHub with details about your problem
