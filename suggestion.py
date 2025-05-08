from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login
import torch
import re
import json
#importing the model
import torch
from transformers import pipeline

pipe = pipeline("text-generation", model="HuggingFaceH4/zephyr-7b-alpha", torch_dtype=torch.bfloat16, device_map="auto")



def extract_last_json_block(text):
    """
    Extracts the last JSON dictionary from a given string.

    Parameters:
        text (str): The input string containing one or more JSON objects.

    Returns:
        dict: The last parsed JSON object, or None if not found or parsing fails.
    """
    try:
        matches = re.findall(r'{[^{}]*(?:{[^{}]*}[^{}]*)*}', text, re.DOTALL)
        if not matches:
            return None
        last_json = matches[-1]
        return json.loads(last_json)
    except json.JSONDecodeError:
        return None

def generate_resume_suggestions(resume_data, job_data):
    messages = [
    {
        "role": "system",
        "content": (
            "You are a helpful career advisor. Respond ONLY in structured JSON format with the following keys: "
            "skills_to_learn (list of strings), experience_gaps (list of strings), "
            "education_advice (list of strings), resume_tips (list of strings)."
        )
    },
    {
        "role": "user",
        "content": f"""A candidate has this resume:
- Skills: {', '.join(resume_data['skills'])}
- Experience: {resume_data['experience_years']} years
- Education: {', '.join(resume_data['education'])}

The job requires:
- Skills: {', '.join(job_data['skills'])}
- Experience: {job_data['required_experience']} years
- Education: {job_data['education']}

Give 4 personalized suggestions in JSON format. Example:
{{
  "skills_to_learn": ["skill1", "skill2"],
  "experience_gaps": ["gap1", "gap2"],
  "education_advice": ["advice1", "advice2"],
  "resume_tips": ["tip1", "tip2"]
}}"""
    }
]

    prompt = pipe.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=1024, do_sample=True, temperature=0.7, top_k=50, top_p=0.95)
    raw_result =outputs[0]["generated_text"]
    parsed_result = extract_last_json_block(raw_result)
    return parsed_result
   

resume = {'skills': ['Python', 'ReactJS'], 'experience_years': 1, 'education': ['B.Tech IT']}
job = {'skills': ['Python', 'AWS'], 'required_experience': 3, 'education': 'M.Tech CSE'}

result = generate_resume_suggestions(resume, job)
print(result)


# Install transformers from source - only needed for versions <= v4.34
# pip install git+https://github.com/huggingface/transformers.git
# pip install accelerate



# We use the tokenizer's chat template to format each message - see https://huggingface.co/docs/transformers/main/en/chat_templating
messages = [
    {
        "role": "system",
        "content": "You are a friendly chatbot who always responds in the style of a pirate",
    },
    {"role": "user", "content": "How many helicopters can a human eat in one sitting?"},
]

# <|system|>
# You are a friendly chatbot who always responds in the style of a pirate.</s>
# <|user|>
# How many helicopters can a human eat in one sitting?</s>
# <|assistant|>
# Ah, me hearty matey! But yer question be a puzzler! A human cannot eat a helicopter in one sitting, as helicopters are not edible. They be made of metal, plastic, and other materials, not food!
