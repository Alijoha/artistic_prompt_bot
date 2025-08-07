import streamlit as st
import os
import openai
from dotenv import load_dotenv
from io import BytesIO
from reportlab.pdfgen import canvas
import zipfile

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_prompt(user_prompt, refinement):
    """
    Generate a creative or optimized prompt based on user input and refinement option.
    """
    if refinement == "🔥 Raw creative prompt":
        system_msg = "You are a creative AI that generates vivid, imaginative, artistic prompts."
    elif refinement == "🎯 Optimized for AI clarity":
        system_msg = "You are an AI trained to write clear, structured prompts optimized for use in MidJourney, DALL·E, and Artisly.ai."
    else:
        system_msg = "You are an AI that first gives a raw, artistic version of the prompt, followed by a version optimized for AI clarity."

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=400
    )

    return response.choices[0].message.content

def show_cache_clear_button():
    if st.button("🔄 Clear Cache"):
        st.cache_data.clear()
        st.success("Cache cleared!")

def download_prompt_as_txt(prompt):
    return BytesIO(prompt.encode("utf-8"))

def download_prompt_as_pdf(prompt):
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    textobject = c.beginText(40, 800)
    for line in prompt.split("\n"):
        textobject.textLine(line)
    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def create_zip_file(prompt, image_url=None):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        # Add TXT
        zipf.writestr("prompt.txt", prompt)
        
        # Add PDF
        pdf_bytes = download_prompt_as_pdf(prompt).read()
        zipf.writestr("prompt.pdf", pdf_bytes)

        # Add image (placeholder)
        if image_url:
            import requests
            image_data = requests.get(image_url).content
            zipf.writestr("preview.png", image_data)

    zip_buffer.seek(0)
    return zip_buffer