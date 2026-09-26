import streamlit as st
from openai import OpenAI
from utils import extract_text_from_pdf, create_pdf_from_text
from prompts import (
    SYSTEM_PROMPT,
    get_analysis_prompt,
    get_tailored_resume_prompt,
    get_cover_letter_prompt
)
from datetime import date

# Page Config
st.set_page_config(
    page_title="JobFit AI – Smart Resume Tailor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional Design
st.markdown("""
<style>
    /* Background */
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }

    /* Main title */
    h1 {
        color: #0f172a !important;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        letter-spacing: -0.5px;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.6rem !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.35) !important;
        transition: all 0.25s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.45) !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #e0e7ff !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label {
        color: #c7d2fe !important;
        font-weight: 500 !important;
    }

    /* Metric */
    [data-testid="stMetricValue"] {
        color: #a5b4fc !important;
        font-size: 1.9rem !important;
        font-weight: 700 !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 14px;
        padding: 1.2rem;
        border: 2px dashed #a5b4fc;
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Card style for results */
    .stTabs [data-baseweb="tab"] {
        background-color: white;
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        padding: 10px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #4f46e5, #7c3aed) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Usage Limit
FREE_LIMIT = 3

def get_today_key():
    return f"usage_{date.today().isoformat()}"

def get_usage_count():
    return st.session_state.get(get_today_key(), 0)

def increment_usage():
    key = get_today_key()
    st.session_state[key] = get_usage_count() + 1

def can_generate():
    return get_usage_count() < FREE_LIMIT

# Header
st.markdown("""
<div style="display:flex; align-items:center; gap:12px; margin-bottom: 5px;">
    <div style="background: linear-gradient(135deg, #4f46e5, #7c3aed); 
                width:48px; height:48px; border-radius:12px; 
                display:flex; align-items:center; justify-content:center;
                font-size:24px;">🎯</div>
    <div>
        <h1 style="margin:0; padding:0;">JobFit AI</h1>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("##### Tailor your resume to any job description in seconds")
st.caption("Upload your resume + paste a job description → Get match score, tailored resume & cover letter")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    api_key = st.text_input("API Key", type="password", placeholder="gsk_...")
    
    provider = st.selectbox("Provider", ["Groq", "OpenAI", "OpenRouter"], index=0)

    if provider == "OpenAI":
        model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
        base_url = None
    elif provider == "Groq":
        model = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)
        base_url = "https://api.groq.com/openai/v1"
    else:
        model = st.selectbox("Model", ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct"], index=0)
        base_url = "https://openrouter.ai/api/v1"

    st.markdown("---")
    remaining = max(0, FREE_LIMIT - get_usage_count())
    st.metric("Free Generations Left", f"{remaining} / {FREE_LIMIT}")

    if remaining == 0:
        st.warning("Daily limit reached. Come back tomorrow!")

    st.markdown("---")
    st.markdown("**Recommended Setup**")
    st.markdown("- Provider: **Groq**")
    st.markdown("- Model: `llama-3.3-70b-versatile`")
    st.caption("Free • Fast • High quality")

# Main Content
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### 📄 Your Resume")
    uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"])
    
    resume_text = ""
    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            resume_text = extract_text_from_pdf(uploaded_file)
        if resume_text and not resume_text.startswith("Error"):
            with st.expander("✅ View extracted text"):
                st.text_area("", resume_text, height=200, label_visibility="collapsed")

with col2:
    st.markdown("#### 💼 Job Description")
    job_description = st.text_area("Paste the full job description here", height=280,
                                   placeholder="Copy the entire job posting and paste it here...")
    company_name = st.text_input("Company Name (optional)", value="the company")

st.markdown("<br>", unsafe_allow_html=True)

# Generate Button
if not can_generate():
    st.button("🚀 Daily Free Limit Reached", disabled=True, use_container_width=True)
    st.info("You have used all 3 free generations for today.")
else:
    if st.button("🚀 Analyze & Generate Tailored Resume", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter your API key in the sidebar.")
        elif not resume_text or resume_text.startswith("Error"):
            st.error("Please upload a valid PDF resume.")
        elif not job_description.strip():
            st.error("Please paste a job description.")
        else:
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            client = OpenAI(**client_kwargs)

            progress = st.progress(0)
            status = st.empty()

            try:
                status.info("📊 Analyzing match score...")
                progress.progress(25)
                analysis = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": get_analysis_prompt(resume_text, job_description)}
                    ],
                    temperature=0.3
                ).choices[0].message.content

                status.info("📝 Rewriting your resume...")
                progress.progress(55)
                tailored = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": get_tailored_resume_prompt(resume_text, job_description)}
                    ],
                    temperature=0.4
                ).choices[0].message.content

                status.info("✉️ Writing cover letter...")
                progress.progress(85)
                cover = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": get_cover_letter_prompt(resume_text, job_description, company_name)}
                    ],
                    temperature=0.5
                ).choices[0].message.content

                progress.progress(100)
                status.success("✅ Done! Scroll down to see results.")
                increment_usage()

                st.session_state["last_analysis"] = analysis
                st.session_state["last_resume"] = tailored
                st.session_state["last_cover"] = cover

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Results
if "last_analysis" in st.session_state:
    st.markdown("---")
    st.markdown("### 🎉 Your Results")

    tab1, tab2, tab3 = st.tabs(["📊 Match Analysis", "📝 Tailored Resume", "✉️ Cover Letter"])

    with tab1:
        st.markdown(st.session_state["last_analysis"])

    with tab2:
        st.markdown(st.session_state["last_resume"])
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download Markdown", st.session_state["last_resume"], 
                               "tailored_resume.md", use_container_width=True)
        with c2:
            try:
                pdf = create_pdf_from_text(st.session_state["last_resume"], "Tailored Resume")
                st.download_button("📄 Download PDF", pdf, "tailored_resume.pdf", 
                                   "application/pdf", use_container_width=True)
            except:
                pass

    with tab3:
        st.markdown(st.session_state["last_cover"])
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download Text", st.session_state["last_cover"], 
                               "cover_letter.txt", use_container_width=True)
        with c2:
            try:
                pdf = create_pdf_from_text(st.session_state["last_cover"], "Cover Letter")
                st.download_button("📄 Download PDF", pdf, "cover_letter.pdf", 
                                   "application/pdf", use_container_width=True)
            except:
                pass

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#64748b; font-size:0.9rem;'>"
    "Built with ❤️ using Streamlit & Groq • JobFit AI"
    "</div>",
    unsafe_allow_html=True
)
