"""全ゲーム共通のUI部品(CSS・効果音再生・タイマー・演出)。"""

import base64
import html
import pathlib
import random
import time

import streamlit as st
import streamlit.components.v1 as components

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"


def esc(text):
    """ユーザー入力をHTML(unsafe_allow_html)に埋め込む前にエスケープする。"""
    return html.escape(str(text))

_CSS = """
<style>
.stApp {
  background: linear-gradient(120deg, #0b0b14 0%, #1a1030 30%, #0e2438 60%, #2a0f2f 85%, #0b0b14 100%);
  background-size: 300% 300%;
  animation: bgshift 25s ease-in-out infinite alternate;
}
@keyframes bgshift {
  0% { background-position: 0% 0%; }
  100% { background-position: 100% 100%; }
}
/* きらめく星 */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    radial-gradient(2px 2px at 12% 25%, rgba(255,255,255,.7), transparent 60%),
    radial-gradient(2px 2px at 75% 15%, rgba(255,215,0,.8), transparent 60%),
    radial-gradient(1.5px 1.5px at 40% 70%, rgba(255,255,255,.5), transparent 60%),
    radial-gradient(2px 2px at 90% 60%, rgba(120,220,255,.7), transparent 60%),
    radial-gradient(1.5px 1.5px at 25% 88%, rgba(255,150,220,.6), transparent 60%),
    radial-gradient(2px 2px at 60% 40%, rgba(255,255,255,.4), transparent 60%);
  animation: twinkle 5s ease-in-out infinite alternate;
}
@keyframes twinkle {
  0% { opacity: 0.3; }
  100% { opacity: 1; }
}
/* ネオン風タイトル */
h1 {
  background: linear-gradient(90deg, #ffd700, #fff6c0, #ffd700, #ff9de2);
  background-size: 200% auto;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 14px rgba(255, 215, 0, 0.45));
  animation: shine 6s linear infinite;
}
@keyframes shine {
  to { background-position: 200% center; }
}
/* ボタンを大きくゴージャスに */
.stButton > button {
  border-radius: 14px;
  font-weight: 800;
  transition: transform 0.1s ease, box-shadow 0.2s ease;
}
.stButton > button:hover {
  transform: scale(1.03);
}
.stButton > button[data-testid="stBaseButton-primary"],
.stButton > button[kind="primary"] {
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.35);
}
/* スロット演出用 */
.slot {
  font-size: clamp(80px, 16vw, 200px);
  font-weight: 900;
  text-align: center;
  color: #9aa;
  line-height: 1.1;
  filter: blur(1.5px);
  opacity: 0.85;
}
/* 紙吹雪 */
.confetti-box {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 9999;
}
.confetti-box i {
  position: absolute;
  top: -5vh;
  display: block;
  animation: confetti-fall linear forwards;
}
@keyframes confetti-fall {
  0% { transform: translateY(0) rotate(0deg); opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(115vh) rotate(var(--rot)); opacity: 0; }
}
.mega {
  font-size: clamp(80px, 16vw, 200px);
  font-weight: 900;
  text-align: center;
  color: #FFD700;
  text-shadow: 0 0 30px rgba(255, 255, 0, 0.6);
  animation: pop 0.6s ease-out;
  line-height: 1.1;
}
.mega-sub {
  font-size: clamp(28px, 5vw, 64px);
  font-weight: 700;
  text-align: center;
  color: #fff;
  animation: pop 0.5s ease-out;
}
.placeholder-dash {
  font-size: 80px;
  text-align: center;
  color: #555;
}
@keyframes pop {
  0% { transform: scale(0.2); opacity: 0; }
  70% { transform: scale(1.15); opacity: 1; }
  100% { transform: scale(1); }
}
.flash-mark {
  font-size: clamp(120px, 24vw, 280px);
  text-align: center;
  font-weight: 900;
  animation: pop 0.4s ease-out;
  line-height: 1.1;
}
.bgrid {
  display: grid;
  grid-template-columns: 48px repeat(15, 1fr);
  gap: 4px;
  margin-top: 12px;
}
.bgrid .rowhead {
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 22px; color: #FFD700;
}
.bgrid .cell {
  aspect-ratio: 1;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  font-weight: 700;
  font-size: clamp(11px, 1.4vw, 20px);
  background: #1d1d2b;
  color: #555;
  border: 1px solid #2a2a3a;
}
.bgrid .cell.drawn {
  background: #3d3d10;
  color: #FFD700;
  border-color: #FFD700;
}
.bgrid .cell.current {
  background: #FFD700;
  color: #111;
  box-shadow: 0 0 16px rgba(255, 215, 0, 0.8);
  animation: pop 0.5s ease-out;
}
.word-card {
  background: #16161f;
  border: 2px solid #FFD700;
  border-radius: 16px;
  padding: 36px 16px;
  text-align: center;
  font-size: clamp(36px, 7vw, 90px);
  font-weight: 900;
  color: #FFD700;
  animation: pop 0.4s ease-out;
}
.team-score {
  text-align: center;
  font-size: clamp(48px, 9vw, 120px);
  font-weight: 900;
  color: #FFD700;
  line-height: 1.1;
}
.team-name {
  text-align: center;
  font-size: clamp(18px, 2.5vw, 32px);
  font-weight: 700;
  color: #fff;
}
</style>
"""


def inject_css():
    st.markdown(_CSS, unsafe_allow_html=True)


@st.cache_data
def _file_b64(name):
    return base64.b64encode((ASSETS / name).read_bytes()).decode()


def _audio_tag(b64, mime):
    # 同じ音を連続再生してもReactに同一要素と見なされないよう、毎回nonceを変える
    n = st.session_state.get("_audio_nonce", 0) + 1
    st.session_state["_audio_nonce"] = n
    return (
        f"<div data-nonce='{n}'>"
        f"<audio autoplay><source src='data:{mime};base64,{b64}'></audio></div>"
    )


def play_wav_b64(b64, container=None):
    target = container if container is not None else st
    target.markdown(_audio_tag(b64, "audio/wav"), unsafe_allow_html=True)


def play_mp3(name, container=None):
    target = container if container is not None else st
    target.markdown(_audio_tag(_file_b64(name), "audio/mp3"), unsafe_allow_html=True)


_CONFETTI_COLORS = [
    "#ffd700", "#ff5e8e", "#54d6ff", "#7dff8a", "#ffa54f", "#c89bff", "#fff",
]


def confetti(count=60):
    """CSSだけの紙吹雪。呼んだ回(rerun)にだけ降る。"""
    pieces = []
    for _ in range(count):
        color = random.choice(_CONFETTI_COLORS)
        left = random.uniform(0, 100)
        w = random.uniform(7, 13)
        h = random.uniform(10, 18)
        dur = random.uniform(2.2, 4.0)
        delay = random.uniform(0, 0.8)
        rot = random.randint(360, 1080)
        radius = "50%" if random.random() < 0.3 else "2px"
        pieces.append(
            f"<i style='left:{left:.1f}%;width:{w:.0f}px;height:{h:.0f}px;"
            f"background:{color};border-radius:{radius};--rot:{rot}deg;"
            f"animation-duration:{dur:.2f}s;animation-delay:{delay:.2f}s;'></i>"
        )
    n = st.session_state.get("_confetti_nonce", 0) + 1
    st.session_state["_confetti_nonce"] = n
    st.markdown(
        f"<div class='confetti-box' data-nonce='{n}'>{''.join(pieces)}</div>",
        unsafe_allow_html=True,
    )


def slot_roll(placeholder, items, css_class="slot"):
    """スロットマシン風に候補を高速表示して徐々に減速する(約1.9秒)。

    items はそのままHTMLとして描画されるので、ユーザー入力を渡す場合は
    呼び出し側で ui.esc() 済みの文字列を渡すこと。
    """
    delays = [0.06, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.16, 0.18, 0.20, 0.23, 0.26]
    for d in delays:
        pick = random.choice(items)
        placeholder.markdown(
            f"<div class='{css_class}'>{pick}</div>", unsafe_allow_html=True
        )
        time.sleep(d)


def countdown(seconds, key, end_sound_b64):
    """iframe内で完結するカウントダウンタイマー(開始/リセットボタン付き)。

    iframe内のクリックを起点にするのでブラウザの自動再生制限に引っかからない。
    """
    components.html(
        f"""
<div style="font-family: sans-serif; text-align: center; color: #fff;">
  <div id="t{key}" style="font-size: 110px; font-weight: 900; color: #FFD700;
       font-variant-numeric: tabular-nums; line-height: 1.1;"></div>
  <button id="b{key}" style="font-size: 24px; padding: 10px 40px; margin-top: 8px;
       border-radius: 10px; border: 2px solid #FFD700; background: #16161f;
       color: #FFD700; cursor: pointer; font-weight: 700;">▶ スタート</button>
</div>
<audio id="a{key}" src="data:audio/wav;base64,{end_sound_b64}"></audio>
<script>
  const total = {int(seconds)};
  const disp = document.getElementById("t{key}");
  const btn = document.getElementById("b{key}");
  const snd = document.getElementById("a{key}");
  let left = total, timer = null;
  function fmt(s) {{
    const m = Math.floor(s / 60), r = s % 60;
    return m + ":" + String(r).padStart(2, "0");
  }}
  function render() {{
    disp.textContent = fmt(left);
    disp.style.color = left <= 10 ? "#ff5555" : "#FFD700";
  }}
  render();
  btn.addEventListener("click", () => {{
    if (timer) {{
      clearInterval(timer); timer = null; left = total;
      btn.textContent = "▶ スタート"; render();
      return;
    }}
    btn.textContent = "↺ リセット";
    timer = setInterval(() => {{
      left -= 1; render();
      if (left <= 0) {{
        clearInterval(timer); timer = null;
        disp.textContent = "終了!";
        btn.textContent = "▶ スタート"; left = total;
        snd.currentTime = 0; snd.play();
      }}
    }}, 1000);
  }});
</script>
""",
        height=240,
    )
