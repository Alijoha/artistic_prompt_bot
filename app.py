import streamlit as st
from dalle_generator import generate_dalle_image
from mj_prompt import generate_mj_prompt
from artistly_prompt import generate_artistly_prompt

st.set_page_config(page_title="Artistic Prompt Generator", layout="wide")

st.markdown("""
    <style>
        body {
            background-color: #fdf6f0;
        }
        .stApp {
            background-color: #f0f8ff;
            color: #333;
        }
        footer {
            text-align: center;
            padding: 2rem 0;
            font-size: 0.85rem;
            color: #999;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎨 Artistic Prompt Generator")

# Sidebar style selector
styles = ["Watercolor", "Hyperrealistic", "Anime", "Oil Painting", "Pop Surrealism"]
selected_style = st.selectbox("Select a style:", styles)

if "prompts" not in st.session_state:
    st.session_state.prompts = ""
if "dalle_prompt" not in st.session_state:
    st.session_state.dalle_prompt = ""
if "dalle_image" not in st.session_state:
    st.session_state.dalle_image = None

# Generate prompts
if st.button("Generate Prompts ✨"):
    mj = generate_mj_prompt(selected_style)
    artistly = generate_artistly_prompt(selected_style)
    st.session_state.prompts = f"## 1. MidJourney Prompt:\n\n{mj}\n\n## 2. Artistly.ai Prompt:\n\n{artistly}"
    st.session_state.dalle_prompt = artistly
    st.session_state.dalle_image = None

# Display prompts
if st.session_state.prompts:
    st.success("✅ Prompts Generated!")
    mj_prompt = st.session_state.prompts.split("Artistly.ai Prompt:")[0].replace("MidJourney Prompt:", "").strip()
    dalle_prompt = st.session_state.dalle_prompt.strip()

    st.markdown(f"### 1. MidJourney Prompt:\n\n\"{mj_prompt}\"")
    st.markdown(f"### 2. Artistly.ai Prompt:\n\n\"{dalle_prompt}\"")

    # Generate image button
    if st.button("🎨 Generate Etsy Image (DALLE-3)"):
        with st.spinner("Generating image..."):
            image_url = generate_dalle_image(dalle_prompt)
            if image_url:
                st.session_state.dalle_image = image_url
            else:
                st.error("❌ Failed to generate image.")

# Show image
if st.session_state.dalle_image:
    st.image(st.session_state.dalle_image, caption="AI Image Preview", use_container_width=True)

# Footer
st.markdown("""
    <hr>
    <footer>
        © 2025 Johanna Polanco — All rights reserved.
    </footer>
""", unsafe_allow_html=True)