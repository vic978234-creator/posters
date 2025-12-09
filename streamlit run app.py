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

# --- CSS 스타일링 ---
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


# --- API 키 설정 ---
# 👇 요청하신 새로운 키를 여기에 넣었습니다.
# 주의: 이 파일은 절대 인터넷에 공유하지 마세요.
key_for_testing = "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"
openai.api_key = key_for_testing


# --- 헬퍼 함수: 이미지 다운로드용 ---
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
    client = openai.OpenAI(api_key=openai.api_key)

    # 스타일 프롬프트
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

    # 프롬프트 조합
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
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url, full_prompt
    except Exception as e:
        st.error(f"이미지 생성 중 오류가 발생했습니다: {e}")
        return None, None


# --- UI 구성 ---
with st.sidebar:
    st.header("🛠️ Studio Controls")
    
    prompt_concept = st.text_area(
        "포스터 주제 또는 문구",
        placeholder="예: 화성 탐사 여행, 'COFFEE & CODE' 페스티벌",
        height=100
    )

    style = st.selectbox(
        "아트 스타일 선택",
        [
            "미니멀리즘 (Minimalist)", "빈티지 여행 포스터 (Vintage Travel)",
            "레트로 퓨처리즘 (Retro Futurism)", "바우하우스 (Bauhaus)",
            "사이버펑크 (Cyberpunk)", "팝아트 (Pop Art)", "추상 표현주의 (Abstract)"
        ]
    )

    aspect_ratio = st.radio(
        "포스터 비율",
        ["세로형 (Portrait, 9:16)", "정사각형 (Square, 1:1)", "가로형 (Landscape, 16:9)"]
    )
    st.markdown("---")
    st.caption("Powered by OpenAI DALL-E 3")

st.title("🎨 Generative Poster Art Studio")

if 'generated_image_url' not in st.session_state:
    st.session_state.generated_image_url = None
if 'used_prompt' not in st.session_state:
    st.session_state.used_prompt = None

generate_btn = st.sidebar.button("✨ 포스터 생성하기 (Generate)", type="primary", use_container_width=True)

if generate_btn:
    if not prompt_concept:
        st.sidebar.warning("포스터 주제나 문구를 먼저 입력해주세요!")
    else:
        with st.spinner("AI 아티스트가 포스터를 디자인하는 중입니다..."):
            image_url, used_prompt = generate_poster(prompt_concept, style, aspect_ratio)
            
            if image_url:
                st.session_state.generated_image_url = image_url
                st.session_state.used_prompt = used_prompt
                st.toast("완료되었습니다!", icon="🎉")

if st.session_state.generated_image_url:
    st.divider()
    st.image(st.session_state.generated_image_url, caption="Generated by DALL-E 3", use_column_width=True)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        img_bytes = get_image_bytes(st.session_state.generated_image_url)
        if img_bytes:
            st.download_button(
                label="💾 이미지 다운로드",
                data=img_bytes,
                file_name="poster.png",
                mime="image/png",
            )
    with col2:
        with st.expander("ℹ️ 프롬프트 보기"):
            st.write(st.session_state.used_prompt)
