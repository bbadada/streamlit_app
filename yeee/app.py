import base64
import json
import random
import re
from typing import Any

import streamlit as st

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


st.set_page_config(
    page_title="WHERE HAVE YOU BEEN?",
    page_icon="☁️",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(255, 208, 231, .72), transparent 32%),
            radial-gradient(circle at 88% 18%, rgba(193, 226, 255, .68), transparent 30%),
            linear-gradient(155deg, #f6dce9 0%, #dcecff 47%, #e4d8f7 100%);
    }
    .block-container {
        max-width: 920px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    h1, h2, h3, p, label, .stMarkdown {
        color: #514960;
    }
    h1 {
        font-family: Georgia, serif;
        letter-spacing: .12em;
        text-align: center;
    }
    .subtitle {
        text-align: center;
        letter-spacing: .08em;
        opacity: .72;
        margin-bottom: 2rem;
    }
    .scene-card {
        background: rgba(255,255,255,.42);
        border: 1px solid rgba(255,255,255,.8);
        border-radius: 28px;
        padding: 25px 27px;
        margin: 18px 0;
        box-shadow: 0 24px 70px rgba(82,65,110,.13);
        backdrop-filter: blur(12px);
    }
    .scene-title {
        font-family: Georgia, serif;
        letter-spacing: .08em;
        font-size: 1.45rem;
        margin-bottom: 12px;
    }
    .scene-text {
        font-size: 1.05rem;
        line-height: 1.95;
        white-space: pre-line;
    }
    .memory {
        font-size: .83rem;
        letter-spacing: .07em;
        opacity: .58;
    }
    div[data-testid="stTextArea"] textarea {
        background: rgba(255,255,255,.58);
        border: 1px solid rgba(255,255,255,.9);
        border-radius: 20px;
        color: #4d465b;
        min-height: 130px;
    }
    div.stButton > button {
        width: 100%;
        min-height: 52px;
        border-radius: 999px;
        border: 1px solid rgba(255,255,255,.95);
        background: rgba(255,255,255,.52);
        color: #554d65;
        font-weight: 700;
        transition: .2s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        background: rgba(255,255,255,.8);
        border-color: white;
    }
    img {
        border-radius: 26px;
        box-shadow: 0 24px 70px rgba(70,55,95,.18);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("WHERE HAVE YOU BEEN?")
st.markdown(
    '<div class="subtitle">A DREAMCORE PLACE THAT REMEMBERS YOUR CHOICES</div>',
    unsafe_allow_html=True,
)


def get_client() -> Any | None:
    """Return an OpenAI client when a Streamlit secret exists."""
    if OpenAI is None:
        return None
    api_key = st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def clean_json(text: str) -> dict:
    """Extract one JSON object even when the model adds code fences."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("AI 응답에서 JSON을 찾지 못했습니다.")

    return json.loads(text[start : end + 1])


def fallback_scene(seed_text: str, choice: str | None, depth: int) -> dict:
    """Free demo scene used before an API key is added."""
    seed = sum(ord(char) for char in f"{seed_text}{choice}{depth}")
    rng = random.Random(seed)

    places = [
        "물이 빠진 옥상 수영장",
        "구름 속에 반쯤 잠긴 학교 복도",
        "밤이 오지 않는 분홍빛 놀이터",
        "창문이 모두 같은 풍경을 비추는 방",
        "천장에 잔디가 자라는 지하철역",
    ]
    objects = [
        "수화기가 들린 채 놓인 전화기",
        "거꾸로 흐르는 벽시계",
        "안쪽에서 바람이 부는 문",
        "아무도 앉지 않은 작은 의자",
        "당신의 문장을 반복하는 오래된 TV",
    ]
    messages = [
        "당신은 이곳을 처음 보지만, 이곳은 당신을 알아본다.",
        "어딘가에서 방금 누른 선택지가 천천히 지워진다.",
        "뒤를 돌아보면 입구가 조금 더 멀어져 있다.",
        "스피커에서는 당신이 아직 하지 않은 말이 흘러나온다.",
    ]

    place = rng.choice(places)
    obj = rng.choice(objects)
    previous = f"당신은 ‘{choice}’를 선택했다. " if choice else ""

    return {
        "title": place,
        "description": (
            f"{previous}{place}에 서 있다. 공기는 지나치게 부드럽고, "
            f"바닥 가까이 옅은 안개가 흐른다.\n\n"
            f"가운데에는 {obj}가 있다. {rng.choice(messages)}"
        ),
        "choices": rng.sample(
            [
                "전화기를 들어 본다",
                "문 너머로 들어간다",
                "물속을 내려다본다",
                "뒤돌아보지 않고 걷는다",
                "가만히 서서 소리를 듣는다",
                "처음 온 척 행동한다",
            ],
            3,
        ),
        "image_prompt": (
            f"dreamcore scene, {place}, {obj}, soft pastel pink blue lavender, "
            "empty liminal architecture, nostalgic uncanny atmosphere, hazy light, "
            "low contrast, no people, cinematic wide composition, subtle film grain"
        ),
        "memory": rng.choice(
            [
                "낯선 장소",
                "반복되는 문",
                "들리지 않는 안내방송",
                "너무 가까운 하늘",
            ]
        ),
    }


def generate_scene(
    client: Any,
    original_prompt: str,
    choice: str | None,
    history: list[dict],
) -> dict:
    history_text = "\n".join(
        f"{index + 1}. {item['title']} → {item.get('chosen', '시작')}"
        for index, item in enumerate(history[-5:])
    )

    prompt = f"""
사용자가 입력한 꿈의 시작:
{original_prompt}

방금 선택한 행동:
{choice or "아직 없음. 첫 장면을 만든다."}

지금까지 지나온 장소와 선택:
{history_text or "없음"}

한국어로 드림코어 인터랙티브 장면을 하나 만들어라.

규칙:
- 심리학적 꿈 해석은 하지 않는다.
- 사건을 길게 설명하지 말고, 공간과 감각을 보여준다.
- 익숙하지만 불가능한 장소를 만든다.
- 파스텔 핑크, 하늘색, 라벤더, 민트 계열의 이미지가 어울려야 한다.
- 공포보다는 낯섦, 향수, 불안한 평온함을 우선한다.
- 이전 장면의 사물이나 문장을 미묘하게 다시 등장시킨다.
- 설명은 3~5문장으로 한다.
- 선택지는 서로 다른 행동 3개로 만든다.
- image_prompt는 영어로 작성하며 사람이나 글자를 포함하지 않는다.
- 반드시 아래 JSON 하나만 출력한다.

{{
  "title": "짧은 장소 이름",
  "description": "장면 묘사",
  "choices": ["선택지 1", "선택지 2", "선택지 3"],
  "image_prompt": "English image prompt",
  "memory": "이번 장면에서 남은 기억 조각"
}}
"""

    response = client.responses.create(
        model="gpt-5.6",
        reasoning={"effort": "low"},
        input=prompt,
    )
    scene = clean_json(response.output_text)

    if not isinstance(scene.get("choices"), list) or len(scene["choices"]) < 3:
        raise ValueError("선택지가 올바르게 생성되지 않았습니다.")

    scene["choices"] = scene["choices"][:3]
    return scene


def generate_image(client: Any, image_prompt: str) -> bytes:
    full_prompt = f"""
{image_prompt}

Dreamcore visual rules:
soft pastel pink, powder blue, lavender and mint;
empty liminal place; hazy diffused lighting; low contrast;
slightly blurry nostalgic digital-camera feeling;
surreal but physically coherent; no humans; no readable text;
wide cinematic composition for an interactive story interface.
"""
    result = client.images.generate(
        model="gpt-image-2",
        prompt=full_prompt,
        size="1536x1024",
        quality="medium",
    )
    return base64.b64decode(result.data[0].b64_json)


def make_demo_image(scene: dict) -> str:
    """Return an SVG data URI so demo mode still has a visual."""
    title = (
        scene["title"]
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#f5c9df"/>
          <stop offset="48%" stop-color="#cfe7f6"/>
          <stop offset="100%" stop-color="#d9cef1"/>
        </linearGradient>
        <filter id="blur"><feGaussianBlur stdDeviation="14"/></filter>
      </defs>
      <rect width="1200" height="760" fill="url(#bg)"/>
      <circle cx="900" cy="160" r="110" fill="#fff1b8" opacity=".75"/>
      <rect x="120" y="305" width="960" height="310" rx="28"
            fill="#eaf4ef" opacity=".68"/>
      <rect x="470" y="230" width="250" height="385" rx="12"
            fill="#f2b8d5" opacity=".77"/>
      <rect x="515" y="275" width="160" height="340" rx="7"
            fill="#b9caed" opacity=".86"/>
      <ellipse cx="600" cy="645" rx="480" ry="65"
               fill="#ffffff" opacity=".26" filter="url(#blur)"/>
      <text x="600" y="110" text-anchor="middle"
            font-family="Georgia, serif" font-size="34"
            letter-spacing="7" fill="#ffffff" opacity=".82">{title}</text>
    </svg>
    """
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def reset_world() -> None:
    for key in ["started", "original_prompt", "scene", "history", "image"]:
        st.session_state.pop(key, None)


client = get_client()
ai_mode = client is not None

with st.sidebar:
    st.subheader("MODE")
    if ai_mode:
        st.success("AI MODE")
        st.caption("텍스트와 이미지가 OpenAI API로 생성됩니다.")
    else:
        st.info("DEMO MODE")
        st.caption("API 키 없이 미리 준비된 방식으로 작동합니다.")

    st.divider()
    if st.button("처음부터 다시 시작", use_container_width=True):
        reset_world()
        st.rerun()

if not st.session_state.get("started"):
    st.markdown(
        """
        <div class="scene-card">
          <div class="scene-title">어젯밤, 어디에 있었나요?</div>
          <div class="scene-text">
          장소, 색, 사물, 들렸던 소리를 자유롭게 적어주세요.
          완전한 문장이 아니어도 됩니다.
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    original_prompt = st.text_area(
        "꿈의 시작",
        placeholder="예: 구름 위에 있는 텅 빈 수영장. 물속에는 분홍색 문이 있고 멀리서 전화벨이 들린다.",
        label_visibility="collapsed",
    )

    if not ai_mode:
        st.caption(
            "현재는 데모 모드입니다. 배포 후 Streamlit Secrets에 API 키를 넣으면 실제 AI 생성 모드가 켜집니다."
        )

    if st.button("ENTER THE DREAM", use_container_width=True, type="primary"):
        if not original_prompt.strip():
            st.warning("장소를 한 문장 이상 적어주세요.")
        else:
            st.session_state.started = True
            st.session_state.original_prompt = original_prompt.strip()
            st.session_state.history = []

            with st.spinner("장소가 당신을 기억하는 중..."):
                try:
                    if ai_mode:
                        scene = generate_scene(
                            client,
                            st.session_state.original_prompt,
                            None,
                            [],
                        )
                        image = generate_image(client, scene["image_prompt"])
                    else:
                        scene = fallback_scene(
                            st.session_state.original_prompt,
                            None,
                            0,
                        )
                        image = make_demo_image(scene)

                    st.session_state.scene = scene
                    st.session_state.image = image
                    st.rerun()
                except Exception as exc:
                    st.error(f"첫 장면을 만들지 못했습니다: {exc}")

else:
    scene = st.session_state.scene
    image = st.session_state.image

    st.image(image, use_container_width=True)

    st.markdown(
        f"""
        <div class="scene-card">
          <div class="scene-title">{scene["title"]}</div>
          <div class="scene-text">{scene["description"]}</div>
          <br>
          <div class="memory">MEMORY FRAGMENT — {scene["memory"]}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        f"지나온 장소: {len(st.session_state.history) + 1}"
    )

    cols = st.columns(3)
    selected_choice = None

    for index, choice in enumerate(scene["choices"]):
        with cols[index]:
            if st.button(
                choice,
                key=f"choice_{len(st.session_state.history)}_{index}",
                use_container_width=True,
            ):
                selected_choice = choice

    if selected_choice:
        st.session_state.history.append(
            {
                "title": scene["title"],
                "chosen": selected_choice,
                "memory": scene["memory"],
            }
        )

        with st.spinner("당신이 보지 않는 동안 장소가 바뀌고 있습니다..."):
            try:
                if ai_mode:
                    next_scene = generate_scene(
                        client,
                        st.session_state.original_prompt,
                        selected_choice,
                        st.session_state.history,
                    )
                    next_image = generate_image(
                        client,
                        next_scene["image_prompt"],
                    )
                else:
                    next_scene = fallback_scene(
                        st.session_state.original_prompt,
                        selected_choice,
                        len(st.session_state.history),
                    )
                    next_image = make_demo_image(next_scene)

                st.session_state.scene = next_scene
                st.session_state.image = next_image
                st.rerun()
            except Exception as exc:
                st.session_state.history.pop()
                st.error(f"다음 장면을 만들지 못했습니다: {exc}")

    with st.expander("지나온 기억"):
        if not st.session_state.history:
            st.write("아직 남은 기억이 없습니다.")
        else:
            for index, item in enumerate(st.session_state.history, start=1):
                st.markdown(
                    f"**{index}. {item['title']}**  \n"
                    f"선택: {item['chosen']}  \n"
                    f"기억: {item['memory']}"
                )
