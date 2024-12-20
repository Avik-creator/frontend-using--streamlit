from deep_translator import GoogleTranslator
from langdetect import detect_langs
def process_uploaded_file(extracted_text):
   
    try:
        detectLanguages = detect_langs(extracted_text)
        
        detectLanguage = detectLanguages[0].lang
        if detectLanguage == 'en':
            print("The text is already in English.")
            return extracted_text

        translated_text = GoogleTranslator(source=detectLanguage, target='en').translate(extracted_text)
        return translated_text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
