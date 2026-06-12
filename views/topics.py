import random

import streamlit as st

from lib import data, sounds, ui

st.title("🎁 お題ガチャ")
st.caption("山手線ゲーム・ジェスチャー・トークのお題をランダムに出します。")

category = st.radio("カテゴリ", list(data.TOPIC_SETS.keys()), horizontal=True)

ss = st.session_state
ss.setdefault("topic_history", {})
history = ss.topic_history.setdefault(category, [])

topic_area = st.empty()

col1, col2 = st.columns([3, 1])
if col1.button("🎰 ガチャを回す!", type="primary", use_container_width=True):
    pool = [t for t in data.TOPIC_SETS[category] if t not in history]
    if not pool:
        history.clear()
        pool = list(data.TOPIC_SETS[category])
    topic = random.choice(pool)
    history.append(topic)
    ui.play_mp3("tada.mp3")

if col2.button("🗑️ 履歴クリア", use_container_width=True):
    history.clear()

with topic_area:
    if history:
        st.markdown(f"<div class='word-card'>{history[-1]}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='placeholder-dash'>—</div>", unsafe_allow_html=True)

st.divider()
st.markdown("##### ⏱️ タイマー(必要なら)")
seconds = st.select_slider("制限時間", [15, 30, 45, 60, 90, 120], value=30)
ui.countdown(seconds, f"topic{seconds}", sounds.beep_b64())

if len(history) > 1:
    with st.expander("これまでに出たお題"):
        st.write("、".join(history[:-1]))
