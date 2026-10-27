import math
from config import WRIST, THUMB_IP, THUMB_TIP, PINKY_MCP, FINGERS, BEATS


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def fingers_up(lm):
    states = [int(dist(lm[THUMB_TIP], lm[PINKY_MCP]) > dist(lm[THUMB_IP], lm[PINKY_MCP]))]
    for tip, pip in FINGERS:
        states.append(int(dist(lm[tip], lm[WRIST]) > dist(lm[pip], lm[WRIST])))
    return states


def classify(states):
    _, index, middle, ring, pinky = states
    if not (index or middle or ring or pinky):
        return "BUA"
    if index and middle and not ring and not pinky:
        return "KEO"
    if index and middle and ring and pinky:
        return "BAO"
    return None


def judge(player, computer):
    if player == computer:
        return "draw"
    if BEATS[player] == computer:
        return "player"
    else:
        return "computer"