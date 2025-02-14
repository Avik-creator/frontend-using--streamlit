import streamlit as st
import os, json
import time  # Simulate delay for the model processing
from translator_script import process_uploaded_file
from Parsing import *
import streamlit_scrollable_textbox as stx
import modelbit

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


# Mock function to simulate model processing
# def process_with_model(resume_text, job_role):
#     time.sleep(5)  # Simulate a delay for processing
#     probability = 75  # Mock match probability
#     suggestions = [
#         "Add more relevant skills",
#         "Highlight leadership experiences",
#         "Optimize your resume for keywords from the job description",
#     ]

#     if saved_path_actual:
#         text = main_parse(saved_path_actual)
#         print(process_uploaded_file(text))
#         return probability, suggestions, text
def process_with_model(saved_path_actual, job_role):
    # Extract and process text
    if saved_path_actual:
        resume_text = main_parse(saved_path_actual)
        processed_result = process_uploaded_file(resume_text)
        # Simulate delay for processing
        probability = 75  # Mock match probability
        suggestions = [
            "Add more relevant skills",
            "Highlight leadership experiences",
            "Optimize your resume for keywords from the job description",
        ]
        return probability, suggestions, processed_result
    else:
        return None, None, None

def group_texts_by_label(data):
    grouped_data = {}
    data_json = json.loads(data)
    for item in data_json:
        # label = item['label']
        text = item['text']
        print(text)    
    #     # Initialize an array for the label if it doesn't exist
    #     if label not in grouped_data:
    #         grouped_data[label] = []
    #     # Append the text to the label's array
    #     grouped_data[label].append(text)

    # return grouped_data
    
def display_data_with_streamlit(data):
    """
    Displays a dictionary with labels as headers and texts as lists using Streamlit.
    """

    for label, texts in data.items():
        st.write(label)  # Display the label
        container = st.container(border=True)
        for text in texts:
            # st.markdown(f"- {text}")  # Display each text as a bulleted list
            container.write(f"- {text}")

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
    
    

    job_role = st.sidebar.selectbox(
        "Enter the Job Role You are targeting For",
        ["Backend", "Frontend", "Full Stack", "None"],
        key="jobrole"
    )

    if uploaded_file:
        saved_path = save_uploaded_file(uploaded_file)
        save_dir = os.path.join(PROJECT_ROOT)
        path = saved_path[1].split("/")
        print("PATH:", path, "PROJECT_ROOT:", PROJECT_ROOT)
        saved_path_actual = os.path.join(save_dir, str(path[0]))
        # print(1234)
        print(saved_path_actual)

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
            probability, suggestions, processed_result = process_with_model(saved_path_actual, job_role)

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
                        {int(probability)}%
                    </text>
                </svg>
            </div>
            """, unsafe_allow_html=True)

        # Improvement suggestions
        with col2:
            st.subheader("Resume Improvement Suggestions")
            for i, suggestion in enumerate(suggestions, 1):
                st.markdown(f"**{i}.** {suggestion}")
# <<<<<<< HEAD
        if saved_path:
            text = main_parse(saved_path_actual)
            st.write(process_uploaded_file(text))

        # Insert a line break
        st.markdown("-------------------------------------------------------------------------")
        st.subheader("Processed Resume")
        stx.scrollableTextbox(processed_result, height=400, fontFamily='monospace', border=True)
        json1 = modelbit.get_inference(
                    region="us-east-1.aws",
                    workspace="nirvikghosh",
                    deployment="ner",
                    data= processed_result
                )
        print("json1@1", json1)
        with open('myfile.json', 'w', encoding ='utf8') as json_file:
            json.dump(json1, json_file, allow_nan=True)

        st.divider()
        st.subheader("Labels & their texts")
        print("PROCESSED RES: ", processed_result)
        grouped_text_by_label_dict = group_texts_by_label(json1['data'])
        display_data_with_streamlit(grouped_text_by_label_dict)
        # stx.scrollableTextbox(grouped_text_by_label_dict, height=100, fontFamily='monospace', border=True)

       
# >>>>>>> c2d9d10acdcf57850703b52ee3eb10b54f8b3b22
    else:
        st.info("Please upload a resume and enter a job description in the sidebar.")


if __name__ == "__main__":
    main()
