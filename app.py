import streamlit as st
from openai import OpenAI
from utils import extract_text_from_pdf, create_pdf_from_text
from prompts import (
    SYSTEM_PROMPT,
    get_analysis_prompt,
    get_tailored_resume_prompt,
    get_cover_letter_prompt
)
from datetime import datetime, date
import uuid

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="JobFit AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Stylish CSS
# -----------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
        color: #e2e8f0;
    }

    h1, h2, h3, h4 {
        color: #f8fafc !important;
        font-weight: 700 !important;
    }

    p, label, .stMarkdown {
        color: #cbd5e1 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95) !important;
        border-right: 1px solid #334155;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
    }

    /* Input fields */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
    }

    /* Metric */
    [data-testid="stMetricValue"] {
        color: #a5b4fc !important;
        font-size: 1.7rem !important;
    }

    /* File uploader */
    [data-testid="stFileUploader"] {
        background: #1e293b;
        border-radius: 12px;
        border: 1px dashed #6366f1;
        padding: 1rem;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 10px;
        color: #94a3b8;
        border: 1px solid #334155;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #6366f1, #8b5cf6) !important;
        color: white !important;
    }

    /* Hide branding */
    #MainMenu, footer, header {visibility: hidden;}

    /* History cards */
    .history-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px 16px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .history-card:hover {
        border-color: #6366f1;
        background: #312e81;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Settings
# -----------------------------
FREE_LIMIT = 3
PRO_ACCESS_CODE = "JOBFIT-PRO-2026"
CHECKOUT_LINK = "https://jobfitai.lemonsqueezy.com/checkout/buy/4f8d5a00-09e7-4d9d-aac8-a51d62e1c2a2"

# Session helpers
def get_today_key():
    return f"usage_{date.today().isoformat()}"

def get_usage_count():
    return st.session_state.get(get_today_key(), 0)

def increment_usage():
    key = get_today_key()
    st.session_state[key] = get_usage_count() + 1

def is_pro_user():
    return st.session_state.get("is_pro", False)

def can_generate():
    if is_pro_user():
        return True
    return get_usage_count() < FREE_LIMIT

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("### 👤 Sign In")
    name = st.text_input("Your Name", value=st.session_state.user_name, placeholder="Enter your name")
    if name:
        st.session_state.user_name = name
        st.success(f"Welcome, {name}!")

    st.markdown("---")
    st.markdown("### ⚙️ Settings")

    api_key = st.text_input("API Key (Groq)", type="password", placeholder="gsk_...")
    
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
    st.markdown("### 🔑 Pro Access")
    pro_code = st.text_input("Pro Access Code", type="password", placeholder="Enter after payment")
    
    if pro_code == PRO_ACCESS_CODE:
        st.session_state["is_pro"] = True
        st.success("✅ Pro Unlocked!")
    elif pro_code:
        st.error("Invalid code")

    st.markdown("---")
    
    if is_pro_user():
        st.success("🚀 Pro User (Unlimited)")
    else:
        remaining = max(0, FREE_LIMIT - get_usage_count())
        st.metric("Free Left Today", f"{remaining}/{FREE_LIMIT}")
        if remaining == 0:
            st.link_button("💎 Upgrade to Pro (₹799/mo)", CHECKOUT_LINK, use_container_width=True)

    # History Section
    st.markdown("---")
    st.markdown("### 📜 History")
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history[-8:])):  # show last 8
            label = f"{item['time']} • {item['preview']}"
            if st.button(label, key=f"hist_{i}", use_container_width=True):
                st.session_state["last_analysis"] = item["analysis"]
                st.session_state["last_resume"] = item["resume"]
                st.session_state["last_cover"] = item["cover"]
                st.rerun()
    else:
        st.caption("No history yet")

# -----------------------------
# Main Header
# -----------------------------
st.markdown("""
<div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
    <div style="background: linear-gradient(135deg, #6366f1, #8b5cf6); 
                width:52px; height:52px; border-radius:14px; 
                display:flex; align-items:center; justify-content:center;
                font-size:26px; box-shadow: 0 4px 15px rgba(99,102,241,0.4);">🎯</div>
    <div>
        <h1 style="margin:0; padding:0; font-size:2.2rem;">JobFit AI</h1>
        <p style="margin:0; color:#94a3b8; font-size:0.95rem;">Tailor your resume in seconds</p>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Input Area
# -----------------------------
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("#### 📄 Your Resume")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    
    resume_text = ""
    if uploaded_file:
        with st.spinner("Extracting text..."):
            resume_text = extract_text_from_pdf(uploaded_file)
        if resume_text and not resume_text.startswith("Error"):
            with st.expander("View extracted text"):
                st.text_area("", resume_text, height=180, label_visibility="collapsed")

with col2:
    st.markdown("#### 💼 Job Description")
    job_description = st.text_area("Paste job description", height=260, 
                                   placeholder="Paste the full job posting here...",
                                   label_visibility="collapsed")
    company_name = st.text_input("Company Name (optional)", value="the company")

st.markdown("<br>", unsafe_allow_html=True)

# Generate
if not can_generate():
    st.warning("Free daily limit reached.")
    st.link_button("💎 Upgrade to Pro – Unlimited Access", CHECKOUT_LINK, use_container_width=True)
else:
    if st.button("🚀 Analyze & Generate", type="primary", use_container_width=True):
        if not api_key:
            st.error("Please enter your API key.")
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
                status.info("📊 Analyzing match...")
                progress.progress(25)
                analysis = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT},
                              {"role": "user", "content": get_analysis_prompt(resume_text, job_description)}],
                    temperature=0.3
                ).choices[0].message.content

                status.info("📝 Rewriting resume...")
                progress.progress(55)
                tailored = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT},
                              {"role": "user", "content": get_tailored_resume_prompt(resume_text, job_description)}],
                    temperature=0.4
                ).choices[0].message.content

                status.info("✉️ Writing cover letter...")
                progress.progress(85)
                cover = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": SYSTEM_PROMPT},
                              {"role": "user", "content": get_cover_letter_prompt(resume_text, job_description, company_name)}],
                    temperature=0.5
                ).choices[0].message.content

                progress.progress(100)
                status.success("✅ Done!")

                if not is_pro_user():
                    increment_usage()

                # Save to history
                preview = (job_description[:40] + "...") if len(job_description) > 40 else job_description
                st.session_state.history.append({
                    "id": str(uuid.uuid4()),
                    "time": datetime.now().strftime("%H:%M"),
                    "preview": preview,
                    "analysis": analysis,
                    "resume": tailored,
                    "cover": cover
                })

                st.session_state["last_analysis"] = analysis
                st.session_state["last_resume"] = tailored
                st.session_state["last_cover"] = cover

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Results
if "last_analysis" in st.session_state:
    st.markdown("---")
    st.markdown("### 🎉 Results")

    tab1, tab2, tab3 = st.tabs(["📊 Analysis", "📝 Tailored Resume", "✉️ Cover Letter"])

    with tab1:
        st.markdown(st.session_state["last_analysis"])

    with tab2:
        st.markdown(st.session_state["last_resume"])
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Markdown", st.session_state["last_resume"], "tailored_resume.md", use_container_width=True)
        with c2:
            try:
                pdf = create_pdf_from_text(st.session_state["last_resume"], "Tailored Resume")
                st.download_button("📄 PDF", pdf, "tailored_resume.pdf", "application/pdf", use_container_width=True)
            except:
                pass

    with tab3:
        st.markdown(st.session_state["last_cover"])
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Text", st.session_state["last_cover"], "cover_letter.txt", use_container_width=True)
        with c2:
            try:
                pdf = create_pdf_from_text(st.session_state["last_cover"], "Cover Letter")
                st.download_button("📄 PDF", pdf, "cover_letter.pdf", "application/pdf", use_container_width=True)
            except:
                pass

st.markdown("<br><div style='text-align:center; color:#64748b; font-size:0.85rem;'>JobFit AI • Built for job seekers</div>", unsafe_allow_html=True)
