"""FLOOR 0 Part 1 soundtrack: synthesized horror SFX + optional voiceover (vo1.mp3 + segments1.txt).
Usage: python3 audio1.py out.wav"""
import os
import subprocess
import sys
import wave

import numpy as np

SR = 44100
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(3)


def add(track, clip, at, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(clip))
    if j > i:
        track[i:j] += clip[: j - i] * gain


def env(n, a=0.01, r=0.1):
    e = np.ones(n)
    ai, ri = int(a * SR), int(r * SR)
    if ai:
        e[:ai] = np.linspace(0, 1, ai)
    if ri:
        e[-ri:] *= np.linspace(1, 0, ri)
    return e


def t_(dur):
    return np.arange(int(dur * SR)) / SR


def lowpass(x, k):
    return np.convolve(x, np.ones(k) / k, mode="same")


def hum(dur, f=55, vol=0.06):
    t = t_(dur)
    s = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4))
    return s * env(len(t), 0.5, 0.5) * vol


def buzz(dur, vol=0.07):
    t = t_(dur)
    s = np.sign(np.sin(2 * np.pi * 120 * t)) * 0.5 + np.sin(2 * np.pi * 240 * t) * 0.3
    crackle = (rng.random(len(t)) > 0.9985) * rng.normal(0, 3, len(t))
    gate = (lowpass(rng.random(len(t)), 2000) > 0.42).astype(float)
    return (s * gate + crackle) * env(len(t), 0.02, 0.2) * vol


def noise(dur, k=40, vol=0.1):
    return lowpass(rng.normal(0, 1, int(dur * SR)), k) * vol


def ding(f=880, vol=0.12):
    t = t_(1.6)
    return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 3) * vol


def drop():
    t = t_(3.2)
    rumble = lowpass(rng.normal(0, 1, len(t)), 300) * 3.0
    whoosh = lowpass(rng.normal(0, 1, len(t)), 12) * np.linspace(0.2, 1, len(t))
    creak = np.sin(2 * np.pi * (180 + 60 * np.sin(t * 7)) * t) * (np.sin(t * 3) > 0.6) * 0.3
    return (rumble + whoosh * 0.5 + creak) * env(len(t), 0.05, 0.8) * 0.35


def slide(dur=1.4, vol=0.18):
    t = t_(dur)
    s = lowpass(rng.normal(0, 1, len(t)), 60) * np.sin(np.pi * t / dur)
    return s * vol


def thud(vol=0.6):
    t = t_(0.9)
    return (np.sin(2 * np.pi * 50 * t * (1 - t * 0.3)) * np.exp(-t * 6) + lowpass(rng.normal(0, 1, len(t)), 30) * np.exp(-t * 14)) * vol


def click(vol=0.35):
    t = t_(0.05)
    return (rng.normal(0, 1, len(t)) + np.sin(2 * np.pi * 2600 * t)) * np.exp(-t * 120) * vol


def sting(vol=0.22):
    t = t_(2.6)
    s = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate((233.1, 246.9, 349.2, 370.0, 493.9)))
    s += lowpass(rng.normal(0, 1, len(t)), 8) * 0.6
    return s / 5 * env(len(t), 0.005, 1.8) * vol * (1 + 0.6 * np.exp(-t * 4))


def drone(dur, f=41.2, vol=0.08):
    t = t_(dur)
    s = sum(np.sin(2 * np.pi * f * m * t + m) for m in (1, 1.5, 2.02, 3.01)) / 4
    s *= 1 + 0.3 * np.sin(2 * np.pi * 0.15 * t)
    return s * env(len(t), 1.0, 1.0) * vol


def heartbeat():
    out = np.zeros(int(0.6 * SR))
    for off, f, g in ((0, 55, 1), (0.22, 48, 0.75)):
        t = t_(0.18)
        b = np.sin(2 * np.pi * f * t * (1 - t * 2)) * np.exp(-t * 22) * g
        i = int(off * SR)
        out[i:i + len(b)] += b
    return out


def load_mp3(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def main(out):
    sfx = np.zeros(N)
    voice = np.zeros(N)
    # 0-3 panel: hum + a faint wrong ding
    add(sfx, hum(8.0, 55, 0.05), 0)
    add(sfx, drone(30, 41.2, 0.05), 0)
    add(sfx, ding(660, 0.08), 0.3)
    # 3-8 elevator: hum continues, quiet
    add(sfx, hum(5.5, 55, 0.05), 7.5)
    # 8-12 press + drop + buzzing lights
    add(sfx, click(0.5), 8.45)
    add(sfx, drop(), 8.8)
    add(sfx, buzz(3.0, 0.09), 8.9)
    add(sfx, thud(0.5), 11.6)
    # 12-17 doors open on floor zero: cold drone
    add(sfx, ding(523, 0.07), 12.0)
    add(sfx, slide(1.6, 0.16), 12.1)
    add(sfx, drone(5.2, 36.7, 0.09), 12.0)
    add(sfx, noise(5.0, 200, 0.03), 12.0)
    # 17-22 apartment: heartbeat under the reveal
    add(sfx, drone(5.2, 32.7, 0.1), 17.0)
    for k in range(5):
        add(sfx, heartbeat(), 17.6 + k * 0.95, 0.7)
    # 22-26 smashing 12, doors close, head turns
    for k in range(10):
        add(sfx, click(0.45), 22.05 + k * 0.33)
    add(sfx, slide(2.4, 0.17), 22.7)
    add(sfx, sting(0.26), 23.0)
    add(sfx, thud(0.7), 25.2)
    # 26-30 floor 12: quiet, warm hum, final hit
    add(sfx, hum(4.0, 60, 0.035), 26.0)
    add(sfx, drone(4.0, 41.2, 0.06), 26.0)
    add(sfx, thud(0.8), 28.75)
    add(sfx, sting(0.18), 28.75)

    if os.path.exists("vo1.mp3") and os.path.exists("segments1.txt"):
        vo = load_mp3("vo1.mp3")
        for ln in open("segments1.txt"):
            if ln.startswith("#") or not ln.strip():
                continue
            a, b, at = map(float, ln.split())
            seg = vo[int(a * SR): int((b + 0.1) * SR)]
            rms = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0
            if 0 < rms < 0.02:
                seg = seg * min(6.0, 0.045 / rms)
            add(voice, seg * env(len(seg), 0.01, 0.06), at)
    duck = 1 - 0.45 * np.clip(lowpass(np.abs(voice), 4000) * 12, 0, 1)
    mix = np.tanh((voice * 1.0 + sfx * duck) * 1.15) * 0.92
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1])
