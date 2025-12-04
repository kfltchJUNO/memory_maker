import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 페이지 설정 ---
st.set_page_config(
    page_title="AI 한국어 일기장",
    page_icon="📸"
)

# --- API 키 설정 (Streamlit Secrets에서 가져옴) ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("API 키가 설정되지 않았습니다. Streamlit Secrets를 확인해주세요.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- UI 구성 ---
st.title("📸 AI 한국어 일기장")
st.markdown("### 사진 한 장으로 배우는 한국어")
st.info("사진을 업로드하면 AI 선생님이 초급 수준의 한국어 일기를 써줍니다.")

# 파일 업로더
uploaded_file = st.file_uploader("추억이 담긴 사진을 올려주세요", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # 이미지 보여주기
    image = Image.open(uploaded_file)
    st.image(image, caption='선택한 사진', use_container_width=True)

    # 버튼 클릭 시 동작
    if st.button("📝 일기 써주세요!", type="primary"):
        with st.spinner('AI 선생님이 사진을 보며 글을 쓰고 있어요...'):
            try:
                # 프롬프트 (명령어)
                prompt = """
                너는 친절한 한국어 선생님이야. 
                이 사진을 보고 '외국인 초급 학습자(TOPIK 2급 수준)'가 쓴 것 같은 짧은 일기를 작성해 줘.
                
                [조건]
                1. 말투: 부드러운 '해요체' (예: 갔어요, 먹었어요)
                2. 분량: 3~4문장
                3. 내용: 사진의 상황을 묘사하고, 기분이나 느낌을 포함할 것.
                4. 추가: 마지막에 사진과 관련된 핵심 단어 3개를 해시태그(#)로 달아줄 것.
                """
                
                # AI 요청
                response = model.generate_content([prompt, image])
                
                # 결과 출력
                st.success("작성 완료!")
                st.markdown("---")
                st.subheader("📖 오늘의 일기")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
