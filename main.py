import streamlit as st

def main():
    st.set_page_config(page_title="Job Fit Predictor", page_icon=":shark:", layout="wide")
    st.sidebar.title("Resume Upload")

    uploaded_file = st.sidebar.file_uploader("Upload your Resume", type=['pdf', 'png', 'jpg', 'jpeg', 'md'], help='Upload your resume in PDF, Image or Markdown Format', key="fileuploader",accept_multiple_files=False)
    st.sidebar.title("Job Description")
    job_description = st.sidebar.text_area("Enter the Job Description", height=400, help="Enter the job description for which you want to predict the job fit")

    st.title("Analysis Results")

    if uploaded_file and job_description:
            # Extract text based on file type
            if uploaded_file.type == 'application/pdf':
                resume_text = "Random Text from PDF"
            elif uploaded_file.type in ['image/png', 'image/jpeg', 'image/jpg']:
                resume_text = "Random Text from Image"
            elif uploaded_file.type == 'text/markdown':
                resume_text = "Random Text from Markdown"
            else:
                st.error("Unsupported file type")
                return

            # Calculate match probability
            probability = 90
            # Create two columns
            col1, col2 = st.columns(2)

            # Probability visualization
            with col1:
                st.subheader("Match Probability")
                # Create a circular progress bar
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
                suggestions = ["Add more relevant skills", "Add more relevant experience", "Add more relevant projects"]

                # Create numbered list of suggestions
                for i, suggestion in enumerate(suggestions, 1):
                    st.markdown(f"**{i}.** {suggestion}")

    else:
        st.info("Please upload a resume and enter a job description in the sidebar.")

if __name__ == "__main__":
    main()
