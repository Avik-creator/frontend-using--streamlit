import streamlit as st
import os
import time  # Simulate delay for the model processing


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
def process_with_model(resume_text, job_description):
    time.sleep(5)  # Simulate a delay for processing
    probability = 75  # Mock match probability
    suggestions = [
        "Add more relevant skills",
        "Highlight leadership experiences",
        "Optimize your resume for keywords from the job description",
    ]
    return probability, suggestions


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
    job_description = st.sidebar.text_area(
        "Enter the Job Description", 
        height=400, 
        help="Enter the job description for which you want to predict the job fit"
    )

    if uploaded_file:
        save_uploaded_file(uploaded_file)

    st.title("Analysis Results")

    if uploaded_file and job_description:
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
        with st.spinner("Analyzing your resume and job description..."):
            probability, suggestions = process_with_model(resume_text, job_description)

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

    else:
        st.info("Please upload a resume and enter a job description in the sidebar.")


if __name__ == "__main__":
    main()
