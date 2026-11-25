"""FLOOR 0 — Part 2/6 "It Got Home First". 30s."""
import math
import random
import sys
from functools import lru_cache

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from hengine import (FONT, FONT_MONO, H, HALE, INK, W, _XX, _YY, cone, ease, font, lerp, lit, noise_tex,
                     render_frame, run_video, spot, stickman, title_overlay, to_arr)
from part1 import hallway, load_caps as _load_caps_p1

DUR = 30.0
DOORWAY = (390, 560, 690, 1440)


# ---------------------------------------------------------------- environments
@lru_cache(None)
def interior_room(seed=0):
    """Dark apartment interior looking at the front door (flat, unlit)."""
    img = Image.new("RGB", (W, H), (86, 88, 86))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 1440), (W, 1440), (W, H), (0, H)], fill=(96, 78, 62))  # wood floor
    for i in range(14):
        y = 1440 + (i ** 1.7) * 6.5
        d.line([(0, y), (W, y)], fill=(78, 62, 48), width=3)
    d.rectangle([0, 1420, W, 1442], fill=(60, 60, 58))
    d.rectangle([DOORWAY[0] - 26, DOORWAY[1] - 26, DOORWAY[2] + 26, DOORWAY[3]], fill=(64, 58, 52))
    # coat hooks + a framed picture
    d.rectangle([110, 700, 300, 900], fill=(60, 60, 64), outline=(30, 30, 30), width=8)
    for i in range(3):
        d.ellipse([800 + i * 60, 800, 820 + i * 60, 820], fill=(40, 40, 40))
    return img


@lru_cache(None)
def doorway_beyond():
    arr, _ = hallway("twelve")
    x0, y0, x1, y1 = DOORWAY
    crop = Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8)).crop((300, 520, 780, 1920))
    crop = crop.resize((x1 - x0, y1 - y0))
    return to_arr(crop) * 1.25


def entry_frame(fr, open_amt, extra_light=1.0):
    """Interior looking at the door; door swings inward (hinged left)."""
    img = interior_room().copy()
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = DOORWAY
    leaf_w = (x1 - x0) * (1 - open_amt)
    swing = (x1 - x0) * 0.35 * math.sin(open_amt * math.pi / 2)
    light = spot(540, 1000, 220, 0.08)
    if open_amt > 0.01:
        # warm light spilling through the door onto the floor
        spill = [(x0, y1), (x1, y1), (x1 + 330 * open_amt, H), (x0 - 140 * open_amt, H)]
        mask = Image.new("L", (W, H), 0)
        ImageDraw.Draw(mask).polygon(spill, fill=255)
        m = to_arr(mask.filter(ImageFilter.GaussianBlur(10)))
        light = light + m * 0.95 * open_amt * extra_light + cone(540, 1000, math.pi / 2, 0.7, 1200, 0.25 * open_amt)
    arr = lit(img, light, ambient=0.05, tint=(1.1, 0.95, 0.75))
    if open_amt > 0.01:
        beyond = doorway_beyond()
        arr[y0:y1, x0:x1] = beyond
    # the door leaf, seen edge-on as it swings toward us
    leaf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leaf)
    lx1 = x0 + leaf_w
    ld.polygon([(x0, y0), (lx1 + swing, y0 - 40 * open_amt), (lx1 + swing, y1 + 60 * open_amt), (x0, y1)],
               fill=(84, 58, 40, 255), outline=(30, 22, 16, 255))
    ld.text((x0 + leaf_w * 0.5 + swing * 0.5, y0 + 120), "12C" if open_amt < 0.4 else "", font=font(40, FONT_MONO),
            fill=(200, 180, 120, 255), anchor="mm")
    la = np.asarray(leaf, np.float32) / 255.0
    arr = arr * (1 - la[..., 3:4]) + la[..., :3] * la[..., 3:4] * 0.55
    fr.set_bg(arr, fig_light=light)


@lru_cache(None)
def kitchen():
    img = Image.new("RGB", (W, H), (92, 96, 92))
    d = ImageDraw.Draw(img)
    d.polygon([(0, 1460), (W, 1460), (W, H), (0, H)], fill=(110, 108, 100))
    for i in range(8):
        y = 1460 + (i ** 1.8) * 9
        d.line([(0, y), (W, y)], fill=(90, 88, 82), width=3)
    for i in range(7):
        d.line([(i * 180, 1460), (i * 180 - 300 + i * 60, H)], fill=(90, 88, 82), width=3)
    # counter + cabinets on the left
    d.rectangle([0, 1080, 520, 1460], fill=(70, 74, 72), outline=INK, width=6)
    d.rectangle([0, 1060, 540, 1090], fill=(120, 116, 108), outline=INK, width=5)
    d.rectangle([0, 520, 520, 860], fill=(78, 82, 80), outline=INK, width=6)
    # fridge body
    d.rectangle([560, 540, 880, 1470], fill=(150, 154, 156), outline=INK, width=8)
    # open interior (bright)
    d.rectangle([590, 580, 850, 1440], fill=(236, 240, 244), outline=(120, 124, 128), width=6)
    for y in (800, 1010, 1220):
        d.rectangle([590, y, 850, y + 12], fill=(200, 206, 212))
    # the same grocery bag, already inside
    bx, by = 720, 1000
    d.polygon([(bx - 70, by - 150), (bx + 70, by - 150), (bx + 82, by), (bx - 82, by)], fill=(150, 118, 82), outline=INK)
    d.line([(bx - 60, by - 120), (bx + 60, by - 120)], fill=(120, 92, 62), width=6)
    d.ellipse([bx - 30, by - 190, bx + 14, by - 146], fill=(170, 60, 50), outline=INK, width=4)
    d.rectangle([640, 1100, 690, 1210], fill=(230, 230, 220), outline=INK, width=4)  # milk
    # fridge door swung open toward us (left)
    d.polygon([(560, 540), (420, 500), (420, 1530), (560, 1470)], fill=(162, 166, 168), outline=INK)
    d.rectangle([440, 980, 456, 1100], fill=(90, 92, 96))
    light = cone(720, 1000, math.radians(165), 0.75, 1300, 1.25) + spot(720, 1000, 300, 0.8) + \
        cone(720, 1300, math.radians(115), 0.6, 900, 0.5)
    arr = lit(img, light, ambient=0.05, tint=(0.86, 0.94, 1.08))
    arr += noise_tex(21)[..., None] * 0.5
    return arr, light


def phone_screen(t, msg_t=1.3):
    """Phone UI, drawn flat (screen is emissive)."""
    sw, sh = 520, 1000
    img = Image.new("RGB", (sw, sh), (14, 16, 22))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, sw, 150], fill=(26, 28, 36))
    d.text((40, 75), "‹", font=font(60), fill=(120, 170, 255), anchor="lm")
    d.ellipse([sw / 2 - 34, 20, sw / 2 + 34, 88], fill=(90, 96, 110))
    d.text((sw / 2, 54), "L", font=font(36), fill=(240, 240, 240), anchor="mm")
    d.text((sw / 2, 118), "Leo (Me)", font=font(28), fill=(230, 230, 235), anchor="mm")
    d.text((sw / 2, 210), "Today 11:52 PM", font=font(22), fill=(130, 134, 145), anchor="mm")
    if t < msg_t:  # typing dots
        bx, by = 40, 260
        d.rounded_rectangle([bx, by, bx + 130, by + 70], radius=34, fill=(48, 50, 60))
        for i in range(3):
            a = 0.4 + 0.6 * (math.sin(t * 9 - i * 0.9) > 0)
            c = int(120 + 100 * a)
            d.ellipse([bx + 26 + i * 30, by + 26, bx + 44 + i * 30, by + 44], fill=(c, c, c))
    else:
        pop = ease((t - msg_t) / 0.25)
        bx, by = 40, 260
        d.rounded_rectangle([bx, by, bx + int(420 * pop) + 10, by + 100], radius=34, fill=(48, 50, 60))
        if pop > 0.8:
            d.text((bx + 30, by + 50), "don't press 0 again.", font=font(34), fill=(240, 240, 244), anchor="lm")
            d.text((bx + 10, by + 130), "Delivered", font=font(20), fill=(110, 114, 124), anchor="lm")
    d.rectangle([0, sh - 110, sw, sh], fill=(26, 28, 36))
    d.rounded_rectangle([30, sh - 85, sw - 30, sh - 30], radius=28, outline=(70, 72, 84), width=3)
    d.text((60, sh - 57), "iMessage", font=font(24), fill=(90, 94, 104), anchor="lm")
    return img


@lru_cache(None)
def feet_floor():
    img = Image.new("RGB", (W, H), (100, 82, 64))
    d = ImageDraw.Draw(img)
    for i in range(9):
        x = i * 150 - 60
        d.line([(x, 0), (x + 40, H)], fill=(80, 64, 50), width=4)
    for i in range(30):
        y = (i * 131) % H
        x = (i * 150 - 60) + 75
        d.line([(x - 70, y), (x + 70, y + 4)], fill=(82, 66, 52), width=3)
    light = cone(-200, 900, math.radians(8), 0.75, 2600, 1.7)
    arr = lit(img, light, ambient=0.06, tint=(1.1, 0.96, 0.8))
    arr += noise_tex(31)[..., None] * 0.6
    return arr, light


# ---------------------------------------------------------------- CCTV post
def cctv_post(t_clock):
    def post(img):
        lum = img @ np.array([0.3, 0.59, 0.11], np.float32)
        lum = np.clip((lum - 0.03) * 1.35, 0, 1)
        # fisheye-ish vignette + scanlines
        r2 = ((_XX - W / 2) / (W * 0.55)) ** 2 + ((_YY - H / 2) / (H * 0.5)) ** 2
        lum *= np.clip(1.15 - r2 * 0.75, 0, 1)
        lum *= (1 - 0.12 * ((_YY.astype(np.int32) // 3) % 2))
        out = np.stack([lum * 0.82, lum * 0.98, lum * 0.86], -1)
        return out
    return post


def cctv_hud(t_sec):
    def draw(img):
        d = ImageDraw.Draw(img)
        secs = 7 + int(t_sec)
        d.text((60, 110), f"FRONT DOOR   11:42:{secs:02d} PM", font=font(38, FONT_MONO), fill=(235, 240, 235), anchor="lm",
               stroke_width=3, stroke_fill=(0, 0, 0))
        if int(t_sec * 2) % 2 == 0:
            d.ellipse([60, 160, 92, 192], fill=(230, 40, 40))
        d.text((108, 176), "REC", font=font(34, FONT_MONO), fill=(235, 240, 235), anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0))
        d.text((W - 60, 110), "▶ 1x", font=font(34, FONT_MONO), fill=(235, 240, 235), anchor="rm", stroke_width=3, stroke_fill=(0, 0, 0))
        d.rectangle([60, 230, W - 60, 240], fill=(70, 74, 70))
        d.rectangle([60, 230, 60 + (W - 120) * min(1, t_sec / 6), 240], fill=(230, 60, 50))
    return draw


# ---------------------------------------------------------------- shots
def s1_door(fr, t):
    op = ease(t / 1.2)
    entry_frame(fr, op)
    if op > 0.2:
        x = 540
        ly = lerp(1460, 1640, ease((t - 0.6) / 2.0))
        fr.cast_shadow(x, ly, 540, 1000, 900, strength=230, width=60)
        stickman(fr, x, ly, lerp(1.7, 2.0, ease((t - 0.6) / 2.0)), facing=0, walk=t * 6 if t < 2.6 else 0,
                 bags=True, arms=[(0.15, 0.1), (0.1, 0.15)])
    fr.zoom = lerp(1.0, 1.06, t / 3)


def s2_fridge(fr, t):
    arr, light = kitchen()
    fr.set_bg(arr, fig_light=light)
    fr.add_glow(720, 1000, 260, (230, 240, 255), 0.35)
    lx, ly = 330, 1660
    fr.cast_shadow(lx, ly, 720, 1520, 520, strength=235, width=58)
    stickman(fr, lx, ly, 2.05, facing=1, bags=True, arms=[(0.35, 0.3), (0.08, 0.12)])
    fr.zoom = lerp(1.0, 1.16, ease((t - 1.5) / 3.2))
    fr.zoom_center = (640, 1080)


def s3_text(fr, t):
    bg = np.zeros((H, W, 3), np.float32) + np.array([0.05, 0.05, 0.07], np.float32)
    # phone: emissive screen inside a dark body, held by Leo's hand
    px, py = 280, 230
    scr = phone_screen(t)
    body = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    bd.rounded_rectangle([px - 22, py - 22, px + 520 + 22, py + 1000 + 22], radius=56, fill=(30, 32, 38, 255),
                         outline=(10, 10, 12, 255), width=6)
    ba = np.asarray(body, np.float32) / 255.0
    bg = bg * (1 - ba[..., 3:4]) + ba[..., :3] * ba[..., 3:4]
    bg[py:py + 1000, px:px + 520] = np.clip(to_arr(scr) * 1.7 + 0.04, 0, 1.3)
    # thumb + sleeve
    hand = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hand)
    hd.line([(900, 1900), (780, 1250)], fill=(10, 10, 12, 255), width=150)
    hd.line([(900, 1900), (780, 1250)], fill=(112, 116, 122, 255), width=130)
    hd.ellipse([700, 1130, 860, 1290], fill=(238, 238, 234, 255), outline=(22, 22, 26, 255), width=12)
    ha = np.asarray(hand, np.float32) / 255.0
    light = spot(540, 700, 700, 0.8)
    bg = bg * (1 - ha[..., 3:4]) + ha[..., :3] * ha[..., 3:4] * (0.35 + light[..., None] * 0.6)
    fr.set_bg(bg)
    fr.add_glow(540, 720, 620, (120, 160, 230), 0.35)
    if 1.3 < t < 1.7:  # buzz
        fr.shake = (random.Random(int(t * 40)).uniform(-6, 6), 0)
    fr.zoom = lerp(1.0, 1.1, ease((t - 1.3) / 2.5))
    fr.zoom_center = (540, 560)


def s4_cctv(fr, t):
    arr, light = hallway("twelve")
    fr.set_bg(arr, fig_light=light)
    # a potted plant by the wall casts its shadow — the walking "Leo" does not
    fr.poly_shadow([(790, 1640), (930, 1640), (1080, 1780), (960, 1820)], 250)
    walk = ease(t / 5.5)
    x = lerp(560, 600, walk)
    y = lerp(1060, 1640, walk)
    stickman(fr, x, y, lerp(0.75, 2.0, walk), facing=0, walk=t * 7, bags=True, arms=[(0.15, 0.1), (0.1, 0.15)])
    plant = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(plant)
    pd.polygon([(790, 1640), (930, 1640), (905, 1500), (815, 1500)], fill=(150, 120, 100, 255), outline=(20, 20, 20, 255), width=6)
    for a in (-0.7, -0.35, 0.0, 0.35, 0.7):
        pd.line([(860, 1500), (860 + math.sin(a) * 170, 1500 - math.cos(a) * 230)], fill=(110, 150, 110, 255), width=22)
    fr.fig.alpha_composite(plant)
    fr.post = cctv_post(t)
    fr.overlay.append(cctv_hud(t))
    fr.zoom = 1.04


def s5_feet(fr, t):
    arr, light = feet_floor()
    fr.set_bg(arr, fig_light=light)
    # looking down at his own feet: huge legs entering from the top
    fx, fy = 430, 1420
    fr.cast_shadow(fx, fy, -600, 1300, 1100, strength=250, width=170)
    stickman(fr, fx, fy, 5.6, facing=0, arms=[(0.1, 0.1), (0.1, 0.1)])
    fr.zoom = lerp(1.05, 1.0, ease(t / 4))


def s6_hale(fr, t):
    knock_end = 0.9
    op = ease((t - 1.0) / 0.9)
    shake = 0
    if t < knock_end:
        shake = 4 * math.sin(t * 60) * (int(t * 3.3) % 1 == 0)
    entry_frame(fr, op, extra_light=0.8)
    if op > 0.3:
        fr.cast_shadow(560, 1470, 560, 1000, 360, strength=210, width=50)
        stickman(fr, 560, 1470, 1.7, facing=0, style=HALE, arms=[(0.25, 0.15), (0.1, 0.2)])
    # Leo from behind, foreground left
    fr.cast_shadow(250, 1880, 540, 1000, 600, strength=230, width=70)
    stickman(fr, 250, 1880, 2.7, facing=2, arms=[(0.1, 0.1), (0.1, 0.1)])
    fr.shake = (shake, 0)
    fr.zoom = lerp(1.0, 1.1, ease((t - 1.5) / 4.0))
    fr.zoom_center = (540, 1000)
    if t > 5.4:
        a = ease((t - 5.4) / 0.4)
        fr.exposure = 1 - 0.75 * a
        fr.overlay.append(title_overlay("PART 3", 900, 130, (230, 40, 36), a))


SCENES = [(0, 3, s1_door), (3, 8, s2_fridge), (8, 13, s3_text), (13, 19, s4_cctv),
          (19, 24, s5_feet), (24, 30, s6_hale)]

LINES = [
    ("Something followed me up.", 0.3),
    ("My groceries… were already in my fridge.", 3.4),
    ("A text. From my own number.", 8.4),
    ("The camera shows me coming home. Ten minutes ago.", 13.4),
    ("That wasn't me.", 19.6),
    ("Leo, dear… you already came by tonight. Twice.", 25.3),
]


def load_caps():
    try:
        caps, cur = [], []
        for ln in open("words2.txt"):
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
    from hengine import words_for
    return [words_for(s, t0, t0 + 0.36 * len(s.split()) + 0.4) for s, t0 in LINES]


if __name__ == "__main__":
    caps = load_caps()
    if sys.argv[1] == "--still":
        render_frame(float(sys.argv[2]), SCENES, caps).save(sys.argv[3])
    else:
        run_video(SCENES, caps, sys.argv[1], DUR)
