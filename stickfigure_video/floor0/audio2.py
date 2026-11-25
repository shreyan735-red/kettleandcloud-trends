"""FLOOR 0 Part 2 soundtrack. VO from (mp3, segments) pairs that exist. Usage: python3 audio2.py out.wav"""
import os
import sys
import wave

import numpy as np

import audio1 as A
from audio1 import add, buzz, click, ding, drone, env, heartbeat, hum, lowpass, noise, slide, sting, t_, thud

SR, N = A.SR, A.N


def knock(vol=0.7):
    t = t_(0.35)
    return (np.sin(2 * np.pi * 110 * t) * np.exp(-t * 28) + lowpass(A.rng.normal(0, 1, len(t)), 6) * np.exp(-t * 40) * 0.6) * vol


def fridge_open():
    t = t_(1.2)
    pop = lowpass(A.rng.normal(0, 1, len(t)), 10) * np.exp(-t * 18) * 0.5
    hm = np.sin(2 * np.pi * 120 * t) * 0.05 * env(len(t), 0.2, 0.3)
    return pop + hm


def vibrate():
    t = t_(0.5)
    return np.sign(np.sin(2 * np.pi * 170 * t)) * 0.18 * (np.sin(2 * np.pi * 8 * t) > 0) * env(len(t), 0.01, 0.05)


def static(dur, vol=0.05):
    return A.rng.normal(0, 1, int(dur * SR)) * vol * env(int(dur * SR), 0.05, 0.2)


def main(out):
    sfx = np.zeros(N)
    voice = np.zeros(N)
    add(sfx, drone(30, 41.2, 0.05), 0)
    # 0-3 door creaks open
    t = t_(1.3)
    add(sfx, np.sin(2 * np.pi * (300 + 90 * np.sin(t * 5)) * t) * 0.05 * env(len(t), 0.1, 0.4), 0.1)
    add(sfx, hum(3.0, 60, 0.03), 0.0)
    # 3-8 fridge
    add(sfx, fridge_open(), 3.1)
    add(sfx, hum(5.0, 120, 0.02), 3.2)
    add(sfx, sting(0.12), 5.6)
    # 8-13 the text arrives
    add(sfx, vibrate(), 9.3)
    add(sfx, vibrate(), 9.85)
    add(sfx, ding(1318, 0.05), 9.3)
    # 13-19 doorbell cam footage: static + tension
    add(sfx, static(6.0, 0.035), 13.0)
    add(sfx, drone(6.0, 36.7, 0.09), 13.0)
    for k in range(6):
        add(sfx, heartbeat(), 14.0 + k * 0.85, 0.6)
    # 19-24 feet / shadow: silence then low hit
    add(sfx, thud(0.45), 19.6)
    add(sfx, drone(4.5, 32.7, 0.1), 19.5)
    # 24-30 knock + door + final hit
    for k, at in enumerate((24.1, 24.35, 24.6)):
        add(sfx, knock(0.8), at)
    add(sfx, slide(1.0, 0.07), 25.0)
    add(sfx, hum(4.5, 60, 0.03), 25.0)
    add(sfx, thud(0.8), 29.4)
    add(sfx, sting(0.18), 29.4)

    for mp3, segf in (("vo2_leo.mp3", "segments2_leo.txt"), ("vo2_hale.mp3", "segments2_hale.txt")):
        if not (os.path.exists(mp3) and os.path.exists(segf)):
            continue
        vo = A.load_mp3(mp3)
        for ln in open(segf):
            if ln.startswith("#") or not ln.strip():
                continue
            a, b, at = list(map(float, ln.split()))[:3]
            seg = vo[int(a * SR): int((b + 0.1) * SR)]
            rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0
            if 0 < rms < 0.02:
                seg = seg * min(6.0, 0.045 / rms)
            add(voice, seg * env(len(seg), 0.01, 0.06), at)
    duck = 1 - 0.45 * np.clip(lowpass(np.abs(voice), 4000) * 12, 0, 1)
    mix = np.tanh((voice + sfx * duck) * 1.15) * 0.92
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
