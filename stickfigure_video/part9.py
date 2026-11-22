"""Part 9 — "Only To Share" (series finale)."""
import math

from series import (BLACK, DARK, GREEN, LIGHT, NAVY, PALE, RED, WARM, WHITE, bg, bridge, circle, city,
                    ease, elder, figure, floater, ground_line, heart, hood_item, lerp, line, make_main,
                    mini, mix, teen, text, timer, tower, S, SW, W, H)

LINES = [
    "One day. That's all it would cost. One day from every person.",
    "The boy climbed to the highest tower in the city.",
    "And he told everyone the truth.",
    "And for one moment… everyone could see the timers.",
    "One by one, they held hands. Strangers. Families. Enemies.",
    "A million people… gave one day each.",
    "The timers turned green. The hood burned to ash.",
    "Death got its debt. And nobody had to pay alone.",
    "Time was never ours to keep. Only to share.",
]
DUSK = (44, 48, 70)
CROWD_X = [70 + i * 105 for i in range(10)]


def crowd(d, t, ground, rows=3, lab=None, col=RED, hands=0.0, c=BLACK, appear=None):
    for r in range(rows):
        gy = ground - r * 165
        s = 0.62 - r * 0.1
        for i, x in enumerate(CROWD_X):
            xx = x + (r % 2) * 50
            k = r * 10 + i
            arms = [(1.4, 0.0), (-1.4, 0.0)] if hands > (k / 30) else None
            figure(d, xx, gy, s, c=c, girl=(k % 3 == 0), arms=arms)
            if lab and (i + r) % 2 == 0 and (appear is None or t > appear + k * 0.05):
                timer(d, xx, gy - 300 * s, lab(k) if callable(lab) else lab, max(14, int(40 * s)), c=col)
        if hands > 0:  # chain of joined hands across the row
            prog = min(1.0, hands * 1.2 - r * 0.15)
            if prog > 0:
                d.line([S(CROWD_X[0] + (r % 2) * 50), S(gy - 130 * s), S(lerp(CROWD_X[0], CROWD_X[-1], prog) + (r % 2) * 50),
                        S(gy - 130 * s)], fill=(255, 200, 70), width=SW(5))


def sc_cost(d, t):  # 0–5.5
    bg(d, DARK)
    z = ease(t / 0.8)
    text(d, (W / 2, 800), "1 DAY", int(lerp(80, 200, z)), c=(110, 220, 130))
    text(d, (W / 2, 990), "FROM EVERY PERSON", 54, c=WHITE)
    teen(d, W / 2, 1300, 0.9, c=PALE)
    text(d, (W / 2, 280), "THE ANSWER", 80, c=WHITE)


def sc_tower(d, t):  # 5.5–13
    bg(d, DUSK)
    ground = 1320
    city(d, ground, c=(80, 84, 110), seed=1)
    tower(d, W / 2, 520, ground, c=(20, 20, 30), fill=(60, 64, 90))
    climb = ease(t / 6.0)
    y = lerp(ground, 600, climb)
    teen(d, W / 2 + 0, y, 0.55, c=PALE, walk=t * 6 if climb < 1 else 0)
    text(d, (W / 2, 260), "THE HIGHEST", 70, c=WHITE)
    text(d, (W / 2, 350), "TOWER", 92, c=RED)


def sc_shout(d, t):  # 13–19
    bg(d, DUSK)
    ground = 1320
    city(d, ground, c=(80, 84, 110), seed=1)
    tower(d, W / 2, 900, ground, c=(20, 20, 30), fill=(60, 64, 90))
    teen(d, W / 2, 980, 1.1, c=PALE, arms=[(2.8, 0.2), (-2.8, -0.2)])
    for i in range(4):  # sound waves
        r = ((t * 260) + i * 110) % 440 + 90
        a = max(0, 255 - int(r * 0.5))
        col = (a, a, int(a * 0.9))
        d.arc([S(W / 2 - r), S(760 - r * 0.6), S(W / 2 + r), S(760 + r * 0.6)], 200, 340, fill=col, width=SW(6))
    text(d, (W / 2, 260), "HE TOLD", 70, c=WHITE)
    text(d, (W / 2, 350), "EVERYONE", 92, c=RED)


def sc_see(d, t):  # 19–25
    bg(d, LIGHT)
    ground = 1250
    crowd(d, t, ground, lab="3 DAYS", appear=1.4)
    if 1.4 < t < 4.0:
        for i in range(3):
            text(d, (180 + i * 360, 700 - (i % 2) * 60), "!", 80, c=RED)
    text(d, (W / 2, 260), "EVERYONE COULD", 64)
    text(d, (W / 2, 350), "SEE THEM", 92, c=RED)


def sc_hands(d, t):  # 25–33
    bg(d, LIGHT)
    ground = 1250
    crowd(d, t, ground, lab="3 DAYS", hands=ease(t / 6.0))
    words = [(1.8, "STRANGERS"), (2.9, "FAMILIES"), (4.0, "ENEMIES")]
    shown = [w for (a, w) in words if t > a]
    if shown:
        text(d, (W / 2, 560), shown[-1], 80, c=RED)
    text(d, (W / 2, 260), "THEY HELD", 70)
    text(d, (W / 2, 350), "HANDS", 92, c=RED)


def sc_million(d, t):  # 33–39
    bg(d, LIGHT)
    ground = 1250
    crowd(d, t, ground, lab="-1 DAY", hands=1.0)
    n = int(min(1.0, ease(t / 4.5)) * 1_000_000)
    text(d, (W / 2, 620), f"{n:,}", 110, c=RED)
    text(d, (W / 2, 720), "DAYS GIVEN", 50)
    text(d, (W / 2, 300), "A MILLION PEOPLE", 70)


def sc_green(d, t):  # 39–46
    bg(d, mix(LIGHT, WARM, ease(t / 3)))
    ground = 1250
    g = ease(t / 1.6)
    crowd(d, t, ground, lab=lambda k: f"{40 + (k * 7) % 45} YEARS", col=mix(RED, GREEN, g), hands=1.0)
    # the hood burning on the bridge rail (inset)
    burn = ease((t - 2.6) / 2.5)
    cx, cy = W / 2, 640
    d.rounded_rectangle([S(cx - 220), S(cy - 170), S(cx + 220), S(cy + 150)], radius=SW(24), fill=DARK)
    if burn < 1:
        hood_item(d, cx, cy + 40 - 0, 1.2 * (1 - burn * 0.7), c=mix(BLACK, (90, 90, 90), burn))
    for i in range(10):
        if 0 < burn < 1:
            fx = cx + math.sin(i * 1.7 + t * 9) * 70
            fy = cy + 60 - ((t * 220 + i * 40) % 180)
            circle(d, fx, fy, 14 - (i % 3) * 3, 2, (255, 150, 40), fill=(255, 190 - i * 8, 60))
    if burn >= 1:
        for i in range(12):  # ash drifting away
            ax = cx + math.sin(i * 2.3) * 160 + (t - 5.1) * 40
            ay = cy - ((t - 5.1) * 120 + i * 18) % 200
            circle(d, ax, ay, 4, 1, (150, 150, 150), fill=(150, 150, 150))
    text(d, (W / 2, 260), "THE TIMERS", 70)
    text(d, (W / 2, 350), "TURNED GREEN", 86, c=GREEN)


def sc_alone(d, t):  # 46–53
    bg(d, WARM)
    ground = 1250
    circle(d, 880, 520, 80, 8, (240, 170, 30), fill=(255, 215, 120))
    ground_line(d, ground)
    # the old collector dissolves into light, freed
    if t < 1.6:
        elder(d, 820, ground, 1.3, facing=-1)
    elif t < 4.5:
        glow = mix((170, 200, 240), WARM, ease((t - 1.6) / 2.9))
        figure(d, 820, ground, 1.3, facing=-1, c=glow)
    for i in range(14):
        if 1.2 < t < 5.5:
            circle(d, 820 + math.sin(i * 1.4 + t * 2) * 100, ground - 60 - ((t * 160 + i * 40) % 460), 6, 1,
                   (255, 215, 110), fill=(255, 225, 140))
    # the couple and the boy together
    figure(d, 180, ground, 1.15, facing=1, girl=True)
    figure(d, 300, ground, 1.15, facing=1)
    teen(d, 450, ground, 1.15, facing=1)
    timer(d, 240, ground - 380, "49 YEARS", 30, c=GREEN)
    timer(d, 450, ground - 380, "69 YEARS", 30, c=GREEN)
    for i in range(4):
        ht = (t - i * 0.7) % 2.8
        heart(d, 320 + math.sin(i * 2 + ht * 2) * 80, ground - 420 - ht * 120, 24)
    text(d, (W / 2, 260), "NOBODY PAID", 76)
    text(d, (W / 2, 350), "ALONE", 96, c=GREEN)


def sc_end(d, t):  # 53–60
    bg(d, WARM)
    ground = 1250
    rise = ease(t / 3)
    circle(d, W / 2, lerp(1100, 700, rise), 120, 8, (240, 170, 30), fill=(255, 215, 120))
    city(d, ground, c=(200, 180, 150), seed=3)
    ground_line(d, ground)
    for i, x in enumerate((240, 360, 480, 600, 720, 840)):
        figure(d, x, ground, 0.6, facing=1, arms=[(1.4, 0.0), (-1.4, 0.0)], girl=(i % 2 == 0))
    if t > 0.5:
        text(d, (W / 2, 260), "TIME WAS NEVER", 66)
        text(d, (W / 2, 350), "OURS TO KEEP", 76, c=RED)
    if t > 3.0:
        text(d, (W / 2, 470), "ONLY TO SHARE", 80, c=GREEN)
    if t > 4.6:
        a = ease((t - 4.6) / 1.2)
        d.rectangle([0, 0, S(W), S(H)], fill=mix(WARM, WHITE, a))
        text(d, (W / 2, 880), "THE END", 120, c=mix(WHITE, BLACK, a))
        text(d, (W / 2, 1000), "THANK YOU FOR WATCHING", 44, c=mix(WHITE, RED, a))


SCENES = [(0, 5.5, sc_cost), (5.5, 13, sc_tower), (13, 19, sc_shout), (19, 25, sc_see),
          (25, 33, sc_hands), (33, 39, sc_million), (39, 46, sc_green), (46, 53, sc_alone), (53, 60, sc_end)]

if __name__ == "__main__":
    make_main(SCENES, "segments_p9.txt", LINES)
