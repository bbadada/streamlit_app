import re
from collections import Counter
from urllib.parse import parse_qs, urlparse

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from googleapiclient.discovery import build
from wordcloud import WordCloud

# -----------------------------
# API
# -----------------------------
youtube = build(
    "youtube",
    "v3",
    developerKey=st.secrets["YOUTUBE_API_KEY"]
)

# -----------------------------
# 영상 ID 추출
# -----------------------------
def get_video_id(url):
    p = urlparse(url)

    if p.hostname == "youtu.be":
        return p.path[1:]

    if p.hostname and "youtube.com" in p.hostname:
        if p.path == "/watch":
            return parse_qs(p.query).get("v", [None])[0]

        if p.path.startswith("/shorts/"):
            return p.path.split("/")[2]

        if p.path.startswith("/embed/"):
            return p.path.split("/")[2]

    return None


st.title("📺 유튜브 댓글 분석기")

url = st.text_input("유튜브 링크")

if st.button("분석"):

    if not url:
        st.warning("유튜브 링크를 입력하세요.")
        st.stop()

    video_id = get_video_id(url)

    if video_id is None:
        st.error("올바른 유튜브 링크가 아닙니다.")
        st.stop()

    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )

        response = request.execute()

        for item in response["items"]:
            comments.append(
                item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            )

    except Exception as e:
        st.error("댓글을 가져올 수 없습니다.")
        st.exception(e)
        st.stop()

    if len(comments) == 0:
        st.warning("댓글이 없습니다.")
        st.stop()

    df = pd.DataFrame({"댓글": comments})

    st.success(f"댓글 {len(df)}개 수집 완료")

    st.dataframe(df)

    # -----------------------------
    # 댓글 길이
    # -----------------------------
    st.subheader("댓글 길이")

    fig, ax = plt.subplots()

    ax.hist(df["댓글"].str.len(), bins=20)

    st.pyplot(fig)

    # -----------------------------
    # 단어 분석
    # -----------------------------
    text = " ".join(comments)

    words = re.findall(r"[가-힣]{2,}", text)

    counter = Counter(words)

    top20 = pd.DataFrame(
        counter.most_common(20),
        columns=["단어", "빈도"]
    )

    st.subheader("많이 나온 단어")

    st.dataframe(top20)

    # -----------------------------
    # 워드클라우드
    # -----------------------------
    try:
        wc = WordCloud(
            font_path="NanumGothic.ttf",
            width=900,
            height=500,
            background_color="white"
        ).generate_from_frequencies(counter)

        fig2, ax2 = plt.subplots(figsize=(10,5))

        ax2.imshow(wc)

        ax2.axis("off")

        st.subheader("워드클라우드")

        st.pyplot(fig2)

    except:
        st.warning("NanumGothic.ttf 파일을 프로젝트에 넣어주세요.")
