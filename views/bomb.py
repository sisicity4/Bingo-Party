import random

import streamlit as st
import streamlit.components.v1 as components

from lib import data, sounds

st.title("💣 爆弾ゲーム")
st.caption("お題に沿って順番に答えながら爆弾(スマホでも何でもOK)を回そう。爆発した時に持っていた人の負け!")

col1, col2 = st.columns(2)
min_s = col1.slider("最短時間(秒)", 10, 60, 20)
max_s = col2.slider("最長時間(秒)", min_s + 5, 120, max(60, min_s + 10))

use_topic = st.toggle("お題も一緒に表示する(山手線ゲーム形式)", value=True)

if st.button("💣 爆弾をセットする", type="primary", use_container_width=True):
    st.session_state.bomb_duration = random.randint(min_s, max_s)
    st.session_state.bomb_topic = random.choice(data.YAMANOTE_TOPICS) if use_topic else None
    st.session_state.bomb_round = st.session_state.get("bomb_round", 0) + 1

if "bomb_duration" in st.session_state:
    if st.session_state.bomb_topic:
        st.markdown(
            f"<div class='word-card'>お題:{st.session_state.bomb_topic}</div>",
            unsafe_allow_html=True,
        )

    # 起爆ボタンは iframe 内に置く(クリック起点なので音の自動再生制限を回避できる)
    # data-round を埋め込み、時間とお題が前回と同じでもHTMLを変えて iframe を確実に再マウントする
    components.html(
        f"""
<div id="stage" data-round="{st.session_state.bomb_round}" style="font-family: sans-serif; text-align: center; color: #fff; padding-top: 8px;">
  <button id="ignite" style="font-size: 28px; padding: 14px 50px; border-radius: 12px;
       border: 2px solid #ff5555; background: #16161f; color: #ff5555;
       cursor: pointer; font-weight: 900;">🔥 点火!</button>
  <div id="bomb" style="display: none; font-size: 130px; line-height: 1.2;">💣</div>
  <div id="msg" style="font-size: 28px; font-weight: 700; margin-top: 4px;"></div>
</div>
<audio id="boom" src="data:audio/wav;base64,{sounds.explosion_b64()}"></audio>
<style>
  @keyframes shake {{
    0% {{ transform: translate(0, 0) rotate(0deg); }}
    25% {{ transform: translate(-6px, 2px) rotate(-4deg); }}
    50% {{ transform: translate(5px, -3px) rotate(3deg); }}
    75% {{ transform: translate(-4px, -2px) rotate(-2deg); }}
    100% {{ transform: translate(0, 0) rotate(0deg); }}
  }}
  .ticking {{ animation: shake 0.4s infinite; }}
</style>
<script>
  const duration = {st.session_state.bomb_duration} * 1000;  // 秒数はプレイヤーには秘密
  const btn = document.getElementById("ignite");
  const bomb = document.getElementById("bomb");
  const msg = document.getElementById("msg");
  const boom = document.getElementById("boom");
  let ctx = null, tickTimer = null;

  function tick() {{
    // WebAudioでカチカチ音
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.frequency.value = 1100;
    g.gain.setValueAtTime(0.25, ctx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
    o.connect(g).connect(ctx.destination);
    o.start();
    o.stop(ctx.currentTime + 0.06);
  }}

  btn.addEventListener("click", () => {{
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    btn.style.display = "none";
    bomb.style.display = "block";
    bomb.classList.add("ticking");
    msg.textContent = "順番に答えて爆弾を回せ!";

    let interval = 800;
    function scheduleTick() {{
      tick();
      tickTimer = setTimeout(scheduleTick, interval);
    }}
    scheduleTick();
    // 終盤ほどカチカチを速くして煽る
    setTimeout(() => {{ interval = 400; }}, duration * 0.6);
    setTimeout(() => {{ interval = 180; }}, duration * 0.85);

    setTimeout(() => {{
      clearTimeout(tickTimer);
      bomb.classList.remove("ticking");
      bomb.textContent = "💥";
      bomb.style.fontSize = "170px";
      msg.textContent = "ドカーン!!持ってた人の負け!";
      msg.style.color = "#ff5555";
      boom.currentTime = 0;
      boom.play();
      document.body.style.background = "rgba(255, 60, 60, 0.25)";
    }}, duration);
  }});
</script>
""",
        height=360,
    )
    st.caption("「点火!」を押したらスタート。爆発までの時間は毎回ランダムです。もう一度遊ぶには「爆弾をセットする」を押してね。")
