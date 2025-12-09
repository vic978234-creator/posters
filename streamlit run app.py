import streamlit as st
import openai
import requests
from PIL import Image
from io import BytesIO

# --- 페이지 설정 ---
st.set_page_config(
    page_title="Generative Poster Art Studio",
    page_icon="🎨",
    layout="wide"
)

# --- CSS 스타일링 (선택사항) ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    h1 {
        color: #FF4B4B;
    }
</style>
""", unsafe_allow_html=True)


# --- API 키 설정 (수정된 부분) ---
# 🚨 보안 경고: API 키가 코드에 직접 노출되었습니다. 테스트 목적으로만 사용하세요.
# 기존 secrets 코드 주석 처리
# try:
#     openai.api_key = st.secrets["OPENAI_API_KEY"]
# except FileNotFoundError:
#     st.error("API 키를 찾을 수 없습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
#     st.stop()

# 👇 여기에 아까 주신 키를 직접 넣었습니다.
key_for_testing = "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"
openai.api_key = key_for_testing


# --- 헬퍼 함수: 이미지 다운로드용 데이터 변환 ---
def get_image_bytes(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        st.error(f"이미지 다운로드 준비 실패: {e}")
        return None


# --- 핵심 함수: DALL-E 3 이미지 생성 ---
def generate_poster(prompt_concept, style, aspect_ratio):
    """
    사용자 입력과 스타일을 조합하여 DALL-E 3에 보낼 최적화된 프롬프트를 생성하고 호출합니다.
    """
    # 전역 설정된 openai.api_key를 사용합니다.
    client = openai.OpenAI(api_key=openai.api_key)

    # 스타일별 추가 프롬프트 정의
    style_prompts = {
        "미니멀리즘 (Minimalist)": "minimalist graphic design poster, clean lines, restrained color palette, lots of negative space, modern typography.",
        "레트로 퓨처리즘 (Retro Futurism)": "retro-futuristic poster art, 1980s sci-fi aesthetic, neon colors, chrome textures, synthwave vibe, bold stylized typography.",
        "빈티지 여행 포스터 (Vintage Travel)": "vintage travel poster style, textured paper look, aged colors, nostalgic illustration, classic serif typography like WPA art.",
        "바우하우스 (Bauhaus)": "Bauhaus design poster, geometric shapes, primary colors (red, blue, yellow), functional typography, asymmetrical balance.",
        "사이버펑크 (Cyberpunk)": "cyberpunk poster, dystopian high-tech low-life, glitch art effects, dark futuristic city background, glowing neon kanji and text.",
        "팝아트 (Pop Art)": "pop art comic book style poster, halftone dots, bold outlines, vibrant contrasting colors, inspired by Roy Lichtenstein.",
        "추상 표현주의 (Abstract)": "abstract expressionism poster art, energetic brushstrokes, splashes of color, emotive, non-representational forms, avant-garde typography."
    }

    # 비율 설정
    ratio_map = {
        "세로형 (Portrait, 9:16)": "1024x1792",
        "정사각형 (Square, 1:1)": "1024x1024",
        "가로형 (Landscape, 16:9)": "1792x1024"
    }
    size = ratio_map[aspect_ratio]

    # 최종 프롬프트 조합 (DALL-E 3가 이미지를 포스터로 인식하도록 유도)
    full_prompt = (
        f"A professionally designed poster titled or themed '{prompt_concept}'. "
        f"Style defined as: {style_prompts[style]} "
        f"Ensure the text is integrated creatively into the design and generated accurately. "
        f"High quality, printable poster design."
    )

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size=size,
            quality="standard", # 'hd'로 하면 더 디테일하지만 비쌈
            n=1,
        )
        image_url = response.data[0].url
        return image_url, full_prompt
    except Exception as e:
        st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")
        return None, None


# --- UI 구성 ---

# 사이드바: 컨트롤 패널
with st.sidebar:
    st.header("🛠️ Studio Controls")
    st.markdown("나만의 포스터를 디자인해보세요.")

    # 1. 포스터 주제/문구 입력
    prompt_concept = st.text_area(
        "포스터 주제 또는 포함할 문구 (필수)",
        placeholder="예: 화성 탐사 여행, 'COFFEE & CODE' 페스티벌, 지속 가능한 미래",
        height=100
    )

    # 2. 스타일 선택
    style = st.selectbox(
        "아트 스타일 선택",
        [
            "미니멀리즘 (Minimalist)",
            "빈티지 여행 포스터 (Vintage Travel)",
            "레트로 퓨처리즘 (Retro Futurism)",
            "바우하우스 (Bauhaus)",
            "사이버펑크 (Cyberpunk)",
            "팝아트 (Pop Art)",
            "추상 표현주의 (Abstract)"
        ]
    )

    # 3. 비율 선택
    aspect_ratio = st.radio(
        "포스터 비율",
        ["세로형 (Portrait, 9:16)", "정사각형 (Square, 1:1)", "가로형 (Landscape, 16:9)"],
        index=0
    )

    st.markdown("---")
    st.caption("Powered by OpenAI DALL-E 3")


# 메인 페이지: 결과물 표시 영역
st.title("🎨 Generative Poster Art Studio")
st.markdown("AI와 함께 당신의 아이디어를 멋진 포스터로 만들어보세요.")

# 세션 상태 초기화 (이미지 유지용)
if 'generated_image_url' not in st.session_state:
    st.session_state.generated_image_url = None
if 'used_prompt' not in st.session_state:
    st.session_state.used_prompt = None


# 생성 버튼 클릭 시 동작
generate_btn = st.sidebar.button("✨ 포스터 생성하기 (Generate)", type="primary", use_container_width=True)

if generate_btn:
    if not prompt_concept:
        st.sidebar.warning("포스터 주제나 문구를 먼저 입력해주세요!")
    else:
        with st.spinner("AI 아티스트가 포스터를 디자인하는 중입니다... (약 15~30초 소요)"):
            # 이미지 생성 함수 호출
            image_url, used_prompt = generate_poster(prompt_concept, style, aspect_ratio)
            
            if image_url:
                st.session_state.generated_image_url = image_url
                st.session_state.used_prompt = used_prompt
                st.toast("포스터 생성이 완료되었습니다!", icon="🎉")


# 결과 이미지 표시 영역
if st.session_state.generated_image_url:
    st.divider()
    st.subheader("생성된 포스터 결과물")
    
    # 이미지 표시
    st.image(st.session_state.generated_image_url, caption="Generated by DALL-E 3", use_column_width=True)

    # 다운로드 버튼 및 프롬프트 정보용 컬럼
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 다운로드를 위해 이미지 데이터 가져오기
        img_bytes = get_image_bytes(st.session_state.generated_image_url)
        if img_bytes:
            st.download_button(
                label="💾 고화질 이미지 다운로드",
                data=img_bytes,
                file_name="generated_poster.png",
                mime="image/png",
            )
    
    with col2:
        with st.expander("ℹ️ 생성에 사용된 실제 AI 프롬프트 보기"):
            st.write(st.session_state.used_prompt)

else:
    # 초기 안내 화면
    st.info("👈 왼쪽 사이드바에서 주제를 입력하고 스타일을 선택한 후 '생성하기' 버튼을 눌러주세요.")
    st.markdown("""
    ### 💡 팁:
    * **구체적인 문구**를 입력하면 더 좋은 결과가 나옵니다. (예: "'JAZZ NIGHT' in Seoul, Oct 26")
    * DALL-E 3는 **영어**를 더 잘 이해하지만 한글도 꽤 잘 표현합니다.
    * 다양한 스타일을 시도해보세요!
    """)
