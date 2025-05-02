import streamlit as st
import os, json
import time  # Simulate delay for the model processing
from translator_script import process_uploaded_file
from Parsing import *
from Final_model import *
import streamlit_scrollable_textbox as stx
import modelbit
from collections import defaultdict

#Global variable to get the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
saved_path_actual = ""

def save_uploaded_file(uploaded_file, upload_dir="uploads"):
    try:
        # Create the directory if it doesn't exist
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)

        # Save the file to the directory
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        

        # Return the directory and file path
        return upload_dir, file_path

    except Exception as e:
        st.error(f"An error occurred while saving the file: {e}")
        return None, None


def process_with_model(saved_path_actual, job_descrip):
    # Extract and process text
    if saved_path_actual:
        resume_text = main_parse(saved_path_actual)
        processed_result = process_uploaded_file(resume_text)
        
        # Process with modelbit to get JSON data
        json_data = modelbit.get_inference(
            region="us-east-1.aws",
            workspace="nirvikghosh",
            deployment="ner",
            data=processed_result
        )
        
        # Save JSON data to file
        with open('myfile.json', 'w', encoding='utf8') as json_file:
            json.dump(json_data, json_file, allow_nan=True)
        
        job_api_output = modelbit.get_inference(
            region = "us-east-1.aws",
            workspace="nirvikghosh",
            deployment = "jobapi",
            data = job_descrip
        )
        # print(job_api_output)
        
        # Get the actual score from final_main
        final_score = final_main(json_data,job_api_output)
        
        # Suggestions (can be improved later to be dynamic based on the score)
        suggestions = [
            "Add more relevant skills",
            "Highlight leadership experiences",
            "Optimize your resume for keywords from the job description",
        ]
        
        return final_score, suggestions, processed_result, json_data
    else:
        return None, None, None, None

def group_texts_by_label(data):
    if isinstance(data, str):
        data = json.loads(data)
    
    grouped_data = {}
    for item in data:
        label = item.get('label')
        text = item.get('text')

        # Initialize an array for the label if it doesn't exist
        if label not in grouped_data:
            grouped_data[label] = []
        # Append the text to the label's array
        grouped_data[label].append(text)

    return grouped_data
    


def display_data_with_streamlit(json_data):
    """
    Displays structured JSON data with labels as headers and grouped texts using Streamlit.
    """
    
    # Group data by label
    grouped_data = defaultdict(list)
    for item in json_data['data']:
        label = item['label']
        text = item['text']
        
        # Check if label contains "SKILL:"
        if "SKILL:" in label:
            skill_name = label.replace("SKILL: ", "").strip()
            grouped_data["Skills".lower()].append(f"{skill_name}")
        else:
            grouped_data[label.lower()].append(text)
    
    # Display each label as a section with a bordered container
    st.title("Extracted Data")
    for label, texts in grouped_data.items():
        st.subheader(label.title())
        if label == "Skills".lower():
            with st.container():
                for text in texts:
                    st.write(text)
        else:
            for text in texts:
                st.write(f"{text}")

def display_json(json_data):
    st.json(json_data)

def main():
    st.set_page_config(page_title="Job Fit Predictor", page_icon=":shark:", layout="wide")
    st.sidebar.title("Resume Upload")

    uploaded_file = st.sidebar.file_uploader(
        "Upload your Resume", 
        type=['pdf', 'png', 'jpg', 'jpeg', 'md'], 
        help='Upload your resume in PDF, Image or Markdown Format',
        key="fileuploader",
        accept_multiple_files=False
    )
    st.sidebar.title("Job Description")
    
    

    # job_role = st.sidebar.selectbox(
    #     "Enter the Job Role You are targeting For",
    #     ["Backend", "Frontend", "Full Stack", "None"],
    #     key="jobrole"
    # )

    job_role = st.sidebar.text_input(
        "Enter the Job Role posted in the Job Description",
        help="Enter the job role you are targeting for. e.g. Data Scientist, Software Engineer, etc.",
        placeholder="e.g. We are looking for a Data Scientist with 5+ years of experience in Python and SQL",
        key="jobrole"
    )

    if uploaded_file:
        saved_path = save_uploaded_file(uploaded_file)

        save_dir = os.path.join(PROJECT_ROOT)
        path = saved_path[1].split("/")
        # path = path[0].split("\\") #Applicable only for Rudra's computer
        saved_path_actual = os.path.join(save_dir, str(path[0]), str(path[1]))

    st.title("Analysis Results")

    if uploaded_file and job_role:
        # Extract text based on file type
        if uploaded_file.type == 'application/pdf':
            resume_text = "Extracted Text from PDF"
        elif uploaded_file.type in ['image/png', 'image/jpeg', 'image/jpg']:
            resume_text = "Extracted Text from Image"
        elif uploaded_file.type == 'text/markdown':
            resume_text = "Extracted Text from Markdown"
        else:
            st.error("Unsupported file type")
            return

        # Show a spinner while the model processes
        with st.spinner("Analyzing your resume with the Job Role..."):
            probability, suggestions, processed_result, json_data = process_with_model(saved_path_actual, job_role)

        # Display the results after processing
        col1, col2 = st.columns(2)
        
        # Probability visualization
        with col1:
            st.subheader("Match Probability")
            st.markdown(f"""
            <div style="position:relative; width:300px; height:300px;">
                <svg width="300" height="300" viewBox="0 0 300 300">
                    <circle cx="150" cy="150" r="140" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                    <circle cx="150" cy="150" r="140" fill="none" stroke="#4CAF50" stroke-width="20"
                            stroke-dasharray="880" stroke-dashoffset="{880 * (1 - probability/100)}"
                            style="transition: stroke-dashoffset 1s ease-in-out;"/>
                    <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="50" font-weight="bold" fill="#ffffff">
                        {round(probability)}%
                    </text>
                </svg>
            </div>
            """, unsafe_allow_html=True)

        # Improvement suggestions
        with col2:
            st.subheader("Resume Improvement Suggestions")
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"**{i}.** {suggestion}")

        # Insert a line break
        st.markdown("-------------------------------------------------------------------------")
        
        st.divider()
        st.subheader("Labels & their texts")
        tab1, tab2, tab3 = st.tabs(["Processed Resume", "Displaying JSON Data in Formatted Way", "Displaying JSON"])
        with tab1:
            stx.scrollableTextbox(processed_result, height=400, fontFamily='monospace', border=True)
        with tab2:
            display_data_with_streamlit(json_data)
        with tab3:
            display_json(json_data)
       
    else:
        st.info("Please upload a resume and enter a job description in the sidebar.")


if __name__ == "__main__":
    main()
