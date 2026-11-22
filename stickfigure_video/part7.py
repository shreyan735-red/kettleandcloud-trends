"""Part 7 — "The First Collector" (the boy)."""
import math

from series import (BLACK, DARK, GREEN, LIGHT, NAVY, PALE, RED, WHITE, bg, bubble, circle, city, ease,
                    elder, figure, ground_line, hood_item, lerp, line, make_main, mini, mix, rain,
                    skyline_timers, teen, text, timer, S, SW, W, H)

LINES = [
    "Three days. Everyone in the city. Including me.",
    "There was only one person who might know why.",
    "A man in a black hood. Older than the city itself.",
    "He said: \"Two collectors broke free. Their debt didn't disappear.\"",
    "\"It spread. To everyone.\"",
    "\"Unless someone takes their place… the whole city pays.\"",
    "He held out the hood.",
    "And I reached for it.",
]
FOG = (70, 74, 92)


def sc_me(d, t):
    bg(d, (215, 230, 245))
    ground = 1250
    skyline_timers(d, t + 2, ground, "3 DAYS", 0.0, n=9)
    teen(d, W / 2, ground, 1.35)
    z = ease((t - 2.0) / 1.0)
    timer(d, W / 2, lerp(ground - 450, 700, z), "3 DAYS", int(lerp(44, 110, z)))
    text(d, (W / 2, 260), "INCLUDING", 70)
    text(d, (W / 2, 350), "ME", 110, c=RED)


def sc_search(d, t):
    bg(d, DARK)
    ground = 1250
    rain(d, t, n=50)
    city(d, ground, c=(60, 64, 84), seed=5)
    d.line([0, S(ground), S(W), S(ground)], fill=(90, 90, 110), width=SW(6))
    x = lerp(150, 760, ease(t / 6))
    teen(d, x, ground, 1.15, walk=t * 7, c=PALE)
    timer(d, x, ground - 410, "3 DAYS", 34)
    text(d, (W / 2, 260), "ONLY ONE PERSON", 66, c=WHITE)
    text(d, (W / 2, 350), "WOULD KNOW", 86, c=RED)


def sc_elder(d, t):
    bg(d, FOG)
    ground = 1250
    for i in range(6):  # drifting fog bands
        y = 700 + i * 110
        x = (t * 40 * (1 + i % 2) + i * 200) % 1400 - 300
        d.rounded_rectangle([S(x), S(y), S(x + 700), S(y + 50)], radius=SW(25), fill=(95, 99, 118))
    d.line([0, S(ground), S(W), S(ground)], fill=(40, 40, 50), width=SW(6))
    teen(d, 230, ground, 1.15, c=PALE)
    if t > 1.6:
        text(d, (230, ground - 440), "!", 100, c=RED)
    arrive = ease(t / 2.6)
    elder(d, lerp(1250, 760, arrive), ground, 1.55)
    text(d, (W / 2, 260), "OLDER THAN", 70, c=WHITE)
    text(d, (W / 2, 350), "THE CITY", 90, c=RED)


def sc_debt(d, t):
    bg(d, FOG)
    ground = 1250
    d.line([0, S(ground), S(W), S(ground)], fill=(40, 40, 50), width=SW(6))
    teen(d, 230, ground, 1.15, c=PALE)
    elder(d, 760, ground, 1.55, arms=[(1.3, 0.2), (0.2, 0.2)])
    if t < 2.6:
        bubble(d, 560, 620, "TWO COLLECTORS BROKE FREE.", 48, 560)
    else:
        bubble(d, 560, 620, "THEIR DEBT DIDN'T DISAPPEAR.", 48, 560)


def sc_spread(d, t):
    bg(d, DARK)
    cx, cy = W / 2, 900
    circle(d, cx, cy, 50, 8, RED, fill=(120, 20, 25))
    text(d, (cx, cy), "DEBT", 30, c=WHITE)
    pts = [(cx + math.cos(a) * r * 0.95, cy + math.sin(a) * r * 0.95)
           for i, (a, r) in enumerate([(i * 0.7, 230 + (i % 4) * 90) for i in range(26)])]
    grow = ease(t / 3.0)
    for i, (x, y) in enumerate(pts):
        if grow * 26 > i:
            d.line([S(cx), S(cy), S(x), S(y)], fill=(200, 40, 50), width=SW(4))
            figure(d, x, y + 60, 0.3, c=PALE)
    text(d, (W / 2, 260), "IT SPREAD", 90, c=RED)
    text(d, (W / 2, 350), "TO EVERYONE", 66, c=WHITE)


def sc_unless(d, t):
    bg(d, FOG)
    ground = 1250
    d.line([0, S(ground), S(W), S(ground)], fill=(40, 40, 50), width=SW(6))
    teen(d, 230, ground, 1.15, c=PALE)
    elder(d, 760, ground, 1.55, arms=[(1.3, 0.2), (0.2, 0.2)])
    if t > 0.3:
        bubble(d, 560, 620, "SOMEONE TAKES THEIR PLACE… OR THE CITY PAYS.", 46, 600)


def sc_offer(d, t):
    bg(d, FOG)
    ground = 1250
    d.line([0, S(ground), S(W), S(ground)], fill=(40, 40, 50), width=SW(6))
    teen(d, 300, ground, 1.25, c=PALE)
    elder(d, 760, ground, 1.55, arms=[(1.65, 0.0), (0.2, 0.2)])
    lift = ease(t / 1.0)
    hood_item(d, 600, lerp(ground - 300, ground - 330, lift), 1.0)
    text(d, (W / 2, 260), "HE HELD OUT", 70, c=WHITE)
    text(d, (W / 2, 350), "THE HOOD", 90, c=RED)


def sc_reach(d, t):
    bg(d, DARK)
    z = ease(t / 1.6)
    s = lerp(1.25, 2.0, z)
    ground = 1300
    teen(d, lerp(300, 260, z), ground, s, c=PALE, arms=[(lerp(0.3, 1.55, ease(t / 2.5)), 0.0), (0.2, 0.2)])
    hood_item(d, lerp(600, 720, z), lerp(ground - 330, ground - 520, z), lerp(1.0, 1.7, z), c=(10, 10, 14))
    d.polygon([(S(lerp(600, 720, z) - 4), S(lerp(ground - 330, ground - 520, z) - 2)), (S(lerp(600, 720, z) + 4), S(lerp(ground - 330, ground - 520, z) - 2)),
               (S(lerp(600, 720, z)), S(lerp(ground - 330, ground - 520, z) + 6))], fill=(90, 90, 110))
    text(d, (W / 2, 260), "AND I REACHED", 70, c=WHITE)
    text(d, (W / 2, 350), "FOR IT", 90, c=RED)
    if t > 4.0:
        text(d, (W / 2, 470), "PART 8 →", 80, c=RED)


SCENES = [(0, 6, sc_me), (6, 13, sc_search), (13, 21, sc_elder), (21, 30, sc_debt), (30, 36, sc_spread),
          (36, 44, sc_unless), (44, 50, sc_offer), (50, 60, sc_reach)]

if __name__ == "__main__":
    make_main(SCENES, "segments_p7.txt", LINES)
