"""Shared drawing helpers + frame loop for the series (Part 1 lives in render.py)."""
import math
import subprocess
from multiprocessing import Pool

from PIL import Image, ImageDraw

from render import (BLACK, FONT_BOLD, FONT_MONO, FPS, GREY, H, PINK, RED, SS, W, WHITE,  # noqa: F401
                    S, SW, caption, circle, city, clamp, ease, figure, font, ground_line, heart,
                    lerp, line, road, text, timer, truck, fmt)

GREEN = (30, 150, 70)
GHOST = (150, 185, 235)
DARK = (14, 14, 20)


def mix(c1, c2, t):
    t = clamp(t)
    return tuple(int(lerp(a, b, t)) for a, b in zip(c1, c2))


def bg(d, c):
    d.rectangle([0, 0, S(W), S(H)], fill=c)


def years(y):
    return f"{max(0, int(round(y)))} YEARS"


def hooded(d, x, ground, scale=1.2, facing=-1, arms=None, walk=0.0):
    """The man with no timer: black hood, white eyes."""
    figure(d, x, ground, scale, walk=walk, facing=facing, arms=arms)
    k = scale
    hx, hy = x, ground - 234 * k
    pts = [(hx - 40 * k, hy + 34 * k), (hx - 38 * k, hy - 20 * k), (hx - 8 * k * facing, hy - 52 * k),
           (hx + 34 * k, hy - 22 * k), (hx + 40 * k, hy + 34 * k)]
    d.polygon([(S(px), S(py)) for px, py in pts], fill=BLACK)
    # cloak
    d.polygon([(S(x - 14 * k), S(ground - 200 * k)), (S(x + 14 * k), S(ground - 200 * k)),
               (S(x + 55 * k), S(ground - 70 * k)), (S(x - 55 * k), S(ground - 70 * k))], fill=BLACK)
    for ex in (-12, 12):
        circle(d, hx + (ex + 8 * facing) * k, hy, 5 * k, 2, WHITE, fill=WHITE)


def no_timer(d, x, y, size=32):
    timer(d, x, y, "--:--:--", size, c=(150, 150, 150))


def rain(d, t, dark=True, n=70):
    c = (110, 120, 140) if dark else (170, 180, 200)
    for i in range(n):
        x = (i * 157.3) % W
        y = ((i * 97.1) + t * 1400) % (H + 200) - 100
        d.line([S(x), S(y), S(x - 10), S(y + 46)], fill=c, width=SW(3))


def bench(d, cx, ground, c=BLACK):
    d.rectangle([S(cx - 210), S(ground - 110), S(cx + 210), S(ground - 90)], fill=c)
    line(d, (cx - 180, ground - 90), (cx - 180, ground), 8, c)
    line(d, (cx + 180, ground - 90), (cx + 180, ground), 8, c)


def bubble(d, x, y, s, size=40, w=560):
    f = font(FONT_BOLD, size)
    words, lines_, cur = s.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=f) > S(w):
            lines_.append(cur)
            cur = wd
        else:
            cur = trial
    lines_.append(cur)
    hgt = len(lines_) * size * 1.25 + 40
    d.rounded_rectangle([S(x - w / 2 - 30), S(y - hgt / 2), S(x + w / 2 + 30), S(y + hgt / 2)],
                        radius=SW(26), fill=WHITE, outline=BLACK, width=SW(6))
    for i, ln in enumerate(lines_):
        text(d, (x, y - hgt / 2 + 20 + size * 0.62 + i * size * 1.25), ln, size)


def floater(d, x, y, s, t, c=RED, size=40):
    """Text that drifts up and fades over 1s (t in seconds since spawn)."""
    if 0 <= t < 1:
        text(d, (x, y - t * 90), s, size, c=mix(c, WHITE, t))


def run_video(scenes, captions, out, duration=60.0):
    n = int(duration * FPS)
    global _SCENES, _CAPS
    _SCENES, _CAPS = scenes, captions
    ff = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool() as pool:
        for frame in pool.imap(_render, range(n), chunksize=8):
            ff.stdin.write(frame)
    ff.stdin.close()
    ff.wait()


_SCENES, _CAPS = [], []


def _render(i):
    return render_frame(i / FPS, _SCENES, _CAPS)


def render_frame(t, scenes, caps):
    img = Image.new("RGB", (W * SS, H * SS), WHITE)
    d = ImageDraw.Draw(img)
    for a, b, fn in scenes:
        if a <= t < b or (b == scenes[-1][1] and t >= a):
            fn(d, t - a)
            break
    for a, b, s in caps:
        if a <= t < b:
            caption(d, s, t - a)
            break
    return img.resize((W, H), Image.LANCZOS).tobytes()


def captions_from(seg_file, lines_):
    rows = [tuple(map(float, ln.split())) for ln in open(seg_file) if ln.strip() and not ln.startswith("#")]
    return [(at, at + (b - a) + 0.35, s) for (a, b, at), s in zip(rows, lines_)]


def still(t, scenes, caps, path):
    Image.frombytes("RGB", (W, H), render_frame(t, scenes, caps)).save(path)
