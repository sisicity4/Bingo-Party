import streamlit as st

from lib import ui

st.set_page_config(
    page_title="Party Games",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="expanded",
)

ui.inject_css()

pages = st.navigation(
    {
        "": [st.Page("views/home.py", title="ホーム", icon="🏠", default=True)],
        "ゲーム": [
            st.Page("views/bingo.py", title="ビンゴ", icon="🎱"),
            st.Page("views/roulette.py", title="ルーレット抽選", icon="🎯"),
            st.Page("views/wordwolf.py", title="ワードウルフ", icon="🐺"),
            st.Page("views/topics.py", title="お題ガチャ", icon="🎁"),
            st.Page("views/bomb.py", title="爆弾ゲーム", icon="💣"),
            st.Page("views/quiz.py", title="クイズ司会ボード", icon="⭕"),
        ],
    }
)
pages.run()
