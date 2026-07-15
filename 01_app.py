import streamlit as st
import requests
import random

st.set_page_config(
    page_title="오늘 뭐 먹지?",
    page_icon="🍽️",
    layout="wide"
)

# -----------------------------
# OpenWeather API Key
# -----------------------------
API_KEY = st.secrets["OPENWEATHER_API_KEY"]

# -----------------------------
# 음식 데이터
# -----------------------------

foods = {
    "cold": [
        {
            "name":"삼계탕",
            "image":"https://images.unsplash.com/photo-1547592180-85f173990554?w=800",
            "calorie":"918 kcal",
            "nutrition":{
                "탄수화물":"25g",
                "단백질":"65g",
                "지방":"38g"
            }
        },
        {
            "name":"김치찌개",
            "image":"https://images.unsplash.com/photo-1604908177522-40229e6c87d6?w=800",
            "calorie":"420 kcal",
            "nutrition":{
                "탄수화물":"18g",
                "단백질":"32g",
                "지방":"22g"
            }
        }
    ],

    "hot":[
        {
            "name":"냉면",
            "image":"https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800",
            "calorie":"560 kcal",
            "nutrition":{
                "탄수화물":"92g",
                "단백질":"20g",
                "지방":"8g"
            }
        },
        {
            "name":"빙수",
            "image":"https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=800",
            "calorie":"490 kcal",
            "nutrition":{
                "탄수화물":"88g",
                "단백질":"9g",
                "지방":"10g"
            }
        }
    ],

    "rain":[
        {
            "name":"파전",
            "image":"https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800",
            "calorie":"530 kcal",
            "nutrition":{
                "탄수화물":"48g",
                "단백질":"18g",
                "지방":"29g"
            }
        }
    ],

    "snow":[
        {
            "name":"어묵탕",
            "image":"https://images.unsplash.com/photo-1544025162-d76694265947?w=800",
            "calorie":"340 kcal",
            "nutrition":{
                "탄수화물":"22g",
                "단백질":"25g",
                "지방":"15g"
            }
        }
    ],

    "default":[
        {
            "name":"비빔밥",
            "image":"https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800",
            "calorie":"620 kcal",
            "nutrition":{
                "탄수화물":"78g",
                "단백질":"24g",
                "지방":"18g"
            }
        }
    ]
}


# -----------------------------
# 날씨 가져오기
# -----------------------------

def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()


# -----------------------------
# 음식 추천
# -----------------------------

def recommend(weather,temp):

    if "Rain" in weather:
        return random.choice(foods["rain"])

    elif "Snow" in weather:
        return random.choice(foods["snow"])

    elif temp >= 28:
        return random.choice(foods["hot"])

    elif temp <= 10:
        return random.choice(foods["cold"])

    else:
        return random.choice(foods["default"])



# -----------------------------
# UI
# -----------------------------

st.title("🍽️ 오늘 날씨에 맞는 음식 추천")

st.write("현재 날씨를 분석하여 음식을 추천합니다.")

city = st.text_input(
    "도시를 입력하세요",
    value="Seoul"
)

if st.button("추천받기"):

    weather_data = get_weather(city)

    if weather_data is None:
        st.error("도시를 찾을 수 없습니다.")
        st.stop()

    temp = weather_data["main"]["temp"]

    weather = weather_data["weather"][0]["main"]

    description = weather_data["weather"][0]["description"]

    food = recommend(weather,temp)

    st.success(f"현재 {city}의 기온은 {temp:.1f}℃ 입니다.")

    st.info(f"날씨 : {description}")

    col1,col2 = st.columns([1,1])

    with col1:

        st.image(food["image"],use_container_width=True)

    with col2:

        st.subheader(food["name"])

        st.metric(
            "칼로리",
            food["calorie"]
        )

        st.write("### 영양성분")

        st.write(f"**탄수화물** : {food['nutrition']['탄수화물']}")
        st.write(f"**단백질** : {food['nutrition']['단백질']}")
        st.write(f"**지방** : {food['nutrition']['지방']}")
