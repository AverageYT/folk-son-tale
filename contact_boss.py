
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

    @property
    def phase_name(self):
        return ["initial.HANDSHAKE", "PACKET LOSS", "404.NOT.found", "turn on mobile data to access the internet"][self.phase]

    def action_done(self, description):
        if self.boss_hp <= 0:
            self.finish(True)
            return
        self.message = description
        self.mode = "notice"
        self.notice_until = time.monotonic() + 1.15

    def finish(self, won):
        self.mode = "end"
        self.result = "VICTORY" if won else "GAME OVER"
        self.message = (
            "* The CONTACT has finally gone silent."
            if won else "* The connection was lost."
        )

    def select_menu(self):
        choice = MENU[self.menu_pos]
        if choice == "FIGHT":
            self.word = random.choice(WORDS).upper()
            self.typed = ""
            self.started_typing = None
            self.mode = "typing"
            self.message = "* Type the exact word, then press ENTER!"
        elif choice == "ACT":
            self.act_pos = 0
            self.mode = "act"
            self.message = "* Choose an ACT."
        elif choice == "ITEM":
            if not self.heroes:
                self.message = "* No Legendary Heroes remaining."
            else:
                self.heroes -= 1
                healed = min(HERO_HEAL, PLAYER_MAX_HP - self.hp)
                self.hp += healed
                self.action_done(f"* LEGENDARY HERO restored {healed} HP! ({self.heroes} left)")
        else:
            self.action_done("* You tried to make contact. No one answered.")

    def choose_act(self):
        if self.act_pos == 3:
            self.mode = "menu"
            return
        cost = ACTIONS[self.act_pos][2]
        if self.tp < cost:
            self.message = f"* Need {cost} TP. You have {self.tp}."
            return
        self.tp -= cost
        if self.act_pos == 0:
            self.atk_turns = 4
            self.action_done("* FOCUS: your next 4 attacks become stronger!")
        elif self.act_pos == 1:
            self.def_turns = 3
            self.action_done("* FORTIFY: incoming damage is halved for 3 rounds!")
        else:
            restored = min(35, PLAYER_MAX_HP - self.hp)
            self.hp += restored
            self.action_done(f"* REPAIR: restored {restored} HP!")

    def submit_attack(self):
        if self.typed.upper() != self.word:
            self.action_done("* The transmission failed. MISS! (0 damage, 0 TP)")
            return
        elapsed = max(0.01, time.monotonic() - (self.started_typing or time.monotonic()))
        base = max(20, 190 - int(max(0, elapsed - 0.65) * 34))
        damage = min(190, int(base * (1.30 if self.atk_turns else 1.0)))
        if self.atk_turns:
            self.atk_turns -= 1
        self.boss_hp = max(0, self.boss_hp - damage)
        gained = min(MAX_TP - self.tp, 16 + max(0, int(8 - elapsed)))
        self.tp += gained
        self.action_done(f"* {elapsed:.2f}s  |  {damage} DAMAGE  |  +{gained} TP")

    def begin_dodge(self):
        self.mode = "dodge"
        self.soul_x = ARENA_W // 2
        self.soul_y = ARENA_H // 2
        self.invulnerable_until = time.monotonic() + 0.5
        self.dodge_start = time.monotonic()
        self.last_update = self.dodge_start
        self.last_spawn = -1.0
        self.bullets.clear()
        self.message = "* DODGE! Use arrow keys or WASD."

    def dodge_duration(self):
        return [8.3, 11.7, 17.4, 22.1][self.phase]

    def spawn(self, kind):
        p = self.phase
        speed = 5.8 + p * 1.5
        if kind == "rain":
            for _ in range(3 + p):
                x = random.uniform(1, ARENA_W - 2)
                self.bullets.append([x, -1.0, random.uniform(-0.8, 0.8), speed + random.random() * 2])
        elif kind == "cross":
            for _ in range(3 + p):
                from_left = random.choice((True, False))
                x = -1.0 if from_left else float(ARENA_W)
                y = random.uniform(0, ARENA_H - 1)
                self.bullets.append([x, y, speed * (1 if from_left else -1) * 1.5, random.uniform(-1, 1)])
        elif kind == "wall":
            self.wall_gap = max(3, min(ARENA_W - 4, self.wall_gap + random.randint(-13, 13)))
            gap_width = max(4, 9 - p)
            for x in range(ARENA_W):
                if abs(x - self.wall_gap) > gap_width // 2:
                    self.bullets.append([float(x), -1.0, 0.0, speed * 1.15])
        elif kind == "spiral":
            fan_angle = self.dodge_elapsed() * 1.8
            for n in range(6 + p * 2):
                a = fan_angle + n * 2 * math.pi / (6 + p * 2)
                self.bullets.append([
                    ARENA_W / 2, 1.0,
                    math.cos(a) * speed * 1.15,
                    math.sin(a) * speed * 1.15,
                ])

    def dodge_elapsed(self):
        return time.monotonic() - self.dodge_start

    def update(self, now):
        if self.mode == "notice" and now >= self.notice_until:
            self.begin_dodge()
        if self.mode != "dodge":
            return

        dt = min(0.10, max(0, now - self.last_update))
        self.last_update = now
        elapsed = now - self.dodge_start
        if elapsed >= self.dodge_duration():
            self.mode = "menu"
            self.menu_pos = 0
            if self.def_turns:
                self.def_turns -= 1
            self.turn += 1
            self.bullets.clear()
            self.message = "* The CONTACT prepares its next response."
            return

        kind = ["rain", "cross", "wall", "spiral"][(self.turn - 1 + self.phase) % 4]
        interval = (1.15 if kind == "wall" else 0.62 if kind == "spiral" else 0.38)
        interval *= [1.0, 0.9, 0.82, 0.74][self.phase]
        if elapsed - self.last_spawn >= interval:
            self.last_spawn = elapsed
            self.spawn(kind)
            if self.phase == 3 and kind != "rain":
                self.spawn("rain")

        living = []
        for bullet in self.bullets:
            bullet[0] += bullet[2] * dt
            bullet[1] += bullet[3] * dt
            x, y = bullet[:2]
            if -2 <= x <= ARENA_W + 1 and -2 <= y <= ARENA_H + 1:
                living.append(bullet)
                if now >= self.invulnerable_until and abs(x - self.soul_x) < 0.65 and abs(y - self.soul_y) < 0.65:
                    damage = [23, 36, 43, 59][self.phase]
                    if self.def_turns:
                        damage = (damage + 1) // 2
                    self.hp = max(0, self.hp - damage)
                    self.invulnerable_until = now + 0.85
                    self.message = f"* SIGNAL HIT! -{damage} HP"
                    if self.hp == 0:
                        self.finish(False)
                        return
        self.bullets = living[-220:]

    def on_key(self, key):
        if key in (ord("q"), ord("Q")) and self.mode not in ("typing",):
            self.mode = "quit"
            return

        enter = key in (10, 13, curses.KEY_ENTER)
        up = key in (curses.KEY_UP, ord("w"), ord("W"))
        down = key in (curses.KEY_DOWN, ord("s"), ord("S"))
        left = key in (curses.KEY_LEFT, ord("a"), ord("A"))
        right = key in (curses.KEY_RIGHT, ord("d"), ord("D"))

        if self.mode == "menu":
            if left or up:
                self.menu_pos = (self.menu_pos - 1) % len(MENU)
            elif right or down:
                self.menu_pos = (self.menu_pos + 1) % len(MENU)
            elif enter:
                self.select_menu()
        elif self.mode == "act":
            if up or left:
                self.act_pos = (self.act_pos - 1) % len(ACTIONS)
            elif down or right:
                self.act_pos = (self.act_pos + 1) % len(ACTIONS)
            elif enter:
                self.choose_act()
            elif key == 27:
                self.mode = "menu"
        elif self.mode == "typing":
            if key == 27:
                self.mode = "menu"
                self.message = "* Attack canceled."
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                self.typed = self.typed[:-1]
            elif enter:
                self.submit_attack()
            elif 32 <= key <= 126 and len(self.typed) < 24:
                if self.started_typing is None:
                    self.started_typing = time.monotonic()
                self.typed += chr(key)
        elif self.mode == "dodge":
            now = time.monotonic()
            if now - self.last_step < 0.045:
                return
            dx = int(right) - int(left)
            dy = int(down) - int(up)
            if dx or dy:
                self.soul_x = max(0, min(ARENA_W - 1, self.soul_x + dx))
                self.soul_y = max(0, min(ARENA_H - 1, self.soul_y + dy))
                self.last_step = now
        elif self.mode == "end":
            if key in (ord("r"), ord("R")):
                self.__init__()
            elif enter:
                self.mode = "quit"

    def draw(self, win):
        win.erase()
        rows, cols = win.getmaxyx()
        if cols < 76 or rows < 28:
            put(win, 1, 1, "CONTACT needs a larger terminal.")
            put(win, 3, 1, f"Current: {cols} x {rows} | Minimum: 76 x 28")
            put(win, 5, 1, "Expand the VS Code terminal panel or zoom out.")
            win.refresh()
            return

        x0 = (cols - (ARENA_W + 2)) // 2
        title = "[ C O N T A C T ]"
        put(win, 0, (cols - len(title)) // 2, title, curses.A_BOLD | curses.color_pair(4))
        put(win, 1, x0, f"PHASE: {self.phase_name}   /   TURN {self.turn}")
        put(win, 2, x0, "CONTACT " + bar(self.boss_hp, BOSS_MAX_HP, 30) + f" {self.boss_hp:5d}", curses.color_pair(2))
        put(win, 3, x0, f"YOU: {self.hp:3d}/{PLAYER_MAX_HP} HP     TP: {self.tp:3d}/{MAX_TP}     HERO x{self.heroes}", curses.color_pair(3))
        put(win, 5, x0, self.message[:ARENA_W + 2])

        top = 7
        put(win, top, x0, "+" + "-" * ARENA_W + "+")
        for y in range(ARENA_H):
            put(win, top + 1 + y, x0, "|")
            put(win, top + 1 + y, x0 + ARENA_W + 1, "|")
        put(win, top + ARENA_H + 1, x0, "+" + "-" * ARENA_W + "+")

        if self.mode == "dodge":
            for bullet in self.bullets:
                bx, by = round(bullet[0]), round(bullet[1])
                if 0 <= bx < ARENA_W and 0 <= by < ARENA_H:
                    put(win, top + 1 + by, x0 + 1 + bx, "*", curses.color_pair(2) | curses.A_BOLD)
            flashing = time.monotonic() < self.invulnerable_until and int(time.monotonic() * 12) % 2 == 0
            if not flashing:
                put(win, top + 1 + self.soul_y, x0 + 1 + self.soul_x, "o", curses.color_pair(3) | curses.A_BOLD)
            remaining = max(0.0, self.dodge_duration() - self.dodge_elapsed())
            put(win, 21, x0, f"SURVIVE: {remaining:4.1f}s    MOVE: ARROWS / WASD", curses.color_pair(4))

        elif self.mode == "menu":
            put(win, top + ARENA_H // 2, x0 + 15, "-- YOUR TURN --", curses.A_BOLD)
            rendered = "   ".join(f"{'>' if i == self.menu_pos else ' '} {name}" for i, name in enumerate(MENU))
            put(win, 21, x0, rendered, curses.color_pair(4) | curses.A_BOLD)
            put(win, 23, x0, "LEFT/RIGHT: choose   ENTER: confirm   Q: quit")

        elif self.mode == "act":
            put(win, 21, x0, "ACT  (UP/DOWN, ENTER, ESC)", curses.A_BOLD)
            for i, (name, explanation, _) in enumerate(ACTIONS):
                if i < 3:
                    line = ("> " if i == self.act_pos else "  ") + name
                    put(win, top + 2 + i * 2, x0 + 5, line, curses.color_pair(4) if i == self.act_pos else 0)
            put(win, top + 9, x0 + 5, "> BACK" if self.act_pos == 3 else "  BACK")
            put(win, 23, x0, ACTIONS[self.act_pos][1])

        elif self.mode == "typing":
            put(win, top + 3, x0 + 5, "TYPE THIS WORD:", curses.A_BOLD)
            put(win, top + 5, x0 + 5, self.word, curses.color_pair(4) | curses.A_BOLD)
            put(win, top + 7, x0 + 5, "> " + self.typed + "_", curses.color_pair(3))
            current = 0 if self.started_typing is None else time.monotonic() - self.started_typing
            put(win, 21, x0, f"TIME: {current:.2f}s    MAX DAMAGE: 190")
            put(win, 23, x0, "TYPE, then ENTER. BACKSPACE edits. ESC cancels.")

        elif self.mode == "notice":
            put(win, top + ARENA_H // 2, x0 + 9, "THE CONTACT RESPONDS...", curses.A_BOLD)
            put(win, 21, x0, "Prepare to dodge!")

        elif self.mode == "end":
            put(win, top + 4, x0 + 17, self.result, curses.A_BOLD | curses.color_pair(4))
            put(win, top + 6, x0 + 7, f"Turns survived: {self.turn}")
            put(win, 21, x0, "R: restart battle   ENTER / Q: exit")

        put(win, 26, x0, "FIGHT: timed typing  ACT: spend TP  ITEM: +40 HP", curses.A_DIM)
        win.refresh()


def main(screen):
    curses.cbreak()
    curses.noecho()
    screen.keypad(True)
    screen.nodelay(True)
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    if curses.has_colors():
        curses.start_color()
        try:
            curses.use_default_colors()
            bg = -1
        except curses.error:
            bg = curses.COLOR_BLACK
        curses.init_pair(2, curses.COLOR_RED, bg)
        curses.init_pair(3, curses.COLOR_CYAN, bg)
        curses.init_pair(4, curses.COLOR_YELLOW, bg)

    fight = ContactFight()
    while fight.mode != "quit":
        frame_start = time.monotonic()
        for _ in range(15):
            k = screen.getch()
            if k == -1:
                break
            fight.on_key(k)
        fight.update(time.monotonic())
        fight.draw(screen)
        time.sleep(max(0, 1 / FPS - (time.monotonic() - frame_start)))


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("Connection closed.")
