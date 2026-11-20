"""Render "I Can See When People Die" — 60s vertical stick-figure short.

Usage: python3 render.py out_video.mp4
Frames are drawn with PIL (2x supersampled) and piped to ffmpeg.
"""
import math
import subprocess
import sys
from multiprocessing import Pool

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
SS = 2  # supersample factor
FPS = 30
DUR = 60.0
N = int(DUR * FPS)

BLACK = (15, 15, 18)
WHITE = (250, 250, 248)
GREY = (200, 200, 200)
RED = (225, 30, 40)
PINK = (240, 80, 120)

FONT_BOLD = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
_fonts = {}


def font(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size * SS)
    return _fonts[key]


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(t, lo=0.0, hi=1.0):
    return max(lo, min(hi, t))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def S(v):
    return v * SS


def SW(v):
    return max(1, int(round(v * SS)))


# ---------------------------------------------------------------- primitives
def line(d, p1, p2, w=10, c=BLACK):
    d.line([S(p1[0]), S(p1[1]), S(p2[0]), S(p2[1])], fill=c, width=SW(w))
    r = S(w) / 2
    for p in (p1, p2):
        d.ellipse([S(p[0]) - r, S(p[1]) - r, S(p[0]) + r, S(p[1]) + r], fill=c)


def circle(d, cx, cy, r, w=10, c=BLACK, fill=None):
    d.ellipse([S(cx - r), S(cy - r), S(cx + r), S(cy + r)], outline=c, width=SW(w), fill=fill)


def text(d, xy, s, size, c=BLACK, path=FONT_BOLD, anchor="mm", stroke=0, stroke_c=WHITE):
    d.text((S(xy[0]), S(xy[1])), s, font=font(path, size), fill=c, anchor=anchor,
           stroke_width=SW(stroke), stroke_fill=stroke_c)


def heart(d, cx, cy, s, c=PINK):
    pts = []
    for i in range(40):
        t = i / 40 * 2 * math.pi
        x = 16 * math.sin(t) ** 3
        y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        pts.append((S(cx + x * s / 16), S(cy + y * s / 16)))
    d.polygon(pts, fill=c)


def figure(d, x, ground, scale=1.0, walk=0.0, facing=1, arms=None, girl=False,
           lean=0.0, c=BLACK, lying=False, run=False):
    """Stick figure standing on `ground` at x. walk = phase in radians."""
    k = scale
    w = 9 * k
    if lying:
        y = ground - 14 * k
        hx = x - 85 * k
        circle(d, hx, y - 6 * k, 26 * k, w, c)
        line(d, (hx + 26 * k, y), (x + 30 * k, y), w, c)
        line(d, (x + 30 * k, y), (x + 95 * k, y + 8 * k), w, c)
        line(d, (x + 30 * k, y), (x + 92 * k, y - 18 * k), w, c)
        line(d, (x - 30 * k, y), (x - 5 * k, y + 12 * k), w, c)
        line(d, (x - 30 * k, y), (x - 10 * k, y - 26 * k), w, c)
        return
    amp = 0.75 if run else 0.45
    hip = (x + lean * 30 * k, ground - 95 * k)
    neck = (x + lean * 75 * k, ground - 200 * k)
    head = (neck[0] + lean * 10 * k, neck[1] - 34 * k)
    # legs
    for ph in (0, math.pi):
        a = math.sin(walk + ph) * amp
        knee = (hip[0] + math.sin(a) * 50 * k * facing, hip[1] + math.cos(a) * 50 * k)
        foot_a = a - (abs(math.sin(walk + ph)) * 0.5 if run else 0.1)
        foot = (knee[0] + math.sin(foot_a) * 48 * k * facing, knee[1] + math.cos(foot_a) * 48 * k)
        line(d, hip, knee, w, c)
        line(d, knee, foot, w, c)
    line(d, hip, neck, w, c)
    # arms
    sh = (lerp(hip[0], neck[0], 0.82), lerp(hip[1], neck[1], 0.82))
    if arms is None:
        sw = math.sin(walk) * amp
        arms = [(sw, 0.3), (-sw, 0.3)]
    for (a_up, a_low) in arms:
        elbow = (sh[0] + math.sin(a_up) * 45 * k * facing, sh[1] + math.cos(a_up) * 45 * k)
        a2 = a_up + a_low
        hand = (elbow[0] + math.sin(a2) * 42 * k * facing, elbow[1] + math.cos(a2) * 42 * k)
        line(d, sh, elbow, w, c)
        line(d, elbow, hand, w, c)
    circle(d, head[0], head[1], 30 * k, w, c, fill=WHITE if c == BLACK else None)
    if girl:
        # ponytail + bow
        bx = head[0] - 30 * k * facing
        line(d, (bx, head[1] - 8 * k), (bx - 28 * k * facing, head[1] + 22 * k), w, c)
        heart(d, head[0] - 18 * k * facing, head[1] - 30 * k, 14 * k, RED)


def timer(d, x, y, label, size=40, c=RED, flash=False, bg=True):
    if flash:
        return
    f = font(FONT_MONO, size)
    bbox = d.textbbox((S(x), S(y)), label, font=f, anchor="mm")
    if bg:
        pad = S(10)
        d.rounded_rectangle([bbox[0] - pad, bbox[1] - pad, bbox[2] + pad, bbox[3] + pad],
                            radius=S(10), fill=(255, 255, 255), outline=c, width=SW(4))
    d.text((S(x), S(y)), label, font=f, fill=c, anchor="mm")


def fmt(sec):
    sec = max(0, int(math.ceil(sec)))
    return f"00:{sec // 60:02d}:{sec % 60:02d}"


def ground_line(d, y, c=BLACK):
    d.line([0, S(y), S(W), S(y)], fill=c, width=SW(6))


def city(d, y, c=GREY, seed=0):
    xs = [0, 140, 260, 420, 560, 700, 860, 1000, 1080]
    hs = [380, 520, 300, 600, 420, 480, 340, 560]
    for i in range(len(xs) - 1):
        h = hs[(i + seed) % len(hs)]
        d.rectangle([S(xs[i] + 6), S(y - h), S(xs[i + 1] - 6), S(y)], outline=c, width=SW(5))
        for wy in range(int(y - h + 40), int(y - 40), 80):
            for wx in range(xs[i] + 30, xs[i + 1] - 50, 60):
                d.rectangle([S(wx), S(wy), S(wx + 26), S(wy + 34)], outline=c, width=SW(3))


def road(d, top, bottom):
    d.line([0, S(top), S(W), S(top)], fill=BLACK, width=SW(6))
    d.line([0, S(bottom), S(W), S(bottom)], fill=BLACK, width=SW(6))
    mid = (top + bottom) / 2
    for x in range(0, W, 120):
        d.line([S(x + 20), S(mid), S(x + 80), S(mid)], fill=GREY, width=SW(8))


def truck(d, x, ground, scale=1.0):
    k = scale
    # body faces left (driving leftwards)
    d.rectangle([S(x), S(ground - 260 * k), S(x + 150 * k), S(ground - 50 * k)],
                fill=WHITE, outline=BLACK, width=SW(8))
    d.rectangle([S(x + 150 * k), S(ground - 330 * k), S(x + 520 * k), S(ground - 50 * k)],
                fill=WHITE, outline=BLACK, width=SW(8))
    d.rectangle([S(x + 25 * k), S(ground - 230 * k), S(x + 110 * k), S(ground - 160 * k)],
                outline=BLACK, width=SW(6))
    for wx in (x + 80 * k, x + 400 * k):
        circle(d, wx, ground - 40 * k, 40 * k, 9, BLACK, fill=WHITE)
    # headlight beam
    d.polygon([(S(x), S(ground - 110 * k)), (S(x - 160 * k), S(ground - 160 * k)),
               (S(x - 160 * k), S(ground - 50 * k))], fill=(255, 235, 140))


def caption(d, s, t_in):
    """Bottom-third subtitle with pop-in."""
    if not s:
        return
    pop = ease(t_in / 0.18)
    size = int(lerp(44, 54, pop))
    words = s.split()
    lines_, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if len(trial) > 22:
            lines_.append(cur)
            cur = wd
        else:
            cur = trial
    lines_.append(cur)
    y0 = 1500 - (len(lines_) - 1) * 38
    for i, ln in enumerate(lines_):
        text(d, (W / 2, y0 + i * 76), ln.upper(), size, c=(255, 255, 255), stroke=4, stroke_c=BLACK)


# --------------------------------------------------------------- the script
# (start, end, caption) — times are replaced by real VO timings if vo_times.txt exists
CAPS = [
    (0.3, 2.9, "I can see exactly when people will die."),
    (3.2, 9.6, "Ever since I was born… everyone has a countdown."),
    (10.4, 17.5, "So I stay away from the ones running low."),
    (18.5, 27.5, "Then I met her. Sixty years. Finally… someone I didn't have to lose."),
    (28.5, 34.5, "For once… I wasn't afraid."),
    (35.5, 41.5, "Until one morning… her timer changed."),
    (42.2, 49.5, "Ten seconds. I didn't think. I just ran."),
    (50.2, 55.0, "She was safe. And for the first time… I saw my own timer."),
    (55.4, 59.8, "I could see everyone's death… except my own."),
]


def load_caps():
    try:
        with open(__file__.replace("render.py", "vo_times.txt")) as f:
            rows = [tuple(map(float, ln.split())) for ln in f if ln.strip()]
        if len(rows) == len(CAPS):
            return [(a, b, c[2]) for (a, b), c in zip(rows, CAPS)]
    except FileNotFoundError:
        pass
    return CAPS


CAPTIONS = load_caps()


# ------------------------------------------------------------------- scenes
def sc_cold_open(d, t):  # 0–3
    ground = 1180
    city(d, ground, seed=2)
    ground_line(d, ground)
    left = 3.0 - t * (3.0 / 2.6)
    if t < 2.6:
        x = 160 + t * 160
        figure(d, x, ground, 1.3, walk=t * 9, facing=1)
        timer(d, x + 40, ground - 330, fmt(left), 46)
    else:
        x = 160 + 2.6 * 160
        figure(d, x, ground, 1.3, lying=True)
        timer(d, x, ground - 140, "00:00:00", 46, flash=(int(t * 8) % 2 == 0))
    # hook title
    text(d, (W / 2, 260), "HIS TIMER SAYS", 70, c=BLACK)
    text(d, (W / 2, 350), "3 SECONDS…", 92, c=RED)


def sc_street(d, t):  # 3–10
    ground = 1180
    city(d, ground, seed=0)
    ground_line(d, ground)
    walkers = [(-150, 1, 140, 1.05, 3 * 3600 * 24 * 365 + 50000),
               (1200, -1, 120, 0.95, 41 * 365 * 86400),
               (300, 1, 90, 1.1, 77 * 3600),
               (900, -1, 160, 1.0, 12 * 365 * 86400),
               (550, 1, 60, 0.9, 5 * 86400)]
    for i, (x0, dirn, speed, sc, life) in enumerate(walkers):
        x = (x0 + dirn * speed * t) % 1400 - 160
        figure(d, x, ground, sc, walk=t * 8 + i, facing=dirn)
        yrs = life / (365 * 86400)
        lab = f"{int(yrs)} YEARS" if yrs >= 1 else (f"{int(life // 86400)} DAYS" if life >= 86400 else f"{int(life // 3600)} HOURS")
        timer(d, x + 30 * dirn * sc, ground - 300 * sc, lab, 30)
    text(d, (W / 2, 300), "EVERYONE HAS", 64)
    text(d, (W / 2, 385), "A COUNTDOWN", 80, c=RED)


def sc_avoid(d, t):  # 10–18
    top, bot = 860, 1130
    road(d, top, bot)
    # protagonist walks right on lower sidewalk, then crosses up
    cross = ease((t - 3.2) / 2.0)
    px = 140 + min(t, 3.2) * 70 + max(0, t - 5.2) * 60
    py = lerp(bot + 190, top, cross)
    figure(d, px, py, 1.15, walk=t * 8, facing=1, run=0 < cross < 1)
    timer(d, px + 30, py - 330, "YOU", 30, c=BLACK)
    if 2.3 < t < 3.6:
        text(d, (px + 20, py - 410), "!", 110, c=RED)
    # danger man walks left on lower sidewalk
    mx = 1150 - t * 90
    figure(d, mx, bot + 190, 1.15, walk=t * 8 + 1, facing=-1)
    timer(d, mx - 30, bot + 190 - 330, fmt(130 - t), 38)
    text(d, (W / 2, 300), "STAY AWAY FROM", 64)
    text(d, (W / 2, 385), "THE LOW ONES", 80, c=RED)


def sc_meet(d, t):  # 18–28
    ground = 1220
    city(d, ground, seed=4)
    ground_line(d, ground)
    meet = ease(t / 2.4)
    px = lerp(-120, 420, meet)
    gx = lerp(1200, 660, meet)
    walking = meet < 1
    figure(d, px, ground, 1.25, walk=t * 8 if walking else 0, facing=1,
           arms=None if walking else [(0.6, 0.5), (0.2, 0.2)])
    figure(d, gx, ground, 1.25, walk=t * 8 + 2 if walking else 0, facing=-1, girl=True,
           arms=None if walking else [(0.6, 0.5), (0.2, 0.2)])
    if t > 2.4 and t < 3.0:
        text(d, (540, ground - 330), "BUMP!", 70, c=BLACK)
    if t > 3.2:
        pulse = 1 + 0.08 * math.sin(t * 6)
        timer(d, gx - 20, ground - 380, "60 YEARS", int(48 * pulse), c=(30, 150, 70))
    if t > 4.5:
        for i in range(7):
            ht = (t - 4.5 - i * 0.6) % 4.2
            hx = 540 + math.sin(i * 2.1 + ht * 2) * 200
            hy = ground - 300 - ht * 170
            if 0 < ht < 4.0:
                heart(d, hx, hy, 26 + i % 3 * 8)
    text(d, (W / 2, 300), "THEN I MET HER", 72)


def sc_montage(d, t):  # 28–35, three vignettes
    ground = 1220
    ground_line(d, ground)
    seg = int(t / 2.34)
    lt = t - seg * 2.34
    if seg == 0:  # bench + sun
        circle(d, 860, 420, 90, 8, (240, 170, 30), fill=(255, 220, 100))
        d.rectangle([S(330), S(ground - 110), S(750), S(ground - 90)], fill=BLACK)
        line(d, (360, ground - 90), (360, ground), 8)
        line(d, (720, ground - 90), (720, ground), 8)
        figure(d, 460, ground - 60, 1.15, arms=[(1.6, 0.2), (0.4, 0.2)])
        figure(d, 620, ground - 60, 1.15, facing=-1, girl=True, arms=[(1.6, 0.2), (0.4, 0.2)])
        heart(d, 540, ground - 420 - lt * 40, 34)
    elif seg == 1:  # laughing
        bounce = abs(math.sin(lt * 10)) * 20
        figure(d, 420, ground - bounce, 1.25, arms=[(2.6, 0.3), (-2.6, -0.3)])
        figure(d, 660, ground - (20 - bounce), 1.25, facing=-1, girl=True, arms=[(2.6, 0.3), (-2.6, -0.3)])
        text(d, (330, ground - 470), "HA", 70)
        text(d, (760, ground - 500), "HA HA", 70)
    else:  # night walk, holding hands
        circle(d, 220, 420, 70, 8, BLACK, fill=(235, 235, 210))
        for sx, sy in [(600, 300), (800, 460), (950, 260), (420, 560)]:
            text(d, (sx, sy), "✦", 40, path=FONT_MONO)
        x = 340 + lt * 90
        figure(d, x, ground, 1.2, walk=lt * 7, arms=[(0.4, 0.2), (-0.9, 0.3)])
        figure(d, x + 150, ground, 1.2, walk=lt * 7 + 1, girl=True, arms=[(-0.4, 0.2), (0.9, 0.3)])
    text(d, (W / 2, 300), "FOR ONCE…", 72)


def sc_change(d, t):  # 35–42
    ground = 1250
    # window with morning sun
    d.rectangle([S(120), S(380), S(470), S(760)], outline=BLACK, width=SW(8))
    line(d, (295, 380), (295, 760), 6)
    line(d, (120, 570), (470, 570), 6)
    circle(d, 380, 470, 50, 6, (240, 170, 30), fill=(255, 220, 100))
    ground_line(d, ground)
    zoom = ease((t - 2.5) / 1.2)
    figure(d, 330, ground, 1.25, arms=[(0.3, 0.3), (0.5, 0.2)])
    gx = 720
    figure(d, gx, ground, 1.25, facing=-1, girl=True)
    if t < 2.4:
        timer(d, gx - 20, ground - 380, "60 YEARS", 48, c=(30, 150, 70))
    elif t < 3.0:  # glitch
        g = ["60 YE@RS", "0#:00:1?", "6 0 Y R S", "00:0?:10"][int(t * 20) % 4]
        timer(d, gx - 20 + (int(t * 50) % 3 - 1) * 12, ground - 380, g, 48)
    else:
        size = int(lerp(48, 120, zoom))
        y = lerp(ground - 380, 820, zoom)
        timer(d, lerp(gx - 20, W / 2, zoom), y, "00:00:10", size)
    if t > 3.0:
        text(d, (330, ground - 420), "!", 110, c=RED)
    text(d, (W / 2, 260), "UNTIL ONE MORNING…", 64)


def sc_rescue(d, t):  # 42–50
    top, bot = 980, 1360
    road(d, top, bot)
    lane = 1250
    left = 8.0 - t  # her countdown
    push_t = 6.6
    # girl standing mid road
    if t < push_t:
        gx, gy = 600, lane
        figure(d, gx, gy, 1.15, facing=-1, girl=True)
    else:
        f = ease((t - push_t) / 0.5)
        gx, gy = lerp(600, 380, f), lerp(lane, top - 10, f)
        figure(d, gx, gy, 1.15, facing=-1, girl=True, lean=-0.4 * (1 - f))
    lab = fmt(left) if t < push_t + 0.3 else "60 YEARS"
    col = RED if t < push_t + 0.3 else (30, 150, 70)
    timer(d, gx - 20, gy - 360, lab, 42, c=col)
    # protagonist runs from left
    if t < push_t:
        run = ease((t - 1.0) / (push_t - 1.0))
        px = lerp(-100, 520, run)
        figure(d, px, lane, 1.15, walk=t * 14, facing=1, run=run > 0, lean=0.35 if run > 0 else 0,
               arms=[(1.4, 0.0), (1.2, 0.1)] if t > push_t - 0.4 else None)
    elif t < push_t + 0.5:
        figure(d, 520, lane, 1.15, facing=1, lean=0.45, arms=[(1.5, 0.0), (1.4, 0.0)])
    # truck from the right
    tx = lerp(1250, 420, ease((t - 2.0) / (push_t + 0.4 - 2.0))) if t < push_t + 0.4 else lerp(420, -700, (t - push_t - 0.4) / 0.6)
    truck(d, tx, lane + 60, 1.0)
    if 1.0 < t < push_t:
        text(d, (W / 2, 300), "10 SECONDS", 86, c=RED)
    if t > push_t + 0.4 and t < push_t + 1.0:
        a = 1 - (t - push_t - 0.4) / 0.6
        d.rectangle([0, 0, S(W), S(H)], fill=(255, 255, 255))
    if t > push_t + 1.0:
        d.rectangle([0, 0, S(W), S(H)], fill=BLACK)


def sc_after(d, t):  # 50–55
    ground = 1220
    ground_line(d, ground, c=(90, 90, 90))
    figure(d, 260, ground, 1.1, facing=1, girl=True, arms=[(2.4, 0.5), (2.4, 0.5)])
    timer(d, 240, ground - 340, "60 YEARS", 34, c=(30, 150, 70))
    px = 680
    figure(d, px, ground, 1.25, lying=True)
    if t > 1.6:
        timer(d, px, ground - 160, "00:00:00", int(lerp(40, 64, ease((t - 1.6) / 1.0))),
              flash=(t > 2.6 and int(t * 5) % 2 == 0))
    text(d, (W / 2, 300), "MY OWN TIMER", 76, c=RED)


def sc_end(d, t, img):  # 55–60
    fade = ease(t / 1.2)
    v = int(lerp(250, 8, fade))
    d.rectangle([0, 0, S(W), S(H)], fill=(v, v, v))
    if t > 1.2:
        text(d, (W / 2, 820), "EVERYONE'S DEATH…", 64, c=(240, 240, 240))
    if t > 2.4:
        text(d, (W / 2, 920), "EXCEPT MY OWN", 80, c=RED)
    if t > 3.6:
        timer(d, W / 2, 1120, "00:00:03", 52, flash=int(t * 4) % 2 == 0, bg=False)


SCENES = [(0, 3, sc_cold_open), (3, 10, sc_street), (10, 18, sc_avoid), (18, 28, sc_meet),
          (28, 35, sc_montage), (35, 42, sc_change), (42, 50, sc_rescue), (50, 55, sc_after),
          (55, 60, sc_end)]


def render(i):
    t = i / FPS
    img = Image.new("RGB", (W * SS, H * SS), WHITE)
    d = ImageDraw.Draw(img)
    for a, b, fn in SCENES:
        if a <= t < b or (b == 60 and t >= a):
            if fn is sc_end:
                fn(d, t - a, img)
            else:
                fn(d, t - a)
            break
    # vignette-ish frame shake on the truck hit
    for a, b, s in CAPTIONS:
        if a <= t < b:
            caption(d, s, t - a)
            break
    return img.resize((W, H), Image.LANCZOS).tobytes()


def main(out):
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool() as pool:
        for frame in pool.imap(render, range(N), chunksize=8):
            ff.stdin.write(frame)
    ff.stdin.close()
    ff.wait()


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--still":
        t = float(sys.argv[2])
        Image.frombytes("RGB", (W, H), render(int(t * FPS))).save(sys.argv[3])
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else "video_silent.mp4")
