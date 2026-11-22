"""Shared characters/props for Parts 6–9 (the boy's arc)."""
import math
import sys

from engine import (BLACK, DARK, GHOST, GREEN, RED, WHITE, bg, bubble, captions_from, circle, city,
                    ease, figure, floater, fmt, ground_line, heart, hooded, lerp, line, mix, no_timer,
                    rain, run_video, still, text, timer, years, S, SW, W, H)

LIGHT = (238, 238, 242)
PALE = (225, 225, 232)
WARM = (252, 246, 236)
NAVY = (30, 34, 52)


def teen(d, x, ground, scale=1.2, c=BLACK, **kw):
    """The boy, ten years older: stick figure with a cap."""
    figure(d, x, ground, scale, c=c, **kw)
    k = scale
    lean = kw.get("lean", 0.0)
    facing = kw.get("facing", 1)
    hx = x + lean * 85 * k
    hy = ground - 234 * k
    d.chord([S(hx - 31 * k), S(hy - 32 * k), S(hx + 31 * k), S(hy + 18 * k)], 180, 360, fill=c)
    d.line([S(hx + 10 * k * facing), S(hy - 8 * k), S(hx + 52 * k * facing), S(hy - 6 * k)],
           fill=c, width=SW(8 * k))


def elder(d, x, ground, scale=1.45, facing=-1, arms=None, eyes=RED, c=BLACK):
    """The first collector: tall, hunched, with a staff."""
    hooded(d, x, ground, scale, facing=facing, arms=arms)
    k = scale
    line(d, (x + 70 * k * facing, ground - 280 * k), (x + 70 * k * facing, ground), 8, c)
    circle(d, x + 70 * k * facing, ground - 290 * k, 14 * k, 6, c, fill=c)
    for ex in (-12, 12):
        circle(d, x + (ex + 8 * facing) * k, ground - 234 * k, 6 * k, 2, eyes, fill=eyes)


def hood_item(d, x, y, s=1.0, c=BLACK):
    d.polygon([(S(x - 55 * s), S(y + 40 * s)), (S(x - 45 * s), S(y - 30 * s)), (S(x), S(y - 70 * s)),
               (S(x + 45 * s), S(y - 30 * s)), (S(x + 55 * s), S(y + 40 * s))], fill=c)


def bridge(d, ground, c=BLACK):
    d.line([0, S(ground), S(W), S(ground)], fill=c, width=SW(10))
    for x0 in (-200, 340, 880):
        d.arc([S(x0), S(ground - 300), S(x0 + 540), S(ground + 300)], 180, 360, fill=c, width=SW(8))
    for x in range(0, W, 60):
        y = ground - 60
        line(d, (x, ground), (x, y), 4, c)
    d.line([0, S(ground - 60), S(W), S(ground - 60)], fill=c, width=SW(5))


def tower(d, cx, top, ground, c=BLACK, fill=WHITE):
    d.polygon([(S(cx - 140), S(ground)), (S(cx + 140), S(ground)), (S(cx + 60), S(top + 80)),
               (S(cx - 60), S(top + 80))], fill=fill, outline=c, width=SW(8))
    d.rectangle([S(cx - 90), S(top + 20), S(cx + 90), S(top + 80)], fill=fill, outline=c, width=SW(8))
    for y in range(int(top + 160), int(ground - 60), 140):
        d.rectangle([S(cx - 22), S(y), S(cx + 22), S(y + 60)], outline=c, width=SW(5))


def mini(d, x, ground, s, lab, col=RED, c=BLACK, girl=False, arms=None):
    figure(d, x, ground, s, c=c, girl=girl, arms=arms)
    if lab:
        timer(d, x, ground - 300 * s, lab, max(16, int(46 * s)), c=col)


def skyline_timers(d, t, ground, lab="3 DAYS", t0=0.0, n=14, col=RED):
    city(d, ground, c=(170, 170, 185), seed=4)
    spots = [(90, 540), (250, 430), (420, 600), (560, 380), (700, 520), (860, 450), (1000, 590),
             (150, 760), (330, 820), (500, 700), (660, 800), (820, 740), (980, 820), (420, 920)]
    for i, (x, y) in enumerate(spots[:n]):
        if t > t0 + i * 0.12:
            timer(d, x, y + 110 + (ground - 1220), lab, 26, c=col)


def make_main(scenes, seg_file, lines_):
    caps = captions_from(seg_file, lines_)
    if sys.argv[1] == "--still":
        still(float(sys.argv[2]), scenes, caps, sys.argv[3])
    else:
        run_video(scenes, caps, sys.argv[1])
