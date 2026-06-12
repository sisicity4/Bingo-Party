"""全ゲーム共通のUI部品(CSS・効果音再生・タイマー)。"""

import base64
import pathlib

import streamlit as st
import streamlit.components.v1 as components

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"

_CSS = """
<style>
.stApp {
  background: radial-gradient(circle at 50% 20%, #1c1c2e 0%, #0b0b14 70%);
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
