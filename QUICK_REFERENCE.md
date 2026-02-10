# Quick Reference Guide

## Hand Gestures

### 1. Cursor Control (Move)
```
✋ Show your hand with fingers spread
👆 Point with your index finger
   → Move your index finger to move the cursor
```
**Visual**: Index finger tip controls cursor position

### 2. Click (Pinch)
```
👌 Bring thumb and index finger together
   → Creates a "pinch" gesture to perform left-click
```
**Visual**: Distance between thumb tip and index tip < threshold

### 3. Pause/Resume (Fist)
```
✊ Close your hand into a fist
   → Toggles pause state (paused ↔ active)
```
**Visual**: All fingers folded down

## Technical Details

### Coordinate System
- **Camera Space**: (0,0) at top-left, normalized to [0,1]
- **Screen Space**: Mapped to actual screen resolution
- **Smoothing**: Applied exponential moving average for stable movement

### Detection Parameters
- **Hand Detection**: MediaPipe with confidence threshold 0.7
- **Pinch Threshold**: Distance < 0.05 (normalized)
- **Fist Detection**: 4+ fingers folded
- **Click Cooldown**: 0.3 seconds
- **Pause Cooldown**: 0.5 seconds

### Hand Landmarks Used
- **Landmark 4**: Thumb tip
- **Landmark 8**: Index finger tip
- **Landmarks 5,9,13,17**: Finger knuckles (MCP joints)
- **Landmarks 12,16,20**: Other finger tips

## Performance Tips

1. **Lighting**: Ensure good, even lighting on your hand
2. **Distance**: Keep hand 30-50cm from camera
3. **Background**: Plain background helps detection
4. **Stability**: Rest your elbow for more stable control
5. **Calibration**: Adjust smooth_factor if cursor is too jittery

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cursor too fast | Increase `smooth_factor` |
| Cursor too slow | Decrease `smooth_factor` |
| Too many clicks | Increase `click_cooldown` |
| Clicks not registering | Decrease `pinch_threshold` |
| Hand not detected | Improve lighting, adjust camera angle |
| Pause too sensitive | Increase `pause_cooldown` |

## Keyboard Shortcuts

- **Q**: Quit application
- **PyAutoGUI Failsafe**: Move mouse to screen corner to emergency stop
