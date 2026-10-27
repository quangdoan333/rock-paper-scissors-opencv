import cv2
import numpy as np
from config import (
    W, H, WHITE, GRAY, PANEL, BG_TINT, ACCENT, GOLD, GREEN, RED, DARK_TEXT,
    CONNECTIONS, WIN_SCORE, COUNTDOWN_SEC, NAMES
)

# ======================================================================
# Text rendering (OpenCV only)
# ======================================================================
_text_cache = {}


def text_width(s, size, bold=False):
    scale = size / 34
    thickness = 1
    return cv2.getTextSize(str(s), cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)[0][0]


def text(img, s, x, y, size=24, color=WHITE, bold=False, align="left", shadow=True):
    """Draw normal OpenCV text; (x, y) is the anchor point and y is the vertical center."""
    s = str(s)
    scale = size / 34
    thickness = 1
    (tw, th), baseline = cv2.getTextSize(
        s, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness
    )
    if align == "center":
        x -= tw // 2
    elif align == "right":
        x -= tw
    baseline_y = int(y + (th - baseline) // 2)
    if shadow:
        cv2.putText(
            img, s, (int(x) + 2, baseline_y + 2),
            cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thickness + 1,
            cv2.LINE_AA
        )
    cv2.putText(
        img, s, (int(x), baseline_y), cv2.FONT_HERSHEY_SIMPLEX,
        scale, color, thickness, cv2.LINE_AA
    )


def wrap(s, size, max_w, bold=False):
    lines, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if text_width(trial, size) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ======================================================================
# Shapes: rounded transparent boxes, circles, gesture icons
# ======================================================================
_mask_cache = {}


def _rmask(w, h, r):
    key = (w, h, r)
    m = _mask_cache.get(key)
    if m is None:
        r = max(1, min(r, w // 2, h // 2))
        m = np.zeros((h, w), np.uint8)
        cv2.rectangle(m, (r, 0), (w - r - 1, h - 1), 255, -1)
        cv2.rectangle(m, (0, r), (w - 1, h - r - 1), 255, -1)
        for cx, cy in ((r, r), (w - r - 1, r), (r, h - r - 1), (w - r - 1, h - r - 1)):
            cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
        _mask_cache[key] = m
    return m


def rrect(img, x, y, w, h, r, color, alpha=1.0, border=None, bw=2):
    ih, iw = img.shape[:2]
    x, y = int(x), int(y)
    if x < 0 or y < 0 or x + w > iw or y + h > ih:
        return
    roi = img[y:y + h, x:x + w]
    m = _rmask(w, h, r)
    a = (m.astype(np.float32) / 255 * alpha)[..., None]
    roi[:] = (np.array(color, np.float32) * a + roi * (1 - a)).astype(np.uint8)
    if border is not None:
        inner = np.zeros((h, w), np.uint8)
        inner[bw:h - bw, bw:w - bw] = _rmask(w - 2 * bw, h - 2 * bw, max(r - bw, 1))
        ring = cv2.subtract(m, inner)
        a2 = (ring.astype(np.float32) / 255)[..., None]
        roi[:] = (np.array(border, np.float32) * a2 + roi * (1 - a2)).astype(np.uint8)


def disc(img, cx, cy, r, color, alpha=1.0):
    ih, iw = img.shape[:2]
    x0, y0, x1, y1 = max(cx - r, 0), max(cy - r, 0), min(cx + r + 1, iw), min(cy + r + 1, ih)
    if x0 >= x1 or y0 >= y1:
        return
    m = np.zeros((y1 - y0, x1 - x0), np.uint8)
    cv2.circle(m, (cx - x0, cy - y0), r, 255, -1, cv2.LINE_AA)
    a = (m.astype(np.float32) / 255 * alpha)[..., None]
    roi = img[y0:y1, x0:x1]
    roi[:] = (np.array(color, np.float32) * a + roi * (1 - a)).astype(np.uint8)


def draw_icon(img, kind, cx, cy, s, color, dark=DARK_TEXT):
    """Simple Rock / Scissors / Paper icons (s ~ half height)."""
    A = cv2.LINE_AA
    if kind == "BUA":
        cv2.ellipse(img, (cx, cy + int(.12 * s)), (int(.55 * s), int(.5 * s)), 0, 0, 360, color, -1, A)
        for i in range(4):
            cv2.circle(img, (cx + int((i - 1.5) * .27 * s), cy - int(.36 * s)), int(.16 * s), color, -1, A)
        cv2.ellipse(img, (cx - int(.5 * s), cy + int(.18 * s)), (int(.3 * s), int(.15 * s)), -35, 0, 360, color, -1, A)
        for i in (-1, 0, 1):
            x = cx + int((i * .27) * s)
            cv2.line(img, (x, cy - int(.45 * s)), (x, cy - int(.2 * s)), dark, max(2, int(.04 * s)), A)
    elif kind == "KEO":
        t = max(4, int(.16 * s))
        cv2.line(img, (cx - int(.3 * s), cy + int(.5 * s)), (cx + int(.38 * s), cy - int(.75 * s)), color, t, A)
        cv2.line(img, (cx + int(.3 * s), cy + int(.5 * s)), (cx - int(.38 * s), cy - int(.75 * s)), color, t, A)
        for sx in (-1, 1):
            cv2.circle(img, (cx + sx * int(.34 * s), cy + int(.62 * s)), int(.22 * s), color, max(3, int(.09 * s)), A)
        cv2.circle(img, (cx, cy - int(.05 * s)), max(2, int(.05 * s)), dark, -1, A)
    else:  # BAO
        t = int(.2 * s)
        cv2.ellipse(img, (cx, cy + int(.3 * s)), (int(.52 * s), int(.42 * s)), 0, 0, 360, color, -1, A)
        for i in range(4):
            x = cx + int((i - 1.5) * .26 * s)
            top = cy - int((.72 - .1 * abs(i - 1.5)) * s)
            cv2.line(img, (x, cy + int(.2 * s)), (x, top), color, t, A)
            cv2.circle(img, (x, top), t // 2, color, -1, A)
        cv2.line(img, (cx - int(.45 * s), cy + int(.25 * s)), (cx - int(.78 * s), cy - int(.1 * s)), color, t, A)
        cv2.circle(img, (cx - int(.78 * s), cy - int(.1 * s)), t // 2, color, -1, A)


# ======================================================================
# Buttons
# ======================================================================
BTN_W, BTN_H = 300, 76
MENU_BUTTONS = [
    {"label": "HOW TO PLAY", "x": W // 2 - BTN_W - 20, "y": 470, "w": BTN_W, "h": BTN_H,
     "action": "guide", "primary": False},
    {"label": "START", "x": W // 2 + 20, "y": 470, "w": BTN_W, "h": BTN_H,
     "action": "start", "primary": True},
]
GUIDE_BUTTONS = [
    {"label": "BACK", "x": W // 2 - 130, "y": 622, "w": 260, "h": 52,
     "action": "back", "primary": True},
]


def hit(btn, pos):
    return btn["x"] <= pos[0] <= btn["x"] + btn["w"] and btn["y"] <= pos[1] <= btn["y"] + btn["h"]


def draw_button(canvas, btn, hovered):
    g = 5 if hovered else 0
    x, y, w, h = btn["x"] - g, btn["y"] - g, btn["w"] + 2 * g, btn["h"] + 2 * g
    if btn["primary"]:
        rrect(canvas, x, y, w, h, h // 2, (150, 240, 135) if hovered else GREEN, 1.0)
        text(canvas, btn["label"], x + w // 2, y + h // 2, 30 if h > 60 else 24, DARK_TEXT, True,
             "center", shadow=False)
    else:
        rrect(canvas, x, y, w, h, h // 2, (110, 80, 62) if hovered else (70, 50, 40), 0.85,
              border=ACCENT, bw=3)
        text(canvas, btn["label"], x + w // 2, y + h // 2, 30 if h > 60 else 24, WHITE, True, "center")


# ======================================================================
# Screens & Components
# ======================================================================
def make_canvas(frame):
    """Crop/scale the webcam image to W x H; return the canvas and landmark-to-pixel converter."""
    fh, fw = frame.shape[:2]
    scale = max(W / fw, H / fh)
    nw, nh = int(round(fw * scale)), int(round(fh * scale))
    resized = cv2.resize(frame, (nw, nh))
    ox, oy = (nw - W) // 2, (nh - H) // 2
    canvas = resized[oy:oy + H, ox:ox + W].copy()

    def to_px(p):
        return int(p.x * nw - ox), int(p.y * nh - oy)

    return canvas, to_px


def soften_background(canvas):
    small = cv2.resize(canvas, (W // 10, H // 10), interpolation=cv2.INTER_AREA)
    small = cv2.GaussianBlur(small, (5, 5), 0)
    blur = cv2.resize(small, (W, H), interpolation=cv2.INTER_LINEAR)
    tint = np.full_like(blur, BG_TINT)
    return cv2.addWeighted(blur, 0.38, tint, 0.62, 0)


def draw_hand(canvas, lm, to_px, color):
    pts = [to_px(p) for p in lm]
    for a, b in CONNECTIONS:
        cv2.line(canvas, pts[a], pts[b], (0, 0, 0), 6, cv2.LINE_AA)
    for a, b in CONNECTIONS:
        cv2.line(canvas, pts[a], pts[b], color, 3, cv2.LINE_AA)
    for p in pts:
        cv2.circle(canvas, p, 6, color, -1, cv2.LINE_AA)
        cv2.circle(canvas, p, 6, WHITE, 1, cv2.LINE_AA)


def draw_menu(canvas, hover):
    cx = W // 2
    for i, (kind, col) in enumerate((("BUA", ACCENT), ("KEO", GOLD), ("BAO", GREEN))):
        x = cx + (i - 1) * 170
        disc(canvas, x, 175, 66, (60, 42, 34), 0.8)
        cv2.circle(canvas, (x, 175), 66, col, 3, cv2.LINE_AA)
        draw_icon(canvas, kind, x, 175, 40, col)
    text(canvas, "ROCK · PAPER · SCISSORS", cx, 318, 88, WHITE, True, "center")
    cv2.line(canvas, (cx - 120, 372), (cx + 120, 372), ACCENT, 5, cv2.LINE_AA)
    text(canvas, "Play against the computer using hand gestures", cx, 415, 28, (215, 215, 215), False, "center")
    for b in MENU_BUTTONS:
        draw_button(canvas, b, hover == b["action"])
    text(canvas, "ENTER: start   ·   H: how to play   ·   Q: quit", cx, H - 44, 20, GRAY, False, "center")


def draw_guide(canvas, hover):
    cx = W // 2
    rrect(canvas, 90, 36, W - 180, 648, 30, PANEL, 0.82, border=(110, 85, 70), bw=2)
    text(canvas, "HOW TO PLAY", cx, 84, 44, WHITE, True, "center")
    cv2.line(canvas, (cx - 90, 118), (cx + 90, 118), ACCENT, 4, cv2.LINE_AA)

    steps = [
        "Place ONE hand in the frame with your palm facing the camera.",
        "Press SPACE to start a new round. The countdown will show 3 - 2 - 1.",
        "When the countdown reaches 0, your gesture is locked and the computer chooses randomly.",
        "The first player to win 3 rounds wins the match. Draws do not count.",
    ]
    y = 164
    for i, s in enumerate(steps, 1):
        lines = wrap(s, 22, 500)
        cv2.circle(canvas, (140, y + 4), 17, ACCENT, -1, cv2.LINE_AA)
        text(canvas, str(i), 140, y + 3, 20, DARK_TEXT, True, "center", shadow=False)
        for j, ln in enumerate(lines):
            text(canvas, ln, 172, y + j * 28, 22, WHITE)
        y += max(len(lines), 1) * 28 + 16

    text(canvas, "Controls", 700, 168, 26, GOLD, True)
    keys = [("SPACE", "Start the next round"), ("R", "Restart the game"),
            ("M", "Return to main menu"), ("Q", "Quit the game")]
    ky = 218
    for k, d in keys:
        kw = max(60, text_width(k, 22, True) + 28)
        rrect(canvas, 700, ky - 20, kw, 40, 10, (95, 72, 58), 1.0, border=(170, 140, 120), bw=2)
        text(canvas, k, 700 + kw // 2, ky, 22, WHITE, True, "center", shadow=False)
        text(canvas, d, 700 + 112 + 14, ky, 22, (225, 225, 225))
        ky += 56

    text(canvas, "Three gestures", 132, 456, 26, GOLD, True)
    cards = [("BUA", "ROCK", "Make a closed fist", ACCENT),
             ("KEO", "SCISSORS", "Extend your index and middle fingers", GOLD),
             ("BAO", "PAPER", "Open all four fingers", GREEN)]
    for i, (kind, name, desc, col) in enumerate(cards):
        x = 130 + i * 342
        rrect(canvas, x, 482, 322, 92, 18, (60, 44, 36), 0.9, border=col, bw=2)
        draw_icon(canvas, kind, x + 52, 528, 32, col)
        text(canvas, name, x + 104, 506, 26, WHITE, True)
        for j, ln in enumerate(wrap(desc, 18, 208)):
            text(canvas, ln, x + 104, 536 + j * 22, 18, (215, 215, 215))
    text(canvas, "Rock beats Scissors   ·   Scissors beats Paper   ·   Paper beats Rock", cx, 596, 22, GOLD, False, "center")
    for b in GUIDE_BUTTONS:
        draw_button(canvas, b, hover == b["action"])


def draw_scoreboard(canvas, score):
    cx = W // 2
    rrect(canvas, cx - 270, 16, 540, 92, 24, PANEL, 0.7, border=(110, 85, 70), bw=2)
    text(canvas, "YOU", cx - 240, 44, 24, GREEN, True)
    text(canvas, "COMPUTER", cx + 240, 44, 24, RED, True, "right")
    text(canvas, str(score["player"]), cx - 72, 56, 58, WHITE, True, "center")
    text(canvas, str(score["computer"]), cx + 72, 56, 58, WHITE, True, "center")
    text(canvas, "-", cx, 56, 44, GRAY, True, "center", shadow=False)
    text(canvas, f"Draws: {score['draw']}", cx, 92, 18, GRAY, False, "center")
    for i in range(WIN_SCORE):
        x = cx - 232 + i * 26
        if i < score["player"]:
            cv2.circle(canvas, (x, 84), 8, GREEN, -1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, (x, 84), 8, (130, 120, 110), 2, cv2.LINE_AA)
        x = cx + 232 - i * 26
        if i < score["computer"]:
            cv2.circle(canvas, (x, 84), 8, RED, -1, cv2.LINE_AA)
        else:
            cv2.circle(canvas, (x, 84), 8, (130, 120, 110), 2, cv2.LINE_AA)
    text(canvas, "ROCK · PAPER · SCISSORS", 32, 40, 28, WHITE, True)
    text(canvas, f"Win {WIN_SCORE} rounds to win the match", W - 32, 40, 20, (225, 225, 225), False, "right")


def draw_live_pill(canvas, live, has_hand):
    if live:
        label, col = f"Gesture: {NAMES[live]}", GREEN
    elif has_hand:
        label, col = "Gesture: Unclear", GOLD
    else:
        label, col = "No hand detected", RED
    w = text_width(label, 24, True) + 64
    x, y = 30, H - 78
    rrect(canvas, x, y, w, 48, 24, PANEL, 0.7, border=col, bw=2)
    cv2.circle(canvas, (x + 26, y + 24), 8, col, -1, cv2.LINE_AA)
    text(canvas, label, x + 46, y + 24, 24, WHITE, True)
    text(canvas, "SPACE: new round  ·  R: restart  ·  M: menu  ·  Q: quit", W - 30, H - 54, 18,
         (215, 215, 215), False, "right")


def draw_idle(canvas):
    rrect(canvas, W // 2 - 340, H - 230, 680, 96, 26, PANEL, 0.75, border=ACCENT, bw=3)
    text(canvas, "Press SPACE to start a new round", W // 2, H - 197, 32, WHITE, True, "center")
    text(canvas, "Place one hand in the frame", W // 2, H - 160, 20, (215, 215, 215), False, "center")


def draw_countdown(canvas, now, t_state):
    elapsed = now - t_state
    num = max(COUNTDOWN_SEC - int(elapsed), 1)
    frac = 1 - (elapsed - int(elapsed))
    cx, cy, r = W // 2, 300, 100
    rrect(canvas, W // 2 - 200, 126, 400, 60, 30, PANEL, 0.7)
    text(canvas, "Show your hand!", W // 2, 156, 40, WHITE, True, "center")
    disc(canvas, cx, cy, r + 8, PANEL, 0.7)
    cv2.circle(canvas, (cx, cy), r, (120, 105, 95), 6, cv2.LINE_AA)
    cv2.ellipse(canvas, (cx, cy), (r, r), -90, 0, int(360 * frac), GOLD, 10, cv2.LINE_AA)
    text(canvas, str(num), cx, cy - 4, 130, GOLD, True, "center")


def draw_result(canvas, round_info):
    out = round_info["outcome"]
    cx, cy = W // 2, H // 2
    col = {"player": GREEN, "computer": RED, "draw": GOLD, "invalid": RED}[out]
    rrect(canvas, cx - 390, cy - 190, 780, 380, 34, PANEL, 0.85, border=col, bw=4)
    if out == "invalid":
        text(canvas, "Gesture not detected!", cx, cy - 30, 50, RED, True, "center")
        text(canvas, "This round does not count", cx, cy + 40, 30, WHITE, False, "center")
        return
    for side, who, kind, x in (("player", "YOU", round_info["player"], cx - 200),
                               ("computer", "COMPUTER", round_info["computer"], cx + 200)):
        winner = out == side
        c = GREEN if side == "player" else RED
        text(canvas, who, x, cy - 150, 28, c, True, "center")
        disc(canvas, x, cy - 40, 82, (60, 44, 36), 0.9)
        cv2.circle(canvas, (x, cy - 40), 82, c if winner else (110, 100, 92), 4 if winner else 2, cv2.LINE_AA)
        draw_icon(canvas, kind, x, cy - 40, 50, WHITE)
        text(canvas, NAMES[kind], x, cy + 70, 24, WHITE, True, "center")
    text(canvas, "VS", cx, cy - 40, 40, GRAY, True, "center")
    msg = {"player": "YOU WIN THIS ROUND!", "computer": "COMPUTER WINS THIS ROUND!", "draw": "DRAW!"}[out]
    text(canvas, msg, cx, cy + 140, 50, col, True, "center")


def draw_match_over(canvas, score):
    cx, cy = W // 2, H // 2
    won = score["player"] > score["computer"]
    col = GREEN if won else RED
    rrect(canvas, cx - 380, cy - 170, 760, 340, 34, PANEL, 0.88, border=col, bw=4)
    text(canvas, "YOU WIN THE MATCH!" if won else "COMPUTER WINS THE MATCH!", cx, cy - 75, 60, col, True, "center")
    text(canvas, f"Score  {score['player']} - {score['computer']}   (draws: {score['draw']})",
         cx, cy + 15, 36, WHITE, False, "center")
    text(canvas, "Press R to restart   ·   M to return to the main menu", cx, cy + 100, 26, (220, 220, 220),
         False, "center")


def render(canvas, to_px, lm, state, score, round_info, live, now, t_state, hover):
    """Render the entire UI on the canvas based on the current state."""
    if state in ("MENU", "GUIDE"):
        canvas[:] = soften_background(canvas)
        if state == "MENU":
            draw_menu(canvas, hover)
        else:
            draw_guide(canvas, hover)
        return

    hand_on_top = state == "COUNTDOWN"   # hand is always rendered above countdown circle
    if lm is not None and not hand_on_top:
        draw_hand(canvas, lm, to_px, GREEN if live else GOLD)
    draw_scoreboard(canvas, score)
    draw_live_pill(canvas, live, lm is not None)
    if state == "IDLE":
        draw_idle(canvas)
    elif state == "COUNTDOWN":
        draw_countdown(canvas, now, t_state)
    elif state == "RESULT":
        draw_result(canvas, round_info)
    elif state == "MATCH_OVER":
        draw_match_over(canvas, score)
    if lm is not None and hand_on_top:
        draw_hand(canvas, lm, to_px, GREEN if live else GOLD)