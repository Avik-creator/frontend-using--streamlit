import streamlit as st
import os, json
import time  # Simulate delay for the model processing
from translator_script import process_uploaded_file
from Parsing import *
from Final_model import *
import streamlit_scrollable_textbox as stx
import modelbit
from collections import defaultdict

# Set page config must be the first Streamlit command
st.set_page_config(page_title="Job Fit Predictor", page_icon="🎯", layout="wide")

# Global variable to get the path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
saved_path_actual = ""

# Custom CSS for better UI with animations
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Base styles */
    body {
        font-family: 'Inter', sans-serif;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }

    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }

    /* Main container */
    .main {
        padding: 2rem;
        animation: fadeIn 0.5s ease-out;
    }

    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: var(--background-color);
        padding: 2rem 1.5rem;
        animation: slideIn 0.5s ease-out;
    }

    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: var(--text-color);
        text-align: left;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        animation: fadeIn 0.5s ease-out;
    }

    /* Button styling */
    .stButton>button {
        width: 100%;
        background-color: var(--primary-color);
        color: white;
        padding: 0.8rem 1.5rem;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px var(--shadow-color);
        position: relative;
        overflow: hidden;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px var(--shadow-color);
    }

    .stButton>button:active {
        transform: translateY(0);
    }

    .stButton>button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }

    .stButton>button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }

    @keyframes ripple {
        0% {
            transform: scale(0, 0);
            opacity: 0.5;
        }
        100% {
            transform: scale(20, 20);
            opacity: 0;
        }
    }

    /* Loading animation */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
    }

    .loading-spinner {
        width: 40px;
        height: 40px;
        border: 3px solid var(--border-color);
        border-top: 3px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin-bottom: 1rem;
    }

    .loading-text {
        color: var(--text-color);
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 500;
    }

    /* Progress steps */
    .progress-steps {
        display: flex;
        justify-content: space-between;
        margin: 2rem 0;
        position: relative;
    }

    .progress-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 1;
    }

    .step-number {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: var(--secondary-background-color);
        border: 2px solid var(--primary-color);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
    }

    .step-active .step-number {
        background-color: var(--primary-color);
        color: white;
        animation: pulse 2s infinite;
    }

    .step-label {
        font-size: 0.9rem;
        color: var(--text-color);
        text-align: center;
    }

    /* Result container */
    .result-container {
        padding: 2.5rem;
        border-radius: 12px;
        background-color: var(--secondary-background-color);
        box-shadow: 0 6px 18px var(--shadow-color);
        margin: 2rem 0;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid var(--border-color);
    }

    /* Match probability circle */
    .match-probability-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem 0;
    }

    .match-probability-container svg {
        animation: fadeIn 0.5s ease-out;
    }

    .match-probability-container svg circle {
        transition: stroke-dashoffset 1s ease-in-out;
    }

    /* Suggestions list */
    .suggestions-list {
        padding-left: 0;
        margin-top: 0.5rem;
    }

    .suggestions-list li {
        background-color: var(--secondary-background-color);
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
        border-radius: 8px;
        border-left: 5px solid var(--primary-color);
        color: var(--text-color);
        list-style-type: none;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
        border: 1px solid var(--border-color);
    }

    .suggestions-list li:hover {
        transform: translateX(5px);
        box-shadow: 0 2px 8px var(--shadow-color);
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        border-bottom: 2px solid var(--border-color);
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 0.9rem 1.4rem;
        background-color: transparent;
        border-radius: 8px 8px 0 0;
        color: var(--text-color);
        font-weight: 600;
        font-size: 1rem;
        border: none;
        border-bottom: 3px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--primary-color);
        transform: translateY(-2px);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: transparent;
        color: var(--primary-color);
        font-weight: 700;
        border-bottom: 3px solid var(--primary-color);
    }

    .stTabs [data-baseweb="tab-panel"] {
        padding: 2rem;
        background-color: var(--secondary-background-color);
        border-radius: 0 0 10px 10px;
        border: 1px solid var(--border-color);
        border-top: none;
        margin-top: -2px;
        box-shadow: 0 4px 12px var(--shadow-color);
        animation: fadeIn 0.5s ease-out;
    }

    /* Skill items */
    .skill-item {
        display: inline-block;
        background-color: var(--secondary-background-color);
        color: var(--primary-color);
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
        margin: 0.3rem;
        border: 1px solid var(--primary-color);
        transition: all 0.3s ease;
        animation: fadeIn 0.5s ease-out;
    }

    .skill-item:hover {
        transform: scale(1.05);
        box-shadow: 0 2px 8px var(--shadow-color);
    }

    /* Scrollable textbox */
    div[data-testid="stScrollableTextbox"] > div {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        background-color: var(--secondary-background-color);
        animation: fadeIn 0.5s ease-out;
    }

    div[data-testid="stScrollableTextbox"] textarea {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace !important;
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important;
        font-size: 0.95rem !important;
        padding: 1rem !important;
        line-height: 1.6 !important;
    }

    /* Progress bar styling */
    .progress-container {
        padding: 2rem;
        text-align: center;
        animation: fadeIn 0.5s ease-out;
    }

    .progress-bar-container {
        width: 100%;
        height: 8px;
        background-color: var(--border-color);
        border-radius: 4px;
        margin: 1rem 0;
        overflow: hidden;
    }

    .progress-bar {
        height: 100%;
        background-color: var(--primary-color);
        border-radius: 4px;
        transition: width 0.5s ease-in-out;
    }

    .progress-text {
        color: var(--text-color);
        font-size: 1rem;
        font-weight: 500;
        margin-bottom: 0.5rem;
    }

    .progress-step {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        opacity: 0.5;
        transition: opacity 0.3s ease;
    }

    .progress-step.active {
        opacity: 1;
    }

    .progress-step.completed {
        opacity: 0.8;
    }

    .progress-step-icon {
        margin-right: 0.5rem;
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

def create_progress_bar(phase, progress):
    """Create a progress bar with current phase and progress"""
    phases = [
        "Extracting Text from Resume",
        "Processing Text",
        "Running AI Analysis",
        "Analyzing Job Description",
        "Calculating Final Score"
    ]
    
    progress_html = f"""
        <div class="progress-container">
            <div class="progress-text">Processing your resume...</div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: {progress}%"></div>
            </div>
    """
    
    for i, p in enumerate(phases):
        status = "completed" if i < phases.index(phase) else "active" if p == phase else ""
        icon = "✅" if i < phases.index(phase) else "🔄" if p == phase else "⏳"
        progress_html += f"""
            <div class="progress-step {status}">
                <span class="progress-step-icon">{icon}</span>
                <span>{p}</span>
            </div>
        """
    
    progress_html += "</div>"
    return progress_html

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
    # Create a placeholder for progress updates
    progress_placeholder = st.empty()
    progress_text = st.empty()
    
    # Phase 1: Text Extraction
    progress_text.text("Phase 1: Extracting Text from Resume")
    progress_placeholder.progress(20)
    resume_text = main_parse(saved_path_actual)
    time.sleep(0.5)
    
    # Phase 2: Text Processing
    progress_text.text("Phase 2: Processing Text")
    progress_placeholder.progress(40)
    processed_result = process_uploaded_file(resume_text)
    time.sleep(0.5)
    
    # Phase 3: Model Inference
    progress_text.text("Phase 3: Running AI Analysis")
    progress_placeholder.progress(60)
    json_data = modelbit.get_inference(
        region="us-east-1.aws",
        workspace="nirvikghosh",
        deployment="ner",
        data=processed_result
    )
    time.sleep(0.5)
    
    # Save JSON data to file
    with open('myfile.json', 'w', encoding='utf8') as json_file:
        json.dump(json_data, json_file, allow_nan=True)
    
    # Phase 4: Job Description Analysis
    progress_text.text("Phase 4: Analyzing Job Description")
    progress_placeholder.progress(80)
    job_api_output = modelbit.get_inference(
        region="us-east-1.aws",
        workspace="nirvikghosh",
        deployment="jobapi",
        data=job_descrip
    )
    time.sleep(0.5)
    
    # Phase 5: Final Scoring
    progress_text.text("Phase 5: Calculating Final Score")
    progress_placeholder.progress(100)
    final_score,suggestions = final_main(json_data, job_api_output)
    
    # Clear progress placeholders
    progress_placeholder.empty()
    progress_text.empty()
    
    # suggestions = [
    #     "Add more relevant skills",
    #     "Highlight leadership experiences",
    #     "Optimize your resume for keywords from the job description",
    # ]
    
    return final_score, suggestions, processed_result, json_data

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
    """Displays structured JSON data with labels as headers and grouped texts using Streamlit."""
    grouped_data = defaultdict(list)
    for item in json_data['data']:
        label = item['label']
        text = item['text']
        
        if "SKILL:" in label:
            skill_name = label.replace("SKILL: ", "").strip()
            grouped_data["Skills"].append(skill_name)
        else:
            grouped_data[label.lower()].append(text)
    
    st.title("Extracted Data")
    for label, texts in grouped_data.items():
        st.markdown(f'<div class="extracted-data-section">', unsafe_allow_html=True)
        st.markdown(f"<h3>{label.title()}</h3>", unsafe_allow_html=True)
        
        if label == "Skills":
            st.markdown('<div class="skill-item-container">', unsafe_allow_html=True)
            for text in texts:
                st.markdown(f'<span class="skill-item">{text}</span>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            for text in texts:
                st.markdown(f'<div class="text-item">{text}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_json(json_data):
    st.json(json_data)

def main():
    # Sidebar with improved styling
    with st.sidebar:
        st.title("📄 Resume Analysis")
        st.markdown("---")
        
        uploaded_file = st.file_uploader(
            "Upload your Resume", 
            type=['pdf', 'png', 'jpg', 'jpeg', 'md'], 
            help='Upload your resume in PDF, Image or Markdown Format',
            key="fileuploader",
            accept_multiple_files=False
        )
        
        st.markdown("---")
        st.title("🎯 Job Description")
        
        job_role = st.text_area(
            "Enter the Job Description",
            help="Enter the job description you are targeting for. e.g. Data Scientist, Software Engineer, etc.",
            placeholder="Paste the complete job description here...",
            key="jobrole",
            height=200
        )
        
        st.markdown("---")
        proceed_button = st.button("🚀 Start Analysis", type="primary")

    # Main content area
    st.title("🎯 Job Fit Analysis")
    
    if uploaded_file and job_role:
        save_dir = os.path.join(PROJECT_ROOT)
        path = save_uploaded_file(uploaded_file)[1].split("/")
        # path = path[0].split("\\")
        saved_path_actual = os.path.join(save_dir, str(path[0]), str(path[1]))
        
        if proceed_button:
            # Process the resume and show results
            probability, suggestions, processed_result, json_data = process_with_model(saved_path_actual, job_role)
            
            # Results container
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            # Display results in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Match Probability")
                st.markdown(f"""
                <div class="match-probability-container">
                    <svg width="300" height="300" viewBox="0 0 300 300">
                        <circle cx="150" cy="150" r="140" fill="none" stroke="#e0e0e0" stroke-width="20"/>
                        <circle cx="150" cy="150" r="140" fill="none" stroke="#4CAF50" stroke-width="20"
                                stroke-dasharray="880" stroke-dashoffset="{880 * (1 - probability/100)}"
                                style="transition: stroke-dashoffset 1s ease-in-out;"/>
                        <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="50" font-weight="bold" fill="#333333">
                            {round(probability)}%
                        </text>
                    </svg>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.subheader("Resume Improvement Suggestions")

                # Mapping keys to user-friendly section headers
                section_headers = {
                    'skills_to_learn': "🧠 Skills to Learn",
                    'experience_gaps': "📉 Experience Gaps",
                    'education_advice': "🎓 Education Advice",
                    'resume_tips': "📄 Resume Tips"
                }

                for key, header in section_headers.items():
                    if suggestions.get(key):
                        st.markdown(f"### {header}")
                        for suggestion in suggestions[key]:
                            # Split into individual bullet points if newline-separated
                            points = suggestion.strip().split('\n- ')
                            for point in points:
                                if point:
                                    st.markdown(f"- {point.strip()}")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Detailed Analysis Section
            st.markdown("## 📝 Detailed Analysis")
            tab1, tab2, tab3 = st.tabs(["📄 Processed Resume", "🏷️ Formatted Data", "🔍 Raw JSON"])
            
            with tab1:
                stx.scrollableTextbox(processed_result, height=400, fontFamily='monospace', border=True)
            with tab2:
                display_data_with_streamlit(json_data)
            with tab3:
                display_json(json_data)
    else:
        st.info("👈 Please upload a resume and enter a job description in the sidebar, then click 'Start Analysis' to begin.")


if __name__ == "__main__":
    main()
