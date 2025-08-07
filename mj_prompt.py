import random

def generate_mj_prompt():
    prompts = [
        "A dreamy landscape of floating islands with waterfalls cascading into the sky, soft pastel hues",
        "An ancient magical library with glowing runes and floating books, warm candlelight ambiance",
        "A futuristic city at night with flying cars and neon signs in a rain-soaked street, cyberpunk style",
        "An enchanted forest with oversized glowing mushrooms, fairies dancing in sparkles of light",
        "A whimsical cottage made of candy and sweets in a magical pastel land, soft lighting and glow"
    ]
    return random.choice(prompts)