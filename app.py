import streamlit as st
from bot import generate_prompt, show_cache_clear_button
from dalle_generator import generate_dalle_image
from translate import translate_prompt
from io import BytesIO
import zipfile
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import openai
import base64

# Load environment variables
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- PAGE CONFIG ---
st.set_page_config(page_title="Artistic Prompt Generator", layout="wide", page_icon="🎨")

# Initialize session state
if "last_prompt" not in st.session_state:
    st.session_state["last_prompt"] = ""

if "last_optimized_prompt" not in st.session_state:
    st.session_state["last_optimized_prompt"] = ""

if "last_refinement" not in st.session_state:
    st.session_state["last_refinement"] = ""

if "prompt_history" not in st.session_state or not isinstance(st.session_state["prompt_history"], list):
    st.session_state["prompt_history"] = []

if "favorite_prompts" not in st.session_state or not isinstance(st.session_state["favorite_prompts"], list):
    st.session_state["favorite_prompts"] = []

# --- DARK THEME ---
st.markdown("""
    <style>
    body, .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button {
        background-color: #21262d; color: #c9d1d9;
        border: 1px solid #30363d; padding: 0.5rem 1rem; border-radius: 6px;
    }
    .stButton>button:hover { background-color: #30363d; }
    .stTextInput>div>input, .stSelectbox>div>div {
        background-color: #161b22; color: #c9d1d9;
    }
            
   /* === Mobile-friendly pickers (Theme, Style, Mood, Language, Refinement) === */
@media (max-width: 560px) {
  /* Make all selectboxes and radios easier to tap */
  .stSelectbox div[data-baseweb="select"] { min-height: 52px; }
  .stSelectbox * { font-size: 16px !important; line-height: 1.2; }

  .stRadio > div { gap: 10px; }
  .stRadio label { padding: 8px 10px; border-radius: 8px; }
  .stRadio * { font-size: 16px !important; }

  /* Buttons a bit larger */
  .stButton > button { padding: 12px 16px; font-size: 16px; border-radius: 8px; }

  /* Inputs full-width */
  .stSelectbox, .stTextInput, .stRadio, .stButton { width: 100% !important; }
}

/* Taller dropdown list so users can scroll more options on phones */
div[role="listbox"] { max-height: 65vh !important; }

/* Slightly bigger hit area on all screens */
.stSelectbox div[data-baseweb="select"] { min-height: 44px; }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
for key in ["last_prompt", "last_optimized_prompt", "last_refinement", "prompt_history", "favorite_prompts"]:
    if key not in st.session_state:
        st.session_state[key] = [] if "prompts" in key else ""

# --- UI TITLE ---
st.markdown("## 🎨 Multi-Platform Artistic Prompt Generator")
st.markdown("Generate prompts for MidJourney, Artisly.ai — and preview DALL·E images instantly.")

# --- CACHE CLEAR ---
show_cache_clear_button()

# --- USER INPUTS ---
# THEME
theme = st.selectbox(
    "🖋️ Theme",
    [
        # existing
        "Elf Queen in an enchanted forest", "Cyberpunk city skyline at night", "Underwater steampunk laboratory",
        "Haunted Victorian mansion", "Magical animal tea party", "Floating crystal island",
        "Ancient jungle ruins", "Dreamy cloud kingdom", "Neon Tokyo alleyway", "Surreal clockwork garden",
        "Galactic dragon shrine", "Rainy street café", "Mythical phoenix rebirth",
        "Retro-futuristic arcade", "Whimsical flying train", "Alien carnival at dusk",
        # added popular universes
        "Marvel Universe", "DC Comics Universe", "Star Wars Galaxy", "Disney Fairytale Kingdom",
        "Pixar Animated World", "Harry Potter Wizarding World", "Lord of the Rings Middle-earth",
        "Game of Thrones Westeros", "Avatar: The Last Airbender World", "Pokemon Universe",
        "Zelda: Hyrule", "Final Fantasy Realm", "Genshin Impact World", "My Hero Academia City"
    ],
    index=None,
    placeholder="Pick or type a theme…"
)

# STYLE
style = st.selectbox(
    "🎨 Style",
    [
        "Watercolor", "Oil Painting", "Graffiti", "Sketch", "Pop Surrealism", "Lowbrow Art",
        "Pixel Art", "Digital Matte Painting", "Studio Ghibli Style", "Ink & Wash", "Concept Art",
        "3D Render", "Chalk Pastel", "Alcohol Ink", "Mosaic Art", "Origami Paper Style",
        "Vaporwave", "Cyberpunk", "Art Nouveau", "Steampunk", "Tattoo Flash", "Woodcut Print",
        "Dark Fantasy", "Line Art", "Cartoon",
        # extra styles
        "Solarpunk", "Dieselpunk", "Biopunk", "Baroque Engraving", "Ukiyo-e",
        "Photobashing", "Cinematic Realism", "Isometric Diorama", "Liminal Space",
        "Low-Poly 3D", "Cel-Shaded", "Pastelcore", "Noir Comic", "Pixel RPG UI"
    ],
    index=None,
    placeholder="Pick or type a style…"
)

# MOOD
mood = st.selectbox(
    "✨ Mood",
    [
        "Whimsical", "Mystical", "Ethereal", "Melancholic", "Dreamy", "Uplifting",
        "Dark Fantasy", "Surreal", "Elegant", "Dramatic", "Romantic", "Peaceful",
        "Intense", "Futuristic", "Retro", "Minimalist", "Cinematic", "Noir",
        "Joyful", "Tranquil", "Spooky", "Playful", "Epic", "Spiritual", "Nostalgic",
        # extra moods
        "Cozy", "Hopeful", "Somber", "Euphoric", "Wholesome", "Gritty",
        "Mysterious", "Whirlwind", "Melodic", "Sacred", "Otherworldly", "Zen",
        "High-Energy", "Cold & Sterile", "Warm & Inviting"
    ],
    index=None,
    placeholder="Pick or type a mood…"
)

language = st.selectbox("🌍 Output Language", [
    "English", "Spanish", "French", "German", "Portuguese",
    "Japanese", "Russian", "Chinese", "Korean", "Italian"
])

refinement = st.radio("🧠 Smart Prompt Refinement", [
    "🔥 Raw creative prompt", "🎯 Optimized for AI clarity", "🪄 Both"
])

# --- EXPAND PROMPT ---
st.markdown("### ✨ Expand a Short Idea into a Full Prompt")
quick_idea = st.text_input("💡 Enter a short idea (e.g. magical forest cat)")
if st.button("Expand Prompt"):
    with st.spinner("Expanding..."):
        base_prompt = f"{quick_idea}. Style: {style}. Mood: {mood}"
        expanded = generate_prompt(base_prompt, refinement)
        if refinement == "🪄 Both":
            raw, optimized = expanded.split("###OPTIMIZED###")
            st.session_state["last_prompt"] = raw.strip()
            st.session_state["last_optimized_prompt"] = optimized.strip()
            st.session_state["prompt_history"].append(raw.strip())
        else:
            st.session_state["last_prompt"] = expanded
            st.session_state["last_optimized_prompt"] = ""
            st.session_state["prompt_history"].append(expanded)

        if language != "English":
            st.session_state["last_prompt"] = translate_prompt(st.session_state["last_prompt"], language)
            if st.session_state["last_optimized_prompt"]:
                st.session_state["last_optimized_prompt"] = translate_prompt(st.session_state["last_optimized_prompt"], language)

# --- GENERATE PROMPTS ---
if st.button("Generate Prompts"):
    with st.spinner("Generating prompts..."):
        user_prompt = f"{theme}. Style: {style}. Mood: {mood}"
        prompt = generate_prompt(user_prompt, refinement)

        st.session_state["last_refinement"] = refinement

        if refinement == "🪄 Both":
            raw, optimized = prompt.split("###OPTIMIZED###")
            st.session_state["last_prompt"] = raw.strip()
            st.session_state["last_optimized_prompt"] = optimized.strip()
            st.session_state["prompt_history"].append(raw.strip())
        else:
            st.session_state["last_prompt"] = prompt
            st.session_state["last_optimized_prompt"] = ""
            st.session_state["prompt_history"].append(prompt)

        if language != "English":
            st.session_state["last_prompt"] = translate_prompt(st.session_state["last_prompt"], language)
            if st.session_state["last_optimized_prompt"]:
                st.session_state["last_optimized_prompt"] = translate_prompt(st.session_state["last_optimized_prompt"], language)

# --- DISPLAY PROMPTS ---
if st.session_state["last_prompt"]:
    r = st.session_state["last_refinement"]
    st.success("✅ Prompts Generated!")

    if r == "🔥 Raw creative prompt":
        st.markdown("### 1. **MidJourney Prompt:**")
        st.markdown(f"> {st.session_state['last_prompt']}")
        st.markdown("### 2. **Artisly.ai Prompt:**")
        st.markdown(f"> {st.session_state['last_prompt']}")
    elif r == "🎯 Optimized for AI clarity":
        st.markdown("### 1. **MidJourney Prompt (Optimized):**")
        st.markdown(f"> {st.session_state['last_prompt']}")
        st.markdown("### 2. **Artisly.ai Prompt (Optimized):**")
        st.markdown(f"> {st.session_state['last_prompt']}")
    else:
        st.markdown("### 1. **MidJourney Prompt (Raw):**")
        st.markdown(f"> {st.session_state['last_prompt']}")
        st.markdown("### 2. **Artisly.ai Prompt (Optimized):**")
        st.markdown(f"> {st.session_state['last_optimized_prompt']}")

    # --- DOWNLOAD OPTIONS ---
    txt = f"MidJourney: {st.session_state['last_prompt']}\n\nArtisly.ai: {st.session_state['last_optimized_prompt'] or st.session_state['last_prompt']}"
    st.download_button("📄 Download as TXT", txt, file_name="prompt.txt")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    story = [Paragraph(txt.replace('\n', '<br/>'), styles['Normal'])]
    doc.build(story)
    st.download_button("📝 Download as PDF", buffer.getvalue(), file_name="prompt.pdf")

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr("prompt.txt", txt)
        zipf.writestr("prompt.pdf", buffer.getvalue())
    st.download_button("🗜️ Download ZIP", zip_buffer.getvalue(), file_name="prompt_bundle.zip")

    # --- DALL·E IMAGE GENERATION ---
    if st.button("🖼️ Generate Etsy Image (DALLE 3)"):
        with st.spinner("Generating image..."):
            dalle_prompt = st.session_state['last_optimized_prompt'] or st.session_state['last_prompt']
            image_url = generate_dalle_image(dalle_prompt)
            if image_url:
                st.image(image_url, caption="DALL·E 3 Preview")
            else:
                st.error("Failed to generate image.")

    # --- PROMPT HISTORY ---
    if st.session_state["prompt_history"]:
        st.markdown("### 🔁 Prompt History")
        for i, p in enumerate(reversed(st.session_state["prompt_history"][-10:]), 1):
            st.markdown(f"**{i}.** {p}")
            if st.button(f"❤️ Favorite #{i}", key=f"fav_{i}"):
                st.session_state["favorite_prompts"].append(p)
                st.success("Added to favorites!")

   # --- IMAGE TO PROMPT (Vision AI for OpenAI v1.x) ---
st.markdown("## 🖼️ Generate Prompt from Image")

uploaded_file = st.file_uploader("Upload an image (JPG or PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Analyze Image and Generate Prompt"):
        with st.spinner("Analyzing image and generating prompt..."):
            try:
                image_bytes = uploaded_file.read()

                response = openai.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional artist assistant. Analyze the uploaded image and describe it as a highly imaginative AI art prompt."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Generate an AI art prompt based on this image."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode()}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=500,
                )

                image_prompt = response.choices[0].message.content.strip()
                st.session_state["last_prompt"] = image_prompt
                st.session_state["last_optimized_prompt"] = ""
                st.session_state["last_refinement"] = "🔥 Raw creative prompt"
                st.session_state["prompt_history"].append(image_prompt)

                st.success("🖼️ Prompt Generated from Image!")
                st.markdown("### **Prompt:**")
                st.markdown(f"> {image_prompt}")

            except Exception as e:
                st.error(f"Image analysis failed: {str(e)}")
# Custom footer (centered with white background)
footer = """
    <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: white;
            color: black;
            text-align: center;
            padding: 10px;
            font-size: 14px;
            z-index: 100;
            box-shadow: 0 -1px 3px rgba(0,0,0,0.1);
        }
    </style>
    <div class="footer">
        © 2025 Johanna Polanco ❤️ With Love ❤️ — All rights reserved.
    </div>
"""
st.markdown(footer, unsafe_allow_html=True)