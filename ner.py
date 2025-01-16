import spacy
import json

# Load the two spaCy models (replace with your actual model paths)
try:
    nlp_skills = spacy.load("model2/model-best")
    nlp_general = spacy.load("model1")
except OSError:
    print("Error: Could not load models. Please ensure the paths are correct.")
    exit()

def combine_ner_predictions(text):
    """Combines predictions from two NER models, prioritizing the skills-only model for skills."""

    doc_skills = nlp_skills(text)
    doc_general = nlp_general(text)

    combined_entities = []

    # Add skills from the skills-only model
    for ent in doc_skills.ents:
        combined_entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char
        })

    # Add other entities from the general model, avoiding duplicates for skills
    for ent in doc_general.ents:
        combined_entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start_char": ent.start_char,
            "end_char": ent.end_char
        })

    # Sort entities by start character to maintain original text order
    combined_entities.sort(key=lambda x: x["start_char"])

    return combined_entities

def process_text_file(filepath):
    """Reads text from a file, processes it with NER, and returns the results as a JSON array."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:  # Handle various encodings
            text = file.read()
            combined_results = combine_ner_predictions(text)

            # Return the combined entities as a JSON array
            return json.dumps(combined_results, ensure_ascii=False, indent=4)

    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return json.dumps({"error": "File not found"})
    except Exception as e:  # Catch other potential exceptions during file processing
        print(f"An error occurred while processing the file: {e}")
        return json.dumps({"error": str(e)})

# Example usage: process a single file
# file_path = "MISS_NAGMA.txt"  # Replace with the path to your text file
# result_json = process_text_file(file_path)
# print(result_json)
