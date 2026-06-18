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
@import url('https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@500;700;800;900&display=swap');

:root {
  --pink:   #ff2d6b;
  --pink-d: #d10049;
  --yellow: #ffcf2d;
  --yellow-d:#e0a500;
  --blue:   #2db6ff;
  --blue-d: #0085d6;
  --green:  #38d66b;
  --purple: #9b6bff;
  --ink:    #33304a;
}

/* 丸ゴシックで全体をポップに */
html, body, .stApp, [class*="css"], button, input, textarea, select {
  font-family: 'M PLUS Rounded 1c', 'Hiragino Maru Gothic ProN', sans-serif !important;
}

/* 明るいパステルの動く背景 */
.stApp {
  background: linear-gradient(125deg, #fff3c4 0%, #ffd9ec 28%, #cfefff 55%, #d8ffe4 78%, #fff3c4 100%);
  background-size: 320% 320%;
  animation: bgshift 24s ease-in-out infinite alternate;
}
@keyframes bgshift {
  0% { background-position: 0% 0%; }
  100% { background-position: 100% 100%; }
}
/* ふわふわ浮かぶ水玉(お祭り感) */
.stApp::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background-image:
    radial-gradient(10px 10px at 12% 22%, rgba(255,45,107,.16), transparent 70%),
    radial-gradient(14px 14px at 78% 16%, rgba(45,182,255,.16), transparent 70%),
    radial-gradient(9px 9px at 40% 72%, rgba(255,207,45,.20), transparent 70%),
    radial-gradient(12px 12px at 90% 62%, rgba(56,214,107,.16), transparent 70%),
    radial-gradient(10px 10px at 24% 90%, rgba(155,107,255,.16), transparent 70%),
    radial-gradient(8px 8px at 62% 42%, rgba(255,45,107,.12), transparent 70%);
  animation: floaty 9s ease-in-out infinite alternate;
}
@keyframes floaty {
  0% { transform: translateY(0); opacity: .75; }
  100% { transform: translateY(-14px); opacity: 1; }
}
/* コンテンツは背景より前面に */
.main .block-container { position: relative; z-index: 1; }

/* ポップで立体感のあるタイトル */
h1 {
  color: var(--pink);
  font-weight: 900 !important;
  -webkit-text-stroke: 2px #fff;
  paint-order: stroke fill;
  text-shadow: 0 4px 0 rgba(255,255,255,.9), 0 7px 10px rgba(0,0,0,.12);
  letter-spacing: .5px;
}
h2, h3, h4, h5 { color: var(--ink); font-weight: 800 !important; }

/* ぷにっと立体ピル型ボタン(押すと沈む) */
.stButton > button {
  border: none;
  border-radius: 999px;
  font-weight: 800;
  min-height: 50px;
  color: #5a3d00;
  background: linear-gradient(180deg, #ffe27a, var(--yellow));
  box-shadow: 0 5px 0 var(--yellow-d), 0 9px 16px rgba(0,0,0,.14);
  transition: transform .08s ease, box-shadow .08s ease, filter .12s ease;
}
.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.04); }
.stButton > button:active {
  transform: translateY(4px);
  box-shadow: 0 1px 0 var(--yellow-d), 0 3px 8px rgba(0,0,0,.14);
}
.stButton > button:disabled {
  background: #e7e3d6; color: #9a988c; box-shadow: 0 4px 0 #c9c5b8; filter: none;
}
/* 主役ボタンは元気なピンク */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
  color: #fff;
  background: linear-gradient(180deg, #ff6b96, var(--pink));
  box-shadow: 0 5px 0 var(--pink-d), 0 9px 16px rgba(0,0,0,.18);
}
.stButton > button[kind="primary"]:active,
.stButton > button[data-testid="stBaseButton-primary"]:active {
  box-shadow: 0 1px 0 var(--pink-d), 0 3px 8px rgba(0,0,0,.18);
}

/* 入力欄・カードを白く丸く */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
  border-radius: 14px !important;
  border: 2px solid #ffd0e0 !important;
}
[data-testid="stExpander"] { border-radius: 16px; }
hr { border-color: rgba(0,0,0,.08); }

/* スロット演出 */
.slot {
  font-size: clamp(80px, 16vw, 200px);
  font-weight: 900;
  text-align: center;
  color: #b9b4d0;
  line-height: 1.1;
  filter: blur(1.2px);
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
/* 主役の大きな数字・結果(白フチ付きで明るい背景でも映える) */
.mega {
  font-size: clamp(80px, 16vw, 200px);
  font-weight: 900;
  text-align: center;
  color: var(--pink);
  -webkit-text-stroke: 5px #fff;
  paint-order: stroke fill;
  text-shadow: 0 7px 0 rgba(0,0,0,.12), 0 12px 22px rgba(0,0,0,.18);
  animation: pop 0.6s cubic-bezier(.2,1.4,.4,1);
  line-height: 1.1;
}
.mega-sub {
  font-size: clamp(28px, 5vw, 64px);
  font-weight: 800;
  text-align: center;
  color: var(--ink);
  animation: pop 0.5s cubic-bezier(.2,1.4,.4,1);
}
.placeholder-dash {
  font-size: 80px;
  text-align: center;
  color: #c6c1d8;
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
  animation: pop 0.4s cubic-bezier(.2,1.4,.4,1);
  line-height: 1.1;
}
/* ビンゴ盤(白マス+カラフルハイライト) */
.bgrid {
  display: grid;
  grid-template-columns: 48px repeat(15, 1fr);
  gap: 4px;
  margin-top: 12px;
}
.bgrid .rowhead {
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 22px; color: var(--blue-d);
}
.bgrid .cell {
  aspect-ratio: 1;
  display: flex; align-items: center; justify-content: center;
  border-radius: 8px;
  font-weight: 800;
  font-size: clamp(11px, 1.4vw, 20px);
  background: #ffffff;
  color: #b9b4cc;
  border: 2px solid #ececf4;
}
.bgrid .cell.drawn {
  background: #fff2bf;
  color: var(--yellow-d);
  border-color: var(--yellow);
}
.bgrid .cell.current {
  background: var(--pink);
  color: #fff;
  border-color: #fff;
  box-shadow: 0 0 0 3px var(--pink), 0 6px 14px rgba(255,45,107,.5);
  animation: pop 0.5s cubic-bezier(.2,1.4,.4,1);
}
/* お題・ワードのカード */
.word-card {
  background: #ffffff;
  border: 5px solid var(--yellow);
  border-radius: 24px;
  padding: 36px 16px;
  text-align: center;
  font-size: clamp(36px, 7vw, 90px);
  font-weight: 900;
  color: var(--pink);
  box-shadow: 0 10px 0 rgba(0,0,0,.06), 0 16px 30px rgba(0,0,0,.12);
  animation: pop 0.4s cubic-bezier(.2,1.4,.4,1);
}
.team-score {
  text-align: center;
  font-size: clamp(48px, 9vw, 120px);
  font-weight: 900;
  color: var(--pink);
  -webkit-text-stroke: 3px #fff;
  paint-order: stroke fill;
  line-height: 1.1;
}
.team-name {
  text-align: center;
  font-size: clamp(18px, 2.5vw, 32px);
  font-weight: 800;
  color: var(--ink);
}
/* 長い名前・お題でも横スクロールせず折り返す */
.mega, .mega-sub, .slot, .word-card, .team-name {
  overflow-wrap: anywhere;
  word-break: break-word;
}
/* スマホ(狭い画面)向け調整: 文字を画面内に収め、タップ領域を広げる */
@media (max-width: 640px) {
  .mega { font-size: clamp(46px, 16vw, 120px); -webkit-text-stroke-width: 3px; }
  .mega-sub { font-size: clamp(22px, 6vw, 40px); }
  .slot { font-size: clamp(46px, 16vw, 120px); }
  .flash-mark { font-size: clamp(96px, 30vw, 170px); }
  .placeholder-dash { font-size: 56px; }
  .word-card { padding: 24px 10px; font-size: clamp(28px, 9vw, 60px); border-width: 4px; }
  /* ビンゴ盤: 15列だとセルが極小になるので、同じDOMのまま列方向に流して
     B/I/N/G/O を縦5列(各列=行頭+15マス)に転置し、セルを大きく保つ */
  .bgrid {
    grid-template-columns: repeat(5, 1fr);
    grid-template-rows: repeat(16, auto);
    grid-auto-flow: column;
    gap: 3px;
  }
  .bgrid .rowhead { font-size: 16px; }
  .bgrid .cell { font-size: clamp(13px, 3.6vw, 22px); border-radius: 6px; }
  /* ボタンはさらに高め+読みやすい文字に */
  .stButton > button { min-height: 54px; font-size: 1.05rem; }
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
    iframeは隔離されページ側の@mediaが届かないため、文字・ボタンはここでvw基準の
    clamp()を使い、スマホ幅でも溢れないようにしている。
    """
    components.html(
        f"""
<div style="font-family: 'M PLUS Rounded 1c','Hiragino Maru Gothic ProN',sans-serif; text-align: center; color: #33304a;">
  <div id="t{key}" style="font-size: clamp(56px, 22vw, 110px); font-weight: 900; color: #2db6ff;
       -webkit-text-stroke: 3px #fff; paint-order: stroke fill;
       font-variant-numeric: tabular-nums; line-height: 1.1;"></div>
  <button id="b{key}" style="font-size: clamp(18px, 5vw, 24px); padding: 12px clamp(20px, 8vw, 40px); margin-top: 8px;
       border-radius: 999px; border: none; background: linear-gradient(180deg,#ff6b96,#ff2d6b);
       box-shadow: 0 5px 0 #d10049; color: #fff; cursor: pointer; font-weight: 800; max-width: 90%;">▶ スタート</button>
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
    disp.style.color = left <= 10 ? "#ff2d6b" : "#2db6ff";
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
