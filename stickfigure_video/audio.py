"""Build the 60s soundtrack: voiceover lines placed per segments.txt + synthesized SFX.

Usage: python3 audio.py vo.mp3 soundtrack.wav
"""
import subprocess
import sys
import wave

import numpy as np

SR = 44100
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(7)


def load_mp3(path):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", "1",
                          "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).copy()


def add(track, clip, at, gain=1.0):
    i = int(at * SR)
    j = min(N, i + len(clip))
    if j > i:
        track[i:j] += clip[: j - i] * gain


def env(n, attack=0.005, release=0.05):
    e = np.ones(n)
    a, r = int(attack * SR), int(release * SR)
    if a:
        e[:a] = np.linspace(0, 1, a)
    if r:
        e[-r:] *= np.linspace(1, 0, r)
    return e


def tone(freq, dur, kind="sine"):
    t = np.arange(int(dur * SR)) / SR
    if kind == "saw":
        return 2 * ((t * freq) % 1) - 1
    return np.sin(2 * np.pi * freq * t)


def tick(strong=False):
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * (2400 if strong else 1800) * t) + rng.normal(0, 0.3, n)) * np.exp(-t * 180)
    return s * 0.5


def heartbeat():
    def thump(f):
        n = int(0.18 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * f * t * (1 - t * 2)) * np.exp(-t * 22)
    out = np.zeros(int(0.6 * SR))
    a = thump(55)
    out[: len(a)] += a
    b = thump(48) * 0.75
    k = int(0.22 * SR)
    out[k:k + len(b)] += b
    return out


def boom(dur=1.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 45 * t * (1 - t * 0.2)) * np.exp(-t * 3)
    s += rng.normal(0, 1, n) * np.exp(-t * 9) * 0.6
    return s


def whoosh(dur=0.5):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    # crude low-pass that sweeps open then closed
    out = np.zeros(n)
    y = 0.0
    for i in range(n):
        a = 0.02 + 0.25 * np.sin(np.pi * i / n)
        y += a * (noise[i] - y)
        out[i] = y
    return out * np.sin(np.pi * np.arange(n) / n) * 1.2


def horn(dur=1.4):
    s = tone(330, dur, "saw") * 0.5 + tone(415, dur, "saw") * 0.5
    return s * env(len(s), 0.02, 0.1) * 0.35


def glitch(dur=0.6):
    n = int(dur * SR)
    s = np.sign(np.sin(2 * np.pi * np.repeat(rng.uniform(200, 2000, n // 900 + 1), 900)[:n]
                       * np.arange(n) / SR))
    return s * 0.25 * env(n, 0.01, 0.05)


def pad(f_list, dur, vol):
    t = np.arange(int(dur * SR)) / SR
    s = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate(f_list)) / len(f_list)
    s *= 1 + 0.15 * np.sin(2 * np.pi * 0.2 * t)
    return s * env(len(s), 1.5, 1.5) * vol


def piano(freq, dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.4 * np.sin(4 * np.pi * freq * t) + 0.15 * np.sin(6 * np.pi * freq * t))
    return s * np.exp(-t * 2.2) * env(len(s), 0.004, 0.2)


def main(vo_path, out):
    vo = load_mp3(vo_path)
    music = np.zeros(N)
    sfx = np.zeros(N)
    voice = np.zeros(N)

    # voiceover placement
    for ln in open("segments.txt"):
        if ln.startswith("#") or not ln.strip():
            continue
        a, b, at = map(float, ln.split())
        seg = vo[int(a * SR): int((b + 0.12) * SR)]
        add(voice, seg * env(len(seg), 0.01, 0.06), at)

    # ambience: dark drone throughout, warm chords during the love section
    add(music, pad([55, 82.4, 110], 18.5, 0.10), 0)
    for i, ch in enumerate([[261.6, 329.6, 392], [220, 261.6, 329.6], [174.6, 220, 261.6], [196, 246.9, 293.7]] * 2):
        for j, f in enumerate(ch):
            add(music, piano(f, 2.0), 18.3 + i * 2.1 + j * 0.12, 0.09)
    add(music, pad([110, 164.8, 220], 17.5, 0.05), 18.0)
    add(music, pad([49, 73.4, 98], 7.0, 0.13), 35.0)
    add(music, pad([46.2, 69.3, 92.5], 5.5, 0.12), 50.0)
    add(music, pad([41.2, 61.7, 82.4], 5.0, 0.12), 55.0)

    # cold open: ticks 3-2-1, flat beep at zero
    for k in range(3):
        add(sfx, tick(True), 0.05 + k * 0.87, 0.9)
    add(sfx, tone(1000, 0.7) * env(int(0.7 * SR), 0.005, 0.2) * 0.18, 2.6)
    # scene transitions
    for at in (2.85, 9.8, 17.8, 27.8, 34.8, 41.8):
        add(sfx, whoosh(0.5), at, 0.5)
    # "!" stingers
    add(sfx, tone(880, 0.12) * env(int(0.12 * SR)) * 0.15, 12.3)
    add(sfx, glitch(0.6), 37.4)
    # ticking from the timer change until the push, accelerating heartbeat
    for k in range(13):
        add(sfx, tick(k % 2 == 0), 37.0 + k * 0.97, 0.7)
    for k, at in enumerate(np.cumsum([0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.42, 0.4, 0.38, 0.36]) + 38.0):
        if at < 48.6:
            add(sfx, heartbeat(), at, 0.9)
    add(sfx, horn(1.6), 46.4)
    add(sfx, boom(), 48.95, 0.9)
    # own timer reveal + end loop beep
    add(sfx, tone(1000, 1.2) * env(int(1.2 * SR), 0.005, 0.4) * 0.12, 51.7)
    for k in range(3):
        add(sfx, tick(True), 58.6 + k * 0.45, 0.7)

    mix = voice * 1.0 + music * 0.9 + sfx * 0.8
    # gentle ducking of music/sfx under voice
    mix = np.tanh(mix * 1.1) * 0.92
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(out, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
