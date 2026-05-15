# AI Virtual Mouse

## Overview
This project implements a real-time virtual mouse using hand gestures captured via a webcam. It leverages OpenCV, MediaPipe, and Autopy to track hand landmarks, move the mouse cursor based on the index finger’s position, and perform clicks when the index and middle fingers are close together. The system is designed for touchless computer interaction, suitable for presentations, accessibility, or innovative interfaces.

## Prerequisites
- Python 3.8+ installed on your system
- A functional webcam (default device, index 0) to capture live video
- Required Python libraries:
  - `opencv-python` (for webcam access and video display)
  - `mediapipe` (for hand landmark detection)
  - `autopy` (for mouse control)
- Install dependencies manually:
  ```bash
  pip install opencv-python mediapipe autopy
  ```

## How to Run
1. Ensure your webcam is connected and functional.
2. Save the project code in two files: `AiVirtualMouseProject.py` and `HandTrackingModule.py` in the same directory.
3. Open a terminal or command prompt.
4. Navigate to the directory containing the project files.
5. Install the required libraries (see Prerequisites).
6. Run the main program:
   ```bash
   python AiVirtualMouseProject.py
   ```
7. The webcam will activate, displaying a live feed with a purple rectangle indicating the active mouse control area.
8. Move your index finger to control the mouse cursor; bring the index and middle fingers close to click.
9. Press the `q` key to exit.

## Application Flow
- The program opens the default webcam using OpenCV to capture live video.
- Frames are flipped horizontally for a mirror-like effect and processed by the `HandTrackingModule` to detect one hand’s landmarks using MediaPipe.
- A purple rectangle defines the active area for mouse control.
- If only the index finger is up, its tip’s position is mapped to screen coordinates, smoothed, and used to move the mouse cursor via Autopy.
- If both index and middle fingers are up and close (<40 pixels), a click is triggered.
- The frame rate (FPS) is displayed on the video feed.
- The loop continues until the `q` key is pressed, with webcam resources cleaned up on exit.

## Code Structure
- **Main Script**: `AiVirtualMouseProject.py` handles webcam capture, mouse control logic, and display.
- **Module**: `HandTrackingModule.py` defines a `handDetector` class for hand tracking, landmark detection, finger state detection, and distance calculations.
- **Webcam Capture**: Uses `cv2.VideoCapture(0)` to access the default webcam.
- **Hand Detection**: MediaPipe’s Hands model detects up to one hand with 50% confidence thresholds.
- **Mouse Control**: Maps index finger position to screen coordinates, smooths movement, and triggers clicks based on finger distance.
- **Exit and Cleanup**: Terminates on `q` key press and releases webcam resources.

## Example Output
```
[Webcam Window: "AI Virtual Mouse"]
- Displays live webcam feed
- Shows a purple rectangle (active mouse control area)
- Overlays hand landmarks (dots and skeletal lines)
- Draws a purple circle on the index finger tip during movement
- Draws a green circle at the midpoint when index and middle fingers are close (click mode)
- Displays FPS in the top-left corner (e.g., "FPS: 30")
```

## Limitations
- Requires a functional webcam; fails if no camera is detected.
- Tracks only one hand at a time (configured for `maxHands=1`).
- May be sensitive to lighting conditions or background noise affecting hand detection.
- Click detection depends on a fixed distance threshold (40 pixels), which may need tuning.
- No support for advanced gestures (e.g., drag, right-click).

## Potential Improvements
- Add webcam availability check:
  ```python
  if not cap.isOpened():
      print("Error: Webcam not detected")
      exit()
  ```
- Support additional gestures (e.g., thumb up for right-click, three fingers for drag).
- Adjust the click distance threshold dynamically based on hand size.
- Add calibration for the active control area (`frameR`) based on screen size.
- Save a recorded video of the session:
  ```python
  out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 30, (640, 480))
  out.write(img)
  out.release()
  ```

## License
This project is unlicensed and free to use or modify.