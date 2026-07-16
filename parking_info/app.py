import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="👑 Princess Parking",
    page_icon="👑",
    layout="wide"
)

# ------------------ CSS ------------------
st.markdown("""
<style>
.stApp{
    background: linear-gradient(to bottom,#fff6fb,#ffeaf5);
}

h1,h2,h3{
    color:#d63384;
    text-align:center;
}

section[data-testid="stSidebar"]{
    background:#fff0f7;
}

div.stButton>button{
    background:#ff7eb6;
    color:white;
    border-radius:12px;
    border:none;
}

div.stButton>button:hover{
    background:#ff4f9c;
}
</style>
""", unsafe_allow_html=True)

st.title("👑 Princess Parking")
st.markdown("### 💖 공주님을 위한 서울 공영주차장 안내 💖")

uploaded = st.file_uploader(
    "📁 서울시 공영주차장 CSV 업로드",
    type="csv"
)

if uploaded is None:
    st.info("CSV 파일을 업로드해주세요.")
    st.stop()

# ------------------ CSV 읽기 ------------------
try:
    df = pd.read_csv(uploaded, encoding="cp949")
except:
    df = pd.read_csv(uploaded, encoding="utf-8")

# ------------------ 자치구 추출 ------------------
if "주소" in df.columns:
    df["자치구"] = df["주소"].astype(str).str.extract(r"([가-힣]+구)")
else:
    df["자치구"] = ""

# ------------------ 숫자 변환 ------------------
num_cols = [
    "기본 주차 요금",
    "기본 주차 시간(분 단위)",
    "추가 단위 요금",
    "추가 단위 시간(분 단위)",
    "위도",
    "경도"
]

for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ------------------ Sidebar ------------------
st.sidebar.title("👑 공주님의 조건")

gu = st.sidebar.selectbox(
    "자치구",
    ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
)

ptype = st.sidebar.selectbox(
    "주차장 종류",
    ["전체"] + sorted(df["주차장 종류명"].dropna().unique().tolist())
)

pay = st.sidebar.selectbox(
    "무료/유료",
    ["전체"] + sorted(df["유무료구분명"].dropna().unique().tolist())
)

hour = st.sidebar.slider(
    "예상 주차시간(시간)",
    1,
    24,
    2
)

# ------------------ 필터 ------------------
result = df.copy()

if gu != "전체":
    result = result[result["자치구"] == gu]

if ptype != "전체":
    result = result[result["주차장 종류명"] == ptype]

if pay != "전체":
    result = result[result["유무료구분명"] == pay]

minutes = hour * 60

# ------------------ 요금 계산 ------------------
def calc_fee(row):

    if row["유무료구분명"] == "무료":
        return 0

    basic_fee = row["기본 주차 요금"]
    basic_time = row["기본 주차 시간(분 단위)"]
    add_fee = row["추가 단위 요금"]
    add_time = row["추가 단위 시간(분 단위)"]

    if basic_fee <= 0:
        return 0

    if minutes <= basic_time:
        return basic_fee

    # 추가시간이 0이면 기본요금만 반환
    if add_time <= 0 or add_fee <= 0:
        return basic_fee

    extra = np.ceil((minutes - basic_time) / add_time)

    return basic_fee + extra * add_fee

result["예상요금"] = result.apply(calc_fee, axis=1)

# ------------------ 추천 ------------------
st.markdown("---")

if len(result):

    best = result.sort_values("예상요금").iloc[0]

    st.success(
        f"""
👑 **오늘의 공주님 추천 주차장**

🏰 **{best['주차장명']}**

📍 {best['주소']}

🚗 {best['주차장 종류명']}

💰 예상요금 **{int(best['예상요금']):,}원**
"""
    )

    st.balloons()

else:

    st.warning("조건에 맞는 주차장이 없습니다.")

# ------------------ 지도 ------------------
st.subheader("🗺️ 공주님의 마차를 위한 주차장 위치")

map_df = result[
    (result["위도"] != 0) &
    (result["경도"] != 0)
]

if len(map_df):

    st.map(
        map_df.rename(
            columns={
                "위도":"lat",
                "경도":"lon"
            }
        )[["lat","lon"]]
    )

else:

    st.warning("표시할 위치 정보가 없습니다.")

# ------------------ 결과표 ------------------
st.subheader("📋 주차장 목록")

show_cols = [
    "주차장명",
    "자치구",
    "주소",
    "주차장 종류명",
    "유무료구분명",
    "기본 주차 요금",
    "예상요금"
]

show_cols = [c for c in show_cols if c in result.columns]

st.dataframe(
    result[show_cols].sort_values("예상요금"),
    use_container_width=True
)

st.caption("👑 Princess Parking · 서울 공영주차장 정보")
