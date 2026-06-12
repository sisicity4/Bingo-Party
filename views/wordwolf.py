import random

import streamlit as st

from lib import data, sounds, ui

st.title("🐺 ワードウルフ")

ss = st.session_state
if "ww_phase" not in ss:
    ss.ww_phase = "setup"


def reset():
    for k in list(ss.keys()):
        if k.startswith("ww_"):
            del ss[k]
    ss.ww_phase = "setup"


# --- 設定 ---
if ss.ww_phase == "setup":
    st.caption("少数派(ウルフ)だけ違うお題が配られます。会話してウルフを見つけ出そう!")
    names_text = st.text_area(
        "参加者の名前(1行に1人・3人以上)",
        key="ww_names_text",
        height=160,
        placeholder="たろう\nはなこ\nけんた",
    )
    names = [n.strip() for n in names_text.splitlines() if n.strip()]

    col1, col2 = st.columns(2)
    max_wolves = max(1, (len(names) - 1) // 2) if len(names) >= 3 else 1
    wolves_n = col1.selectbox("ウルフの人数", list(range(1, max_wolves + 1)))
    minutes = col2.selectbox("議論時間(分)", [1, 2, 3, 4, 5], index=2)

    if st.button("🎮 ゲーム開始", type="primary", use_container_width=True, disabled=len(names) < 3):
        majority, minority = random.choice(data.WORD_PAIRS)
        if random.random() < 0.5:
            majority, minority = minority, majority
        wolf_idx = set(random.sample(range(len(names)), wolves_n))
        ss.ww_players = names
        ss.ww_words = [minority if i in wolf_idx else majority for i in range(len(names))]
        ss.ww_wolves = wolf_idx
        ss.ww_minutes = minutes
        ss.ww_reveal_idx = 0
        ss.ww_showing = False
        ss.ww_phase = "reveal"
        st.rerun()
    if len(names) < 3:
        st.info("3人以上の名前を入れると開始できます。")

# --- お題確認(端末を回す) ---
elif ss.ww_phase == "reveal":
    i = ss.ww_reveal_idx
    name = ss.ww_players[i]
    st.progress((i + (1 if ss.ww_showing else 0)) / len(ss.ww_players))
    st.markdown(f"<div class='mega-sub'>{name} さんの番</div>", unsafe_allow_html=True)
    st.caption("⚠️ 他の人は画面を見ないでください(端末を回すか、順番に前に来てね)")

    if not ss.ww_showing:
        if st.button("👀 自分のお題を見る", type="primary", use_container_width=True):
            ss.ww_showing = True
            st.rerun()
    else:
        st.markdown(f"<div class='word-card'>{ss.ww_words[i]}</div>", unsafe_allow_html=True)
        label = "✅ 覚えた!次の人へ" if i + 1 < len(ss.ww_players) else "✅ 覚えた!議論スタートへ"
        if st.button(label, type="primary", use_container_width=True):
            ss.ww_showing = False
            if i + 1 < len(ss.ww_players):
                ss.ww_reveal_idx += 1
            else:
                ss.ww_phase = "discuss"
            st.rerun()
    st.button("🔄 最初からやり直す", on_click=reset)

# --- 議論 ---
elif ss.ww_phase == "discuss":
    st.markdown("<div class='mega-sub'>🗣️ 議論タイム!</div>", unsafe_allow_html=True)
    st.caption("自分のお題を直接言わずに話して、ウルフ(少数派)を探そう。")
    ui.countdown(ss.ww_minutes * 60, "ww", sounds.beep_b64())
    if st.button("🗳️ 投票へ進む", type="primary", use_container_width=True):
        ss.ww_phase = "vote"
        st.rerun()
    st.button("🔄 最初からやり直す", on_click=reset)

# --- 投票 ---
elif ss.ww_phase == "vote":
    st.markdown("<div class='mega-sub'>🗳️ ウルフだと思う人は?</div>", unsafe_allow_html=True)
    # 同名プレイヤーがいても正しく判定できるよう、名前ではなくインデックスで持つ
    players = ss.ww_players
    voted_idx = st.radio(
        "せーので指差し投票!一番票を集めた人を選んでください",
        range(len(players)),
        format_func=lambda i: players[i],
    )
    if st.button("🎬 結果発表!", type="primary", use_container_width=True):
        ss.ww_voted_idx = voted_idx
        ss.ww_phase = "result"
        st.rerun()
    st.button("🔄 最初からやり直す", on_click=reset)

# --- 結果 ---
elif ss.ww_phase == "result":
    wolves = [ss.ww_players[i] for i in sorted(ss.ww_wolves)]
    voted_is_wolf = ss.ww_voted_idx in ss.ww_wolves
    ui.play_mp3("tada.mp3")
    ui.confetti(80)

    if voted_is_wolf:
        st.markdown("<div class='mega'>市民の勝ち!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='mega'>ウルフの勝ち!</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='mega-sub'>🐺 ウルフは {'、'.join(wolves)} でした</div>",
        unsafe_allow_html=True,
    )
    majority_word = next(
        w for i, w in enumerate(ss.ww_words) if i not in ss.ww_wolves
    )
    minority_word = ss.ww_words[sorted(ss.ww_wolves)[0]]
    col1, col2 = st.columns(2)
    col1.metric("市民のお題", majority_word)
    col2.metric("ウルフのお題", minority_word)

    st.button("🔁 もう一回遊ぶ", type="primary", use_container_width=True, on_click=reset)
