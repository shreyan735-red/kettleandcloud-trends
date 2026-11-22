"""Soundtracks for Part 2 and Part 3. Usage: python3 audio_parts.py 2|3 out.wav"""
import sys
import wave

import numpy as np

from audio import N, SR, add, boom, env, glitch, heartbeat, horn, load_mp3, pad, piano, rng, tick, tone, whoosh


def rain_noise(dur, vol=0.08):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    x = np.convolve(x, np.ones(6) / 6, mode="same")  # soften
    return x * env(n, 1.0, 1.0) * vol


def beep(f=1000, dur=0.12, vol=0.12):
    return tone(f, dur) * env(int(dur * SR), 0.004, 0.03) * vol


def drain(dur=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.01, 0.1) * 0.18


def chime(f):
    return piano(f, 2.5) * 0.12


def part2(music, sfx):
    add(music, pad([49, 73.4, 98], 12.5, 0.10), 0)
    for k in range(2):
        add(sfx, beep(1000, 0.7, 0.12), 0.2 + k * 0.9)
    for k in range(10):
        add(sfx, tick(True), 2.1 + k * 0.22, 0.6)
    for k in range(9):  # heart monitor beeps
        add(sfx, beep(1400, 0.1, 0.1), 4.6 + k * 0.82)
    add(music, pad([110, 164.8, 220], 7.5, 0.05), 4.2)
    for k in range(6):
        add(music, piano([261.6, 329.6, 392, 329.6, 293.7, 261.6][k], 1.8), 4.6 + k * 1.2, 0.07)
    add(music, pad([46.2, 69.3, 92.5], 21.5, 0.11), 12.0)
    for at in (13.4, 16.5, 19.7):
        add(sfx, drain(0.6), at, 1.0)
    for k in range(8):
        add(sfx, drain(0.35), 25.0 + k * 0.9, 0.8)
    for k, at in enumerate(np.cumsum([0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.48, 0.46]) + 25.5):
        add(sfx, heartbeat(), at, 0.8)
    add(sfx, whoosh(0.6), 32.8, 0.6)
    add(music, pad([41.2, 61.7, 82.4], 16.0, 0.14), 33.0)
    add(sfx, boom(1.2), 35.4, 0.35)
    add(sfx, glitch(0.3), 42.0, 0.6)
    add(sfx, rain_noise(7.2, 0.07), 49.0)
    for k, f in enumerate([220, 196, 174.6, 164.8]):
        add(music, chime(f), 49.4 + k * 1.6)
    add(music, pad([36.7, 55, 73.4], 4.2, 0.15), 55.9)
    for k in range(5):
        add(sfx, tick(k % 2 == 0), 57.2 + k * 0.5, 0.7)
    add(sfx, glitch(0.25), 57.3, 0.5)
    add(sfx, boom(1.5), 58.4, 0.5)


def part3(music, sfx):
    for k in range(4):
        add(sfx, tick(True), 0.2 + k * 0.85, 0.8)
    add(sfx, heartbeat(), 0.5, 0.8)
    add(sfx, heartbeat(), 1.6, 0.8)
    add(sfx, rain_noise(18.6, 0.08), 3.4)
    add(music, pad([55, 82.4, 110], 8.6, 0.09), 3.4)
    for k, f in enumerate([220, 196, 174.6, 164.8]):
        add(music, chime(f), 4.0 + k * 2.0)
    add(music, pad([41.2, 61.7, 82.4], 10.0, 0.13), 12.0)
    add(sfx, whoosh(0.6), 11.8, 0.5)
    add(sfx, boom(1.0), 17.0, 0.3)
    add(sfx, whoosh(0.5), 21.8, 0.6)
    add(sfx, rain_noise(11.0, 0.05), 22.0)
    for k in range(int(11 / 0.33)):  # footsteps
        add(sfx, tick(False) * 0.6, 22.2 + k * 0.33, 0.6)
    for k in range(11):
        add(sfx, heartbeat(), 22.3 + k * 1.0, 0.7)
    add(music, pad([49, 73.4, 98], 11.0, 0.12), 22.0)
    # the exchange: rising shimmer
    t = np.arange(int(2.2 * SR)) / SR
    shimmer = np.sin(2 * np.pi * (400 + 500 * t) * t) * env(len(t), 0.3, 0.6) * 0.12
    add(sfx, shimmer, 35.4)
    add(music, pad([130.8, 164.8, 196], 8.0, 0.06), 36.0)
    # goodbye: soft piano, his last ticks
    for k, f in enumerate([261.6, 246.9, 220, 196, 174.6, 196]):
        add(music, piano(f, 2.4), 44.2 + k * 1.3, 0.09)
    for k in range(8):
        add(sfx, tick(k % 2 == 0), 44.2 + k * 0.94, 0.45)
    add(sfx, beep(880, 1.4, 0.06), 51.6)
    # 60 years later: warm resolve
    for i, ch in enumerate([[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 392]]):
        for j, f in enumerate(ch):
            add(music, piano(f, 2.4), 52.2 + i * 1.9 + j * 0.15, 0.08)
    add(music, pad([130.8, 196, 261.6], 7.8, 0.05), 52.2)


def part4(music, sfx):
    # hook: timers pop in one by one
    for k in range(7):
        add(sfx, beep(900 + k * 90, 0.08, 0.09), 0.9 + k * 0.32)
    add(music, pad([55, 82.4, 110], 12.0, 0.09), 0)
    add(sfx, boom(1.0), 7.2, 0.3)  # "except one man"
    add(music, pad([46.2, 69.3, 92.5], 10.0, 0.12), 12.0)
    for seg in range(3):  # three zeros
        for k in range(2):
            add(sfx, tick(True), 12.0 + seg * 3.3 + k * 0.7, 0.7)
        add(sfx, beep(1000, 0.6, 0.1), 13.5 + seg * 3.3)
    add(sfx, whoosh(0.5), 21.8, 0.6)
    for k in range(8):
        add(sfx, tick(k % 2 == 0), 23.5 + k * 0.9, 0.7)
    add(sfx, heartbeat(), 24.2, 0.8)
    add(music, pad([49, 73.4, 98], 16.0, 0.12), 22.0)
    add(sfx, horn(1.4), 30.8, 0.9)
    for k, at in enumerate(np.cumsum([0.6, 0.55, 0.5, 0.45, 0.42]) + 29.8):
        add(sfx, heartbeat(), at, 0.8)
    add(sfx, whoosh(0.9), 32.4, 1.0)
    add(sfx, boom(1.0), 33.2, 0.35)
    # hood reveal: rising shimmer, then soft piano for "it was him"
    t = np.arange(int(2.4 * SR)) / SR
    add(sfx, np.sin(2 * np.pi * (300 + 400 * t) * t) * env(len(t), 0.4, 0.6) * 0.10, 40.6)
    add(music, pad([110, 164.8, 220], 9.0, 0.05), 38.0)
    for k, f in enumerate([329.6, 293.7, 261.6, 246.9]):
        add(music, piano(f, 2.0), 47.6 + k * 0.9, 0.09)
    # sorry + counting up
    add(music, pad([41.2, 61.7, 82.4], 9.0, 0.14), 51.0)
    for k in range(9):
        add(sfx, tick(True), 55.2 + k * 0.5, 0.6)
    add(sfx, boom(1.5), 58.2, 0.45)


def part5(music, sfx):
    for k in range(6):
        add(sfx, tick(True), 0.3 + k * 0.6, 0.7)
    add(music, pad([46.2, 69.3, 92.5], 12.0, 0.11), 0)
    for at in (4.8, 7.3, 9.7):
        add(sfx, drain(0.6), at, 1.0)
    add(music, pad([110, 164.8, 220], 9.0, 0.05), 12.0)
    for k, f in enumerate([220, 196, 174.6, 164.8]):
        add(music, chime(f), 12.4 + k * 2.0)
    add(sfx, whoosh(0.5), 20.8, 0.6)
    for k in range(4):  # scale creaks / thuds as it tips
        add(sfx, boom(0.5), 21.4 + k * 0.8, 0.12)
    add(music, pad([49, 73.4, 98], 8.0, 0.11), 21.0)
    add(music, pad([130.8, 164.8, 196], 7.0, 0.05), 29.0)
    # together: rising shimmer, warm chord swell
    t = np.arange(int(2.6 * SR)) / SR
    add(sfx, np.sin(2 * np.pi * (300 + 450 * t) * t) * env(len(t), 0.4, 0.6) * 0.11, 37.2)
    for i, ch in enumerate([[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7],
                            [261.6, 329.6, 392], [220, 261.6, 329.6]]):
        for j, f in enumerate(ch):
            add(music, piano(f, 2.2), 38.4 + i * 1.9 + j * 0.12, 0.08)
    # the boy: tension returns
    add(music, pad([41.2, 61.7, 82.4], 10.0, 0.13), 50.0)
    add(sfx, glitch(0.3), 55.0, 0.6)
    for k in range(3):
        add(sfx, beep(900 + k * 120, 0.08, 0.09), 56.0 + k * 0.35)
    for k in range(5):
        add(sfx, tick(True), 57.5 + k * 0.45, 0.6)
    add(sfx, boom(1.5), 58.4, 0.45)


def part6(music, sfx):
    # sepia flashback: soft piano
    for k, f in enumerate([261.6, 329.6, 392, 329.6, 293.7]):
        add(music, piano(f, 2.0), 0.3 + k * 1.3, 0.08)
    add(sfx, whoosh(0.6), 1.0, 0.5)
    add(music, pad([110, 164.8, 220], 13.0, 0.05), 7.0)
    for k in range(3):
        add(sfx, beep(900 + k * 150, 0.1, 0.09), 15.3 + k * 0.9)
    add(music, pad([55, 82.4, 110], 8.0, 0.08), 21.0)
    add(sfx, beep(1200, 0.25, 0.06), 22.6)  # alarm-ish
    add(sfx, beep(1200, 0.25, 0.06), 23.0)
    add(music, pad([46.2, 69.3, 92.5], 17.0, 0.12), 29.0)
    add(sfx, boom(1.0), 29.5, 0.3)
    add(sfx, heartbeat(), 30.4, 0.8)
    for k in range(2):
        add(sfx, boom(0.6), 35.5 + k * 1.4, 0.2)
    for k in range(6):  # footsteps to the window
        add(sfx, tick(False) * 0.7, 42.2 + k * 0.25, 0.6)
    add(sfx, whoosh(0.7), 45.8, 0.7)
    for k in range(14):
        add(sfx, beep(800 + (k % 5) * 110, 0.06, 0.07), 46.3 + k * 0.12)
    add(music, pad([41.2, 61.7, 82.4], 14.0, 0.14), 46.0)
    for k in range(6):
        add(sfx, tick(True), 54.6 + k * 0.8, 0.6)
    add(sfx, boom(1.6), 58.2, 0.5)


def part9(music, sfx):
    add(music, pad([65.4, 98, 130.8], 13.0, 0.09), 0)
    add(sfx, boom(0.8), 0.4, 0.25)
    for k in range(10):  # climbing steps
        add(sfx, tick(False) * 0.6, 6.0 + k * 0.6, 0.5)
    add(sfx, rain_noise(6.0, 0.04), 13.0)  # crowd/wind bed
    add(music, pad([73.4, 110, 146.8], 12.0, 0.09), 13.0)
    for k in range(10):
        add(sfx, beep(700 + (k % 4) * 150, 0.06, 0.07), 20.4 + k * 0.15)
    # building hope: chord progression from hands to the end
    prog = [[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7]]
    for i in range(14):
        for j, f in enumerate(prog[i % 4]):
            add(music, piano(f, 2.2), 25.3 + i * 1.95 + j * 0.12, 0.06 + min(0.05, i * 0.004))
    add(music, pad([130.8, 164.8, 196], 21.0, 0.06), 25.0)
    t = np.arange(int(3.0 * SR)) / SR
    add(sfx, np.sin(2 * np.pi * (300 + 500 * t) * t) * env(len(t), 0.5, 0.8) * 0.10, 39.3)
    add(sfx, rain_noise(2.5, 0.06), 41.8)  # fire crackle
    add(music, pad([130.8, 196, 261.6], 14.0, 0.07), 46.0)
    for i, ch in enumerate([[261.6, 329.6, 392, 523.3], [349.2, 440, 523.3], [261.6, 329.6, 392, 523.3]]):
        for j, f in enumerate(ch):
            add(music, piano(f, 3.0), 53.4 + i * 2.2 + j * 0.15, 0.08)


def main(part, out):
    vo = load_mp3(f"vo_p{part}.mp3")
    voice, music, sfx = np.zeros(N), np.zeros(N), np.zeros(N)
    for ln in open(f"segments_p{part}.txt"):
        if ln.startswith("#") or not ln.strip():
            continue
        a, b, at = map(float, ln.split())
        seg = vo[int(a * SR): int((b + 0.12) * SR)]
        add(voice, seg * env(len(seg), 0.01, 0.06), at)
    {"2": part2, "3": part3, "4": part4, "5": part5, "6": part6, "9": part9}[part](music, sfx)
    mixd = np.tanh((voice + music * 0.9 + sfx * 0.8) * 1.1) * 0.92
    pcm = (np.clip(mixd, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
