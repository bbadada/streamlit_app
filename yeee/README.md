# WHERE HAVE YOU BEEN?

사용자가 입력한 장소를 드림코어 세계로 바꾸고, 세 개의 선택지를 따라 장면을 이동하는 Streamlit 인터랙티브 웹앱입니다.

## 별도 설치 없이 실행하기

### 1. GitHub 저장소 만들기

GitHub 웹사이트에서 새 저장소를 만들고 다음 두 파일을 추가합니다.

- `app.py`
- `requirements.txt`

이 폴더에 들어 있는 같은 이름의 파일 내용을 각각 붙여 넣습니다.

### 2. Streamlit Community Cloud에 배포하기

1. Streamlit Community Cloud에 GitHub 계정으로 로그인합니다.
2. `Create app`을 누릅니다.
3. 만든 GitHub 저장소를 선택합니다.
4. Branch는 `main`, Main file path는 `app.py`로 설정합니다.
5. Deploy를 누릅니다.

API 키가 없으면 데모 모드로 실행됩니다.

## 실제 AI 생성 모드 켜기

OpenAI API 키가 필요하며 API 사용료가 발생할 수 있습니다.

Streamlit 앱의 `Manage app → Settings → Secrets`에 다음을 넣습니다.

```toml
OPENAI_API_KEY = "여기에_API_키"
```

API 키를 GitHub의 `app.py`나 공개 파일에 직접 적지 마세요.

Secrets를 저장하고 앱을 재부팅하면:

- `gpt-5.6`: 장면 묘사와 선택지 생성
- `gpt-image-2`: 드림코어 이미지 생성

이 활성화됩니다.

## 현재 기능

- API 키 없는 데모 모드
- 입력문 기반 첫 장면
- 세 개의 선택지
- 이전 장소와 선택 기억
- 기억 조각 수집
- AI 장면 설명
- AI 이미지 생성
- 파스텔 드림코어 UI
