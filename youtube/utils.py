import re
import io
import pandas as pd
from urllib.parse import urlparse, parse_qs


# -----------------------------
# 유튜브 URL → Video ID 추출
# -----------------------------
def extract_video_id(url: str):
    """
    지원 URL

    https://www.youtube.com/watch?v=xxxx
    https://youtu.be/xxxx
    https://youtube.com/shorts/xxxx
    """

    try:
        parsed = urlparse(url)

        if parsed.hostname in [
            "youtu.be"
        ]:
            return parsed.path[1:]

        if parsed.hostname in [
            "www.youtube.com",
            "youtube.com",
            "m.youtube.com"
        ]:

            if parsed.path == "/watch":
                return parse_qs(parsed.query)["v"][0]

            if parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[2]

            if parsed.path.startswith("/embed/"):
                return parsed.path.split("/")[2]

    except:
        return None

    return None


# -----------------------------
# 숫자 포맷
# -----------------------------
def format_number(num):

    try:
        num = int(num)

        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"

        if num >= 1000:
            return f"{num/1000:.1f}K"

        return str(num)

    except:
        return "0"


# -----------------------------
# 댓글 정리
# -----------------------------
def clean_text(text):

    if text is None:
        return ""

    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"www\S+", "", text)

    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\r", " ", text)
    text = re.sub(r"\t", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# -----------------------------
# CSV 다운로드
# -----------------------------
def dataframe_to_csv(df):

    return df.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")


# -----------------------------
# Excel 다운로드
# -----------------------------
def dataframe_to_excel(df):

    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Comments"
        )

    return output.getvalue()


# -----------------------------
# 댓글 길이
# -----------------------------
def comment_length(text):

    if not isinstance(text, str):
        return 0

    return len(text)


# -----------------------------
# 빈 문자열 제거
# -----------------------------
def remove_empty(df):

    return df[
        df["comment"].astype(str).str.strip() != ""
    ]


# -----------------------------
# 중복 제거
# -----------------------------
def remove_duplicates(df):

    return df.drop_duplicates(
        subset="comment"
    )


# -----------------------------
# 날짜 변환
# -----------------------------
def convert_datetime(df):

    df["publishedAt"] = pd.to_datetime(
        df["publishedAt"],
        errors="coerce"
    )

    return df


# -----------------------------
# 시간 컬럼 생성
# -----------------------------
def add_hour_column(df):

    df["hour"] = df["publishedAt"].dt.hour

    return df


# -----------------------------
# 길이 컬럼 생성
# -----------------------------
def add_length_column(df):

    df["length"] = df["comment"].apply(
        comment_length
    )

    return df
