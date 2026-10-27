"""
Configuration and Constants for Rock-Paper-Scissors Game.
"""

# ======================================================================
# Model & Asset Configuration
# ======================================================================
MODEL_PATH = "hand_landmarker.task"
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)

# ======================================================================
# Game Rules & Timers
# ======================================================================
WIN_SCORE = 3          # Rounds needed to win the match
COUNTDOWN_SEC = 3      # Countdown duration in seconds
RESULT_SEC = 2.5       # Result display time per round in seconds

# Dynamic mapping
NAMES = {"BUA": "ROCK", "KEO": "SCISSORS", "BAO": "PAPER"}
SHORT = {"BUA": "ROCK", "KEO": "SCISSORS", "BAO": "PAPER"}
BEATS = {"BUA": "KEO", "KEO": "BAO", "BAO": "BUA"}  # Winning relationships

# ======================================================================
# MediaPipe Hand Landmarks Mapping
# ======================================================================
WRIST = 0
THUMB_IP, THUMB_TIP = 3, 4
PINKY_MCP = 17
FINGERS = [(8, 6), (12, 10), (16, 14), (20, 18)]
CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12), (9, 13), (13, 14), (14, 15),
    (15, 16), (13, 17), (17, 18), (18, 19), (19, 20), (0, 17),
]

# ======================================================================
# UI Layout & Dimensions
# ======================================================================
WIN_NAME = "Rock - Paper - Scissors"
W, H = 1280, 720       # UI frame size

# Color Palette (BGR format)
WHITE = (255, 255, 255)
GRAY = (190, 190, 190)
PANEL = (34, 24, 20)
BG_TINT = (52, 30, 24)
ACCENT = (255, 175, 70)    # Blue tint
GOLD = (70, 205, 255)      # Gold
GREEN = (125, 225, 120)
RED = (100, 100, 245)
DARK_TEXT = (36, 26, 20)

GAME_STATES = ("IDLE", "COUNTDOWN", "RESULT", "MATCH_OVER")