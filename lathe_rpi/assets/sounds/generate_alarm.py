#!/usr/bin/env python3
"""
Generate the limit-switch alarm sound (limit_alarm.wav).

Creates a short, urgent two-tone "warble" alarm as a 16-bit mono WAV using only
the Python standard library – no downloads or third-party audio packages, so it
is fully reproducible and license-free.

Run:  python generate_alarm.py
"""

import math
import os
import struct
import wave

SAMPLE_RATE = 44_100
AMPLITUDE = 0.55           # 0.0 – 1.0 (headroom to avoid clipping)
SEGMENT_S = 0.16           # length of each alternating tone
CYCLES = 5                 # number of (high, low) pairs -> ~1.6 s total
TONE_HIGH = 988.0          # Hz (B5)
TONE_LOW = 740.0           # Hz (F#5)
FADE_S = 0.006             # per-segment attack/release to avoid clicks

OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "limit_alarm.wav")


def _tone(freq: float, duration_s: float) -> list[float]:
    n = int(SAMPLE_RATE * duration_s)
    fade = max(1, int(SAMPLE_RATE * FADE_S))
    out = []
    for i in range(n):
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = max(0.0, (n - i) / fade)
        out.append(AMPLITUDE * env * math.sin(2.0 * math.pi * freq * (i / SAMPLE_RATE)))
    return out


def main() -> None:
    samples: list[float] = []
    for _ in range(CYCLES):
        samples += _tone(TONE_HIGH, SEGMENT_S)
        samples += _tone(TONE_LOW, SEGMENT_S)

    with wave.open(OUT_PATH, "w") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)          # 16-bit
        wav.setframerate(SAMPLE_RATE)
        frames = b"".join(
            struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
        )
        wav.writeframes(frames)

    print(f"Wrote {OUT_PATH} ({len(samples) / SAMPLE_RATE:.2f} s, {len(samples)} samples)")


if __name__ == "__main__":
    main()
