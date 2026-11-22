"""Part 8 — "We Came Back" (his point of view)."""
import math

from series import (BLACK, DARK, GREEN, LIGHT, NAVY, PALE, RED, WARM, WHITE, bg, bridge, bubble, circle,
                    city, ease, elder, figure, ground_line, heart, hood_item, lerp, line, make_main, mix,
                    skyline_timers, teen, text, timer, S, SW, W, H)

LINES = [
    "Ten years. We thought it was over.",
    "Then every timer in the city turned to three days.",
    "We knew exactly whose debt it was. Ours.",
    "We found the boy on the bridge, holding the hood.",
    "She grabbed his hand. \"You don't have to do this.\"",
    "The old collector laughed. \"Then someone has to.\"",
    "I looked at her. She looked at me. We both knew.",
    "But the boy said something we never expected.",
    "\"What if everyone pays… just a little?\"",
]
NIGHT = (40, 44, 62)


def sc_over(d, t):
    bg(d, WARM)
    ground = 1250
    ground_line(d, ground)
    figure(d, 420, ground, 1.3, facing=1, girl=True, arms=[(1.2, 0.1), (0.2, 0.2)])
    figure(d, 620, ground, 1.3, facing=-1, arms=[(1.2, 0.1), (0.2, 0.2)])
    flick = t > 3.4
    for x in (400, 650):
        if flick and int(t * 8) % 2 == 0:
            timer(d, x, ground - 410, "3 DAYS", 36)
        else:
            timer(d, x, ground - 410, "49 YEARS", 36, c=GREEN)
    text(d, (W / 2, 260), "TEN YEARS", 76)
    text(d, (W / 2, 350), "LATER", 92, c=RED)


def sc_city(d, t):
    bg(d, (215, 230, 245))
    skyline_timers(d, t, 1250, "3 DAYS", 0.2)
    ground_line(d, 1250)
    figure(d, 470, 1250, 1.0, facing=1, girl=True)
    figure(d, 600, 1250, 1.0, facing=1)
    text(d, (W / 2, 260), "EVERY TIMER", 76)
    text(d, (W / 2, 350), "3 DAYS", 96, c=RED)


def sc_ours(d, t):
    bg(d, DARK)
    ground = 1250
    d.line([0, S(ground), S(W), S(ground)], fill=(60, 60, 70), width=SW(6))
    figure(d, 420, ground, 1.35, facing=1, girl=True, c=PALE)
    figure(d, 640, ground, 1.35, facing=-1, c=PALE)
    if t > 1.4:
        text(d, (W / 2, 820), "OUR DEBT", 120, c=RED)
    text(d, (W / 2, 280), "WE KNEW", 86, c=WHITE)


def bridge_scene(d, t):
    bg(d, NIGHT)
    ground = 1180
    bridge(d, ground, c=(15, 15, 22))
    d.rectangle([0, S(ground + 6), S(W), S(H)], fill=(30, 40, 66))
    for i in range(8):
        y = ground + 80 + i * 60
        x = (i * 173 + t * 30) % W
        d.line([S(x), S(y), S(x + 120), S(y)], fill=(70, 85, 120), width=SW(4))
    return ground


def sc_bridge(d, t):
    ground = bridge_scene(d, t)
    teen(d, 640, ground, 1.15, c=PALE, arms=[(1.0, 0.4), (0.2, 0.2)])
    hood_item(d, 700, ground - 140, 0.6)
    run = ease(t / 3.0)
    figure(d, lerp(-120, 240, run), ground, 1.15, walk=t * 13, facing=1, run=run < 1, girl=True, c=PALE)
    figure(d, lerp(-260, 110, run), ground, 1.15, walk=t * 13 + 1, facing=1, run=run < 1, c=PALE)
    text(d, (W / 2, 260), "THE BOY", 80, c=WHITE)
    text(d, (W / 2, 350), "ON THE BRIDGE", 76, c=RED)


def sc_grab(d, t):
    ground = bridge_scene(d, t)
    teen(d, 640, ground, 1.15, c=PALE, arms=[(1.0, 0.4), (0.2, 0.2)])
    hood_item(d, 700, ground - 140, 0.6)
    figure(d, 500, ground, 1.15, facing=1, girl=True, c=PALE, arms=[(1.5, 0.0), (0.2, 0.2)])
    figure(d, 300, ground, 1.15, facing=1, c=PALE)
    if t > 1.2:
        bubble(d, 520, 600, "YOU DON'T HAVE TO DO THIS.", 48, 560)


def sc_laugh(d, t):
    ground = bridge_scene(d, t)
    teen(d, 600, ground, 1.15, c=PALE)
    figure(d, 460, ground, 1.15, facing=1, girl=True, c=PALE)
    figure(d, 300, ground, 1.15, facing=1, c=PALE)
    arrive = ease(t / 1.4)
    elder(d, lerp(1200, 880, arrive), ground, 1.45)
    if t > 1.4:
        text(d, (900, ground - 520), "HA HA HA", 46, c=RED)
    if t > 2.6:
        bubble(d, 560, 600, "THEN SOMEONE HAS TO.", 54, 520)


def sc_knew(d, t):
    bg(d, DARK)
    ground = 1250
    d.line([0, S(ground), S(W), S(ground)], fill=(60, 60, 70), width=SW(6))
    z = ease(t / 1.5)
    s = lerp(1.3, 1.8, z)
    figure(d, lerp(380, 320, z), ground, s, facing=1, girl=True, c=PALE)
    figure(d, lerp(660, 720, z), ground, s, facing=-1, c=PALE)
    if t > 2.5:
        heart(d, W / 2, 760 - (t - 2.5) * 20, 50)
    text(d, (W / 2, 260), "WE BOTH", 76, c=WHITE)
    text(d, (W / 2, 350), "KNEW", 96, c=RED)


def sc_idea(d, t):
    ground = bridge_scene(d, t)
    figure(d, 260, ground, 1.15, facing=1, girl=True, c=PALE)
    figure(d, 390, ground, 1.15, facing=1, c=PALE)
    teen(d, 600, ground, 1.25, c=PALE, arms=[(2.8, 0.2), (0.2, 0.2)])
    elder(d, 880, ground, 1.45)
    if t > 0.6:
        text(d, (600, ground - 470), "!", 100, c=(255, 210, 80)) if t < 3.4 else None
    if t > 3.4:
        bubble(d, 560, 640, "WHAT IF EVERYONE PAYS… JUST A LITTLE?", 46, 620)
    text(d, (W / 2, 260), "THEN THE BOY SAID…", 64, c=WHITE)
    if t > 7.6:
        text(d, (W / 2, 400), "PART 9 →", 72, c=RED)


SCENES = [(0, 5, sc_over), (5, 12, sc_city), (12, 19, sc_ours), (19, 26, sc_bridge), (26, 33, sc_grab),
          (33, 40, sc_laugh), (40, 47, sc_knew), (47, 60, sc_idea)]

if __name__ == "__main__":
    make_main(SCENES, "segments_p8.txt", LINES)
