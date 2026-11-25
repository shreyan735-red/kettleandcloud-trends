"""FLOOR 0 — Part 1/6. 30s cinematic stickman horror."""
import math
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from hengine import (FONT_MONO, H, INK, W, cone, ease, font, lerp, lit, noise_tex, run_video, spot,
                     stickman, title_overlay, to_arr, words_for, render_frame)

DUR = 30.0
STEEL = (132, 136, 140)
STEEL_DK = (84, 87, 92)
RED0 = (255, 46, 40)

# ---------------------------------------------------------------- environments
BTN_X = (430, 650)
BTN_Y0, BTN_STEP = 1180, 160


def btn_pos(n):
    if n == 0:
        return BTN_X[0], BTN_Y0 + 160
    row = (n - 1) // 2
    return BTN_X[(n - 1) % 2], BTN_Y0 - row * BTN_STEP


@lru_cache(None)
def panel_bg():
    img = Image.new("RGB", (W, H), STEEL)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([250, 220, 830, 1520], radius=26, fill=STEEL_DK, outline=(50, 52, 56), width=8)
    for sx, sy in [(285, 255), (795, 255), (285, 1485), (795, 1485)]:
        d.ellipse([sx - 12, sy - 12, sx + 12, sy + 12], fill=(150, 152, 156), outline=(40, 40, 44), width=3)
        d.line([sx - 7, sy, sx + 7, sy], fill=(60, 60, 64), width=3)
    for n in range(0, 13):
        x, y = btn_pos(n)
        d.ellipse([x - 66, y - 66, x + 66, y + 66], fill=(46, 48, 52))
        d.ellipse([x - 58, y - 58, x + 58, y + 58], fill=(104, 108, 112) if n else (60, 30, 30),
                  outline=(170, 172, 176) if n else (140, 40, 36), width=6)
        d.text((x, y), str(n), font=font(64, FONT_MONO), fill=(30, 32, 36) if n else RED0, anchor="mm")
    light = cone(120, -260, math.radians(62), 0.55, 2600, 1.15)
    arr = lit(img, light, ambient=0.16, tint=(1.0, 0.97, 0.92))
    arr += noise_tex(3, streak=True)[..., None] * (0.4 + light[..., None])
    return arr


ELEV_BACK = dict(x0=210, x1=870, y0=380, y1=1240)


def _elev_room(d, wall_fill, w):
    x0, x1, y0, y1 = w["x0"], w["x1"], w["y0"], w["y1"]
    d.polygon([(0, 0), (x0, y0), (x0, y1), (0, H)], fill=(104, 108, 112))  # left wall
    d.polygon([(W, 0), (x1, y0), (x1, y1), (W, H)], fill=(96, 100, 104))  # right wall
    d.polygon([(0, 0), (W, 0), (x1, y0), (x0, y0)], fill=(70, 72, 76))  # ceiling
    d.polygon([(x0, y1), (x1, y1), (W, H), (0, H)], fill=(108, 102, 94))  # floor
    for i in range(1, 8):  # floor tiles toward the vanishing point
        tx = lerp(x0, 0, i / 8), lerp(x1, W, i / 8)
        yy = lerp(y1, H, (i / 8) ** 1.7)
        d.line([(lerp(x0, 0, (yy - y1) / (H - y1)), yy), (lerp(x1, W, (yy - y1) / (H - y1)), yy)], fill=(84, 80, 74), width=3)
    for i in range(1, 6):
        fx = lerp(x0, x1, i / 6)
        d.line([(fx, y1), (lerp(0, W, i / 6), H)], fill=(84, 80, 74), width=3)
    d.rectangle([x0, y0, x1, y1], fill=wall_fill)
    # panel seams on side walls
    for t in (0.33, 0.66):
        d.line([(lerp(0, x0, t), lerp(0, y0, t)), (lerp(0, x0, t), lerp(H, y1, t))], fill=(80, 82, 86), width=4)
        d.line([(lerp(W, x1, t), lerp(0, y0, t)), (lerp(W, x1, t), lerp(H, y1, t))], fill=(76, 78, 82), width=4)
    # ceiling light panel
    d.polygon([(380, 110), (700, 110), (650, 260), (430, 260)], fill=(236, 232, 218))


@lru_cache(None)
def elevator_back(dim=False):
    img = Image.new("RGB", (W, H), STEEL)
    d = ImageDraw.Draw(img)
    _elev_room(d, (122, 126, 130), ELEV_BACK)
    # mirror
    d.rectangle([300, 440, 780, 1010], fill=(70, 80, 88), outline=(40, 42, 46), width=10)
    for i in range(5):
        d.line([(330 + i * 90, 470), (300 + i * 90 + 160, 980)], fill=(84, 94, 102), width=10)
    # handrail
    d.rectangle([210, 1080, 870, 1100], fill=(170, 172, 176))
    # button panel on the right wall
    d.polygon([(925, 760), (985, 742), (985, 1080), (925, 1070)], fill=(70, 72, 76), outline=(30, 30, 34))
    for i in range(6):
        for j in range(2):
            d.ellipse([936 + j * 24, 780 + i * 44, 950 + j * 24, 794 + i * 44], fill=(140, 142, 146))
    d.ellipse([936, 1040, 950, 1054], fill=(200, 40, 36))
    light = spot(540, 200, 760, 1.15, squash=0.8) + spot(540, 1350, 520, 0.55, squash=1.6)
    arr = lit(img, light, ambient=0.07, tint=(1.0, 0.96, 0.88))
    arr += noise_tex(5, streak=True)[..., None] * light[..., None]
    return arr, light


CORR = dict(x0=440, x1=640, y0=780, y1=990)  # far end wall of the corridor


@lru_cache(None)
def hallway(kind):
    """kind: 'zero' (cold blue, every door open) or 'twelve' (warm, doors shut, 12C ajar)."""
    zero = kind == "zero"
    wall = (118, 124, 126) if zero else (128, 116, 98)
    img = Image.new("RGB", (W, H), wall)
    d = ImageDraw.Draw(img)
    x0, x1, y0, y1 = CORR["x0"], CORR["x1"], CORR["y0"], CORR["y1"]
    d.polygon([(0, 0), (W, 0), (x1, y0), (x0, y0)], fill=(90, 94, 98) if zero else (100, 92, 80))
    d.polygon([(x0, y1), (x1, y1), (W, H), (0, H)], fill=(92, 96, 102) if zero else (110, 90, 70))
    d.polygon([(0, 0), (x0, y0), (x0, y1), (0, H)], fill=wall)
    d.polygon([(W, 0), (x1, y0), (x1, y1), (W, H)], fill=tuple(int(c * 0.92) for c in wall))
    d.rectangle([x0, y0, x1, y1], fill=tuple(int(c * 0.85) for c in wall))
    # carpet runner
    d.polygon([(x0 + 50, y1), (x1 - 50, y1), (W - 230, H), (230, H)], fill=(78, 86, 96) if zero else (120, 58, 48))
    # end door: 12C
    ed = (495, 845, 585, 990)
    d.rectangle(ed, fill=(18, 22, 30) if zero else (90, 60, 40), outline=(30, 30, 30), width=4)
    lights = []
    # side doors at several depths (t = depth 0 near .. 1 far)
    for side in (-1, 1):
        for t in (0.18, 0.45, 0.68):
            def wx(tt):
                return lerp(0, x0, tt) if side < 0 else lerp(W, x1, tt)

            def wy(tt, top):
                return lerp(0 if top else H, y0 if top else y1, tt)
            ta, tb = t, t + 0.12
            fx0, fx1 = wx(ta), wx(tb)
            top0 = lerp(wy(ta, True), wy(ta, False), 0.28)
            top1 = lerp(wy(tb, True), wy(tb, False), 0.28)
            bot0, bot1 = wy(ta, False), wy(tb, False)
            door = [(fx0, top0), (fx1, top1), (fx1, bot1), (fx0, bot0)]
            if zero:
                d.polygon(door, fill=(14, 18, 26), outline=(30, 30, 34))
                # light spilling onto the floor from each open door
                spill = [(fx0, bot0), (fx1, bot1), (lerp(fx1, 540, 0.35), bot1 + (bot0 - bot1) * 0.2 + 30),
                         (lerp(fx0, 540, 0.45), bot0 + 40)]
                d.polygon(spill, fill=(108, 126, 148))
                lights.append(((fx0 + fx1) / 2, (top0 + bot0) / 2, (fx1 - fx0) * 2.2))
            else:
                ajar = side < 0 and t == 0.45
                d.polygon(door, fill=(92, 62, 42) if not ajar else (240, 200, 120), outline=(40, 30, 24))
                if ajar:
                    # door leaf swung slightly, warm light wedge
                    d.polygon([(fx1, top1), (fx1 - (fx1 - fx0) * 0.75, top0 + 6), (fx1 - (fx1 - fx0) * 0.75, bot0 - 6), (fx1, bot1)],
                              fill=(92, 62, 42), outline=(40, 30, 24))
                    d.polygon([(fx0, bot0), (fx1, bot1), (fx1 + 160, bot1 + 260), (fx0 + 60, bot0 + 300)], fill=(200, 160, 96))
                    lights.append(((fx0 + fx1) / 2, bot0 - 60, 420))
                d.ellipse([fx1 - 22, (top1 + bot1) / 2 - 6, fx1 - 10, (top1 + bot1) / 2 + 6], fill=(200, 170, 90))
            # number plates
            d.rectangle([fx1 - 26, top1 - 50, fx1 + 6, top1 - 26], fill=(40, 40, 40))
    # ceiling strip lights toward the vanishing point
    for t in (0.12, 0.38, 0.6, 0.78):
        cy = lerp(0, y0, t) + 30 * (1 - t)
        hw = lerp(160, 30, t)
        d.rectangle([540 - hw, cy, 540 + hw, cy + lerp(26, 6, t)], fill=(225, 235, 245) if zero else (250, 220, 160))
    if zero:
        light = sum(spot(540, lerp(0, y0, t) + 40, lerp(520, 140, t), 0.55) for t in (0.12, 0.38, 0.6, 0.78))
        for lx, ly, lr in lights:
            light = light + spot(lx, ly + 120, lr, 0.5, squash=0.7)
        light = light + spot(540, 915, 120, 0.9)
        light = light + spot(540, 1500, 650, 0.35, squash=1.5)
        arr = lit(img, light, ambient=0.06, tint=(0.7, 0.86, 1.15))
    else:
        light = spot(540, 200, 760, 0.6) + spot(540, 1500, 600, 0.35, squash=1.5) + sum(spot(lx, ly, lr, 1.4) for lx, ly, lr in lights)
        arr = lit(img, light, ambient=0.1, tint=(1.12, 0.95, 0.72))
    arr += noise_tex(9)[..., None] * 0.6
    arr = to_arr(Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)))
    return arr, light


@lru_cache(None)
def apartment():
    img = Image.new("RGB", (W, H), (98, 102, 100))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 1260], fill=(96, 100, 98))
    d.polygon([(0, 1260), (W, 1260), (W, H), (0, H)], fill=(70, 58, 48))
    for i in range(12):
        y = 1260 + (i ** 1.6) * 9
        d.line([(0, y), (W, y)], fill=(56, 46, 38), width=3)
    d.rectangle([0, 1236, W, 1262], fill=(60, 60, 58))  # baseboard
    # window (the hard light source): moonlight
    d.rectangle([640, 300, 960, 760], fill=(200, 215, 235), outline=(40, 40, 44), width=14)
    d.line([(800, 300), (800, 760)], fill=(40, 40, 44), width=12)
    d.line([(640, 530), (960, 530)], fill=(40, 40, 44), width=12)
    # window light on the floor, skewed toward the left
    for (a, b, c, e) in [((360, 1420), (590, 1420), (520, 1640), (230, 1640)),
                         ((610, 1420), (840, 1420), (780, 1640), (540, 1640)),
                         ((330, 1670), (560, 1670), (480, 1900), (180, 1900)),
                         ((580, 1670), (810, 1670), (760, 1900), (500, 1900))]:
        d.polygon([a, b, c, e], fill=(176, 186, 198))
    # couch, side view, facing the left wall
    d.rounded_rectangle([170, 1180, 520, 1300], radius=24, fill=(78, 70, 64), outline=INK, width=6)  # seat
    d.rounded_rectangle([470, 960, 560, 1300], radius=24, fill=(70, 62, 58), outline=INK, width=6)  # back
    d.rectangle([180, 1300, 200, 1340], fill=INK)
    d.rectangle([520, 1300, 540, 1340], fill=INK)
    light = cone(800, 520, math.radians(118), 0.45, 1700, 1.25) + spot(800, 530, 260, 0.8)
    arr = lit(img, light, ambient=0.06, tint=(0.78, 0.9, 1.12))
    arr += noise_tex(13)[..., None] * 0.6
    return arr, light


# doors view (inside the elevator looking out) ------------------------
DOOR = (300, 360, 780, 1500)


@lru_cache(None)
def elevator_front():
    """RGBA of the elevator's front wall with a transparent doorway."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = 170, 240, 910, 1560
    d.polygon([(0, 0), (x0, y0), (x0, y1), (0, H)], fill=(102, 106, 110, 255))
    d.polygon([(W, 0), (x1, y0), (x1, y1), (W, H)], fill=(96, 100, 104, 255))
    d.polygon([(0, 0), (W, 0), (x1, y0), (x0, y0)], fill=(66, 68, 72, 255))
    d.polygon([(x0, y1), (x1, y1), (W, H), (0, H)], fill=(100, 96, 90, 255))
    d.rectangle([x0, y0, x1, y1], fill=(120, 124, 128, 255))
    d.rectangle([DOOR[0] - 14, DOOR[1] - 14, DOOR[2] + 14, DOOR[3]], fill=(70, 72, 76, 255))
    d.rectangle(DOOR, fill=(0, 0, 0, 0))
    # floor display above the doors
    d.rectangle([470, 270, 610, 330], fill=(20, 20, 22, 255))
    # button panel by the doors
    d.rectangle([830, 760, 900, 1120], fill=(70, 72, 76, 255), outline=(30, 30, 34, 255))
    for i in range(6):
        for j in range(2):
            d.ellipse([840 + j * 30, 790 + i * 46, 858 + j * 30, 808 + i * 46], fill=(150, 150, 154, 255))
    d.ellipse([840, 1070, 858, 1088], fill=(220, 40, 36, 255))
    return img


def doors_view(fr, t, open_amt, beyond_arr, beyond_light, floor_label="0", label_col=(255, 60, 50)):
    base = beyond_arr.copy()
    front = elevator_front().copy()
    d = ImageDraw.Draw(front)
    half = (DOOR[2] - DOOR[0]) / 2
    gap = half * open_amt
    lx1 = DOOR[0] + half - gap
    rx0 = DOOR[0] + half + gap
    if lx1 > DOOR[0]:
        d.rectangle([DOOR[0], DOOR[1], lx1, DOOR[3]], fill=(128, 132, 136, 255), outline=(50, 52, 56, 255), width=4)
    if rx0 < DOOR[2]:
        d.rectangle([rx0, DOOR[1], DOOR[2], DOOR[3]], fill=(124, 128, 132, 255), outline=(50, 52, 56, 255), width=4)
    d.text((540, 300), floor_label, font=font(46, FONT_MONO), fill=label_col + (255,), anchor="mm")
    fa = np.asarray(front, np.float32) / 255.0
    inside_light = spot(540, 120, 900, 0.75) + 0.1
    lit_front = fa[..., :3] * np.clip(inside_light, 0, 1.2)[..., None] * np.array([1.0, 0.96, 0.9], np.float32)
    a = fa[..., 3:4]
    arr = base * (1 - a) + lit_front * a
    fr.set_bg(arr, fig_light=np.maximum(inside_light * 0.8, beyond_light * (1 - a[..., 0])))
    fr.add_glow(540, 300, 90, label_col, 0.35)


# ---------------------------------------------------------------- shots
def s1_panel(fr, t):
    fr.set_bg(panel_bg())
    x, y = btn_pos(0)
    pulse = 0.75 + 0.25 * math.sin(t * 5.0)
    fr.add_glow(x, y, 120, RED0, 0.9 * pulse)
    fr.add_glow(x, y, 360, (180, 20, 20), 0.25 * pulse)
    fr.zoom = lerp(1.0, 1.18, ease(t / 3.0))
    fr.zoom_center = (540, lerp(960, 1180, ease(t / 3.0)))


def leo_in_elevator(fr, t, reach=0.0, buzz=False):
    arr, light = elevator_back()
    fr.set_bg(arr, fig_light=light)
    lx, ly = 640, 1660
    fr.cast_shadow(lx, ly, 560, 1380, 420, strength=230, width=58)
    arm_up = lerp(1.0, 1.75, reach)
    stickman(fr, lx, ly, 2.0, facing=1, arms=[(arm_up, lerp(0.6, 0.05, reach)), (0.08, 0.12)], bags=True)
    fr.add_glow(943, 1047, 30, (255, 50, 40), 0.6)
    fr.add_glow(540, 185, 260, (255, 240, 210), 0.25)


def s2_hover(fr, t):
    hover = 0.55 + 0.05 * math.sin(t * 3)
    leo_in_elevator(fr, t, reach=hover)
    fr.zoom = lerp(1.0, 1.08, t / 5.0)
    fr.zoom_center = (700, 1100)


def s3_press(fr, t):
    reach = ease(t / 0.5) if t < 1.0 else lerp(1.0, 0.3, ease((t - 1.0) / 0.6))
    leo_in_elevator(fr, t, reach=reach)
    if t > 0.8:  # the drop: buzzing lights, shake
        rnd = random.Random(int(t * 30))
        fr.exposure = 0.35 + 0.65 * (1 if rnd.random() > 0.28 else rnd.random() * 0.3)
        amp = 14 * (1 - ease((t - 2.8) / 1.2)) if t < 4.0 else 0
        fr.shake = (rnd.uniform(-amp, amp), rnd.uniform(-amp, amp))
    fr.zoom = 1.08
    fr.zoom_center = (700, 1100)


def s4_open(fr, t):
    arr, light = hallway("zero")
    doors_view(fr, t, ease(t / 1.6), arr, light)
    # Leo from behind, foreground, lit from the hallway (shadow falls toward us)
    fr.cast_shadow(540, 1800, 540, 1050, 520, strength=230, width=70)
    stickman(fr, 540, 1800, 2.55, facing=2, bags=False, arms=[(0.15, 0.1), (0.15, 0.1)])
    fr.zoom = lerp(1.0, 1.06, t / 5)


def s5_apartment(fr, t):
    arr, light = apartment()
    fr.set_bg(arr, fig_light=light)
    fr.blob_shadow([160, 1300, 560, 1370], 150)  # the couch casts a shadow; the Copy does not
    stickman(fr, 330, 1300, 1.55, facing=-1, sit=True, copy=True, arms=[(0.9, 0.6), (0.8, 0.6)], eye_glow=0.0)
    # Leo at the doorway, right edge, half hidden
    fr.cast_shadow(940, 1720, 1060, 1400, 520, strength=230, width=58)
    stickman(fr, 940, 1720, 1.95, facing=-1, arms=[(0.1, 0.1), (0.2, 0.2)], lean=-0.15)
    fr.zoom = lerp(1.0, 1.12, ease(t / 5))
    fr.zoom_center = (420, 1150)


def s6_close(fr, t):
    arr, light = hallway("zero")
    # the Copy, at the far end in 12C's doorway, turns its head
    sub = type(fr)(fr.tg)
    sub.set_bg(arr, fig_light=light)
    turn = ease((t - 1.0) / 1.0)
    stickman(sub, 540, 990, 0.52, facing=2, copy=True, head_turn=turn, eye_glow=turn)
    beyond = sub.base * (1 - np.asarray(sub.fig, np.float32)[..., 3:4] / 255.0) + \
        np.asarray(sub.fig, np.float32)[..., :3] / 255.0 * (np.asarray(sub.fig, np.float32)[..., 3:4] / 255.0) * 0.8
    beyond += sub.glow
    open_amt = 1 - ease((t - 0.6) / 2.6)
    doors_view(fr, t, open_amt, beyond, light)
    # Leo smashing the button, right side
    hit = abs(math.sin(t * 9)) if t < 3.2 else 0
    fr.cast_shadow(860, 1820, 540, 1050, 460, strength=230, width=64)
    stickman(fr, 860, 1820, 2.5, facing=1, arms=[(lerp(1.2, 1.75, hit), 0.0), (0.2, 0.2)], lean=0.1)
    if turn > 0.5 and open_amt > 0.08:
        fr.add_glow(540, 845, 60, (220, 230, 255), 0.5 * turn)
    if t > 3.3:
        fr.fade = ease((t - 3.3) / 0.5)
    fr.zoom = lerp(1.0, 1.1, ease(t / 3))
    fr.zoom_center = (540, 900)


def s7_twelve(fr, t):
    arr, light = hallway("twelve")
    fr.set_bg(arr, fig_light=light)
    fr.fade = max(0.0, 1 - ease(t / 0.6))
    fr.cast_shadow(700, 1760, 300, 1420, 560, strength=235, width=64)
    stickman(fr, 700, 1760, 2.3, facing=-1, arms=[(0.15, 0.1), (0.1, 0.2)], bags=True)
    fr.zoom = lerp(1.0, 1.1, ease(t / 4))
    fr.zoom_center = (420, 1050)
    if t > 2.7:
        a = ease((t - 2.7) / 0.5)
        fr.exposure = 1 - 0.75 * a
        fr.overlay.append(title_overlay("PART 2", 900, 130, (230, 40, 36), a))


SCENES = [(0, 3, s1_panel), (3, 8, s2_hover), (8, 12, s3_press), (12, 17, s4_open),
          (17, 22, s5_apartment), (22, 26, s6_close), (26, 30, s7_twelve)]

LINES = [
    ("My building has 12 floors. Tonight it has 13.", 0.2),
    ("There's never been a floor zero.", 3.4),
    ("So obviously… I pressed it.", 8.3),
    ("My hallway. But wrong.", 12.8),
    ("Someone was sitting in my apartment.", 17.4),
    ("Then it turned around.", 22.6),
    ("I live alone. So who left my light on?", 26.4),
]


def load_caps():
    """Word timings: from words.txt (start end word per line, blank line between lines) if present."""
    try:
        caps, cur = [], []
        for ln in open("words.txt"):
            if not ln.strip():
                if cur:
                    caps.append(cur)
                cur = []
                continue
            a, b, w = ln.split(maxsplit=2)
            cur.append((w.strip(), float(a), float(b)))
        if cur:
            caps.append(cur)
        if caps:
            return caps
    except FileNotFoundError:
        pass
    return [words_for(s, t0, t0 + 0.34 * len(s.split()) + 0.4) for s, t0 in LINES]


if __name__ == "__main__":
    caps = load_caps()
    if sys.argv[1] == "--still":
        render_frame(float(sys.argv[2]), SCENES, caps).save(sys.argv[3])
    else:
        run_video(SCENES, caps, sys.argv[1], DUR)
