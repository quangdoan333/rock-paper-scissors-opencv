# Rock - Paper - Scissors with MediaPipe & OpenCV

A computer-vision-based Rock-Paper-Scissors game implemented in Python using OpenCV and MediaPipe Tasks. Play against the computer using your hand gestures detected via webcam!

## Project Structure

The project is cleanly modularized into the following files:
- `config.py`: Configuration parameters, constants, and color palettes.
- `gesture.py`: Hand gesture recognition logic and game rule judgment.
- `ui.py`: UI rendering, screens, buttons, and visual elements.
- `main.py`: Entry point managing the main game loop, webcam capture, and event handling.

## Installation

1. Make sure you have **Python** installed on your system.
2. Place all four files (`config.py`, `gesture.py`, `ui.py`, and `main.py`) in the same directory.
3. Install the required dependencies using `pip`:
   ```bash
   pip install opencv-python mediapipe numpy
