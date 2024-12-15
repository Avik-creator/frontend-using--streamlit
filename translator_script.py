from deep_translator import GoogleTranslator
import textract
from langdetect import detect_langs

def process_uploaded_file(file_path):
   
    try:
        
        extracted_text = textract.process(file_path).decode('utf-8')
        
        if not extracted_text.strip():
            raise ValueError("No text could be extracted from the file.")

       
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


if __name__ == "__main__":
    file_path = "cv13.docx"  
    translated_text = process_uploaded_file(file_path)
    if translated_text:
        print("Translated Text:")
        print(translated_text)
