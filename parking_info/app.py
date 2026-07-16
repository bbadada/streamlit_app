import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="서울 공영주차장", layout="wide")

st.title("🚗 서울 공영주차장 검색")

uploaded = st.file_uploader("CSV 업로드", type="csv")

if uploaded is None:
    st.info("서울시 공영주차장 CSV를 업로드하세요.")
    st.stop()

# -----------------------------
# CSV 읽기
# -----------------------------
try:
    df = pd.read_csv(uploaded, encoding="cp949")
except:
    df = pd.read_csv(uploaded, encoding="utf-8")

# -----------------------------
# 주소에서 자치구 추출
# -----------------------------
df["자치구"] = df["주소"].astype(str).str.extract(r"([가-힣]+구)")

# -----------------------------
# 숫자형 변환
# -----------------------------
num_cols = [
    "기본 주차 요금",
    "기본 주차 시간(분 단위)",
    "추가 단위 요금",
    "추가 단위 시간(분 단위)",
    "위도",
    "경도"
]

for c in num_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("검색")

gu = st.sidebar.selectbox(
    "자치구",
    ["전체"] + sorted(df["자치구"].dropna().unique())
)

ptype = st.sidebar.selectbox(
    "주차장 종류",
    ["전체"] + sorted(df["주차장 종류명"].dropna().unique())
)

pay = st.sidebar.selectbox(
    "무료/유료",
    ["전체"] + sorted(df["유무료구분명"].dropna().unique())
)

hour = st.sidebar.number_input(
    "예상 주차시간(시간)",
    min_value=1,
    value=1
)

# -----------------------------
# 필터
# -----------------------------
result = df.copy()

if gu != "전체":
    result = result[result["자치구"] == gu]

if ptype != "전체":
    result = result[result["주차장 종류명"] == ptype]

if pay != "전체":
    result = result[result["유무료구분명"] == pay]

# -----------------------------
# 예상요금 계산
# -----------------------------
minutes = hour * 60

def calc_fee(row):

    if row["유무료구분명"] == "무료":
        return 0

    basic_fee = row["기본 주차 요금"]
    basic_time = row["기본 주차 시간(분 단위)"]

    add_fee = row["추가 단위 요금"]
    add_time = row["추가 단위 시간(분 단위)"]

    if pd.isna(basic_fee):
        return np.nan

    if pd.isna(add_fee) or pd.isna(add_time):
        return basic_fee

    if minutes <= basic_time:
        return basic_fee

    extra = np.ceil((minutes-basic_time)/add_time)

    return basic_fee + extra*add_fee

result["예상요금"] = result.apply(calc_fee, axis=1)

# -----------------------------
# 가장 저렴한 주차장
# -----------------------------
st.subheader("💰 가장 저렴한 주차장")

cheap = result.dropna(subset=["예상요금"])

if len(cheap):

    best = cheap.sort_values("예상요금").iloc[0]

    st.success(
        f"""
주차장명 : {best['주차장명']}

주소 : {best['주소']}

종류 : {best['주차장 종류명']}

유무료 : {best['유무료구분명']}

예상요금 : {int(best['예상요금']):,}원
"""
    )

else:
    st.warning("조건에 맞는 주차장이 없습니다.")

# -----------------------------
# 결과
# -----------------------------
st.subheader("검색 결과")

show = [
    "주차장명",
    "자치구",
    "주소",
    "주차장 종류명",
    "유무료구분명",
    "기본 주차 요금",
    "예상요금"
]

st.dataframe(result[show], use_container_width=True)

# -----------------------------
# 지도
# -----------------------------
st.subheader("📍 주차장 위치")

map_df = result.dropna(subset=["위도", "경도"])

if len(map_df):
    st.map(
        map_df.rename(
            columns={
                "위도": "lat",
                "경도": "lon"
            }
        )[["lat", "lon"]]
    )
else:
    st.warning("위도/경도 정보가 없습니다.")
