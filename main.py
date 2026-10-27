import os
import random
import time
import urllib.request
from collections import deque, Counter

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from config import (
    MODEL_PATH, MODEL_URL, WIN_SCORE, COUNTDOWN_SEC, RESULT_SEC,
    NAMES, WIN_NAME, W, H, GAME_STATES
)
from gesture import fingers_up, classify, judge
from ui import make_canvas, render, hit, MENU_BUTTONS, GUIDE_BUTTONS


def main():
    if not os.path.exists(MODEL_PATH):
        print("Downloading model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)

    options = vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Could not open the webcam.")
        return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    mouse = {"pos": (-1, -1), "click": None}

    def on_mouse(event, x, y, flags, param):
        mouse["pos"] = (x, y)
        if event == cv2.EVENT_LBUTTONDOWN:
            mouse["click"] = (x, y)

    cv2.namedWindow(WIN_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WIN_NAME, W, H)
    cv2.setMouseCallback(WIN_NAME, on_mouse)

    history = deque(maxlen=7)
    start = time.monotonic()

    state = "MENU"            # MENU <-> GUIDE ; MENU -> IDLE -> COUNTDOWN -> RESULT -> IDLE / MATCH_OVER
    t_state = 0.0
    score = {"player": 0, "computer": 0, "draw": 0}
    round_info = {"player": None, "computer": None, "outcome": None}

    with vision.HandLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))
            now = time.monotonic()
            result = landmarker.detect_for_video(mp_image, int((now - start) * 1000))

            live = None  # current detected gesture
            lm = None
            if result.hand_landmarks:
                lm = result.hand_landmarks[0]
                live = classify(fingers_up(lm))
                history.append(live)
            else:
                history.clear()
            stable = Counter(history).most_common(1)[0][0] if history else None

            # ---------- Update state ----------
            if state == "COUNTDOWN" and now - t_state >= COUNTDOWN_SEC:
                player = stable
                if player is None:
                    round_info = {"player": None, "computer": None, "outcome": "invalid"}
                else:
                    computer = random.choice(list(NAMES))
                    outcome = judge(player, computer)
                    score[outcome] += 1
                    round_info = {"player": player, "computer": computer, "outcome": outcome}
                state, t_state = "RESULT", now

            elif state == "RESULT" and now - t_state >= RESULT_SEC:
                if score["player"] >= WIN_SCORE or score["computer"] >= WIN_SCORE:
                    state = "MATCH_OVER"
                else:
                    state = "IDLE"

            # ---------- Render UI ----------
            buttons = MENU_BUTTONS if state == "MENU" else GUIDE_BUTTONS if state == "GUIDE" else []
            hover = next((b["action"] for b in buttons if hit(b, mouse["pos"])), None)
            canvas, to_px = make_canvas(frame)
            render(canvas, to_px, lm, state, score, round_info, live, now, t_state, hover)
            cv2.imshow(WIN_NAME, canvas)
            if cv2.getWindowProperty(WIN_NAME, cv2.WND_PROP_VISIBLE) < 1:
                break

            # ---------- Mouse and keyboard ----------
            key = cv2.waitKey(1) & 0xFF
            ch = chr(key).lower() if key != 255 else ""
            click, mouse["click"] = mouse["click"], None
            action = None
            if click:
                action = next((b["action"] for b in buttons if hit(b, click)), None)
            if state == "MENU":
                if ch == "h":
                    action = "guide"
                elif key == 13:
                    action = "start"
            elif state == "GUIDE" and (key in (13, 27) or ch == "b"):
                action = "back"

            if ch == "q":
                break
            if action == "guide":
                state = "GUIDE"
            elif action == "back":
                state = "MENU"
            elif action == "start":
                score = {"player": 0, "computer": 0, "draw": 0}
                round_info = {"player": None, "computer": None, "outcome": None}
                history.clear()
                state = "IDLE"
            elif state in GAME_STATES:
                if ch == " " and state == "IDLE":
                    state, t_state = "COUNTDOWN", now
                    history.clear()
                elif ch == "r":
                    score = {"player": 0, "computer": 0, "draw": 0}
                    round_info = {"player": None, "computer": None, "outcome": None}
                    state = "IDLE"
                elif ch == "m":
                    state = "MENU"

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()