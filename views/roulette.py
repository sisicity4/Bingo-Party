import random

import streamlit as st

from lib import ui

st.title("🎯 ルーレット抽選")
st.caption("名前を入れて、当たり抽選・順番決め・チーム分けに使えます。")

names_text = st.text_area(
    "参加者の名前(1行に1人)",
    key="roulette_names",
    height=160,
    placeholder="たろう\nはなこ\nけんた",
)
names = [n.strip() for n in names_text.splitlines() if n.strip()]

mode = st.radio(
    "モード",
    ["🏆 当たり抽選", "🔢 順番決め", "👥 チーム分け"],
    horizontal=True,
)

if mode == "🏆 当たり抽選":
    max_win = max(1, len(names))
    winners_n = st.slider("当たりの人数", 1, max_win, 1) if max_win > 1 else 1
elif mode == "👥 チーム分け":
    max_teams = max(2, len(names))
    teams_n = st.slider("チーム数", 2, min(6, max_teams), 2)

sound_area = st.empty()
result_area = st.empty()

if st.button("🎲 ルーレットスタート!", type="primary", use_container_width=True, disabled=len(names) < 2):
    ui.play_mp3("drum-roll.mp3", sound_area)
    ui.slot_roll(result_area, [ui.esc(n) for n in names])
    sound_area.empty()

    if mode == "🏆 当たり抽選":
        winners = random.sample(names, min(winners_n, len(names)))
        html = "".join(f"<div class='mega'>{ui.esc(w)}</div>" for w in winners)
        st.session_state.roulette_result = html + "<div class='mega-sub'>🎉 当たり!</div>"
    elif mode == "🔢 順番決め":
        order = random.sample(names, len(names))
        rows = "".join(
            f"<div class='mega-sub'>{i + 1}. {ui.esc(n)}</div>" for i, n in enumerate(order)
        )
        st.session_state.roulette_result = rows
    else:
        shuffled = random.sample(names, len(names))
        rows = []
        for t in range(teams_n):
            members = shuffled[t::teams_n]
            rows.append(
                f"<div class='mega-sub'>チーム{chr(ord('A') + t)}:{'、'.join(ui.esc(m) for m in members)}</div>"
            )
        st.session_state.roulette_result = "".join(rows)

    # 結果がどの入力・モードのものかを記録し、入力変更時に古い結果を出さないようにする
    st.session_state.roulette_sig = (tuple(names), mode)
    ui.play_mp3("tada.mp3", sound_area)
    ui.confetti(70)

if len(names) < 2:
    st.info("2人以上の名前を入れるとスタートできます。")

# 名前やモードを変えたら、前回の結果は表示しない(古い当選者を出し続けないため)
if (
    st.session_state.get("roulette_result")
    and st.session_state.get("roulette_sig") == (tuple(names), mode)
):
    with result_area:
        st.markdown(st.session_state.roulette_result, unsafe_allow_html=True)
