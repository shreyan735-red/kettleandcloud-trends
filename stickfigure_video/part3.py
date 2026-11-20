"""Part 3 — "Death Came Back For Her" (finale)."""
import math
import sys

from engine import (BLACK, DARK, GHOST, GREEN, RED, WHITE, bench, bg, bubble, captions_from, circle,
                    city, ease, figure, ground_line, heart, hooded, lerp, line, mix, no_timer, rain,
                    run_video, still, text, timer, years, fmt, S, SW, W, H)

LINES = [
    "Death came back for her. Ten seconds. Again.",
    "Since that day, I lived alone. Away from everyone. Away from her.",
    "The man with no timer found me. \"A debt must be paid,\" he said. \"Hers… or yours.\"",
    "I ran. Faster than I ever had.",
    "Five seconds left. I took her hand… and gave death back its ten seconds.",
    "Ten seconds. Just enough to say goodbye.",
    "Sixty years later… he was still waiting for her.",
]
NIGHT = (52, 56, 70)
INK = (20, 20, 26)


def sc_hook(d, t):  # 0–3.5
    bg(d, DARK)
    d.line([0, S(1250), S(W), S(1250)], fill=(60, 60, 70), width=SW(6))
    figure(d, W / 2, 1250, 1.3, facing=-1, girl=True, c=(210, 210, 220))
    z = ease(t / 1.0)
    timer(d, W / 2, lerp(850, 760, z), "00:00:10", int(lerp(60, 120, z)))
    text(d, (W / 2, 300), "DEATH CAME BACK", 70, c=WHITE)
    text(d, (W / 2, 395), "FOR HER", 92, c=RED)


def sc_alone(d, t):  # 3.5–12
    ground = 1250
    bg(d, NIGHT)
    city(d, ground, c=(80, 84, 100), seed=5)
    rain(d, t)
    d.line([0, S(ground), S(W), S(ground)], fill=INK, width=SW(6))
    bench(d, 540, ground, INK)
    figure(d, 540, ground - 60, 1.2, facing=1, c=INK, arms=[(0.6, 0.8), (0.5, 0.8)], lean=0.25)
    timer(d, 560, ground - 420, f"+{214 + int(t * 9)} DAYS", 36)
    # distant people keep away
    for k, x0 in enumerate((80, 960)):
        x = x0 + math.sin(t * 0.8 + k) * 30
        figure(d, x, ground - 300, 0.55, walk=t * 6 + k, facing=1 if k else -1, c=(90, 94, 110))
    text(d, (W / 2, 300), "ALONE", 96, c=WHITE)


def sc_debt(d, t):  # 12–22
    ground = 1250
    bg(d, NIGHT)
    rain(d, t)
    d.line([0, S(ground), S(W), S(ground)], fill=INK, width=SW(6))
    bench(d, 400, ground, INK)
    figure(d, 400, ground - 60, 1.2, facing=1, c=INK, arms=[(0.6, 0.8), (0.5, 0.8)],
           lean=0.25 if t < 1.8 else 0)
    timer(d, 420, ground - 420, "+290 DAYS", 34)
    arrive = ease(t / 1.6)
    hx = lerp(1250, 820, arrive)
    hooded(d, hx, ground, 1.35, walk=t * 6 if arrive < 1 else 0)
    no_timer(d, hx - 10, ground - 440, 34)
    if 2.2 < t < 4.6:
        bubble(d, 560, 640, "A DEBT MUST BE PAID.", 50, 560)
    elif t >= 4.6:
        bubble(d, 560, 640, "HERS… OR YOURS.", 60, 560)
        # inset: her timer
        d.rounded_rectangle([S(720), S(160), S(1040), S(470)], radius=SW(20), fill=DARK, outline=RED, width=SW(5))
        figure(d, 880, 440, 0.7, facing=-1, girl=True, c=(210, 210, 220))
        timer(d, 880, 220, "00:00:10", 30)


def sc_run(d, t):  # 22–33
    ground = 1250
    bg(d, NIGHT)
    rain(d, t, n=40)
    off = (t * 900) % 1080
    for k in (0, 1):
        for i, (x, h) in enumerate([(0, 380), (180, 520), (330, 300), (500, 600), (700, 420), (880, 480)]):
            bx = x - off + k * 1080
            d.rectangle([S(bx + 8), S(ground - h), S(bx + 170), S(ground)], outline=(80, 84, 100), width=SW(5))
    d.line([0, S(ground), S(W), S(ground)], fill=INK, width=SW(6))
    for i in range(6):  # speed lines
        y = 700 + i * 90
        x = (i * 223 - t * 1800) % 1300 - 100
        d.line([S(x), S(y), S(x + 160), S(y)], fill=(200, 205, 220), width=SW(4))
    figure(d, 470, ground, 1.3, walk=t * 15, facing=1, run=True, lean=0.4, c=INK)
    timer(d, 520, ground - 430, "+291 DAYS", 34)
    # her countdown inset
    left = lerp(10, 5, t / 11.0)
    d.rounded_rectangle([S(690), S(500), S(1030), S(640)], radius=SW(20), fill=DARK, outline=RED, width=SW(5))
    text(d, (860, 535), "HER", 30, c=WHITE)
    timer(d, 860, 595, fmt(left), 40, bg=False)
    text(d, (W / 2, 300), "I RAN", 110, c=WHITE)


def sc_give(d, t):  # 33–44
    ground = 1250
    top, bot = 980, 1360
    d.line([0, S(top), S(W), S(top)], fill=BLACK, width=SW(6))
    d.line([0, S(bot), S(W), S(bot)], fill=BLACK, width=SW(6))
    for x in range(0, W, 120):
        d.line([S(x + 20), S(1170), S(x + 80), S(1170)], fill=(200, 200, 200), width=SW(8))
    arrive = ease(t / 1.4)
    px = lerp(-120, 450, arrive)
    hold = t > 1.4
    figure(d, px, ground, 1.25, walk=t * 14 if not hold else 0, facing=1, run=not hold,
           lean=0.35 if not hold else 0, arms=[(1.2, 0.1), (0.2, 0.2)] if hold else None)
    figure(d, 640, ground, 1.25, facing=-1, girl=True, arms=[(1.2, 0.1), (0.2, 0.2)] if hold else None)
    swap = ease((t - 2.5) / 2.0)
    # her timer: 00:00:05 -> 60 YEARS
    if swap < 0.5:
        timer(d, 760, ground - 390, "00:00:05", 42)
    else:
        timer(d, 770, ground - 390, "60 YEARS", 42, c=GREEN)
    # his: +days -> 00:00:10
    if swap < 0.5:
        timer(d, px - 80, ground - 390, "+292 DAYS", 36)
    else:
        timer(d, px - 90, ground - 390, "00:00:10", 42)
    # glowing particles flowing from her to him
    if 0 < swap < 1:
        for i in range(14):
            f = ((t * 1.3) + i / 14) % 1
            x = lerp(620, 470, f)
            y = ground - 200 - math.sin(f * math.pi) * 220 + (i % 3) * 12
            circle(d, x, y, 9, 2, (255, 200, 60), fill=(255, 220, 90))
    if t > 0.3 and swap < 0.5:
        text(d, (W / 2, 300), "5 SECONDS LEFT", 80, c=RED)
    elif swap >= 0.5:
        text(d, (W / 2, 260), "I GAVE DEATH BACK", 62)
        text(d, (W / 2, 350), "ITS 10 SECONDS", 80, c=RED)


def sc_goodbye(d, t):  # 44–52
    ground = 1250
    ground_line(d, ground)
    fade = ease((t - 3.5) / 4.0)
    col = mix(BLACK, (235, 235, 235), fade)
    figure(d, 480, ground, 1.3, facing=1, c=col, arms=[(1.5, 0.9), (1.3, 0.9)] if fade < 0.98 else None)
    figure(d, 600, ground, 1.3, facing=-1, girl=True, arms=[(1.5, 0.9), (1.3, 0.9)])
    left = lerp(10, 0, clamp01(t / 7.5))
    if fade < 0.95:
        timer(d, 360, ground - 400, fmt(left), 42, c=mix(RED, (240, 200, 200), fade))
    timer(d, 740, ground - 400, "60 YEARS", 36, c=GREEN)
    for i in range(5):
        ht = (t - i * 0.8) % 4
        heart(d, 540 + math.sin(i * 2 + ht) * 90, ground - 360 - ht * 130, 24, mix((240, 80, 120), WHITE, fade * 0.6))
    text(d, (W / 2, 260), "JUST ENOUGH TO", 64)
    text(d, (W / 2, 350), "SAY GOODBYE", 84, c=RED)


def clamp01(v):
    return max(0.0, min(1.0, v))


def sc_later(d, t):  # 52–60
    ground = 1250
    warm = (252, 246, 236)
    bg(d, warm)
    circle(d, 860, 540, 80, 8, (240, 170, 30), fill=(255, 215, 120))
    ground_line(d, ground)
    bench(d, 600, ground)
    # old her walks slowly to the bench, cane in hand
    walk = ease(t / 3.2)
    ox = lerp(140, 420, walk)
    figure(d, ox, ground, 1.15, walk=t * 4 if walk < 1 else 0, facing=1, girl=True, lean=0.25,
           arms=[(0.9, -0.2), (0.3, 0.2)])
    line(d, (ox + 70, ground - 150), (ox + 80, ground), 7)
    timer(d, ox + 20, ground - 380, "00:00:03", 36)
    text(d, (ox - 70, ground - 440), "AGE 84", 30, c=(120, 120, 120))
    # ghost of him waiting, hand out
    gx = 720
    bob = math.sin(t * 2) * 8
    figure(d, gx, ground - 20 + bob, 1.25, facing=-1, c=GHOST,
           arms=[(1.4, 0.0), (0.2, 0.2)] if t > 3.2 else None)
    for i in range(5):  # sparkles
        sx, sy = gx + math.sin(t * 1.5 + i * 1.3) * 110, ground - 260 - ((t * 60 + i * 70) % 300)
        circle(d, sx, sy, 5, 2, GHOST, fill=GHOST)
    if t > 4.0:
        heart(d, (ox + gx) / 2, ground - 300 - (t - 4.0) * 30, 30, RED)
    text(d, (W / 2, 260), "60 YEARS LATER…", 72)
    if t > 6.0:
        a = ease((t - 6.0) / 1.5)
        d.rectangle([0, 0, S(W), S(H)], fill=mix(warm, WHITE, a))
        text(d, (W / 2, 900), "THE END", 110, c=mix(WHITE, BLACK, a))


SCENES = [(0, 3.5, sc_hook), (3.5, 12, sc_alone), (12, 22, sc_debt), (22, 33, sc_run),
          (33, 44, sc_give), (44, 52, sc_goodbye), (52, 60, sc_later)]

if __name__ == "__main__":
    caps = captions_from("segments_p3.txt", LINES)
    if sys.argv[1] == "--still":
        still(float(sys.argv[2]), SCENES, caps, sys.argv[3])
    else:
        run_video(SCENES, caps, sys.argv[1])
