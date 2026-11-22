"""Part 6 — "Everyone Had Three Days" (the boy, ten years later)."""
import math

from series import (BLACK, DARK, GREEN, LIGHT, RED, WARM, WHITE, bg, bubble, circle, ease, figure,
                    fmt, ground_line, heart, lerp, line, make_main, mini, mix, skyline_timers, teen,
                    text, timer, years, S, SW, W, H)

LINES = [
    "Ten years ago, a woman saved my life. That day, I started seeing timers.",
    "I never told anyone. Who would believe me?",
    "I learned to read them. Years. Days. Hours.",
    "Then one morning, I woke up… and something was wrong.",
    "My mom's timer said three days.",
    "So did my dad's. So did my teacher's.",
    "I ran to the window.",
    "Everyone in the city had the same timer.",
    "Three days.",
]
SEPIA = (240, 228, 205)
INKS = (90, 70, 50)


def sc_flash(d, t):  # flashback
    bg(d, SEPIA)
    lane = 1250
    d.line([0, S(lane + 100), S(W), S(lane + 100)], fill=INKS, width=SW(6))
    f = ease((t - 1.0) / 0.8)
    figure(d, lerp(560, 430, f), lane, 1.1, facing=-1, girl=True, c=INKS, lean=0.3 * (1 - f),
           arms=[(1.6, 0.0), (1.4, 0.0)])
    figure(d, lerp(400, 160, f), lerp(lane, lane + 90, f), 0.7, facing=1, c=INKS)
    if t > 1.8:
        timer(d, lerp(400, 160, f), lane - 230, "70 YEARS", 30, c=GREEN)
    text(d, (W / 2, 260), "10 YEARS AGO", 64, c=INKS)
    text(d, (W / 2, 350), "SHE SAVED MY LIFE", 70, c=RED)


def sc_secret(d, t):
    ground = 1230
    bg(d, LIGHT)
    ground_line(d, ground)
    for i, (x, lab) in enumerate([(110, "52 YEARS"), (300, "9 YEARS"), (790, "66 YEARS"), (975, "31 YEARS")]):
        mini(d, x, ground, 0.85, lab)
    teen(d, 540, ground, 1.25, arms=[(2.6, 1.2), (0.2, 0.2)])  # hand over mouth
    text(d, (540, ground - 430), "…", 80)
    text(d, (W / 2, 260), "I NEVER", 70)
    text(d, (W / 2, 350), "TOLD ANYONE", 86, c=RED)


def sc_read(d, t):
    ground = 1230
    ground_line(d, ground)
    teen(d, 170, ground, 1.15, arms=[(1.7, 0.0), (0.2, 0.2)])
    rows = [(460, "47 YEARS", "YEARS"), (700, "12 DAYS", "DAYS"), (940, "05 HOURS", "HOURS")]
    for i, (x, lab, word) in enumerate(rows):
        if t > 1.9 + i * 0.9:
            mini(d, x, ground, 0.95, lab)
            text(d, (x, ground + 70), word, 40, c=RED)
    text(d, (W / 2, 300), "I LEARNED TO READ THEM", 62)


def sc_wake(d, t):
    ground = 1230
    bg(d, WARM)
    d.rectangle([S(640), S(420), S(960), S(760)], outline=BLACK, width=SW(8))
    line(d, (800, 420), (800, 760), 6)
    circle(d, 880, 520, 46, 6, (240, 170, 30), fill=(255, 220, 100))
    ground_line(d, ground)
    d.rectangle([S(120), S(ground - 190), S(620), S(ground - 160)], fill=WHITE, outline=BLACK, width=SW(7))
    line(d, (140, ground - 160), (140, ground), 8)
    line(d, (600, ground - 160), (600, ground), 8)
    if t < 1.5:
        figure(d, 380, ground - 190, 1.05, lying=True)
    else:
        teen(d, 380, ground - 160, 1.05, arms=[(0.4, 0.2), (0.3, 0.2)])
        if t > 2.2:
            text(d, (380, ground - 560), "?", 100, c=RED)
    text(d, (W / 2, 260), "ONE MORNING…", 76)


def sc_mom(d, t):
    ground = 1230
    bg(d, WARM)
    ground_line(d, ground)
    teen(d, 280, ground, 1.25)
    z = ease((t - 0.4) / 1.2)
    figure(d, 720, ground, 1.3, facing=-1, girl=True, arms=[(0.6, 0.6), (0.3, 0.2)])
    timer(d, lerp(710, W / 2, z), lerp(ground - 400, 700, z), "3 DAYS", int(lerp(40, 120, z)))
    text(d, (W / 2, 260), "MOM", 96, c=RED)


def sc_dad(d, t):
    ground = 1230
    bg(d, WARM)
    ground_line(d, ground)
    who = [("DAD", 300), ("TEACHER", 780)]
    for i, (name, x) in enumerate(who):
        if t > 0.2 + i * 1.4:
            figure(d, x, ground, 1.2, facing=1 if i else -1)
            timer(d, x, ground - 390, "3 DAYS", 48)
            text(d, (x, ground + 80), name, 40)
    text(d, (W / 2, 260), "SO DID…", 86)


def sc_run(d, t):
    ground = 1230
    bg(d, WARM)
    ground_line(d, ground)
    d.rectangle([S(700), S(360), S(1040), S(900)], fill=(215, 230, 245), outline=BLACK, width=SW(10))
    line(d, (870, 360), (870, 900), 7)
    line(d, (700, 630), (1040, 630), 7)
    x = lerp(150, 600, ease(t / 1.4))
    teen(d, x, ground, 1.25, walk=t * 14, run=t < 1.4, lean=0.35 if t < 1.4 else 0,
         arms=[(1.7, 0.0), (1.5, 0.0)] if t >= 1.4 else None)
    text(d, (W / 2, 260), "TO THE WINDOW", 80)


def sc_city(d, t):
    bg(d, (215, 230, 245))
    ground = 1240
    skyline_timers(d, t, ground, "3 DAYS", 0.3)
    d.rectangle([0, 0, S(W), S(H)], outline=BLACK, width=SW(40))
    text(d, (W / 2, 220), "EVERYONE", 92)
    text(d, (W / 2, 310), "THE SAME TIMER", 66, c=RED)


def sc_three(d, t):
    bg(d, DARK)
    z = ease(t / 0.8)
    timer(d, W / 2, 820, "3 DAYS", int(lerp(60, 150, z)))
    teen(d, W / 2, 1250, 1.2, c=(225, 225, 232))
    if t > 2.6:
        text(d, (W / 2, 470), "PART 7 →", 80, c=RED)


# boundaries set from segments_p6.txt placement
SCENES = [(0, 7, sc_flash), (7, 13, sc_secret), (13, 21, sc_read), (21, 29, sc_wake),
          (29, 35, sc_mom), (35, 42, sc_dad), (42, 46, sc_run), (46, 54, sc_city), (54, 60, sc_three)]

if __name__ == "__main__":
    make_main(SCENES, "segments_p6.txt", LINES)
