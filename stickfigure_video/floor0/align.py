"""Estimate per-word timings: spread each line's words over its voiced frames (weighted by length).
Usage: python3 align.py vo.mp3 segments.txt lines.txt > words.txt"""
import subprocess
import sys

import numpy as np

SR = 16000
vo = np.frombuffer(subprocess.run(["ffmpeg", "-loglevel", "error", "-i", sys.argv[1], "-f", "f32le", "-ac", "1",
                                   "-ar", str(SR), "-"], capture_output=True, check=True).stdout, dtype=np.float32)
segs = [tuple(map(float, l.split())) for l in open(sys.argv[2]) if l.strip() and not l.startswith("#")]
# optional 4th column: where the words start inside the clip (skip a laugh/breath)
lines = [l.strip() for l in open(sys.argv[3]) if l.strip()]
hop = 160  # 10 ms
for row, text in zip(segs, lines):
    a, b, at = row[:3]
    a0 = row[3] if len(row) > 3 else a
    at = at + (a0 - a)
    x = vo[int(a0 * SR): int(b * SR)]
    rms = np.array([np.sqrt(np.mean(x[i:i + 400] ** 2)) for i in range(0, max(1, len(x) - 400), hop)])
    voiced = rms > max(0.012, rms.max() * 0.12)
    times = np.nonzero(voiced)[0] * hop / SR
    words = text.split()
    wt = np.array([len(w.strip(".,?!…")) + 1.5 for w in words], float)
    cum = np.concatenate([[0], np.cumsum(wt)]) / wt.sum()
    n = len(times)
    for i, w in enumerate(words):
        s = times[min(n - 1, int(cum[i] * n))]
        e = times[min(n - 1, max(int(cum[i + 1] * n) - 1, 0))] + 0.06
        print(f"{at + s:.3f} {at + e:.3f} {w}")
    print()
