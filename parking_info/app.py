import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="서울 주차장 정보", layout="wide")

st.title("🚗 서울 주차장 정보 검색")

st.write("CSV 파일(cp949)을 업로드하세요.")

uploaded_file = st.file_uploader(
    "주차장 CSV 업로드",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file, encoding="cp949")
    except:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

    st.success("데이터 업로드 완료!")

    st.subheader("데이터 미리보기")
    st.dataframe(df)

    # -------------------------------
    # 컬럼명
    # -------------------------------

    # 아래 컬럼명은 CSV에 맞게 수정 가능
    # 예시
    # 자치구
    # 주차장명
    # 위도
    # 경도
    # 기본요금
    # 종류
    # 무료여부

    district_col = "자치구"
    name_col = "주차장명"
    lat_col = "위도"
    lon_col = "경도"
    fee_col = "기본요금"
    type_col = "주차장종류"
    free_col = "무료여부"

    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구",
        ["전체"] + sorted(df[district_col].dropna().unique().tolist())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df[type_col].dropna().unique().tolist())
    )

    fee_type = st.sidebar.selectbox(
        "무료/유료",
        ["전체", "무료", "유료"]
    )

    hour = st.sidebar.number_input(
        "예상 주차시간(시간)",
        min_value=1,
        value=1
    )

    result = df.copy()

    if gu != "전체":
        result = result[result[district_col] == gu]

    if parking_type != "전체":
        result = result[result[type_col] == parking_type]

    if fee_type != "전체":
        result = result[result[free_col] == fee_type]

    # -------------------------------
    # 예상요금 계산
    # -------------------------------

    def calc_fee(row):
        if row[free_col] == "무료":
            return 0
        else:
            return row[fee_col] * hour

    result["예상주차요금"] = result.apply(calc_fee, axis=1)

    st.subheader("검색 결과")

    st.dataframe(result)

    # -------------------------------
    # 가장 저렴한 주차장
    # -------------------------------

    if len(result) > 0:

        cheapest = result.sort_values("예상주차요금").iloc[0]

        st.success("💰 가장 저렴한 주차장")

        col1, col2 = st.columns(2)

        with col1:

            st.write("###", cheapest[name_col])

            st.write("자치구 :", cheapest[district_col])
            st.write("종류 :", cheapest[type_col])
            st.write("무료여부 :", cheapest[free_col])
            st.write("예상요금 :", f"{int(cheapest['예상주차요금']):,} 원")

        with col2:

            map_df = pd.DataFrame({
                "lat":[cheapest[lat_col]],
                "lon":[cheapest[lon_col]]
            })

            st.map(map_df)

    # -------------------------------
    # 전체 지도
    # -------------------------------

    st.subheader("주차장 위치")

    map_df = result.rename(
        columns={
            lat_col:"lat",
            lon_col:"lon"
        }
    )

    st.map(map_df[["lat","lon"]])

else:

    st.info("CSV 파일을 업로드하세요.")
