import curses
import math
import random
import time

FPS = 30
BOSS_MAX_HP = 13_000
PLAYER_MAX_HP = 210
MAX_TP = 100
ARENA_W = 46
ARENA_H = 11
HERO_HEAL = 40

WORDS = [
    "connection", "frequency", "distortion", "afterlife", "resonance",
    "dimension", "fragmented", "heartbeat", "forgotten", "protocol",
    "nightmare", "interference", "transmission", "reflection", "terminal",
    "electrical", "shattered", "determined", "collision", "threshold",
    "turbulence", "paradoxical", "unanswered", "resistance", "coordinate",
]
assert all(len(w) >= 7 for w in WORDS)

MENU = ["FIGHT", "ACT", "ITEM", "MERCY"]
ACTIONS = [
    ("FOCUS  - 25 TP", "ATK +30% for your next 4 attacks", 25),
    ("FORTIFY - 25 TP", "Take half damage for 3 dodge rounds", 25),
    ("REPAIR - 40 TP", "Restore 35 HP (up to 210)", 40),
    ("BACK", "Return to the main menu", 0),
]


def put(win, y, x, text, color=0):
    """Print safely, even while resizing the terminal."""
    rows, cols = win.getmaxyx()
    if y < 0 or y >= rows or x >= cols:
        return
    text = str(text)
    if x < 0:
        text = text[-x:]
        x = 0
    text = text[: max(0, cols - x - 1)]
    if not text:
        return
    try:
        win.addstr(y, x, text, color)
    except curses.error:
        pass


def bar(current, maximum, width):
    fill = max(0, min(width, round(width * current / maximum)))
    return "[" + "#" * fill + "-" * (width - fill) + "]"


class ContactFight:
    def __init__(self):
        self.boss_hp = BOSS_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.tp = 0
        self.heroes = 5
        self.turn = 1
        self.menu_pos = 0
        self.act_pos = 0
        self.mode = "menu"
        self.message = "* The CONTACT is waiting for a response."
        self.word = ""
        self.typed = ""
        self.started_typing = None
        self.atk_turns = 0
        self.def_turns = 0
        self.soul_x = ARENA_W // 2
        self.soul_y = ARENA_H // 2
        self.invulnerable_until = 0.0
        self.last_step = 0.0
        self.dodge_start = 0.0
        self.last_update = time.monotonic()
        self.last_spawn = 0.0
        self.bullets = []
        self.wall_gap = ARENA_W // 2
        self.notice_until = 0.0
        self.result = ""

    @property
    def phase(self):
        pct = self.boss_hp / BOSS_MAX_HP
        return 0 if pct > 0.70 else 1 if pct > 0.40 else 2 if pct > 0.15 else 3
