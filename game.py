import pygame
import asyncio
import sys
import random
import math
import threading
import queue
import array
import json
import os
from datetime import date
from TrikiPy import TrikiDevice

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SIZE = 36
OBSTACLE_SIZE = 34
COIN_RADIUS = 10
LANE_COUNT = 7
LANE_WIDTH = WIDTH // LANE_COUNT
LANE_OFFSET = (WIDTH - LANE_COUNT * LANE_WIDTH) // 2
SCROLL_SPEED_BASE = 4
MILESTONE_INTERVAL = 1000
BOSS_INTERVAL = 2000
PORTAL_INTERVAL = 3000
BOOST_DURATION = 120
BOOST_SPEED_MUL = 2.0
NIGHT_INTERVAL = 900
NIGHT_DURATION = 300

BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
GREEN = (60, 220, 80)
RED = (230, 40, 60)
YELLOW = (255, 220, 30)
GOLD = (255, 215, 0)
SILVER = (200, 210, 220)
ORANGE = (255, 160, 20)
PURPLE = (180, 80, 255)
LIGHT_GRAY = (140, 140, 140)
ROAD_COLOR = (45, 45, 50)
ROAD_LINE = (70, 70, 80)
CYAN = (80, 220, 255)
PINK = (255, 100, 200)

triki_status_queue = queue.Queue()
triki_analog = 0.0
triki_connected = False
triki_running = True
triki_raw = (0, 0, 0)
triki_battery = -1
triki_offset = 0.0

triki_button = False
triki_button_raw = False
triki_accel = (0, 0, 0)

s_coin = s_hit = s_shield = s_milestone = s_boost = s_portal = s_shoot = None

UPGRADE_FILE = "triki_upgrades.json"
TOTAL_COINS_FILE = "triki_total_coins.txt"
CHALLENGES_FILE = "triki_challenges.json"

def make_sound(freq, duration, volume=0.15):
    sr = 22050
    n = int(sr * duration / 1000)
    buf = array.array('h', [0]) * n
    for i in range(n):
        t = i / sr
        env = max(0, 1 - i / n)
        val = int(volume * 32767 * math.sin(2 * math.pi * freq * t) * env)
        buf[i] = val
    return pygame.mixer.Sound(buffer=buf)

class Particle:
    def __init__(self, x, y, color, count=8):
        self.parts = []
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 4)
            self.parts.append([x, y, math.cos(angle) * speed, math.sin(angle) * speed, 255,
                              random.uniform(2, 5)])

    def update(self):
        for p in self.parts[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.1
            p[4] -= p[5]
            if p[4] <= 0:
                self.parts.remove(p)

    def draw(self, screen, offset=(0, 0)):
        ox, oy = offset
        for p in self.parts:
            alpha = max(0, p[4])
            sz = max(1, int(p[5] * 0.6))
            s = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, int(alpha)), (sz, sz), sz)
            screen.blit(s, (int(p[0] - sz + ox), int(p[1] - sz + oy)))

    @property
    def alive(self):
        return len(self.parts) > 0

def load_upgrades():
    default = {'sprint_level': 0, 'magnet_level': 0, 'life_level': 0, 'stars': 0}
    try:
        with open(UPGRADE_FILE) as f:
            return {**default, **json.load(f)}
    except:
        return default

def save_upgrades(data):
    try:
        with open(UPGRADE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def load_total_coins():
    try:
        with open(TOTAL_COINS_FILE) as f:
            return int(f.read().strip())
    except:
        return 0

def save_total_coins(val):
    try:
        with open(TOTAL_COINS_FILE, "w") as f:
            f.write(str(val))
    except:
        pass

def load_challenges():
    today = str(date.today())
    try:
        with open(CHALLENGES_FILE) as f:
            data = json.load(f)
            if data.get('date') == today:
                return data
    except:
        pass
    pool = [
        ('coins', 'Zbierz 20 monet', 20),
        ('coins', 'Zbierz 30 monet', 30),
        ('coins', 'Zbierz 40 monet', 40),
        ('dodge', 'Uniknij 5 przeszkód z rzędu', 5),
        ('dodge', 'Uniknij 8 przeszkód z rzędu', 8),
        ('dodge', 'Uniknij 12 przeszkód z rzędu', 12),
        ('distance', 'Przebiegnij 2000', 2000),
        ('distance', 'Przebiegnij 4000', 4000),
        ('sprint', 'Użyj sprintu 3 razy', 3),
        ('sprint', 'Użyj sprintu 5 razy', 5),
        ('special', 'Zbierz 3 specjalne monety', 3),
        ('special', 'Zbierz 5 specjalnych monet', 5),
        ('shoot', 'Zestrzel 2 przeszkody', 2),
        ('shoot', 'Zestrzel 4 przeszkody', 4),
        ('shoot', 'Zestrzel 3 drony', 3),
    ]
    chosen = random.sample(pool, 3)
    data = {'date': today, 'challenges': [
        {'type': c[0], 'desc': c[1], 'target': c[2], 'progress': 0, 'done': False} for c in chosen
    ]}
    try:
        with open(CHALLENGES_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass
    return data

def save_challenges(data):
    try:
        with open(CHALLENGES_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

class Player:
    def __init__(self, extra_lives=0):
        self.x = WIDTH // 2 - PLAYER_SIZE // 2
        self.target_x = self.x
        self.y = HEIGHT - 100
        self.min_x = LANE_OFFSET
        self.max_x = LANE_OFFSET + LANE_COUNT * LANE_WIDTH - PLAYER_SIZE
        self.lives = 3 + extra_lives
        self.invincible = 0
        self.shield = False
        self.combo = 0
        self.max_combo = 0
        self.boost_timer = 0
        self.ghost_positions = []
        self.dodge_streak = 0
        self.sprint_count = 0
        self.special_coins = 0
        self.ammo = 5
        self.max_ammo = 5
        self.shoot_cooldown = 0

    def shoot(self):
        if self.ammo <= 0 or self.shoot_cooldown > 0:
            return None
        self.ammo -= 1
        self.shoot_cooldown = 15
        return Bullet(self.x, self.y)

    def reload(self, amount=1):
        self.ammo = min(self.max_ammo, self.ammo + amount)

    def move_left(self):
        self.target_x = max(self.min_x, self.target_x - LANE_WIDTH)

    def move_right(self):
        self.target_x = min(self.max_x, self.target_x + LANE_WIDTH)

    def update(self, triki_val=None, total_coins=0):
        if triki_val is not None:
            self.x += triki_val * 14
            self.x = max(self.min_x, min(self.max_x, self.x))
        else:
            if abs(self.target_x - self.x) > 0.5:
                self.x += (self.target_x - self.x) * 0.25
            else:
                self.x = float(self.target_x)
        if self.invincible > 0:
            self.invincible -= 1
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.boost_timer > 0:
            self.boost_timer -= 1
        if abs(triki_val or 0) > 0.7:
            self.ghost_positions.append([self.x, self.y, 180])
        if len(self.ghost_positions) > 10:
            self.ghost_positions.pop(0)
        for g in self.ghost_positions[:]:
            g[2] -= 4
            if g[2] <= 0:
                self.ghost_positions.remove(g)

    def skin_color(self, total_coins):
        if total_coins >= 500:
            return GOLD
        if total_coins >= 300:
            return ORANGE
        if total_coins >= 150:
            return PURPLE
        if total_coins >= 50:
            return (80, 150, 255)
        return GREEN

    def draw(self, screen, offset=(0, 0), total_coins=0):
        if self.invincible > 0 and self.invincible % 6 < 3:
            return
        px, py = int(self.x) + offset[0], int(self.y) + offset[1]

        for gx, gy, ga in self.ghost_positions:
            if ga <= 0:
                continue
            gpx = int(gx) + offset[0]
            gpy = int(gy) + offset[1]
            gh = pygame.Rect(gpx, gpy, PLAYER_SIZE, PLAYER_SIZE)
            c = self.skin_color(total_coins)
            alpha_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            alpha_surf.fill((c[0], c[1], c[2], min(ga, 80)))
            screen.blit(alpha_surf, (gpx, gpy))

        body = pygame.Rect(px, py, PLAYER_SIZE, PLAYER_SIZE)
        color = PURPLE if self.shield else self.skin_color(total_coins)
        if self.boost_timer > 0:
            glow = int(128 + 127 * math.sin(pygame.time.get_ticks() * 0.02))
            color = (min(255, color[0] + glow // 4), min(255, color[1] + glow // 4), min(255, color[2] + glow // 4))
        pygame.draw.rect(screen, color, body, border_radius=6)
        darker = tuple(max(0, c - 40) for c in color)
        pygame.draw.rect(screen, darker, body, 2, border_radius=6)
        if self.boost_timer > 0:
            for _ in range(4):
                bx = px + random.randint(-6, PLAYER_SIZE + 6)
                by = py + random.randint(-6, PLAYER_SIZE + 6)
                pygame.draw.rect(screen, (255, 255, 255, 120), (bx, by, random.randint(4, 10), random.randint(2, 4)))
        eye_x, eye_y = px + 6, py + 7
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), 4)
        pygame.draw.circle(screen, WHITE, (eye_x + 12, eye_y), 4)
        pygame.draw.circle(screen, BLACK, (eye_x + 1, eye_y + 1), 2)
        pygame.draw.circle(screen, BLACK, (eye_x + 13, eye_y + 1), 2)
        if self.shield:
            pygame.draw.circle(screen, (180, 80, 255, 80), (px + PLAYER_SIZE // 2, py + PLAYER_SIZE // 2), PLAYER_SIZE // 2 + 4, 2)

    def get_rect(self):
        return pygame.Rect(int(self.x), self.y, PLAYER_SIZE, PLAYER_SIZE)

class Obstacle:
    TYPES = {
        'small': {'size': 22, 'speed_mul': 1.6, 'color': (230, 80, 60)},
        'normal': {'size': 34, 'speed_mul': 1.0, 'color': (230, 40, 60)},
        'big': {'size': 48, 'speed_mul': 0.6, 'color': (180, 30, 50)},
        'boss': {'size': 0, 'speed_mul': 0.5, 'color': (120, 20, 40)},
    }

    def __init__(self, x, base_speed, otype='normal'):
        if otype == 'boss':
            self.size = LANE_WIDTH * 3 - 20
            self.x = LANE_OFFSET + 10
            self.speed = base_speed * 0.5
            self.color = (120, 20, 40)
        else:
            info = self.TYPES[otype]
            self.x = x
            self.speed = base_speed * info['speed_mul']
            self.size = info['size']
            self.color = info['color']
        self.y = -self.size
        self.otype = otype
        self.rot = 0
        self.rot_speed = random.uniform(-4, 4)
        self.hp = 3 if otype == 'boss' else 1

    def update(self):
        self.y += self.speed
        self.rot += self.rot_speed

    def draw(self, screen, offset=(0, 0), night=False):
        ox, oy = offset
        if self.otype == 'boss':
            s = pygame.Surface((self.size, 34), pygame.SRCALPHA)
            c = (120, 20, 40) if self.hp > 1 else (180, 20, 30)
            pygame.draw.rect(s, c, (0, 0, self.size, 34), border_radius=4)
            pygame.draw.rect(s, (80, 10, 30), (0, 0, self.size, 34), 2, border_radius=4)
            for i in range(5):
                lx = 8 + i * (self.size - 16) // 4
                pygame.draw.circle(s, (200, 30, 50), (lx, 17), 5)
            if night:
                pygame.draw.rect(s, (255, 50, 50, 200), (0, 0, self.size, 34), 3, border_radius=4)
            screen.blit(s, (int(self.x + ox), int(self.y + oy)))
            return
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.rect(s, self.color, (2, 2, self.size - 4, self.size - 4), border_radius=4)
        darker = tuple(max(0, c - 50) for c in self.color)
        pygame.draw.rect(s, darker, (0, 0, self.size, self.size), 2, border_radius=4)
        if night:
            glow_color = (255, 100, 100)
            pygame.draw.rect(s, glow_color, (0, 0, self.size, self.size), 3, border_radius=4)
        s2 = pygame.transform.rotate(s, self.rot)
        cx, cy = self.x + self.size // 2 + ox, self.y + self.size // 2 + oy
        r = s2.get_rect(center=(cx, cy))
        screen.blit(s2, r.topleft)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size if self.otype != 'boss' else 34)

class CoinObj:
    def __init__(self, x, speed, ctype='normal'):
        self.x = x
        self.y = -20
        self.speed = speed
        self.vx = 0.0
        self.ctype = ctype
        self.phase = random.uniform(0, math.pi * 2)
        self.radius = COIN_RADIUS
        if ctype == 'gold':
            self.radius = 13
            self.color = GOLD
            self.dark = (200, 170, 0)
            self.points = 3
            self.special = True
        elif ctype == 'silver':
            self.radius = 11
            self.color = SILVER
            self.dark = (160, 170, 180)
            self.points = 2
            self.special = True
        else:
            self.color = YELLOW
            self.dark = (200, 180, 0)
            self.points = 1
            self.special = False

    def update(self):
        self.y += self.speed + abs(self.vx) * 0.3
        self.x += self.vx
        self.phase += 0.08

    def draw(self, screen, offset=(0, 0)):
        bob = math.sin(self.phase) * 3
        cy = int(self.y + bob + offset[1])
        cx = int(self.x + offset[0])
        r = self.radius
        if self.ctype == 'gold':
            glow = int(128 + 127 * math.sin(self.phase * 2))
            gs = pygame.Surface((r * 4, r * 4), pygame.SRCALPHA)
            pygame.draw.circle(gs, (255, 215, 0, glow // 4), (r * 2, r * 2), r * 2)
            screen.blit(gs, (cx - r * 2, cy - r * 2))
        pygame.draw.circle(screen, self.color, (cx, cy), r)
        pygame.draw.circle(screen, self.dark, (cx, cy), r, 2)
        pygame.draw.circle(screen, self.dark, (cx - r // 3, cy), max(2, r // 3))

    def get_rect(self):
        r = self.radius
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

class PortalObj:
    def __init__(self, x):
        self.x = x
        self.y = -60
        self.speed = 3
        self.phase = 0

    def update(self):
        self.y += self.speed
        self.phase += 0.1

    def draw(self, screen, offset=(0, 0)):
        ox, oy = offset
        cx = int(self.x + ox)
        cy = int(self.y + oy)
        pulse = math.sin(self.phase) * 5
        for r in range(30, 10, -5):
            alpha = int(100 + 155 * (1 - r / 30))
            pg = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            clr = (80 + int(pulse * 5), 200 + int(pulse * 3), 255, alpha)
            pygame.draw.circle(pg, clr, (r, r), r)
            screen.blit(pg, (cx - r, cy - r))
        pygame.draw.circle(screen, CYAN, (cx, cy), 12 + int(pulse))
        pygame.draw.circle(screen, WHITE, (cx, cy), 6 + int(pulse * 0.5))

    def get_rect(self):
        return pygame.Rect(self.x - 30, self.y - 30, 60, 60)

class Bullet:
    def __init__(self, x, y):
        self.x = x + PLAYER_SIZE // 2 - 3
        self.y = y
        self.speed = -10
        self.alive = True

    def update(self):
        self.y += self.speed
        if self.y < -20:
            self.alive = False

    def draw(self, screen, offset=(0, 0)):
        ox, oy = offset
        cx, cy = int(self.x + ox), int(self.y + oy)
        pygame.draw.rect(screen, CYAN, (cx - 2, cy - 8, 6, 16), border_radius=2)
        pygame.draw.circle(screen, WHITE, (cx, cy - 8), 4)
        for i in range(3):
            alpha = 100 - i * 30
            pygame.draw.circle(screen, (80, 220, 255, alpha), (cx, cy + i * 6), 3 - i)

    def get_rect(self):
        return pygame.Rect(self.x - 3, self.y - 10, 6, 20)

class Drone:
    def __init__(self, base_speed):
        side = random.choice([-1, 1])
        self.x = LANE_OFFSET - 30 if side == -1 else LANE_OFFSET + LANE_COUNT * LANE_WIDTH + 30
        self.y = random.uniform(80, 250)
        self.dir = side
        self.speed = random.uniform(2, 4)
        self.base_scroll = base_speed
        self.phase = random.uniform(0, math.pi * 2)
        self.size = 24
        self.hp = 1

    def update(self):
        self.x += self.dir * self.speed
        self.y += math.sin(self.phase) * 0.5
        self.phase += 0.03
        if self.dir == -1 and self.x > LANE_OFFSET + LANE_COUNT * LANE_WIDTH + 30:
            self.alive = False
        elif self.dir == 1 and self.x < LANE_OFFSET - 30:
            self.alive = False
        else:
            self.alive = True

    def draw(self, screen, offset=(0, 0)):
        ox, oy = offset
        cx, cy = int(self.x + ox), int(self.y + oy)
        s = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(s, (200, 40, 80), (self.size // 2, self.size // 2), self.size // 2 - 2)
        pygame.draw.circle(s, (255, 80, 120), (self.size // 2, self.size // 2), self.size // 2 - 4, 2)
        for i in range(3):
            angle = self.phase + i * math.pi * 2 / 3
            px = self.size // 2 + int(math.cos(angle) * (self.size // 2 - 2))
            py = self.size // 2 + int(math.sin(angle) * (self.size // 2 - 2))
            pygame.draw.circle(s, (255, 60, 100), (px, py), 3)
        screen.blit(s, (cx - self.size // 2, cy - self.size // 2))

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    @property
    def alive(self):
        return hasattr(self, '_alive') and self._alive

    @alive.setter
    def alive(self, val):
        self._alive = val

class Target:
    def __init__(self, base_speed):
        self.x = random.uniform(LANE_OFFSET + 20, LANE_OFFSET + LANE_COUNT * LANE_WIDTH - 20)
        self.y = -30
        self.speed = base_speed * 0.7
        self.radius = 16
        self.phase = 0
        self.mult = random.choice([2, 3, 5])

    def update(self):
        self.y += self.speed
        self.phase += 0.05

    def draw(self, screen, offset=(0, 0)):
        ox, oy = offset
        cx, cy = int(self.x + ox), int(self.y + oy)
        pulse = math.sin(self.phase * 2) * 2
        r = self.radius + int(pulse)
        colors = {2: (100, 255, 100), 3: (100, 200, 255), 5: GOLD}
        col = colors.get(self.mult, WHITE)
        pygame.draw.circle(screen, col, (cx, cy), r, 3)
        pygame.draw.circle(screen, (col[0], col[1], col[2], 60), (cx, cy), r + 4, 1)
        draw_text(screen, f"x{self.mult}", 14, cx, cy, col)

    def get_rect(self):
        r = self.radius + 4
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)

class Road:
    def __init__(self):
        self.offset = 0
        self.stars = []
        for _ in range(80):
            sx = random.randint(20, WIDTH - 20)
            sy = random.randint(20, HEIGHT - 20)
            bright = random.randint(60, 200)
            r = random.choice([1, 1, 1, 2])
            self.stars.append((sx, sy, bright, r))

    def update(self, speed):
        self.offset = (self.offset + speed) % 80

    def _draw_starfield(self, screen, blink_frame=0):
        for i, (sx, sy, bright, r) in enumerate(self.stars):
            blink = abs(60 - (blink_frame + i * 7) % 120) / 60
            b = int(bright * (0.6 + 0.4 * blink))
            pygame.draw.circle(screen, (b, b, b), (sx, sy), r)

    def draw(self, screen, speed=4, tod=0.0, night=False, portal_mode=False):
        if portal_mode:
            bg = (10, 5, 30)
            screen.fill(bg)
            for _ in range(60):
                sx = random.randint(0, WIDTH)
                sy = random.randint(0, HEIGHT)
                pygame.draw.circle(screen, (255, 255, 255, random.randint(30, 100)), (sx, sy), random.randint(1, 2))
            pygame.draw.rect(screen, (20, 10, 50), (LANE_OFFSET, 0, LANE_COUNT * LANE_WIDTH, HEIGHT))
            lc = (60, 30, 100)
            for i in range(LANE_COUNT + 1):
                lx = i * LANE_WIDTH + LANE_OFFSET
                pygame.draw.line(screen, lc, (lx, 0), (lx, HEIGHT), 2)
            return

        bg_colors = [
            (8, 4, 22), (12, 6, 32), (20, 10, 40), (30, 15, 50), (20, 10, 35), (8, 4, 22),
        ]
        idx = int(tod) % (len(bg_colors) - 1)
        t = tod - int(tod)
        c1, c2 = bg_colors[idx], bg_colors[idx + 1]
        bg = (int(c1[0] + (c2[0] - c1[0]) * t),
              int(c1[1] + (c2[1] - c1[1]) * t),
              int(c1[2] + (c2[2] - c1[2]) * t))
        if night:
            bg = (max(0, bg[0] - 20), max(0, bg[1] - 20), max(0, bg[2] - 20))
        screen.fill(bg)
        self._draw_starfield(screen, speed * 10)

        glow = (60, 30, 120)
        for g in range(3, 0, -1):
            glow_alpha = int(15 / (g + 1))
            r = max(0, glow[0] - g * 8)
            gv = max(0, glow[1] - g * 5)
            b = max(0, glow[2] - g * 15)
            pygame.draw.rect(screen, (r, gv, b), (LANE_OFFSET - g, 0, LANE_COUNT * LANE_WIDTH + g * 2, HEIGHT), g)

        road_bg = (max(0, bg[0] - 3), max(0, bg[1] - 3), max(0, bg[2] - 3))
        pygame.draw.rect(screen, road_bg, (LANE_OFFSET, 0, LANE_COUNT * LANE_WIDTH, HEIGHT))

        for i in range(LANE_COUNT + 1):
            lx = i * LANE_WIDTH + LANE_OFFSET
            for g in (3, 1):
                c = (min(20, 255), min(g * 60, 255), min(g * 80 + 40, 255)) if i == 0 or i == LANE_COUNT else (0, min(g * 40, 255), min(g * 60, 255))
                pygame.draw.line(screen, c, (lx, 0), (lx, HEIGHT), g if g > 1 else 1)

        neon = (0, 180, 255)
        for y in range(-80 + int(self.offset), HEIGHT, 80):
            for i in range(LANE_COUNT):
                lx = i * LANE_WIDTH + LANE_WIDTH // 2 + LANE_OFFSET
                for g in (5, 3, 1):
                    a = max(0, 100 - g * 20)
                    c = (0, a, min(255, a + 100))
                    if g < 3:
                        pygame.draw.line(screen, c, (lx, y + 4 - g), (lx, y + 36 + g), g)
                pygame.draw.line(screen, (180, 255, 255), (lx, y + 4), (lx, y + 36), 1)

        sl = max(0, int(speed - 3))
        if sl > 0:
            for side_x in (LANE_OFFSET - 10, LANE_OFFSET + LANE_COUNT * LANE_WIDTH + 4):
                for j in range(3):
                    ly = (j * 200 + int(self.offset * 1.5)) % (HEIGHT + 100) - 50
                    llen = 15 + sl * 3
                    bright = min(200, 80 + sl * 20)
                    pygame.draw.line(screen, (bright // 2, bright, bright), (side_x, ly), (side_x, ly + llen), 2)

def triki_thread():
    asyncio.run(_triki_loop())

async def _triki_loop():
    global triki_connected, triki_running, triki_analog, triki_raw, triki_battery, triki_offset, triki_button, triki_button_raw, triki_accel
    triki = TrikiDevice(BTName="Triki", literal=False)
    if not await triki.connectTriki(timeout=5.0):
        triki_status_queue.put("Triki nie znaleziony. Graj strzałkami.")
        return
    triki_connected = True
    b = await triki.getBatteryLevel()
    triki_battery = b
    triki_status_queue.put(f"Triki podłączony! Bateria: {b}%")
    if not await triki.startTriki():
        triki_status_queue.put("Błąd strumienia Triki")
        return
    samples = []
    for _ in range(10):
        try:
            d = await asyncio.wait_for(triki.getTrikiData(), timeout=0.2)
            samples.append(d.gx)
        except asyncio.TimeoutError:
            pass
    if samples:
        triki_offset = sum(samples) / len(samples)
    triki_status_queue.put("Triki gotowy! Przechylaj w lewo/prawo")
    triki_prev_button = False
    try:
        while triki_running:
            try:
                d = await asyncio.wait_for(triki.getTrikiData(), timeout=0.05)
                triki_raw = (d.gx, d.gy, d.gz)
                triki_accel = (d.ax, d.ay, d.az)
            except asyncio.TimeoutError:
                pass

            btn = triki.isButtonPressed()
            if btn and not triki_prev_button:
                triki_button = True
            triki_prev_button = btn
            triki_button_raw = btn

            gx_corrected = triki_raw[0] - triki_offset
            if abs(gx_corrected) < 50:
                triki_analog = 0.0
            else:
                triki_analog = max(-1.0, min(1.0, gx_corrected / 1000.0))
    finally:
        await triki.stopTriki()

def draw_text(screen, text, size, x, y, color=WHITE, center=True, right=False, font_name="Arial"):
    font = pygame.font.SysFont(font_name, size, bold=True)
    surf = font.render(text, True, color)
    if right:
        r = surf.get_rect(topright=(x, y))
    elif center:
        r = surf.get_rect(center=(x, y))
    else:
        r = surf.get_rect(topleft=(x, y))
    screen.blit(surf, r)

def load_highscore():
    try:
        with open("triki_highscore.txt") as f:
            data = f.read().strip().split(",")
            return int(data[0]), int(data[1]) if len(data) > 1 else 0
    except:
        return 0, 0

def save_highscore(score, stars):
    try:
        old_score, old_stars = load_highscore()
        best_score = max(old_score, score)
        best_stars = max(old_stars, stars)
        with open("triki_highscore.txt", "w") as f:
            f.write(f"{best_score},{best_stars}")
    except:
        pass

def calc_stars(score, coins, max_combo):
    s = 0
    if score >= 500:
        s += 1
    if score >= 2000 and coins >= 10:
        s += 1
    if score >= 5000 and coins >= 30 and max_combo >= 10:
        s += 1
    return s

def upgrade_cost(level, base):
    return base + level * base // 2

def show_shop(screen, upgrades):
    global triki_button
    max_levels = {'sprint_level': 3, 'magnet_level': 3, 'life_level': 2}
    keys = ['sprint_level', 'magnet_level', 'life_level']
    items = keys + ['POWRÓT']
    selected = 0
    clock = pygame.time.Clock()
    last_tilt_time = 0
    last_shake_mag = 0

    def buy_upgrade():
        nonlocal upgrades
        key = keys[selected]
        lvl = upgrades[key]
        if lvl < max_levels[key]:
            cost = upgrade_cost(lvl, 2)
            if upgrades['stars'] >= cost:
                upgrades['stars'] -= cost
                upgrades[key] += 1
                save_upgrades(upgrades)
                make_sound(880, 100).play()
            else:
                make_sound(200, 200).play()

    blink = 0
    shop_stars = make_menu_stars()

    while True:
        clock.tick(30)
        blink = (blink + 1) % 60

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return True
                if e.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(items)
                if e.key == pygame.K_UP:
                    selected = (selected - 1) % len(items)
                if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                    if selected == len(keys):
                        return True
                    buy_upgrade()

        now = pygame.time.get_ticks()
        shake_mag = abs(triki_accel[0]) + abs(triki_accel[1]) + abs(triki_accel[2])
        if shake_mag > 22000 and last_shake_mag < 17000 and now - last_tilt_time > 400:
            selected = (selected + 1) % len(items)
            last_tilt_time = now
        last_shake_mag = shake_mag

        if triki_button:
            triki_button = False
            if selected == len(keys):
                return True
            buy_upgrade()

        labels = {
            'sprint_level': ('Dłuższy sprint', f'Czas sprintu +{50 * (upgrades["sprint_level"] + 1)}%'),
            'magnet_level': ('Większy magnes', f'Zasięg +{(upgrades["magnet_level"] + 1) * 40}px'),
            'life_level': ('Dodatkowe życie', f'+{upgrades["life_level"] + 1} życie na start'),
        }

        screen.fill(BLACK)
        draw_menu_stars(screen, shop_stars, blink)
        menu_draw_frame(screen, GOLD)
        draw_text(screen, "SKLEP ULEPSZEŃ", 42, WIDTH // 2, 50, GOLD)
        draw_text(screen, f"Dostępne gwiazdki: {upgrades['stars']} ★", 26, WIDTH // 2, 95, WHITE)

        for i, key in enumerate(keys):
            y = 150 + i * 110
            lvl = upgrades[key]
            ml = max_levels[key]
            name, desc = labels[key]
            maxed = lvl >= ml
            color = CYAN if i == selected else WHITE
            prefix = "► " if i == selected else "  "
            draw_text(screen, prefix + name, 24, 150, y, color, center=False)
            draw_text(screen, desc, 16, 150, y + 30, LIGHT_GRAY, center=False)
            stars_disp = "★" * lvl + "☆" * (ml - lvl)
            draw_text(screen, stars_disp, 20, 150, y + 52, GOLD, center=False)
            if not maxed:
                cost = upgrade_cost(lvl, 2)
                draw_text(screen, f"Koszt: {cost} ★", 18, 500, y + 15, color, center=False)
            else:
                draw_text(screen, "MAX", 20, 500, y + 15, GREEN, center=False)

        y_back = 150 + len(keys) * 110
        back_color = CYAN if selected == len(keys) else WHITE
        prefix = "► " if selected == len(keys) else "  "
        draw_text(screen, prefix + "POWRÓT", 24, 150, y_back, back_color, center=False)

        draw_text(screen, "Przechyl Triki / Strzałki - wybór  |  Przycisk / ENTER - akceptuj", 16, WIDTH // 2, HEIGHT - 40, LIGHT_GRAY)
        pygame.display.flip()

def make_menu_stars():
    stars = []
    for _ in range(80):
        sx = random.randint(20, WIDTH - 20)
        sy = random.randint(20, HEIGHT - 20)
        bright = random.randint(60, 200)
        r = random.choice([1, 1, 1, 2])
        stars.append((sx, sy, bright, r))
    return stars

def draw_menu_stars(screen, stars, blink_frame=0):
    for i, (sx, sy, bright, r) in enumerate(stars):
        blink = abs(60 - (blink_frame + i * 7) % 120) / 60
        b = int(bright * (0.6 + 0.4 * blink))
        pygame.draw.circle(screen, (b, b, b), (sx, sy), r)

def menu_draw_frame(screen, color=CYAN):
    pygame.draw.rect(screen, color, (10, 10, WIDTH - 20, HEIGHT - 20), 3)
    for i in range(8):
        px = 14 + i * ((WIDTH - 28) // 7)
        pygame.draw.rect(screen, color, (px, 14, (WIDTH - 28) // 7 - 2, 4))

def show_start(screen):
    global triki_button
    menu_options = ["NOWA GRA", "SKLEP", "WYJŚCIE"]
    selected = 0
    clock = pygame.time.Clock()
    blink = 0
    last_tilt_time = 0
    last_shake_mag = 0
    connection_status = "Łączenie z Triki..."
    status_color = LIGHT_GRAY
    status_msgs = []
    while not triki_status_queue.empty():
        status_msgs.append(triki_status_queue.get())
    if status_msgs:
        connection_status = status_msgs[-1]
        if "nie znaleziony" in connection_status:
            status_color = RED
        elif "gotowy" in connection_status or "podłączony" in connection_status:
            status_color = GREEN

    menu_stars = make_menu_stars()

    while True:
        clock.tick(30)
        blink = (blink + 1) % 60

        while not triki_status_queue.empty():
            connection_status = triki_status_queue.get()
            if "nie znaleziony" in connection_status:
                status_color = RED
            elif "gotowy" in connection_status or "podłączony" in connection_status:
                status_color = GREEN

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP or e.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(menu_options)
                if e.key == pygame.K_DOWN or e.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(menu_options)
                if e.key == pygame.K_SPACE or e.key == pygame.K_RETURN:
                    if selected == 0:
                        return True
                    elif selected == 1:
                        upgrades = load_upgrades()
                        if not show_shop(screen, upgrades):
                            return False
                    elif selected == 2:
                        return False
                if e.key == pygame.K_ESCAPE:
                    return False

        now = pygame.time.get_ticks()
        shake_mag = abs(triki_accel[0]) + abs(triki_accel[1]) + abs(triki_accel[2])
        if shake_mag > 22000 and last_shake_mag < 17000 and now - last_tilt_time > 400:
            selected = (selected + 1) % len(menu_options)
            last_tilt_time = now
        last_shake_mag = shake_mag

        if triki_button:
            triki_button = False
            if selected == 0:
                return True
            elif selected == 1:
                upgrades = load_upgrades()
                if not show_shop(screen, upgrades):
                    return False
            elif selected == 2:
                return False

        screen.fill(BLACK)
        draw_menu_stars(screen, menu_stars, blink)
        menu_draw_frame(screen, CYAN)

        draw_text(screen, "TRiKI RUNNER", 56, WIDTH // 2, 65, GREEN)
        for i in range(WIDTH):
            c = (min(255, i // 2), min(255, i // 3), 80)
            pygame.draw.line(screen, c, (i, 115), (i, 116))

        for i, opt in enumerate(menu_options):
            y = 200 + i * 80
            color = CYAN if i == selected else WHITE
            if i == selected:
                prefix = "► " if blink < 30 else "  "
                draw_text(screen, prefix + opt, 34, WIDTH // 2, y, color)
            else:
                draw_text(screen, "  " + opt, 34, WIDTH // 2, y, color)

        if triki_connected and triki_battery >= 0:
            status_text = f"Triki: Połączony (Bateria: {triki_battery}%)"
            status_color = GREEN
        elif triki_connected:
            status_text = "Triki: Połączony"
            status_color = GREEN
        else:
            status_text = f"Triki: {connection_status}"
        draw_text(screen, status_text, 16, WIDTH // 2, HEIGHT - 55, status_color)

        draw_text(screen, "Przechyl Triki / Strzałki - wybór  |  Przycisk / SPACJA - akceptuj", 14, WIDTH // 2, HEIGHT - 30, LIGHT_GRAY)

        pygame.display.flip()

def show_over(screen, score, coins, highscore, stars, best_stars, challenges):
    global triki_button
    menu_options = ["GRAJ PONOWNIE", "SKLEP", "WYJŚCIE"]
    selected = 0
    clock = pygame.time.Clock()
    blink = 0
    last_tilt_time = 0
    last_shake_mag = 0
    menu_stars = make_menu_stars()

    while True:
        clock.tick(30)
        blink = (blink + 1) % 60

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return False
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP or e.key == pygame.K_LEFT:
                    selected = (selected - 1) % len(menu_options)
                if e.key == pygame.K_DOWN or e.key == pygame.K_RIGHT:
                    selected = (selected + 1) % len(menu_options)
                if e.key == pygame.K_SPACE or e.key == pygame.K_RETURN:
                    if selected == 0:
                        return True
                    elif selected == 1:
                        upgrades = load_upgrades()
                        if not show_shop(screen, upgrades):
                            return False
                    elif selected == 2:
                        return False
                if e.key == pygame.K_ESCAPE:
                    return False

        now = pygame.time.get_ticks()
        shake_mag = abs(triki_accel[0]) + abs(triki_accel[1]) + abs(triki_accel[2])
        if shake_mag > 22000 and last_shake_mag < 17000 and now - last_tilt_time > 400:
            selected = (selected + 1) % len(menu_options)
            last_tilt_time = now
        last_shake_mag = shake_mag

        if triki_button:
            triki_button = False
            if selected == 0:
                return True
            elif selected == 1:
                upgrades = load_upgrades()
                if not show_shop(screen, upgrades):
                    return False
            elif selected == 2:
                return False

        screen.fill(BLACK)
        draw_menu_stars(screen, menu_stars, blink)
        menu_draw_frame(screen, RED)

        draw_text(screen, "KONIEC GRY", 56, WIDTH // 2, 60, RED)

        star_text = " ".join(["★" if i < stars else "☆" for i in range(3)])
        draw_text(screen, star_text, 36, WIDTH // 2, 115, GOLD)
        draw_text(screen, f"Dystans: {score}", 22, WIDTH // 2, 155, WHITE)
        draw_text(screen, f"Monety: {coins}", 20, WIDTH // 2, 185, YELLOW)
        draw_text(screen, f"Rekord: {highscore}", 16, WIDTH // 2, 215, ORANGE)
        best_star_text = " ".join(["★" if i < best_stars else "☆" for i in range(3)])
        draw_text(screen, f"Najlepsze: {best_star_text}", 16, WIDTH // 2, 235, GOLD)

        done_count = sum(1 for c in challenges['challenges'] if c['done'])
        draw_text(screen, f"Wyzwania: {done_count}/3", 18, WIDTH // 2, HEIGHT - 100, PURPLE)

        for i, opt in enumerate(menu_options):
            y = 290 + i * 60
            color = CYAN if i == selected else WHITE
            if i == selected:
                prefix = "► " if blink < 30 else "  "
                draw_text(screen, prefix + opt, 28, WIDTH // 2, y, color)
            else:
                draw_text(screen, "  " + opt, 28, WIDTH // 2, y, color)

        draw_text(screen, "Przechyl Triki / Strzałki - wybór  |  Przycisk / SPACJA - akceptuj", 14, WIDTH // 2, HEIGHT - 40, LIGHT_GRAY)
        pygame.display.flip()

def draw_tilt_bar(screen, val):
    bar_w, bar_h = 200, 10
    bx = WIDTH // 2 - bar_w // 2
    by = HEIGHT - 30
    pygame.draw.rect(screen, (50, 50, 50), (bx, by, bar_w, bar_h), border_radius=3)
    cx = bx + bar_w // 2
    cx += val * (bar_w // 2 - 2)
    color = GREEN if abs(val) < 0.3 else ORANGE if abs(val) < 0.7 else RED
    pygame.draw.rect(screen, color, (cx - 4, by - 2, 8, bar_h + 4), border_radius=2)

def draw_lives(screen, lives):
    for i in range(3):
        x = 20 + i * 24
        c = RED if i < lives else (40, 10, 15)
        pygame.draw.rect(screen, c, (x, HEIGHT - 55, 16, 16), border_radius=3)
    if lives > 3:
        draw_text(screen, f"+{lives - 3}", 16, 20 + 3 * 24, HEIGHT - 55, RED, center=False)

def draw_shield_indicator(screen, shielded):
    if shielded:
        draw_text(screen, "TARCZA", 16, 20, HEIGHT - 80, PURPLE, center=False)

def draw_ammo(screen, ammo, max_ammo):
    for i in range(max_ammo):
        x = 20 + i * 16
        c = CYAN if i < ammo else (30, 35, 45)
        pygame.draw.rect(screen, c, (x, HEIGHT - 28, 10, 14), border_radius=2)
        if i < ammo:
            pygame.draw.rect(screen, (150, 240, 255), (x + 2, HEIGHT - 26, 6, 4), border_radius=1)
    if ammo == 0:
        draw_text(screen, "BRAK AMUNICJI!", 14, 20 + max_ammo * 16 + 4, HEIGHT - 26, (255, 100, 100), center=False)

def draw_button_indicator(screen, triki_connected, button_pressed):
    x, y = WIDTH - 50, HEIGHT - 55
    if not triki_connected:
        return
    outer = CYAN if button_pressed else (50, 50, 60)
    inner = (150, 240, 255) if button_pressed else (30, 35, 45)
    pygame.draw.circle(screen, outer, (x, y), 10)
    pygame.draw.circle(screen, inner, (x, y), 6)
    if button_pressed:
        for r in range(12, 18, 3):
            pygame.draw.circle(screen, (60, 180, 220), (x, y), r, 1)

def draw_combo_bar(screen, combo):
    bar_w, bar_h = 120, 8
    bx = 20
    by = HEIGHT - 40
    pygame.draw.rect(screen, (30, 30, 30), (bx, by, bar_w, bar_h), border_radius=2)
    fill = min(combo / 10, 1.0)
    pygame.draw.rect(screen, PURPLE, (bx + 1, by + 1, int((bar_w - 2) * fill), bar_h - 2), border_radius=2)

def draw_flare(screen, timer):
    if timer <= 0:
        return
    alpha = int(timer * 3)
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for side in range(4):
        r = [pygame.Rect(0, 0, WIDTH, 4), pygame.Rect(0, HEIGHT - 4, WIDTH, 4),
             pygame.Rect(0, 0, 4, HEIGHT), pygame.Rect(WIDTH - 4, 0, 4, HEIGHT)][side]
        pygame.draw.rect(surf, (180, 80, 255, min(alpha, 180)), r)
    screen.blit(surf, (0, 0))

def draw_challenge_hud(screen, challenges):
    if not challenges:
        return
    y = 80
    for ch in challenges['challenges']:
        bar_w = 150
        pct = min(ch['progress'] / ch['target'], 1.0) if ch['target'] > 0 else 0
        color = GREEN if ch['done'] else PURPLE
        draw_text(screen, ch['desc'], 14, WIDTH - 10, y, color, center=False, right=True)
        pygame.draw.rect(screen, (40, 40, 40), (WIDTH - 160, y + 16, bar_w, 6), border_radius=2)
        pygame.draw.rect(screen, color, (WIDTH - 160, y + 16, int(bar_w * pct), 6), border_radius=2)
        y += 36

def draw_night_overlay(screen, night_active, night_timer):
    if not night_active:
        return
    alpha = min(180, int((1 - night_timer / NIGHT_DURATION) * 180))
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    surf.fill((0, 0, 30, alpha))
    screen.blit(surf, (0, 0))

def spawn_group_obstacle(obstacles, base_speed):
    count = random.randint(2, 3)
    area_left = LANE_OFFSET + 10
    area_right = LANE_OFFSET + LANE_COUNT * LANE_WIDTH - 10 - 22
    total_w = count * 26
    cx = random.uniform(area_left + total_w // 2, area_right - total_w // 2)
    start_x = cx - total_w // 2
    for i in range(count):
        x = start_x + i * 26 + random.uniform(-3, 3)
        obstacles.append(Obstacle(x, base_speed, 'small'))

def game_loop(screen, upgrades):
    global triki_analog, triki_running, triki_battery, triki_button, triki_button_raw
    extra_lives = upgrades.get('life_level', 0)
    sprint_bonus = upgrades.get('sprint_level', 0) * 60
    magnet_bonus = upgrades.get('magnet_level', 0) * 40
    total_coins = load_total_coins()

    player = Player(extra_lives)
    road = Road()
    obstacles = []
    coin_objs = []
    particles = []
    portals = []
    bullets = []
    drones = []
    targets = []
    score = 0
    coins_collected = 0
    scroll = SCROLL_SPEED_BASE
    spawn_tick = 0
    coin_tick = 0
    diff_tick = 0
    status_msg = ""
    status_timer = 0
    paused = False
    shake_timer = 0
    shake_intensity = 0
    last_milestone = 0
    last_boss_score = 0
    last_portal_score = 0
    boss_active = False
    last_wave = 0
    wave_cooldown = 0
    current_zone = 0
    portal_mode = False
    portal_timer = 0
    flare_timer = 0
    last_mult = 1
    last_shake_check = (0, 0)
    clock = pygame.time.Clock()
    boost_active = False
    night_timer = 0
    night_active = False
    challenges = load_challenges()
    prev_obstacles_len = 0
    shoot_hits = 0
    drones_destroyed = 0

    boost_dur = BOOST_DURATION + sprint_bonus

    while triki_running:
        clock.tick(FPS)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                triki_running = False
                return None, None, None, None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    paused = not paused
                if e.key == pygame.K_s and not paused and not portal_mode:
                    player.boost_timer = boost_dur
                    boost_active = True
                    player.sprint_count += 1
                    for ch in challenges['challenges']:
                        if ch['type'] == 'sprint' and not ch['done']:
                            ch['progress'] = min(ch['target'], ch['progress'] + 1)
                            if ch['progress'] >= ch['target']:
                                ch['done'] = True
                    save_challenges(challenges)
                    s_boost.play()
                    status_msg = "SPRINT!"
                    status_timer = 60
                if not paused:
                    if e.key == pygame.K_LEFT or e.key == pygame.K_a:
                        player.move_left()
                    if e.key == pygame.K_RIGHT or e.key == pygame.K_d:
                        player.move_right()
                    if e.key == pygame.K_ESCAPE:
                        triki_running = False
                        return None, None, None, None
                if not paused and not portal_mode:
                    if e.key == pygame.K_SPACE:
                        bullet = player.shoot()
                        if bullet:
                            bullets.append(bullet)
                            s_shoot.play()

        if paused:
            road.draw(screen, scroll)
            player.draw(screen, total_coins=total_coins)
            for o in obstacles:
                o.draw(screen)
            for c in coin_objs:
                c.draw(screen)
            draw_text(screen, "PAUZA", 72, WIDTH // 2, HEIGHT // 2, WHITE)
            draw_text(screen, "Naciśnij P, aby kontynuować", 20, WIDTH // 2, HEIGHT // 2 + 60, LIGHT_GRAY)
            pygame.display.flip()
            continue

        if portal_mode:
            portal_timer -= 1
            road.draw(screen, scroll, portal_mode=True)
            player.draw(screen, total_coins=total_coins)
            for c in coin_objs:
                c.draw(screen)
            for p in particles:
                p.draw(screen)

            if portal_timer % 8 == 0:
                x = random.uniform(LANE_OFFSET + 10, LANE_OFFSET + LANE_COUNT * LANE_WIDTH - 10)
                coin_objs.append(CoinObj(x, scroll + 1, random.choice(['normal', 'normal', 'normal', 'silver', 'gold'])))

            draw_text(screen, "STREFA PORTALU!", 36, WIDTH // 2, 60, CYAN)
            draw_text(screen, f"Czas: {portal_timer // FPS}s", 22, WIDTH // 2, 100, WHITE)

            for c in coin_objs[:]:
                c.update()
                if c.y > HEIGHT + 20:
                    coin_objs.remove(c)
                elif player.get_rect().colliderect(c.get_rect()):
                    coin_objs.remove(c)
                    coins_collected += c.points
                    if c.special:
                        player.special_coins += 1
                    total_coins += 1
                    save_total_coins(total_coins)
                    score += 50 * c.points
                    particles.append(Particle(c.x, c.y, c.color, 8))
                    s_coin.play()
                    for ch in challenges['challenges']:
                        if ch['type'] == 'coins' and not ch['done']:
                            ch['progress'] = min(ch['target'], ch['progress'] + 1)
                            if ch['progress'] >= ch['target']:
                                ch['done'] = True
                        if ch['type'] == 'special' and c.special and not ch['done']:
                            ch['progress'] = min(ch['target'], ch['progress'] + 1)
                            if ch['progress'] >= ch['target']:
                                ch['done'] = True
                    save_challenges(challenges)

            for p in particles[:]:
                p.update()
                if not p.alive:
                    particles.remove(p)

            if portal_timer <= 0:
                portal_mode = False
                coin_objs.clear()
                status_msg = "Powrót do gry!"
                status_timer = 60
                s_portal.play()

            player.update(triki_analog if triki_connected else None, total_coins)
            if player.boost_timer > 0:
                player.boost_timer -= 1

            draw_text(screen, f"Dystans: {score}", 22, 110, 25, WHITE, center=False)
            draw_text(screen, f"Monety: {coins_collected}", 22, 110, 55, YELLOW, center=False)
            draw_challenge_hud(screen, challenges)
            pygame.display.flip()
            continue

        spawn_tick += 1
        coin_tick += 1
        diff_tick += 1

        if triki_button and not triki_connected:
            triki_button = False

        if triki_connected:
            gx, gy, gz = triki_raw
            if triki_button and not portal_mode:
                bullet = player.shoot()
                if bullet:
                    bullets.append(bullet)
                    s_shoot.play()
                triki_button = False
            shake_mag = abs(gy) + abs(gz)
            last_shake_mag = abs(last_shake_check[0]) + abs(last_shake_check[1])
            if shake_mag > 2500 and last_shake_mag < 1000 and not boost_active and player.boost_timer <= 0:
                player.boost_timer = boost_dur
                boost_active = True
                player.sprint_count += 1
                for ch in challenges['challenges']:
                    if ch['type'] == 'sprint' and not ch['done']:
                        ch['progress'] = min(ch['target'], ch['progress'] + 1)
                        if ch['progress'] >= ch['target']:
                            ch['done'] = True
                save_challenges(challenges)
                s_boost.play()
                status_msg = "SPRINT z Triki!"
                status_timer = 60
            last_shake_check = (gy, gz)

        speed_mul = BOOST_SPEED_MUL if player.boost_timer > 0 else 1.0
        effective_scroll = scroll * speed_mul

        player.update(triki_analog if triki_connected else None, total_coins)
        road.update(effective_scroll)

        try:
            msg = triki_status_queue.get_nowait()
            status_msg = msg
            status_timer = 180
        except queue.Empty:
            pass

        if status_timer > 0:
            status_timer -= 1
        if shake_timer > 0:
            shake_timer -= 1
        if flare_timer > 0:
            flare_timer -= 1
        if player.boost_timer <= 0:
            boost_active = False

        night_timer += 1
        if night_timer % NIGHT_INTERVAL < NIGHT_DURATION:
            night_active = True
        else:
            night_active = False

        scroll = min(SCROLL_SPEED_BASE + score // 500, 14)

        spawn_interval = max(20, 70 - int(scroll * 4))
        coin_interval = max(12, 35 - int(scroll * 2))

        new_zone = (score >= 10000) * 3 + (score >= 5000) * 2 + (score >= 2000) * 1
        if new_zone > current_zone:
            current_zone = new_zone
            zone_labels = ["", "ŚREDNIA", "TRUDNA", "SZALONA"]
            status_msg = f"STREFA {current_zone} – {zone_labels[current_zone]}"
            status_timer = 120

        wave_check = score // 1000
        if wave_check > last_wave:
            last_wave = wave_check
            wave_cooldown = 90
            status_msg = f"FALA {wave_check}!"
            status_timer = 90
            for _ in range(random.randint(3, 5)):
                ox = random.uniform(LANE_OFFSET + 10, LANE_OFFSET + LANE_COUNT * LANE_WIDTH - 30)
                obstacles.append(Obstacle(ox, scroll, random.choice(['small', 'normal'])))
            spawn_tick = 0

        if wave_cooldown > 0:
            wave_cooldown -= 1

        spawn_chance = min(0.85, 0.35 + scroll * 0.035)

        if not boss_active and spawn_tick > spawn_interval and random.random() < spawn_chance and wave_cooldown == 0:
            r = random.random()
            area_left = LANE_OFFSET + 10
            area_right = LANE_OFFSET + LANE_COUNT * LANE_WIDTH - 10
            group_chance = min(0.4, 0.1 + scroll * 0.02)
            big_chance = min(0.3, 0.1 + scroll * 0.015)
            if r < group_chance:
                spawn_group_obstacle(obstacles, scroll)
            elif r < group_chance + big_chance:
                x = random.uniform(area_left, area_right - 48)
                obstacles.append(Obstacle(x, scroll, 'big'))
            else:
                otype = 'small' if r < group_chance + big_chance + 0.15 else 'normal'
                size = Obstacle.TYPES[otype]['size']
                x = random.uniform(area_left, area_right - size)
                obstacles.append(Obstacle(x, scroll, otype))
            spawn_tick = 0

        coin_spawn_chance = min(0.65, 0.3 + scroll * 0.025)
        if coin_tick > coin_interval and random.random() < coin_spawn_chance:
            r2 = random.random()
            al = LANE_OFFSET + COIN_RADIUS
            ar = LANE_OFFSET + LANE_COUNT * LANE_WIDTH - COIN_RADIUS
            x = random.uniform(al, ar)
            gold_chance = min(0.1, 0.03 + scroll * 0.005)
            silver_chance = min(0.2, 0.1 + scroll * 0.008)
            if r2 < gold_chance:
                coin_objs.append(CoinObj(x, scroll, 'gold'))
            elif r2 < gold_chance + silver_chance:
                coin_objs.append(CoinObj(x, scroll, 'silver'))
            else:
                coin_objs.append(CoinObj(x, scroll, 'normal'))
            coin_tick = 0

        if spawn_tick > spawn_interval and random.random() < 0.08 and not boss_active and not portal_mode:
            targets.append(Target(scroll))

        if spawn_tick > spawn_interval and random.random() < 0.06 and not portal_mode:
            drones.append(Drone(scroll))

        boss_wave = last_wave
        if boss_wave >= 5 and boss_wave % 5 == 0 and not boss_active and last_boss_score < boss_wave:
            last_boss_score = boss_wave
            boss_active = True
            obstacles.append(Obstacle(0, scroll, 'boss'))
            status_msg = "BOSS! Omijaj!"
            status_timer = 90

        portal_check = score // PORTAL_INTERVAL
        if portal_check > last_portal_score and not portal_mode and not boss_active:
            last_portal_score = portal_check
            px = random.uniform(LANE_OFFSET + 20, LANE_OFFSET + LANE_COUNT * LANE_WIDTH - 20)
            portals.append(PortalObj(px))
            status_msg = "PORTAL! Wskakuj!"
            status_timer = 90

        m_range = 120 + magnet_bonus
        if player.shield:
            for c in coin_objs:
                dx = (player.x + PLAYER_SIZE // 2) - c.x
                dy = (player.y + PLAYER_SIZE // 2) - c.y
                dist = math.hypot(dx, dy)
                if dist < m_range and dist > 5:
                    pull = (m_range - dist) / m_range * 4
                    c.vx += (dx / dist) * pull * 0.3
                    c.vx = max(-6, min(6, c.vx))

        for b in bullets[:]:
            b.update()
            if not b.alive:
                bullets.remove(b)
                continue
            hit = False
            for o in obstacles[:]:
                if b.get_rect().colliderect(o.get_rect()):
                    if o.otype == 'boss':
                        o.hp -= 1
                        particles.append(Particle(o.x + o.size // 2, o.y + o.size // 2, CYAN, 8))
                        if o.hp <= 0:
                            obstacles.remove(o)
                            boss_active = False
                            score += 100
                            for _ in range(5):
                                particles.append(Particle(o.x + o.size // 2, HEIGHT // 2, RED, 15))
                            status_msg = "BOSS zestrzelony! +100"
                            status_timer = 90
                    elif o.otype != 'boss':
                        obstacles.remove(o)
                        score += 5
                        shoot_hits += 1
                        particles.append(Particle(o.x + o.size // 2, o.y + o.size // 2, CYAN, 6))
                    bullets.remove(b)
                    hit = True
                    break
            if hit:
                continue
            for d in drones[:]:
                if b.get_rect().colliderect(d.get_rect()):
                    drones.remove(d)
                    drones_destroyed += 1
                    score += 15
                    for _ in range(4):
                        particles.append(Particle(d.x, d.y, (255, 60, 100), 6))
                    bullets.remove(b)
                    hit = True
                    break
            if hit:
                continue
            for t in targets[:]:
                if b.get_rect().colliderect(t.get_rect()):
                    targets.remove(t)
                    coins_collected += t.mult
                    total_coins += t.mult
                    player.combo += 1
                    if player.combo > player.max_combo:
                        player.max_combo = player.combo
                    for _ in range(4):
                        particles.append(Particle(t.x, t.y, GOLD, 6))
                    status_msg = f"Tarcza! x{t.mult}"
                    status_timer = 45
                    bullets.remove(b)
                    break

        dodging = True
        for o in obstacles[:]:
            o.update()
            if o.y > HEIGHT + 20:
                obstacles.remove(o)
                if o.otype == 'boss':
                    boss_active = False
                    score += 100
                    for _ in range(5):
                        particles.append(Particle(o.x + o.size // 2, HEIGHT // 2, RED, 15))
                    status_msg = "BOSS pokonany! +100"
                    status_timer = 90
                else:
                    score += 10
            elif player.get_rect().colliderect(o.get_rect()):
                dodging = False
                if o.otype == 'boss':
                    if player.shield:
                        player.shield = False
                        particles.append(Particle(player.x + PLAYER_SIZE // 2, player.y, PURPLE, 12))
                        s_shield.play()
                    elif player.invincible <= 0:
                        player.lives -= 1
                        player.invincible = 90
                        player.combo = 0
                        shake_timer = 10
                        shake_intensity = 8
                        s_hit.play()
                        particles.append(Particle(player.x + PLAYER_SIZE // 2, player.y, RED, 14))
                        if player.lives <= 0:
                            save_total_coins(total_coins)
                            return score, coins_collected, player.max_combo, challenges
                        status_msg = f"Pozostało żyć: {player.lives}"
                        status_timer = 60
                    continue
                if player.shield:
                    player.shield = False
                    obstacles.remove(o)
                    particles.append(Particle(o.x + o.size // 2, o.y + o.size // 2, PURPLE, 12))
                    score += 10
                    status_msg = "Tarcza zniszczona!"
                    status_timer = 60
                    s_shield.play()
                elif player.invincible <= 0:
                    player.lives -= 1
                    player.invincible = 90
                    player.combo = 0
                    obstacles.remove(o)
                    particles.append(Particle(o.x + o.size // 2, o.y + o.size // 2, RED, 14))
                    shake_timer = 10
                    shake_intensity = 8
                    s_hit.play()
                    if player.lives <= 0:
                        save_total_coins(total_coins)
                        return score, coins_collected, player.max_combo, challenges
                    status_msg = f"Pozostało żyć: {player.lives}"
                    status_timer = 60

        if dodging and len(obstacles) == prev_obstacles_len:
            player.dodge_streak += 1
        else:
            player.dodge_streak = 0
            prev_obstacles_len = len(obstacles)

        for d in drones[:]:
            d.update()
            d.y += effective_scroll
            if not d.alive or d.y > HEIGHT + 40:
                drones.remove(d)

        for t in targets[:]:
            t.update()
            t.y += effective_scroll
            if t.y > HEIGHT + 40:
                targets.remove(t)

        for ch in challenges['challenges']:
            if ch['type'] == 'dodge' and not ch['done']:
                ch['progress'] = max(ch['progress'], min(ch['target'], player.dodge_streak))
                if ch['progress'] >= ch['target']:
                    ch['done'] = True
        for ch in challenges['challenges']:
            if ch['type'] == 'distance' and not ch['done']:
                ch['progress'] = min(ch['target'], score)
                if ch['progress'] >= ch['target']:
                    ch['done'] = True
        for ch in challenges['challenges']:
            if ch['type'] == 'shoot' and not ch['done']:
                target_key = ch.get('desc', '')
                if 'dron' in target_key.lower():
                    ch['progress'] = min(ch['target'], drones_destroyed)
                else:
                    ch['progress'] = min(ch['target'], shoot_hits)
                if ch['progress'] >= ch['target']:
                    ch['done'] = True
        save_challenges(challenges)

        for c in coin_objs[:]:
            c.update()
            if c.y > HEIGHT + 20:
                coin_objs.remove(c)
            elif player.get_rect().colliderect(c.get_rect()):
                coin_objs.remove(c)
                coins_collected += c.points
                if c.special:
                    player.special_coins += 1
                    for ch in challenges['challenges']:
                        if ch['type'] == 'special' and not ch['done']:
                            ch['progress'] = min(ch['target'], ch['progress'] + 1)
                            if ch['progress'] >= ch['target']:
                                ch['done'] = True
                total_coins += 1
                if total_coins % 10 == 0:
                    player.reload(1)
                save_total_coins(total_coins)
                pt = 50 * c.points
                multiplier = min(coins_collected // 5 + 1, 10)
                if multiplier != last_mult and multiplier > 1:
                    flare_timer = 20
                    last_mult = multiplier
                score += pt * multiplier
                player.combo += 1
                if player.combo > player.max_combo:
                    player.max_combo = player.combo
                if player.combo >= 10:
                    player.combo = 0
                    player.shield = True
                    status_msg = "TARCZA! +1 ochrona"
                    status_timer = 90
                    s_shield.play()
                particles.append(Particle(c.x, c.y, c.color, 8))
                s_coin.play()
                for ch in challenges['challenges']:
                    if ch['type'] == 'coins' and not ch['done']:
                        ch['progress'] = min(ch['target'], ch['progress'] + 1)
                        if ch['progress'] >= ch['target']:
                            ch['done'] = True
                save_challenges(challenges)

        for p in portals[:]:
            p.update()
            if p.y > HEIGHT + 20:
                portals.remove(p)
            elif player.get_rect().colliderect(p.get_rect()):
                portals.remove(p)
                portal_mode = True
                portal_timer = FPS * 5
                coin_objs.clear()
                s_portal.play()
                status_msg = "Portal! Zbieraj monety!"
                status_timer = 60

        milestone = score // MILESTONE_INTERVAL
        if milestone > last_milestone:
            last_milestone = milestone
            status_msg = f"Kamień milowy! {milestone * MILESTONE_INTERVAL}"
            status_timer = 120
            for _ in range(3):
                particles.append(Particle(WIDTH // 2, HEIGHT // 2, ORANGE, 20))
            s_milestone.play()

        for p in particles[:]:
            p.update()
            if not p.alive:
                particles.remove(p)

        shake_offset = (0, 0)
        if shake_timer > 0:
            sx = random.randint(-shake_intensity, shake_intensity)
            sy = random.randint(-shake_intensity, shake_intensity)
            shake_offset = (sx, sy)

        tod = (diff_tick / 10800) % 6
        road.draw(screen, effective_scroll, tod, night_active)
        if not portal_mode:
            player.draw(screen, shake_offset, total_coins)
            for o in obstacles:
                o.draw(screen, shake_offset, night_active)
            for c in coin_objs:
                c.draw(screen, shake_offset)
            for p in portals:
                p.draw(screen, shake_offset)
            for d in drones:
                d.draw(screen, shake_offset)
            for t in targets:
                t.draw(screen, shake_offset)
            for b in bullets:
                b.draw(screen, shake_offset)
        for p in particles:
            p.draw(screen, shake_offset)

        draw_night_overlay(screen, night_active, night_timer % NIGHT_INTERVAL)
        draw_flare(screen, flare_timer)

        mult = min(coins_collected // 5 + 1, 10)
        mult_text = f"x{mult}" if mult > 1 else ""
        draw_text(screen, f"Dystans: {score}", 22, 110, 25, WHITE, center=False)
        draw_text(screen, f"Monety: {coins_collected} {mult_text}", 22, 110, 55, YELLOW, center=False)

        if triki_connected:
            gx, gy, gz = triki_raw
            draw_text(screen, f"Gyr X:{gx:+5d}  Y:{gy:+5d}  Z:{gz:+5d}", 14, WIDTH - 10, 14, (255, 200, 100), center=False, right=True)
            draw_text(screen, f"Tilt: {triki_analog:+.2f}", 14, WIDTH - 10, 32, (255, 200, 100), center=False, right=True)
            if triki_battery >= 0:
                bc = GREEN if triki_battery > 50 else ORANGE if triki_battery > 20 else RED
                draw_text(screen, f"Bateria: {triki_battery}%", 14, WIDTH - 10, 50, bc, center=False, right=True)
        else:
            draw_text(screen, "Klawiatura", 14, WIDTH - 60, 15, ORANGE, center=True)

        draw_tilt_bar(screen, triki_analog if triki_connected else 0)
        draw_lives(screen, player.lives)
        draw_shield_indicator(screen, player.shield)
        draw_ammo(screen, player.ammo, player.max_ammo)
        draw_button_indicator(screen, triki_connected, triki_button_raw)
        draw_combo_bar(screen, player.combo)
        draw_challenge_hud(screen, challenges)

        if player.boost_timer > 0:
            draw_text(screen, f"SPRINT {int(player.boost_timer / boost_dur * 100)}%", 16, 110, 80, (100, 255, 255), center=False)
        if night_active:
            draw_text(screen, "NOC", 16, 110, 100, (100, 100, 255), center=False)

        if status_timer > 0:
            draw_text(screen, status_msg, 20, WIDTH // 2, 105, WHITE)

        pygame.display.flip()

    return None, None, None, None

def main():
    global triki_running
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Triki Runner")

    global s_coin, s_hit, s_shield, s_milestone, s_boost, s_portal, s_shoot
    s_coin = make_sound(880, 80)
    s_hit = make_sound(200, 200)
    s_shield = make_sound(660, 150)
    s_milestone = make_sound(440, 300, 0.25)
    s_boost = make_sound(1040, 300)
    s_portal = make_sound(660, 400, 0.3)
    s_shoot = make_sound(1200, 60)

    thread = threading.Thread(target=triki_thread, daemon=True)
    thread.start()

    if not show_start(screen):
        triki_running = False
        pygame.quit()
        return

    highscore, best_stars = load_highscore()
    upgrades = load_upgrades()

    while triki_running:
        score, collected, max_combo, challenges = game_loop(screen, upgrades)
        if score is None:
            break
        stars = calc_stars(score, collected, max_combo)
        done_challenges = sum(1 for c in challenges['challenges'] if c['done'])
        if done_challenges == 3:
            stars = min(3, stars + 1)
            upgrades = load_upgrades()
            upgrades['stars'] += 1
            save_upgrades(upgrades)
        upgrades = load_upgrades()
        upgrades['stars'] += stars
        save_upgrades(upgrades)
        save_highscore(score, stars)
        highscore, best_stars = load_highscore()
        again = show_over(screen, score, collected, highscore, stars, best_stars, challenges)
        if not again:
            break

    triki_running = False
    pygame.quit()

if __name__ == "__main__":
    main()
