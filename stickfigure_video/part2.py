"""Part 2 — "My Timer Hit Zero… Then It Started Counting UP"."""
import math
import sys

from engine import *  # noqa: F401,F403
from engine import (BLACK, DARK, GREEN, RED, WHITE, bg, bubble, captions_from, circle, city, ease,
                    figure, floater, ground_line, heart, hooded, lerp, line, mix, no_timer, rain,
                    run_video, still, text, timer, years, S, SW, W, H)

LINES = [
    "My timer hit zero. Then it started counting… up.",
    "I should have died. But I woke up next to her.",
    "Then I noticed something. Everyone I walked past… lost time.",
    "Even her. The closer I got… the faster it fell.",
    "Then I met a man with no timer at all.",
    "\"You stole ten seconds from death,\" he said. \"Now everyone near you pays for it.\"",
    "So I did the only thing I could. I left her.",
    "But death never forgets a debt.",
]


def up(sec):
    sec = int(sec)
    return f"+{sec // 3600:02d}:{sec // 60 % 60:02d}:{sec % 60:02d}"


def sc_hook(d, t):  # 0–3
    bg(d, DARK)
    if t < 2.1:
        timer(d, W / 2, 900, "00:00:00", 110, flash=(int(t * 6) % 2 == 1))
    else:
        timer(d, W / 2, 900, up((t - 2.1) * 2.2 + 1), 110)
        text(d, (W / 2, 1060), "▲ COUNTING UP", 46, c=RED)
    text(d, (W / 2, 300), "MY TIMER HIT ZERO…", 66, c=WHITE)
    if t > 2.1:
        text(d, (W / 2, 390), "THEN IT COUNTED UP", 72, c=RED)


def sc_hospital(d, t):  # 3–12
    ground = 1250
    ground_line(d, ground)
    # bed
    d.rectangle([S(140), S(ground - 190), S(640), S(ground - 160)], fill=WHITE, outline=BLACK, width=SW(7))
    line(d, (160, ground - 160), (160, ground), 8)
    line(d, (620, ground - 160), (620, ground), 8)
    line(d, (140, ground - 260), (140, ground), 8)
    figure(d, 400, ground - 190, 1.1, lying=True)
    timer(d, 330, ground - 370, up(t * 3 + 40), 36)
    # heart monitor
    d.rectangle([S(150), S(560), S(470), S(760)], fill=(20, 30, 25), outline=BLACK, width=SW(7))
    pts = []
    for i in range(60):
        x = 165 + i * 5
        ph = (i * 5 + t * 260) % 300
        y = 660 - (70 if 140 < ph < 150 else (-30 if 150 <= ph < 158 else 0))
        pts.append((S(x), S(y)))
    d.line(pts, fill=(80, 240, 120), width=SW(4))
    # her
    figure(d, 820, ground, 1.25, facing=-1, girl=True, arms=[(1.0, 0.6), (0.2, 0.2)])
    timer(d, 800, ground - 380, "60 YEARS", 40, c=GREEN)
    if t > 2.5:
        for i in range(4):
            ht = (t - 2.5 - i * 0.9) % 3.6
            heart(d, 620 + math.sin(i * 2 + ht * 2) * 70, ground - 330 - ht * 120, 24)
    text(d, (W / 2, 300), "I SHOULD BE DEAD", 72)


def sc_drain(d, t):  # 12–23
    ground = 1220
    city(d, ground, seed=1)
    ground_line(d, ground)
    px = 540 + math.sin(t * 0.6) * 20
    figure(d, px, ground, 1.25, walk=t * 7, facing=1)
    timer(d, px + 30, ground - 400, up(t * 3 + 90000), 34)
    walkers = [(0.5, 41, 1.0), (3.6, 27, 1.1), (6.8, 63, 0.95)]
    for k, (t0, life, sc) in enumerate(walkers):
        lt = t - t0
        if not 0 <= lt <= 4.0:
            continue
        x = 1200 - lt * 360
        figure(d, x, ground, sc, walk=lt * 9 + k, facing=-1)
        dist = abs(x - px)
        lost = clamp_(1 - (x - px + 150) / 300) * 6
        near = dist < 220
        lab = years(life - lost)
        timer(d, x - 30, ground - 320 * sc, lab, 32, c=RED)
        if near:
            floater(d, x - 30, ground - 400 * sc, "-%dY" % max(1, int(lost)), (dist / 220), RED, 44)
            d.line([S(x), S(ground - 150), S(px), S(ground - 150)], fill=(240, 120, 120), width=SW(3))
    text(d, (W / 2, 300), "EVERYONE NEAR ME", 66)
    text(d, (W / 2, 390), "LOST TIME", 84, c=RED)


def clamp_(v):
    return max(0.0, min(1.0, v))


def sc_her(d, t):  # 23–33
    ground = 1250
    ground_line(d, ground)
    close = ease((t - 0.8) / 6.0)
    px = lerp(260, 470, close)
    gx = lerp(840, 640, close)
    figure(d, px, ground, 1.3, walk=t * 6 if 0 < close < 1 else 0, facing=1)
    figure(d, gx, ground, 1.3, walk=t * 6 if 0 < close < 1 else 0, facing=-1, girl=True)
    yrs = 60 - close * 34 - max(0, t - 7) * 2
    col = mix(GREEN, RED, close * 2)
    shake = (math.sin(t * 60) * 5) if close > 0.5 else 0
    timer(d, gx - 10 + shake, ground - 400, years(yrs), int(lerp(40, 64, close)), c=col)
    if close > 0.15:
        for i in range(3):
            floater(d, gx + 90, ground - 470, "-1Y", ((t * 1.5 + i / 3) % 1), RED, 38)
    if t > 8.0:
        text(d, (px, ground - 420), "!", 110, c=RED)
    text(d, (W / 2, 300), "EVEN HER", 92, c=RED)


def sc_stranger(d, t):  # 33–38
    ground = 1250
    bg(d, (235, 235, 240))
    city(d, ground, c=(190, 190, 200), seed=3)
    ground_line(d, ground)
    figure(d, 300, ground, 1.3, facing=1)
    timer(d, 330, ground - 400, up(t * 3 + 200000), 34)
    arrive = ease(t / 2.4)
    hx = lerp(1250, 760, arrive)
    hooded(d, hx, ground, 1.35, walk=t * 6 if arrive < 1 else 0)
    no_timer(d, hx - 10, ground - 440, 36)
    if t > 2.6:
        text(d, (300, ground - 470), "!", 110, c=RED)
    text(d, (W / 2, 300), "A MAN WITH", 66)
    text(d, (W / 2, 390), "NO TIMER", 92, c=RED)


def sc_warning(d, t):  # 38–49
    ground = 1230
    bg(d, (235, 235, 240))
    ground_line(d, ground)
    figure(d, 260, ground, 1.35, facing=1, arms=[(0.3, 0.2), (0.2, 0.2)])
    timer(d, 290, ground - 410, up(t * 3 + 200015), 34)
    point = [(1.75, 0.0), (0.2, 0.2)] if t > 1.0 else None
    hooded(d, 780, ground, 1.4, facing=-1, arms=point)
    no_timer(d, 770, ground - 450, 36)
    if 0.6 < t < 4.1:
        bubble(d, 560, 650, "YOU STOLE 10 SECONDS FROM DEATH.", 46, 640)
    elif t >= 4.1:
        bubble(d, 560, 650, "NOW EVERYONE NEAR YOU PAYS FOR IT.", 46, 640)
    # dark vignette pulse
    if t > 4.1:
        a = int(30 + 20 * math.sin(t * 4))
        d.rectangle([0, 0, S(W), S(60)], fill=(a, a, a))
        d.rectangle([0, S(H - 60), S(W), S(H)], fill=(a, a, a))


def sc_leave(d, t):  # 49–56
    ground = 1250
    bg(d, (60, 64, 78))
    rain(d, t)
    d.line([0, S(ground), S(W), S(ground)], fill=(20, 20, 26), width=SW(6))
    away = ease((t - 0.5) / 5.5)
    px = lerp(560, -150, away)
    figure(d, px, ground, 1.25, walk=t * 6 if 0 < away < 1 else 0, facing=-1, c=(20, 20, 26))
    gx = 780
    figure(d, gx, ground, 1.25, facing=-1, girl=True, c=(20, 20, 26),
           arms=[(1.6 + 0.1 * math.sin(t * 3), 0.0), (0.2, 0.2)] if t > 1 else None)
    yrs = lerp(22, 60, away)
    timer(d, gx - 10, ground - 380, years(yrs), 42, c=mix(RED, GREEN, away))
    if away > 0.95:
        timer(d, gx - 10, ground - 380, "60 YEARS", 42, c=GREEN)
    text(d, (W / 2, 300), "SO I LEFT HER", 82, c=WHITE)


def sc_debt(d, t):  # 56–60
    ground = 1250
    bg(d, DARK)
    d.line([0, S(ground), S(W), S(ground)], fill=(60, 60, 70), width=SW(6))
    figure(d, 700, ground, 1.25, facing=-1, girl=True, c=(200, 200, 210))
    flick = int(t * 7) % 3 == 0 and t > 1.2
    timer(d, 690, ground - 380, "00:00:10" if flick else "60 YEARS", 42, c=RED if flick else GREEN)
    if t > 0.8:
        a = ease((t - 0.8) / 1.5)
        hooded(d, lerp(200, 330, a), ground, 1.35, facing=1)
        for ex in (-12, 12):  # glowing eyes
            circle(d, lerp(200, 330, a) + ex + 8, ground - 234 * 1.35, 7, 2, RED, fill=RED)
    text(d, (W / 2, 300), "DEATH NEVER FORGETS", 62, c=WHITE)
    if t > 2.2:
        text(d, (W / 2, 520), "PART 3 →", 86, c=RED)


SCENES = [(0, 4.2, sc_hook), (4.2, 12, sc_hospital), (12, 23, sc_drain), (23, 33, sc_her),
          (33, 38, sc_stranger), (38, 49, sc_warning), (49, 56, sc_leave), (56, 60, sc_debt)]

if __name__ == "__main__":
    caps = captions_from("segments_p2.txt", LINES)
    if sys.argv[1] == "--still":
        still(float(sys.argv[2]), SCENES, caps, sys.argv[3])
    else:
        run_video(SCENES, caps, sys.argv[1])
