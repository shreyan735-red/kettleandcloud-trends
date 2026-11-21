"""Part 5 — "We Paid It Together" (her point of view)."""
import math
import sys

from engine import (BLACK, DARK, GREEN, RED, WHITE, bg, bubble, captions_from, circle, city, ease,
                    figure, floater, ground_line, heart, lerp, line, mix, no_timer, run_video, still,
                    text, timer, years, S, SW, W, H)
from part4 import PALE, collector, up

LINES = [
    "My timer was counting up. Now I was cursed too.",
    "Everyone near me started losing time. Just like him.",
    "He told me the truth. Collectors never die. They just… wait.",
    "Every life we save has to be paid for. By someone.",
    "So I asked him: what if we paid it together?",
    "We held hands… and both our timers started counting down.",
    "For the first time in a year… his timer came back.",
    "But the little boy I saved… was staring at us.",
    "He could see the timers too.",
]
LIGHT = (238, 238, 242)


def sc_hook(d, t):  # 0–4
    bg(d, DARK)
    d.line([0, S(1250), S(W), S(1250)], fill=(60, 60, 70), width=SW(6))
    figure(d, W / 2, 1250, 1.4, facing=1, girl=True, c=PALE)
    z = ease(t / 1.0)
    timer(d, W / 2, lerp(840, 680, z), up(t * 3 + 7), int(lerp(60, 110, z)))
    text(d, (W / 2, 790), "▲ COUNTING UP", 44, c=RED) if t > 1.2 else None
    text(d, (W / 2, 260), "NOW I'M", 70, c=WHITE)
    text(d, (W / 2, 355), "CURSED TOO", 90, c=RED)


def sc_drain(d, t):  # 4–12
    ground = 1220
    city(d, ground, seed=2)
    ground_line(d, ground)
    hx = 540 + math.sin(t * 0.6) * 20
    figure(d, hx, ground, 1.25, walk=t * 7, facing=1, girl=True)
    timer(d, hx + 20, ground - 400, up(t * 3 + 900), 34)
    for k, (t0, life) in enumerate([(0.3, 38), (2.8, 71), (5.2, 24)]):
        lt = t - t0
        if not 0 <= lt <= 3.4:
            continue
        x = 1200 - lt * 400
        figure(d, x, ground, 1.0, walk=lt * 9 + k, facing=-1)
        lost = max(0.0, min(1.0, 1 - (x - hx + 150) / 300)) * 5
        timer(d, x - 30, ground - 320, years(life - lost), 32)
        if abs(x - hx) < 220:
            floater(d, x - 30, ground - 400, "-%dY" % max(1, int(lost)), abs(x - hx) / 220, RED, 44)
    text(d, (W / 2, 260), "JUST LIKE HIM", 86, c=RED)


def sc_truth(d, t):  # 12–21
    ground = 1220
    bg(d, LIGHT)
    ground_line(d, ground)
    figure(d, 330, ground, 1.3, facing=1, girl=True)
    timer(d, 320, ground - 400, up(t * 3 + 960), 32)
    collector(d, 720, ground, 1.35, facing=-1, hood=0.0, arms=[(0.5, 0.4), (0.2, 0.2)])
    no_timer(d, 710, ground - 440, 32)
    if 1.5 < t < 3.5:
        bubble(d, 600, 600, "COLLECTORS NEVER DIE.", 50, 560)
    elif t >= 3.5:
        bubble(d, 600, 600, "WE JUST… WAIT.", 60, 480)
    text(d, (W / 2, 260), "THE TRUTH", 92, c=RED)


def scale_pan(d, cx, cy, w=170):
    d.line([S(cx - w / 2), S(cy), S(cx + w / 2), S(cy)], fill=BLACK, width=SW(8))
    d.arc([S(cx - w / 2), S(cy - 60), S(cx + w / 2), S(cy + 60)], 0, 180, fill=BLACK, width=SW(8))


def sc_price(d, t):  # 21–29
    bg(d, WHITE)
    cx, cy = W / 2, 760
    tilt = math.sin(min(t, 3.0) / 3.0 * math.pi / 2) * 0.28 + math.sin(t * 2.2) * 0.02
    line(d, (cx, cy - 20), (cx, cy + 520), 12)
    d.polygon([(S(cx - 140), S(cy + 540)), (S(cx + 140), S(cy + 540)), (S(cx), S(cy + 470))], fill=BLACK)
    arm = 330
    lx, ly = cx - arm * math.cos(tilt), cy - arm * math.sin(tilt) * -1
    rx, ry = cx + arm * math.cos(tilt), cy + arm * math.sin(tilt) * -1
    lx, ly = cx - arm * math.cos(tilt), cy + arm * math.sin(tilt)
    rx, ry = cx + arm * math.cos(tilt), cy - arm * math.sin(tilt)
    line(d, (lx, ly), (rx, ry), 12)
    circle(d, cx, cy, 20, 8, BLACK, fill=WHITE)
    for px, py in ((lx, ly), (rx, ry)):
        line(d, (px, py), (px - 70, py + 170), 5)
        line(d, (px, py), (px + 70, py + 170), 5)
        scale_pan(d, px, py + 170)
    heart(d, lx, ly + 130, 50, RED)
    text(d, (lx, ly + 260), "A LIFE SAVED", 36)
    timer(d, rx, ry + 120, "TIME OWED", 34)
    text(d, (W / 2, 260), "EVERY LIFE", 70)
    text(d, (W / 2, 355), "HAS A PRICE", 90, c=RED)


def sc_ask(d, t):  # 29–36
    ground = 1220
    bg(d, LIGHT)
    ground_line(d, ground)
    figure(d, 360, ground, 1.35, facing=1, girl=True, arms=[(0.9, 0.5), (0.2, 0.2)])
    collector(d, 700, ground, 1.35, facing=-1, hood=0.0)
    if t > 1.4:
        bubble(d, 420, 620, "WHAT IF WE PAY IT TOGETHER?", 50, 600)
    if t > 4.5:
        text(d, (700, ground - 470), "?", 100, c=RED)


def sc_hands(d, t):  # 36–44
    ground = 1220
    bg(d, DARK)
    d.line([0, S(ground), S(W), S(ground)], fill=(60, 60, 70), width=SW(6))
    figure(d, 440, ground, 1.35, facing=1, girl=True, c=PALE, arms=[(1.2, 0.1), (0.2, 0.2)])
    cloak = mix((85, 85, 100), DARK, ease((t - 3.0) / 3.0))
    collector(d, 640, ground, 1.35, facing=-1, hood=0.0, c=PALE, cloak=cloak,
              arms=[(1.2, 0.1), (0.2, 0.2)])
    swap = ease((t - 2.2) / 2.0)
    for i in range(18):  # swirl of light around their hands
        a = t * 2.5 + i * (2 * math.pi / 18)
        r = 70 + 120 * (1 - swap) + 30 * math.sin(t * 3 + i)
        circle(d, 540 + math.cos(a) * r, ground - 190 + math.sin(a) * r * 0.6, 8, 2,
               (255, 210, 80), fill=(255, 225, 120))
    if swap < 0.5:
        timer(d, 410, ground - 420, up(t * 3 + 1500), 36)
        no_timer(d, 670, ground - 440, 34)
    else:
        timer(d, 410, ground - 420, "59 YEARS", 38, c=GREEN)
        timer(d, 670, ground - 440, "59 YEARS", 38, c=GREEN)
        text(d, (W / 2, 620), "▼ COUNTING DOWN", 50, c=(90, 210, 120))
    text(d, (W / 2, 260), "WE PAID IT", 70, c=WHITE)
    text(d, (W / 2, 355), "TOGETHER", 92, c=RED)


def sc_back(d, t):  # 44–50
    ground = 1250
    bg(d, (252, 246, 236))
    circle(d, 860, 560, 80, 8, (240, 170, 30), fill=(255, 215, 120))
    ground_line(d, ground)
    z = ease(t / 1.4)
    figure(d, lerp(440, 380, z), ground, 1.35, facing=1, girl=True, arms=[(1.2, 0.1), (0.2, 0.2)])
    figure(d, lerp(640, 600, z), ground, 1.35, facing=-1, arms=[(1.2, 0.1), (0.2, 0.2)])
    timer(d, lerp(410, 330, z), ground - 410, "59 YEARS", 36, c=GREEN)
    timer(d, lerp(670, 720, z), lerp(ground - 410, 760, z), "59 YEARS", int(lerp(36, 70, z)), c=GREEN)
    for i in range(6):
        ht = (t - i * 0.5) % 3
        heart(d, 500 + math.sin(i * 2 + ht * 2) * 90, ground - 330 - ht * 140, 26)
    text(d, (W / 2, 260), "HIS TIMER", 76)
    text(d, (W / 2, 355), "CAME BACK", 92, c=GREEN)


def sc_boy(d, t):  # 50–60
    ground = 1250
    bg(d, (252, 246, 236))
    ground_line(d, ground)
    away = ease(t / 2.0)
    # the couple walks away left, hand in hand
    figure(d, lerp(300, 120, away), ground, 1.0, walk=t * 5, facing=-1, girl=True)
    figure(d, lerp(430, 250, away), ground, 1.0, walk=t * 5 + 1, facing=-1)
    # the boy, staring
    z = ease((t - 3.5) / 1.4)
    sc = lerp(0.75, 1.6, z)
    bx = lerp(820, 700, z)
    figure(d, bx, ground, sc, facing=-1)
    timer(d, bx - 10, ground - 280 * sc, "70 YEARS", int(lerp(30, 46, z)), c=GREEN)
    if t > 5.0:
        hy = ground - 234 * sc / 1.0 + 0
        for ex in (-11, 11):  # glowing red eyes
            circle(d, bx + ex * sc - 6 * sc, ground - 234 * sc, 5 * sc, 2, RED, fill=RED)
    if t > 6.0:  # tiny timers appear around him — he can see them
        for i, (dx, dy, lab) in enumerate([(-260, -520, "00:03:11"), (200, -600, "14 DAYS"), (-200, -760, "9 YEARS")]):
            if t > 6.0 + i * 0.35:
                timer(d, bx + dx, ground + dy, lab, 30)
    text(d, (W / 2, 260), "HE COULD SEE", 70)
    text(d, (W / 2, 355), "THEM TOO", 92, c=RED)
    if t > 8.0:
        text(d, (W / 2, 470), "PART 6 →", 70, c=RED)


SCENES = [(0, 4, sc_hook), (4, 12, sc_drain), (12, 21, sc_truth), (21, 29, sc_price),
          (29, 36, sc_ask), (36, 44, sc_hands), (44, 50, sc_back), (50, 60, sc_boy)]

if __name__ == "__main__":
    caps = captions_from("segments_p5.txt", LINES)
    if sys.argv[1] == "--still":
        still(float(sys.argv[2]), SCENES, caps, sys.argv[3])
    else:
        run_video(SCENES, caps, sys.argv[1])
