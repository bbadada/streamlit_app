# WHERE HAVE YOU BEEN? — v0.1

사용자가 입력한 장소를 드림코어풍 3D 공간으로 변환하고, 1인칭 시점으로 탐험하는 Streamlit 웹앱입니다.

## 현재 기능

- 한국어·영어 키워드에 따라 수영장, 학교, 놀이터, 방, 들판 생성
- 파스텔 팔레트 선택
- 안개와 기괴함 조절
- WASD 이동 및 마우스 시점 조작
- 문, 전화기, 달, 구름 등 드림코어 오브젝트 배치
- Web Audio API를 이용한 저작권 없는 합성 앰비언트 사운드
- 이동 거리에 따른 메시지 이벤트

## 로컬 실행

Python 3.11 이상을 권장합니다.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

설치 및 실행:

```bash
pip install -r requirements.txt
streamlit run app.py
```

브라우저가 열리면 문장을 입력하고 `ENTER THE DREAM`을 누르세요.
3D 화면의 `CLICK TO ENTER`를 누르면 마우스가 잠기고 음악이 시작됩니다.

- 이동: `W A S D`
- 시점: 마우스
- 나가기: `ESC`

## GitHub 업로드

1. GitHub에서 새 저장소를 만듭니다.
2. 이 폴더 안의 파일을 저장소에 업로드합니다.
3. 커밋 메시지 예시: `v0.1 build first-person procedural dream world`

명령어로 올릴 경우:

```bash
git init
git add .
git commit -m "v0.1 build first-person procedural dream world"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

## Streamlit Community Cloud 배포

1. Streamlit Community Cloud에 GitHub 계정으로 로그인합니다.
2. `Create app`을 선택합니다.
3. 방금 만든 저장소를 선택합니다.
4. Branch는 `main`, Main file path는 `app.py`로 설정합니다.
5. Deploy를 누릅니다.

## 다음 개발 후보

- OpenAI API로 입력문을 구조화된 JSON으로 변환
- GLB/GLTF 3D 모델 추가
- 문을 통한 장면 전환
- 공간 음향
- 꿈 저장과 공유
- 텍스처 노이즈 및 CRT 효과
