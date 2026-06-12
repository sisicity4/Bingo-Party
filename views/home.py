import streamlit as st

st.title("🎉 Party Games")
st.markdown("##### 大画面に映してみんなで遊ぶパーティーゲーム集")

GAMES = [
    ("views/bingo.py", "🎱", "ビンゴ", "定番のビンゴ抽選。1〜75の数字をドラムロール付きで発表。", "何人でも"),
    ("views/roulette.py", "🎯", "ルーレット抽選", "名前を入れて当たり抽選・順番決め・チーム分け。", "何人でも"),
    ("views/wordwolf.py", "🐺", "ワードウルフ", "少数派(ウルフ)のお題を当てる会話ゲーム。", "3〜10人"),
    ("views/topics.py", "🎁", "お題ガチャ", "山手線ゲーム・ジェスチャー・トークテーマのお題をランダム表示。", "3人〜"),
    ("views/bomb.py", "💣", "爆弾ゲーム", "いつ爆発するかわからない時限爆弾。持っていた人の負け!", "3人〜"),
    ("views/quiz.py", "⭕", "クイズ司会ボード", "ピンポン・ブー効果音とチーム得点ボードでクイズ大会。", "何人でも"),
]

cols = st.columns(3)
for i, (page, icon, name, desc, players) in enumerate(GAMES):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"### {icon} {name}")
            st.markdown(desc)
            st.caption(f"👥 {players}")
            st.page_link(page, label=f"{name}で遊ぶ", icon="▶️")

st.divider()
st.caption("左のサイドバーからもゲームを切り替えられます。音が出るのでボリュームに注意!")
