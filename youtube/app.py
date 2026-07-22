import streamlit as st
import pandas as pd
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
from collections import Counter
from konlpy.tag import Okt
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# API
api_key = st.secrets["YOUTUBE_API_KEY"]
youtube = build("youtube", "v3", developerKey=api_key)

st.title("📺 유튜브 댓글 분석기")

url = st.text_input("유튜브 링크")

if st.button("분석"):

    video_id = parse_qs(urlparse(url).query)["v"][0]

    comments = []

    req = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100
    )

    res = req.execute()

    for item in res["items"]:
        comments.append(
            item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
        )

    df = pd.DataFrame({"댓글": comments})

    st.write("댓글 수:", len(df))
    st.dataframe(df)

    # 댓글 길이
    st.subheader("댓글 길이")

    fig, ax = plt.subplots()
    ax.hist(df["댓글"].str.len())
    st.pyplot(fig)

    # 단어 분석
    okt = Okt()

    words = []

    for c in comments:
        words += okt.nouns(c)

    count = Counter(words)

    st.subheader("TOP20 단어")
    st.dataframe(
        pd.DataFrame(
            count.most_common(20),
            columns=["단어", "빈도"]
        )
    )

    # 워드클라우드
    wc = WordCloud(
        font_path="NanumGothic.ttf",
        width=800,
        height=400,
        background_color="white"
    ).generate_from_frequencies(count)

    fig2, ax2 = plt.subplots(figsize=(10,5))
    ax2.imshow(wc)
    ax2.axis("off")

    st.subheader("한글 워드클라우드")
    st.pyplot(fig2)
