import streamlit as st
import google.generativeai as genai
from PIL import Image
import imageio.v2 as imageio
import io

# --- 페이지 설정 ---
st.set_page_config(page_title="우리 반 추억 모음집", page_icon="🏫")

# --- API 키 설정 ---
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
except FileNotFoundError:
    st.error("API 키가 없습니다. 설정(Secrets)을 확인해주세요.")
    st.stop()

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 제목 ---
st.title("🏫 우리 반 한 학기 추억 모음")
st.markdown("사진들을 올려주세요. AI가 **학급 편지**와 **움직이는 앨범**을 만들어 줍니다!")

# 1. 파일 여러 개 업로드 (accept_multiple_files=True)
uploaded_files = st.file_uploader(
    "학생들 사진을 모두 선택해서 올려주세요 (최대 20장 권장)", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if uploaded_files:
    # 이미지 처리
    images = []
    for file in uploaded_files:
        img = Image.open(file)
        images.append(img)
    
    st.success(f"총 {len(images)}장의 사진이 올라왔어요!")

    # 탭으로 기능 나누기
    tab1, tab2, tab3 = st.tabs(["📝 학급 편지 쓰기", "🎞️ 움짤(GIF) 만들기", "🖼️ 사진 모아보기"])

    # [기능 1] AI 종합 분석 (편지 쓰기)
    with tab1:
        if st.button("AI 선생님, 편지 써주세요!", type="primary"):
            with st.spinner('AI가 사진들을 보며 추억을 회상하는 중...'):
                try:
                    # 사진이 너무 많으면 AI가 힘들어하니 최대 10장만 추려서 분석 (앞부분)
                    analyze_images = images[:10] 
                    
                    prompt = """
                    너는 한국어 어학당 선생님이야.
                    이 사진들은 우리 반 학생들의 한 학기 동안의 모습들이야.
                    
                    1. 사진들의 전체적인 분위기(즐거움, 열정, 감동 등)를 파악해 줘.
                    2. 학생들에게 보내는 '종강 편지'를 써 줘.
                    3. 말투는 다정하고 감동적인 '해요체'를 써 줘.
                    4. 편지 제목도 멋지게 지어 줘.
                    """
                    
                    # 텍스트와 이미지 리스트를 함께 전송
                    response = model.generate_content([prompt] + analyze_images)
                    
                    st.markdown("### 💌 우리 반에게 보내는 편지")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"오류가 났어요: {e}")

    # [기능 2] 슬라이드쇼 (GIF) 만들기
    with tab2:
        st.write("사진들을 연결해서 움직이는 짤(GIF)로 만들어 드려요.")
        duration = st.slider("사진 넘어가는 속도 (초)", 0.2, 2.0, 0.5)
        
        if st.button("GIF 앨범 생성하기"):
            with st.spinner('앨범을 만드는 중...'):
                # 메모리에 GIF 파일 생성
                with io.BytesIO() as gif_bytes:
                    # 이미지를 리사이즈해서 용량 줄이기 (가로 400px 기준)
                    resized_images = []
                    for img in images:
                        img_resized = img.resize((400, int(400 * img.height / img.width)))
                        resized_images.append(img_resized)
                    
                    # imageio로 GIF 저장
                    imageio.mimsave(gif_bytes, resized_images, format='GIF', duration=duration, loop=0)
                    
                    st.image(gif_bytes.getvalue(), caption="완성된 앨범")
                    
                    # 다운로드 버튼
                    st.download_button(
                        label="💾 앨범 다운로드 (GIF)",
                        data=gif_bytes.getvalue(),
                        file_name="class_memory.gif",
                        mime="image/gif"
                    )

    # [기능 3] 갤러리 뷰
    with tab3:
        st.write("업로드된 사진들")
        # 3열 그리드로 보여주기
        cols = st.columns(3)
        for idx, img in enumerate(images):
            cols[idx % 3].image(img, use_container_width=True)
