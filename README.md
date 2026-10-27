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
2. Clone or download all repository files (`config.py`, `gesture.py`, `ui.py`, `main.py`, and `requirements.txt`) into the same directory.
3. Install the required dependencies using `pip`:
   ```bash
   pip install opencv-python mediapipe numpy
   pip install -r requirements.txt
4. *(Optional but recommended)* Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

## Run
   ```bash
   python main.py
   ```

## How to Play

1. **Main Menu:**
   - Press **ENTER** or click **START** to enter the game.
   - Press **H** or click **HOW TO PLAY** to view instructions.

2. **During the Game:**
   - Position one hand clearly in front of the webcam with your palm facing the camera.
   - Press **SPACE** to start a new round (3-2-1 countdown).
   - When the countdown hits 0, your gesture is locked and the computer chooses randomly.
   - The first player to win **3 rounds** wins the match.
  
## Keyboard Controls & Shortcuts

| Key / Control | Action |
| :--- | :--- |
| **SPACE** | Start a new round (during IDLE state) |
| **R** | Restart the game / score |
| **M** | Return to the main menu |
| **Q** | Quit the game |
| **H** | Open the instruction guide (from the menu) |
| **ENTER** | Start the game (from the menu) |
