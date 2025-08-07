import random

def generate_artistly_prompt():
    prompts = [
        "A dreamy watercolor illustration of a mystical cat floating through a neon galaxy, glowing stars surrounding it, 300 DPI, white background",
        "A cute cartoon character dancing in pastel clouds with sparkly accessories and soft lighting, inspired by modern kawaii style",
        "A magical enchanted forest made of candy and glittering mushrooms, in a whimsical soft color palette",
        "A chibi-style unicorn painting a rainbow in the sky with a glowing brush, surrounded by twinkling stars and soft sparkles",
        "An aesthetic flat illustration of a retro robot in a vintage coffee shop, sipping espresso, with warm lighting and pastel tones"
    ]
    return random.choice(prompts)