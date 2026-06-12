"""効果音をPython標準ライブラリだけで合成して base64 WAV にする。

mp3アセットを増やさずにピンポン・ブー・ビープ等を用意するためのモジュール。
"""

import base64
import io
import math
import random
import struct
import wave

import streamlit as st

RATE = 22050


def _to_wav_b64(samples):
    frames = b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, s)) * 32767)) for s in samples
    )
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(frames)
    return base64.b64encode(buf.getvalue()).decode()


def _tone(freq, dur, vol=0.6, shape="sine"):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        t = i / RATE
        v = math.sin(2 * math.pi * freq * t)
        if shape == "square":
            v = 1.0 if v >= 0 else -1.0
        # クリックノイズ防止のアタック/リリース
        env = min(1.0, i / 200, (n - i) / 400)
        out.append(v * vol * env)
    return out


def _silence(dur):
    return [0.0] * int(RATE * dur)


@st.cache_data
def pinpon_b64():
    """正解音「ピンポンピンポン」"""
    unit = _tone(880, 0.12, 0.5) + _silence(0.03) + _tone(1318, 0.30, 0.5)
    return _to_wav_b64(unit + _silence(0.06) + unit)


@st.cache_data
def boo_b64():
    """不正解音「ブッブー」"""
    s = (
        _tone(196, 0.16, 0.35, "square")
        + _silence(0.05)
        + _tone(147, 0.45, 0.35, "square")
    )
    return _to_wav_b64(s)


@st.cache_data
def beep_b64():
    """タイマー終了音「ピピピッ」"""
    s = []
    for _ in range(3):
        s += _tone(1760, 0.12, 0.45) + _silence(0.07)
    return _to_wav_b64(s)


@st.cache_data
def explosion_b64():
    """爆発音(減衰ホワイトノイズ)"""
    rnd = random.Random(0)
    n = int(RATE * 1.2)
    out = []
    for i in range(n):
        decay = (1 - i / n) ** 2
        out.append(rnd.uniform(-1, 1) * decay * 0.9)
    return _to_wav_b64(out)
