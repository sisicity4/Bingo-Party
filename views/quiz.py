import streamlit as st

from lib import sounds, ui

st.title("⭕ クイズ司会ボード")
st.caption("司会者用の効果音ボタンとチーム得点ボード。早押しクイズや〇✕クイズの進行に。")

ss = st.session_state
if "quiz_teams" not in ss:
    ss.quiz_teams = [
        {"name": "チームA", "score": 0},
        {"name": "チームB", "score": 0},
    ]

# --- 効果音 & 判定表示 ---
sound_area = st.empty()
flash_area = st.empty()

col1, col2, col3 = st.columns(3)
if col1.button("⭕ ピンポン!", type="primary", use_container_width=True):
    ui.play_wav_b64(sounds.pinpon_b64(), sound_area)
    flash_area.markdown(
        "<div class='flash-mark' style='color:#ff5555;'>⭕</div>", unsafe_allow_html=True
    )
    ui.confetti(25)
if col2.button("❌ ブッブー", use_container_width=True):
    ui.play_wav_b64(sounds.boo_b64(), sound_area)
    flash_area.markdown(
        "<div class='flash-mark' style='color:#5599ff;'>❌</div>", unsafe_allow_html=True
    )
if col3.button("🥁 シンキングタイム", use_container_width=True):
    ui.play_mp3("drum-roll.mp3", sound_area)
    flash_area.markdown(
        "<div class='flash-mark'>🤔</div>", unsafe_allow_html=True
    )

st.divider()

# --- 得点ボード ---
st.markdown("##### 🏆 得点ボード")
cols = st.columns(len(ss.quiz_teams))
for i, (col, team) in enumerate(zip(cols, ss.quiz_teams)):
    with col:
        team["name"] = st.text_input(
            "チーム名", team["name"], key=f"quiz_name_{i}", label_visibility="collapsed"
        )
        st.markdown(f"<div class='team-score'>{team['score']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='team-name'>{team['name']}</div>", unsafe_allow_html=True)
        b1, b2, b3 = st.columns(3)
        if b1.button("+1", key=f"quiz_p1_{i}", use_container_width=True):
            team["score"] += 1
            st.rerun()
        if b2.button("+3", key=f"quiz_p3_{i}", use_container_width=True):
            team["score"] += 3
            st.rerun()
        if b3.button("-1", key=f"quiz_m1_{i}", use_container_width=True):
            team["score"] -= 1
            st.rerun()

st.write("")
c1, c2, c3 = st.columns(3)
if c1.button("➕ チームを追加", use_container_width=True, disabled=len(ss.quiz_teams) >= 6):
    ss.quiz_teams.append({"name": f"チーム{chr(ord('A') + len(ss.quiz_teams))}", "score": 0})
    st.rerun()
if c2.button("➖ チームを減らす", use_container_width=True, disabled=len(ss.quiz_teams) <= 2):
    ss.quiz_teams.pop()
    st.rerun()
if c3.button("0️⃣ 全スコアリセット", use_container_width=True):
    for team in ss.quiz_teams:
        team["score"] = 0
    st.rerun()
