"""Cinematic stickman horror engine: lit environments, hard cast shadows, film grain, grading,
word-highlight captions. 1080x1920 @ 30fps.

A scene function gets a Frame and the scene-local time t. It sets a lit background (cached),
adds shadows, figures and glows; Frame.finish() composites + grades.
"""
import math
import subprocess
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FPS = 30
SS = 2  # figure supersampling

FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
_fonts = {}

INK = (22, 22, 26)
HOODIE = (112, 116, 122)
HOODIE_DK = (82, 86, 92)
JEANS = (40, 48, 64)
SKIN = (238, 238, 234)


def font(size, path=FONT):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]


def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))


def ease(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


# ---------------------------------------------------------------- lighting helpers
_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float32)


def spot(x, y, r, power=1.0, squash=1.0):
    """Hard-ish light falloff map (0..1) centered at x,y."""
    d2 = ((_XX - x) ** 2 + ((_YY - y) * squash) ** 2) / (r * r)
    return (power / (1.0 + d2 * 2.2)).astype(np.float32)


def cone(x, y, angle, spread, length, power=1.0):
    """Directional cone of light from (x,y) pointing at angle (radians)."""
    dx, dy = _XX - x, _YY - y
    dist = np.sqrt(dx * dx + dy * dy) + 1e-3
    ang = np.arctan2(dy, dx) - angle
    ang = (ang + np.pi) % (2 * np.pi) - np.pi
    edge = np.clip(1 - np.abs(ang) / spread, 0, 1) ** 0.6
    fall = np.clip(1 - dist / length, 0, 1) ** 1.4
    return (edge * fall * power).astype(np.float32)


def to_arr(img):
    return np.asarray(img, dtype=np.float32) / 255.0


def lit(flat_img, light, ambient=0.12, tint=(1.0, 1.0, 1.0)):
    """Multiply a flat-colored environment by a light map."""
    a = to_arr(flat_img)
    L = np.clip(ambient + light, 0, 1.6)[..., None] * np.array(tint, dtype=np.float32)
    return a * L


def noise_tex(seed, scale=1.0, streak=False):
    rng = np.random.default_rng(seed)
    if streak:  # brushed steel: vertical streaks
        col = rng.normal(0, 1, (1, W)).astype(np.float32)
        col = np.convolve(col[0], np.ones(5) / 5, mode="same")[None, :]
        n = np.repeat(col, H, axis=0) + rng.normal(0, 0.35, (H, W)).astype(np.float32)
        return n * 0.035 * scale
    n = rng.normal(0, 1, (H // 4, W // 4)).astype(np.float32)
    img = Image.fromarray(((n * 40) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return (to_arr(img) - 0.5) * 0.12 * scale


# ---------------------------------------------------------------- frame
GRAIN = None


def _grain_pool():
    global GRAIN
    if GRAIN is None:
        rng = np.random.default_rng(11)
        GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
    return GRAIN


class Frame:
    def __init__(self, t_global):
        self.tg = t_global
        self.base = None
        self.shadow = Image.new("L", (W, H), 0)
        self.sd = ImageDraw.Draw(self.shadow)
        self.fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        self.glow = np.zeros((H, W, 3), np.float32)
        self.fig_light = None  # optional light map for figure shading
        self.overlay = []  # callables(img) after grading (captions, titles)
        self.exposure = 1.0
        self.shake = (0, 0)
        self.fade = 0.0  # 0 = none, 1 = black
        self.zoom = 1.0
        self.zoom_center = (W / 2, H / 2)

    # background ------------------------------------------------------
    def set_bg(self, arr, fig_light=None):
        self.base = arr
        self.fig_light = fig_light

    # shadows (hard light) ---------------------------------------------
    def cast_shadow(self, fx, fy, sx, sy, length, strength=220, width=46):
        """Hard shadow of a standing figure. Feet at (fx,fy); (sx,sy) = the point on the floor
        directly under the light. The shadow points away from it, flattened by perspective."""
        dx, dy = fx - sx, (fy - sy) * 1.8
        n = math.hypot(dx, dy) + 1e-3
        ux, uy = dx / n, dy / n
        tipx, tipy = fx + ux * length, fy + uy * length * 0.42
        px, py = -uy, ux
        w0, w1 = width, width * 0.75
        pts = [(fx + px * w0, fy + py * w0 * 0.35), (tipx + px * w1, tipy + py * w1 * 0.35),
               (tipx - px * w1, tipy - py * w1 * 0.35), (fx - px * w0, fy - py * w0 * 0.35)]
        self.sd.polygon(pts, fill=strength)
        hr = width * 1.0
        self.sd.ellipse([tipx - hr, tipy - hr * 0.5, tipx + hr, tipy + hr * 0.5], fill=strength)
        self.sd.ellipse([fx - width * 1.3, fy - 16, fx + width * 1.3, fy + 16], fill=min(255, strength + 25))

    def blob_shadow(self, box, strength=170):
        self.sd.ellipse(box, fill=strength)

    def poly_shadow(self, pts, strength=170):
        self.sd.polygon(pts, fill=strength)

    # glow -------------------------------------------------------------
    def add_glow(self, x, y, r, color, power=1.0):
        g = spot(x, y, r, power)
        self.glow += g[..., None] * np.array(color, np.float32) / 255.0

    # compose ----------------------------------------------------------
    def finish(self):
        img = self.base.copy()
        sh = to_arr(self.shadow.filter(ImageFilter.GaussianBlur(3)))
        img *= (1 - sh * 0.82)[..., None]
        # figures: shade by local light so they sit in the scene
        fig = np.asarray(self.fig, np.float32) / 255.0
        a = fig[..., 3:4]
        rgb = fig[..., :3]
        if self.fig_light is not None:
            rgb = rgb * np.clip(0.42 + self.fig_light[..., None] * 0.75, 0, 1.15)
        img = img * (1 - a) + rgb * a
        img += self.glow
        img *= self.exposure
        # grade: muted, cool shadows, slightly lifted blacks
        lum = img @ np.array([0.299, 0.587, 0.114], np.float32)
        img = img * 0.72 + lum[..., None] * 0.28
        img = img * np.array([0.96, 1.0, 1.04], np.float32)
        img = img * 0.94 + 0.025
        # vignette
        v = 1 - 0.55 * (((_XX - W / 2) / (W * 0.62)) ** 2 + ((_YY - H / 2) / (H * 0.62)) ** 2)
        img *= np.clip(v, 0.25, 1)[..., None]
        # film grain
        g = _grain_pool()[int(self.tg * FPS) % 6]
        g = np.asarray(Image.fromarray(((g * 32) + 128).clip(0, 255).astype(np.uint8)).resize((W, H)), np.float32)
        img += ((g / 255.0) - 0.5)[..., None] * 0.11
        if self.fade > 0:
            img *= (1 - self.fade)
        out = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
        if self.zoom > 1.001:
            zw, zh = W / self.zoom, H / self.zoom
            cx = min(max(self.zoom_center[0], zw / 2), W - zw / 2)
            cy = min(max(self.zoom_center[1], zh / 2), H - zh / 2)
            out = out.resize((W, H), Image.BICUBIC, box=(cx - zw / 2, cy - zh / 2, cx + zw / 2, cy + zh / 2))
        if self.shake != (0, 0):
            out = out.transform(out.size, Image.AFFINE, (1, 0, -self.shake[0], 0, 1, -self.shake[1]),
                                resample=Image.BILINEAR, fillcolor=(0, 0, 0))
        for fn in self.overlay:
            fn(out)
        return out


# ---------------------------------------------------------------- characters
def _seg(d, p1, p2, w, c, outline=INK, ow=6):
    if outline is not None:
        d.line([p1, p2], fill=outline, width=int(w + ow * 2))
        for p in (p1, p2):
            r = (w + ow * 2) / 2
            d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=outline)
    d.line([p1, p2], fill=c, width=int(w))
    for p in (p1, p2):
        r = w / 2
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=c)


def stickman(frame, x, ground, scale=1.0, facing=1, walk=0.0, arms=None, copy=False, head_turn=0.0,
             bags=False, sit=False, lean=0.0, eye_glow=1.0):
    """Leo (or the Copy). facing: 1 right, -1 left, 0 toward camera, 2 = back to camera.
    head_turn: for back view, 0 = back of head, 1 = fully turned to face camera."""
    k = scale * SS
    bw, bh = int(260 * k), int(560 * k)
    box = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
    d = ImageDraw.Draw(box)
    cx, gy = bw / 2, bh - 40 * k
    hip = (cx + lean * 30 * k, gy - (95 if not sit else 40) * k)
    neck = (cx + lean * 75 * k, gy - 205 * k)
    head = (neck[0] + lean * 10 * k, neck[1] - 40 * k)
    side = facing in (1, -1)
    f = facing if side else 1
    # legs (jeans) + sneakers
    if sit:
        for i, off in enumerate((-12, 12)):
            knee = (hip[0] + 62 * k * f, hip[1] + 4 * k)
            foot = (knee[0] + 6 * k * f, knee[1] + 58 * k)
            _seg(d, (hip[0] + off * k * 0.3, hip[1]), knee, 26 * k, JEANS, ow=5 * k)
            _seg(d, knee, foot, 24 * k, JEANS, ow=5 * k)
            d.ellipse([foot[0] - 12 * k, foot[1] - 8 * k, foot[0] + 26 * k * f if f > 0 else foot[0] + 12 * k,
                       foot[1] + 12 * k], fill=SKIN, outline=INK, width=int(4 * k)) if f > 0 else \
                d.ellipse([foot[0] - 26 * k, foot[1] - 8 * k, foot[0] + 12 * k, foot[1] + 12 * k],
                          fill=SKIN, outline=INK, width=int(4 * k))
    else:
        for ph in (0, math.pi):
            a = math.sin(walk + ph) * 0.42
            if side:
                knee = (hip[0] + math.sin(a) * 50 * k * f, hip[1] + math.cos(a) * 50 * k)
                fa = a - 0.12
                foot = (knee[0] + math.sin(fa) * 50 * k * f, knee[1] + math.cos(fa) * 50 * k)
            else:
                sx = -16 if ph == 0 else 16
                knee = (hip[0] + sx * k, hip[1] + 50 * k)
                foot = (hip[0] + sx * 1.3 * k, gy)
            _seg(d, hip, knee, 26 * k, JEANS, ow=5 * k)
            _seg(d, knee, foot, 24 * k, JEANS, ow=5 * k)
            if side:
                d.ellipse([foot[0] - 14 * k if f > 0 else foot[0] - 30 * k, foot[1] - 9 * k,
                           foot[0] + 30 * k if f > 0 else foot[0] + 14 * k, foot[1] + 11 * k],
                          fill=SKIN, outline=INK, width=int(4 * k))
            else:
                d.ellipse([foot[0] - 17 * k, foot[1] - 10 * k, foot[0] + 17 * k, foot[1] + 12 * k],
                          fill=SKIN, outline=INK, width=int(4 * k))
    # hood behind the head (visible from back / sides)
    d.ellipse([neck[0] - 40 * k, neck[1] - 30 * k, neck[0] + 40 * k, neck[1] + 22 * k],
              fill=HOODIE_DK, outline=INK, width=int(5 * k))
    # torso (hoodie)
    tw = 36 * k
    torso = [(neck[0] - tw, neck[1] + 6 * k), (neck[0] + tw, neck[1] + 6 * k),
             (hip[0] + tw * 0.95, hip[1] + 14 * k), (hip[0] - tw * 0.95, hip[1] + 14 * k)]
    d.polygon(torso, fill=HOODIE, outline=INK, width=int(6 * k))
    d.line([(hip[0] - tw * 0.9, hip[1] - 2 * k), (hip[0] + tw * 0.9, hip[1] - 2 * k)], fill=HOODIE_DK, width=int(7 * k))
    if facing != 2:  # drawstrings
        for sx in (-10, 10):
            x0 = neck[0] + sx * k * (0.5 if side else 1)
            d.line([(x0, neck[1] + 10 * k), (x0 + sx * 0.15 * k, neck[1] + 52 * k)], fill=(235, 235, 232), width=int(4 * k))
            d.ellipse([x0 - 4 * k, neck[1] + 50 * k, x0 + 4 * k, neck[1] + 58 * k], fill=(235, 235, 232))
    # arms (sleeves) + hands
    sh = (neck[0], neck[1] + 18 * k)
    if arms is None:
        sw = math.sin(walk) * 0.35
        arms = [(sw, 0.25), (-sw, 0.25)]
    hands = []
    for i, (a_up, a_low) in enumerate(arms):
        ox = 0 if side else (-30 if i == 0 else 30) * k
        s0 = (sh[0] + ox, sh[1])
        fx = f if side else (-1 if i == 0 else 1)
        el = (s0[0] + math.sin(a_up) * 48 * k * fx, s0[1] + math.cos(a_up) * 48 * k)
        a2 = a_up + a_low
        hd = (el[0] + math.sin(a2) * 44 * k * fx, el[1] + math.cos(a2) * 44 * k)
        _seg(d, s0, el, 22 * k, HOODIE, ow=5 * k)
        _seg(d, el, hd, 20 * k, HOODIE, ow=5 * k)
        d.ellipse([hd[0] - 11 * k, hd[1] - 11 * k, hd[0] + 11 * k, hd[1] + 11 * k], fill=SKIN, outline=INK, width=int(4 * k))
        hands.append(hd)
    if bags:  # paper grocery bag in the lower hand
        hx, hy = hands[1]
        d.polygon([(hx - 34 * k, hy + 8 * k), (hx + 34 * k, hy + 8 * k), (hx + 40 * k, hy + 96 * k), (hx - 40 * k, hy + 96 * k)],
                  fill=(150, 118, 82), outline=INK, width=int(5 * k))
        d.line([(hx - 30 * k, hy + 22 * k), (hx + 30 * k, hy + 22 * k)], fill=(120, 92, 62), width=int(4 * k))
        d.ellipse([hx - 18 * k, hy - 8 * k, hx + 6 * k, hy + 14 * k], fill=(170, 60, 50), outline=INK, width=int(3 * k))
    # head
    r = 34 * k
    d.ellipse([head[0] - r, head[1] - r, head[0] + r, head[1] + r], fill=SKIN, outline=INK, width=int(7 * k))
    show_face = facing != 2 or head_turn > 0.35
    if show_face:
        if facing == 2:
            ex0 = lerp(-26, 0, ease((head_turn - 0.35) / 0.65))
            spread = lerp(4, 13, ease((head_turn - 0.35) / 0.65))
        elif side:
            ex0, spread = 12 * f, 6
        else:
            ex0, spread = 0, 13
        for sx in (-1, 1):
            ex, ey = head[0] + (ex0 + sx * spread) * k, head[1] - 2 * k
            if copy:
                rr = 9 * k
                d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=INK)
                rr2 = 6 * k
                d.ellipse([ex - rr2, ey - rr2, ex + rr2, ey + rr2], fill=(255, 255, 255))
            else:
                rr = 4.5 * k
                d.ellipse([ex - rr, ey - rr, ex + rr, ey + rr], fill=INK)
    # downsample + paste
    small = box.resize((bw // SS, bh // SS), Image.LANCZOS)
    px = int(x - (bw // SS) / 2)
    py = int(ground - (bh // SS) + 40 * scale)
    frame.fig.alpha_composite(small, (max(0, px), max(0, py)), (max(0, -px), max(0, -py)))
    if copy and show_face and eye_glow > 0:
        ex = x + (lean * 85 + (ex0 if facing == 2 else 0)) * scale
        frame.add_glow(ex, ground - 280 * scale + 40 * scale * 0, 40 * scale, (220, 230, 255), 0.35 * eye_glow)
    return hands


# ---------------------------------------------------------------- captions
def caption_overlay(words, t, y=1430, size=64, hl=(255, 214, 64)):
    """words: list of (word, start, end). Shows the current phrase, highlights the spoken word."""
    def draw(img):
        cur = [w for w in words if w[1] - 0.05 <= t <= words[-1][2] + 0.4]
        if not cur or t < words[0][1] - 0.05 or t > words[-1][2] + 0.5:
            return
        d = ImageDraw.Draw(img)
        f = font(size)
        # chunk into lines of <= 3 words around the current word
        idx = max(i for i, w in enumerate(words) if w[1] - 0.05 <= t) if any(w[1] - 0.05 <= t for w in words) else 0
        start = (idx // 3) * 3
        chunk = words[start:start + 3]
        texts = [w[0].upper() for w in chunk]
        sizes = [int(size * (1.12 if (start + i) == idx else 1.0)) for i in range(len(texts))]
        widths = [d.textlength(s, font=font(sz)) for s, sz in zip(texts, sizes)]
        gap = size * 0.32
        total = sum(widths) + gap * (len(texts) - 1)
        x = W / 2 - total / 2
        for i, (s, wdt) in enumerate(zip(texts, widths)):
            active = (start + i) == idx
            col = hl if active else (255, 255, 255)
            fs = font(int(size * (1.12 if active else 1.0)))
            yy = y - (size * 0.06 if active else 0)
            d.text((x + wdt / 2, yy), s, font=fs, fill=col, anchor="mm", stroke_width=6, stroke_fill=(10, 10, 12))
            x += wdt + gap
    return draw


def words_for(text_, t0, t1):
    """Spread words across [t0, t1] weighted by length (fallback when no alignment is known)."""
    ws = text_.split()
    wt = [len(w.strip(".,?!…")) + 2 for w in ws]
    tot = sum(wt)
    out, cur = [], t0
    for w, k in zip(ws, wt):
        dur = (t1 - t0) * k / tot
        out.append((w, cur, cur + dur))
        cur += dur
    return out


def title_overlay(s, y, size, color=(255, 255, 255), alpha=1.0):
    def draw(img):
        if alpha <= 0:
            return
        d = ImageDraw.Draw(img)
        c = tuple(int(v * alpha) for v in color)
        d.text((W / 2, y), s, font=font(size), fill=c, anchor="mm", stroke_width=5, stroke_fill=(8, 8, 10))
    return draw


# ---------------------------------------------------------------- render loop
_SCENES, _CAPS = [], []


def render_frame(tg, scenes, caps):
    fr = Frame(tg)
    for a, b, fn in scenes:
        if a <= tg < b or (b == scenes[-1][1] and tg >= a):
            fn(fr, tg - a)
            break
    for words in caps:
        fr.overlay.append(caption_overlay(words, tg))
    return fr.finish()


def _render(i):
    return render_frame(i / FPS, _SCENES, _CAPS).tobytes()


def run_video(scenes, caps, out, duration):
    global _SCENES, _CAPS
    _SCENES, _CAPS = scenes, caps
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                           "-crf", "25", "-tune", "grain", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool() as pool:
        for fb in pool.imap(_render, range(int(duration * FPS)), chunksize=4):
            ff.stdin.write(fb)
    ff.stdin.close()
    ff.wait()
