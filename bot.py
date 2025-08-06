import os
import openai
import requests
from dotenv import load_dotenv

# Load API keys
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_prompts(theme, style, mood):
    """Generates MidJourney and Artistly prompts."""
    prompt_request = f"""
    You are an expert AI art prompt engineer. Create two separate prompts:

    Theme: {theme}
    Style: {style}
    Mood: {mood}

    1. MidJourney Prompt:
    - Include detailed scene, subject, environment, colors, mood.
    - Add MidJourney parameters (--ar 1:1 --q 2 --stylize 500).
    - Be visually rich and cinematic.

    2. Artistly.ai Prompt:
    - Detailed description only, no parameters.
    - Highly visual, artistic, descriptive.

    Output clearly labeled for each platform.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_request}],
        temperature=0.85,
        max_tokens=400
    )

    return response.choices[0].message.content


def generate_dalle_image(prompt):
    """Generates an image using DALL·E 3."""
    try:
        result = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024"
        )
        return result.data[0].url
    except Exception as e:
        print("DALL·E error:", e)
        return None