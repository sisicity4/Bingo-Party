import streamlit as st
import random
import time

st.set_page_config(page_title="BINGO 抽選", layout="centered")
st.title("ビンゴ！")

# --- 初期化 ---
if "numbers" not in st.session_state:
    st.session_state.numbers = list(range(1, 76))
    random.shuffle(st.session_state.numbers)
    st.session_state.drawn = []
    st.session_state.current = None

# --- CSS ---
st.markdown(
    """
<style>
.big-number {
  font-size: 120px;
  font-weight: bold;
  text-align: center;
  color: #FFD700;
  text-shadow: 0 0 20px #ff0;
  animation: pop 0.6s ease-out;
}
@keyframes pop {
  0% { transform: scale(0.2); opacity: 0; }
  70% { transform: scale(1.2); opacity: 1; }
  100% { transform: scale(1); }
}
.stApp {
  background: radial-gradient(circle, #111 0%, #000 70%);
}
</style>
""",
    unsafe_allow_html=True,
)

# --- 現在の数字 ---
st.subheader("現在の数字")
if st.session_state.current is None:
    st.markdown(
        "<div style='font-size:64px; text-align:center;'>—</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<div class='big-number'>{st.session_state.current}</div>",
        unsafe_allow_html=True,
    )


# ドラムロール時間

def play_drumroll_2s(file):
    st.markdown(
        f"""
        <audio id="drumroll" autoplay>
            <source src="{file}" type="audio/mp3">
        </audio>
        <script>
            const audio = document.getElementById("drumroll");
            setTimeout(() => {{
                audio.pause();
                audio.currentTime = 0;
            }}, 2000);
        </script>
        """,
        unsafe_allow_html=True,
    )
# サウンドの指定
def play_sound(file):
    st.markdown(
        f"""
        <audio autoplay>
            <source src="{file}" type="audio/mp3">
        </audio>
        """,
        unsafe_allow_html=True,
    )
    
# --- 抽選処理 ---
def draw():
    if st.session_state.numbers:
        play_drumroll_2s("drum-roll.mp3")

        with st.spinner("抽選中..."):
            time.sleep(2)

        num = st.session_state.numbers.pop()
        st.session_state.drawn.append(num)
        st.session_state.current = num

        play_sound("tada.mp3")

# --- ボタン ---
col1, col2 = st.columns(2)
with col1:
    st.button("🎲 次の数字を引く", on_click=draw, use_container_width=True)
with col2:
    if st.button("🔄 リセット", use_container_width=True):
        st.session_state.numbers = list(range(1, 76))
        random.shuffle(st.session_state.numbers)
        st.session_state.drawn = []
        st.session_state.current = None

# --- 状態 ---
st.caption(f"抽選回数：{len(st.session_state.drawn)} 回")

# --- 履歴 ---
st.subheader("出た数字一覧")
if st.session_state.drawn:
    st.write(" ".join([f"**{n}**" for n in st.session_state.drawn]))
else:
    st.write("まだ出ていません")