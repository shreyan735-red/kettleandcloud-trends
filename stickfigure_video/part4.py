"""Part 4 — "Now I See The Timers" (her point of view)."""
import math
import sys

from engine import (BLACK, DARK, GREEN, RED, WHITE, bg, bubble, captions_from, circle, city, ease,
                    figure, fmt, ground_line, heart, hooded, lerp, line, mix, no_timer, run_video,
                    still, text, timer, truck, years, S, SW, W, H)

LINES = [
    "The day he disappeared… I started seeing timers.",
    "Everyone had a countdown. Everyone… except one man.",
    "A man in a black hood. He was always there when a timer hit zero.",
    "Then I saw a little boy. Ten seconds.",
    "I didn't think. I just ran. Just like he did.",
    "The hooded man grabbed my arm… and lowered his hood.",
    "It was him.",
    "He looked at my timer… and whispered, \"I'm sorry.\"",
    "It was counting up.",
]
PALE = (225, 225, 232)


def up(sec):
    sec = int(sec)
    return f"+{sec // 3600:02d}:{sec // 60 % 60:02d}:{sec % 60:02d}"


def collector(d, x, ground, scale, facing=-1, hood=1.0, arms=None, walk=0.0, c=BLACK, cloak=BLACK):
    """Hooded figure; hood=0 shows his face (it's him)."""
    if hood >= 0.999:
        hooded(d, x, ground, scale, facing=facing, arms=arms, walk=walk)
        return
    k = scale
    figure(d, x, ground, scale, walk=walk, facing=facing, arms=arms, c=c)
    d.polygon([(S(x - 14 * k), S(ground - 200 * k)), (S(x + 14 * k), S(ground - 200 * k)),
               (S(x + 55 * k), S(ground - 70 * k)), (S(x - 55 * k), S(ground - 70 * k))], fill=cloak)
    # hood sliding back off the head
    hx, hy = x, ground - 234 * k
    off = (1 - hood) * 70 * k
    pts = [(hx - 40 * k, hy + 34 * k + off * 0.4), (hx - 38 * k, hy - 20 * k + off),
           (hx - 8 * k * facing, hy - 52 * k + off), (hx + 34 * k, hy - 22 * k + off),
           (hx + 40 * k, hy + 34 * k + off * 0.4)]
    if hood > 0.05:
        d.polygon([(S(px + 26 * k * (1 - hood)), S(py + 50 * k * (1 - hood))) for px, py in pts], fill=BLACK)


def sc_hook(d, t):  # 0–4
    bg(d, DARK)
    d.line([0, S(1250), S(W), S(1250)], fill=(60, 60, 70), width=SW(6))
    figure(d, W / 2, 1250, 1.4, facing=1, girl=True, c=PALE)
    spots = [(170, 640, "41 YEARS"), (900, 560, "6 DAYS"), (230, 900, "12 YEARS"), (860, 880, "3 HOURS"),
             (540, 560, "77 YEARS"), (130, 1100, "29 YEARS"), (950, 1120, "00:04:12")]
    for i, (x, y, lab) in enumerate(spots):
        if t > 0.9 + i * 0.32:
            timer(d, x, y, lab, 34)
    text(d, (W / 2, 260), "HE DISAPPEARED…", 66, c=WHITE)
    text(d, (W / 2, 350), "NOW I SEE TIMERS", 76, c=RED)


def sc_except(d, t):  # 4–12
    ground = 1220
    city(d, ground, seed=6)
    ground_line(d, ground)
    walkers = [(-150, 1, 150, 1.0, "18 YEARS"), (1200, -1, 130, 0.95, "52 YEARS"),
               (300, 1, 110, 1.05, "4 YEARS"), (950, -1, 170, 1.0, "61 YEARS")]
    for i, (x0, dirn, sp, sc, lab) in enumerate(walkers):
        x = (x0 + dirn * sp * t) % 1400 - 160
        figure(d, x, ground, sc, walk=t * 8 + i, facing=dirn)
        timer(d, x + 30 * dirn, ground - 300 * sc, lab, 30)
    collector(d, 560, ground, 1.3, facing=-1)
    if t > 3.0:
        no_timer(d, 550, ground - 430, 36)
        d.ellipse([S(440), S(ground - 470), S(660), S(ground - 390)], outline=RED, width=SW(5))
    text(d, (W / 2, 260), "EVERYONE…", 66)
    text(d, (W / 2, 350), "EXCEPT HIM", 86, c=RED)


def sc_zero(d, t):  # 12–22
    ground = 1220
    ground_line(d, ground)
    # three quick "zero" moments, the hood is always there
    seg = min(2, int(t / 3.3))
    lt = t - seg * 3.3
    xs = [(330, 700), (680, 330), (420, 760)]
    vx, hx = xs[seg]
    if lt < 1.5:
        figure(d, vx, ground, 1.15, facing=1 if hx > vx else -1, lean=0.15 * lt)
        timer(d, vx, ground - 360, fmt(1.5 - lt), 36)
    else:
        figure(d, vx, ground, 1.15, lying=True)
        timer(d, vx, ground - 140, "00:00:00", 36, flash=int(t * 6) % 2 == 0)
    collector(d, hx, ground, 1.3, facing=-1 if hx > vx else 1)
    # her, watching from far
    figure(d, 980 if seg != 1 else 100, ground - 380, 0.55, facing=-1 if seg != 1 else 1, girl=True)
    text(d, (W / 2, 260), "ALWAYS THERE", 70)
    text(d, (W / 2, 350), "AT ZERO", 86, c=RED)


def boy(d, x, ground, t, run=False, c=BLACK):
    figure(d, x, ground, 0.72, walk=t * 12 if run else 0, facing=1, run=run, c=c)


def sc_boy(d, t):  # 22–30
    top, bot = 960, 1360
    d.line([0, S(top), S(W), S(top)], fill=BLACK, width=SW(6))
    d.line([0, S(bot), S(W), S(bot)], fill=BLACK, width=SW(6))
    for x in range(0, W, 120):
        d.line([S(x + 20), S(1160), S(x + 80), S(1160)], fill=(200, 200, 200), width=SW(8))
    lane = 1250
    # ball rolls into the road, boy follows
    bx = lerp(200, 560, ease(t / 2.5))
    circle(d, bx + 70, lane - 22, 22, 6, RED, fill=(255, 120, 120))
    boyx = lerp(80, 500, ease(t / 3.0))
    boy(d, boyx, lane, t, run=t < 3.0)
    left = 10 - max(0, t - 1.5) * 0.45
    timer(d, boyx, lane - 270, fmt(left), 38)
    # her on the far sidewalk
    figure(d, 820, top - 10, 1.0, facing=-1, girl=True)
    if t > 2.0:
        text(d, (820, top - 330), "!", 100, c=RED)
    # truck at the edge
    if t > 4.5:
        truck(d, lerp(1300, 1080, ease((t - 4.5) / 3)), lane + 70, 0.85)
    text(d, (W / 2, 260), "A LITTLE BOY", 76)
    text(d, (W / 2, 350), "10 SECONDS", 86, c=RED)


def sc_run(d, t):  # 30–38
    top, bot = 960, 1360
    d.line([0, S(top), S(W), S(top)], fill=BLACK, width=SW(6))
    d.line([0, S(bot), S(W), S(bot)], fill=BLACK, width=SW(6))
    for x in range(0, W, 120):
        d.line([S(x + 20), S(1160), S(x + 80), S(1160)], fill=(200, 200, 200), width=SW(8))
    lane = 1250
    push = 3.2
    # her: runs down from the top sidewalk to the boy
    if t < push:
        f = ease(t / push)
        hx, hy = lerp(820, 600, f), lerp(top - 10, lane, f)
        figure(d, hx, hy, 1.1, walk=t * 14, facing=-1, girl=True, run=True, lean=-0.35)
    else:
        f = ease((t - push) / 0.6)
        hx, hy = lerp(600, 760, f), lerp(lane, top - 10, f)  # pulled back by him
        figure(d, hx, hy, 1.1, facing=-1, girl=True, arms=[(1.6, 0.0), (0.3, 0.2)])
    # boy: pushed to the near sidewalk
    if t < push:
        boy(d, 500, lane, t)
        timer(d, 500, lane - 270, fmt(8.6 - t * 0.9), 38)
    else:
        f = ease((t - push) / 0.5)
        boy(d, lerp(500, 300, f), lerp(lane, bot + 150, f), t)
        timer(d, lerp(500, 300, f), lerp(lane, bot + 150, f) - 270, "70 YEARS", 36, c=GREEN)
    # the hooded man appears behind her and grabs her arm
    if t > push - 0.4:
        collector(d, 880, top - 10, 1.2, facing=-1, arms=[(1.6, 0.0), (0.2, 0.2)])
    # truck sweeps through
    tx = lerp(1150, -800, ease((t - 2.4) / 2.2)) if t > 2.4 else 1150
    truck(d, tx, lane + 70, 1.0)
    text(d, (W / 2, 260), "I JUST RAN", 86, c=RED)


def sc_hood(d, t):  # 38–47
    ground = 1220
    bg(d, (238, 238, 242))
    ground_line(d, ground)
    figure(d, 360, ground, 1.35, facing=1, girl=True, arms=[(1.2, 0.0), (0.3, 0.2)])
    hood = 1 - ease((t - 2.6) / 2.2)
    collector(d, 680, ground, 1.4, facing=-1, hood=hood, arms=[(1.2, 0.0), (0.2, 0.2)])
    no_timer(d, 670, ground - 460, 34)
    text(d, (W / 2, 260), "HE LOWERED", 70)
    text(d, (W / 2, 350), "HIS HOOD", 86, c=RED)


def sc_him(d, t):  # 47–51
    ground = 1300
    bg(d, (238, 238, 242))
    ground_line(d, ground)
    z = ease(t / 1.2)
    sc = lerp(1.4, 2.2, z)
    figure(d, lerp(360, 180, z), ground, sc, facing=1, girl=True)
    collector(d, lerp(680, 760, z), ground, sc, facing=-1, hood=0.0)
    for i in range(4):
        ht = (t - i * 0.6) % 2.4
        heart(d, 480 + math.sin(i * 2 + ht * 2) * 60, 640 - ht * 120, 26)
    text(d, (W / 2, 300), "IT WAS HIM", 110, c=RED)


def sc_sorry(d, t):  # 51–60
    ground = 1250
    bg(d, DARK)
    d.line([0, S(ground), S(W), S(ground)], fill=(60, 60, 70), width=SW(6))
    figure(d, 380, ground, 1.3, facing=1, girl=True, c=PALE)
    collector(d, 700, ground, 1.3, facing=-1, hood=0.0, c=PALE, cloak=(85, 85, 100))
    if t > 2.4:
        bubble(d, 720, 640, "I'M SORRY.", 56, 360)
    z = ease((t - 4.2) / 1.3)
    if t < 4.2:
        timer(d, 380, ground - 400, "60 YEARS", 42, c=GREEN)
    else:
        size = int(lerp(42, 100, z))
        timer(d, lerp(380, W / 2, z), lerp(ground - 400, 900, z), up((t - 4.2) * 2 + 1), size)
        if z > 0.9:
            text(d, (W / 2, 1010), "▲ COUNTING UP", 46, c=RED)
    text(d, (W / 2, 260), "MY TIMER…", 70, c=WHITE)
    if t > 7.0:
        text(d, (W / 2, 1110), "PART 5 →", 80, c=RED)


SCENES = [(0, 4, sc_hook), (4, 12, sc_except), (12, 22, sc_zero), (22, 30, sc_boy),
          (30, 38, sc_run), (38, 47, sc_hood), (47, 51, sc_him), (51, 60, sc_sorry)]

if __name__ == "__main__":
    caps = captions_from("segments_p4.txt", LINES)
    if sys.argv[1] == "--still":
        still(float(sys.argv[2]), SCENES, caps, sys.argv[3])
    else:
        run_video(SCENES, caps, sys.argv[1])
