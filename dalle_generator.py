import openai
import os

def generate_dalle_image(prompt):
    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )

    image_url = response['data'][0]['url']
    return image_url