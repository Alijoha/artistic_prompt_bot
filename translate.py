from deep_translator import GoogleTranslator

def translate_prompt(prompt, target_language):
    if target_language == "English":
        return prompt  # No translation needed
    try:
        translated = GoogleTranslator(source="auto", target=target_language.lower()).translate(prompt)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return prompt  # Fallback to original if translation fails