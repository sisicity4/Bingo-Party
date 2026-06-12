import random
import time

import streamlit as st

from lib import ui

st.title("🎱 ビンゴ!")

if "bingo_numbers" not in st.session_state:
    st.session_state.bingo_numbers = list(range(1, 76))
    random.shuffle(st.session_state.bingo_numbers)
    st.session_state.bingo_drawn = []
    st.session_state.bingo_current = None


def letter_of(n):
    return "BINGO"[(n - 1) // 15]


col1, col2 = st.columns(2)
draw_clicked = col1.button(
    "🎲 次の数字を引く",
    use_container_width=True,
    type="primary",
    disabled=not st.session_state.bingo_numbers,
)
if col2.button("🔄 リセット", use_container_width=True):
    st.session_state.bingo_numbers = list(range(1, 76))
    random.shuffle(st.session_state.bingo_numbers)
    st.session_state.bingo_drawn = []
    st.session_state.bingo_current = None
    st.rerun()

number_area = st.empty()
sound_area = st.empty()

if draw_clicked and st.session_state.bingo_numbers:
    # ドラムロールを鳴らして2秒ためる(プレースホルダを消すと音も止まる)
    ui.play_mp3("drum-roll.mp3", sound_area)
    with number_area:
        st.markdown("<div class='placeholder-dash'>🥁 抽選中...</div>", unsafe_allow_html=True)
    time.sleep(2)
    sound_area.empty()

    num = st.session_state.bingo_numbers.pop()
    st.session_state.bingo_drawn.append(num)
    st.session_state.bingo_current = num
    ui.play_mp3("tada.mp3", sound_area)

cur = st.session_state.bingo_current
with number_area:
    if cur is None:
        st.markdown("<div class='placeholder-dash'>—</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            f"<div class='mega'><span style='font-size:0.45em;color:#fff;'>{letter_of(cur)}</span> {cur}</div>",
            unsafe_allow_html=True,
        )

st.caption(f"抽選回数:{len(st.session_state.bingo_drawn)} / 75 回")

# --- 75マスの履歴ボード ---
drawn = set(st.session_state.bingo_drawn)
cells = []
for row, letter in enumerate("BINGO"):
    cells.append(f"<div class='rowhead'>{letter}</div>")
    for n in range(row * 15 + 1, row * 15 + 16):
        cls = "cell"
        if n == cur:
            cls += " current"
        elif n in drawn:
            cls += " drawn"
        cells.append(f"<div class='{cls}'>{n}</div>")
st.markdown(f"<div class='bgrid'>{''.join(cells)}</div>", unsafe_allow_html=True)

if st.session_state.bingo_drawn:
    with st.expander("出た順に見る"):
        st.write(" → ".join(f"**{letter_of(n)}-{n}**" for n in st.session_state.bingo_drawn))
