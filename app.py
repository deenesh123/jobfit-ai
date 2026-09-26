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

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="JobFit AI – Smart Resume Tailor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Usage Limit System (Free Tier)
# -----------------------------
FREE_LIMIT = 3   # Free generations per day

def get_today_key():
    return f"usage_{date.today().isoformat()}"

def get_usage_count():
    key = get_today_key()
    return st.session_state.get(key, 0)

def increment_usage():
    key = get_today_key()
    st.session_state[key] = get_usage_count() + 1

def can_generate():
    return get_usage_count() < FREE_LIMIT

# -----------------------------
# Header
# -----------------------------
st.title("🎯 JobFit AI")
st.markdown("### Tailor your resume to any job description in seconds")
st.caption("Upload resume + paste job description → Get match score, tailored resume & cover letter")

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    api_key = st.text_input(
        "API Key (OpenAI / Groq / OpenRouter)",
        type="password",
        help="Get a free key from console.groq.com (recommended) or platform.openai.com"
    )

    provider = st.selectbox(
        "Provider",
        ["Groq", "OpenAI", "OpenRouter"],
        index=0
    )

    if provider == "OpenAI":
        model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], index=0)
        base_url = None
    elif provider == "Groq":
        model = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"], index=0)
        base_url = "https://api.groq.com/openai/v1"
    else:  # OpenRouter
        model = st.selectbox("Model", ["openai/gpt-4o-mini", "meta-llama/llama-3.3-70b-instruct"], index=0)
        base_url = "https://openrouter.ai/api/v1"

    st.markdown("---")
    used = get_usage_count()
    remaining = max(0, FREE_LIMIT - used)
    st.metric("Free Generations Left Today", f"{remaining} / {FREE_LIMIT}")

    if remaining == 0:
        st.warning("Daily free limit reached. Come back tomorrow or upgrade later.")

    st.markdown("---")
    st.markdown("**Recommended**")
    st.markdown("- Use **Groq** → Fast + generous free tier")
    st.markdown("- `llama-3.3-70b-versatile` works great")
    st.caption("Built for portfolio + side income 🚀")

# -----------------------------
# Main Input Area
# -----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    uploaded_file = st.file_uploader(
        "Upload PDF Resume",
        type=["pdf"],
        help="Only PDF files are supported"
    )

    resume_text = ""
    if uploaded_file is not None:
        with st.spinner("Extracting text from PDF..."):
            resume_text = extract_text_from_pdf(uploaded_file)

        if resume_text.startswith("Error"):
            st.error(resume_text)
        else:
            with st.expander("✅ Extracted Resume Text", expanded=False):
                st.text_area("Resume content", resume_text, height=220, label_visibility="collapsed")

with col2:
    st.subheader("💼 Job Description")
    job_description = st.text_area(
        "Paste the full job description here",
        height=280,
        placeholder="Copy the entire job posting and paste it here..."
    )
    company_name = st.text_input("Company Name (optional)", value="the company")

# -----------------------------
# Generate Button
# -----------------------------
st.markdown("---")

if not can_generate():
    st.button("🚀 Daily Free Limit Reached", disabled=True, use_container_width=True)
    st.info("You have used all 3 free generations for today. Come back tomorrow!")
else:
    generate = st.button("🚀 Analyze & Generate Tailored Resume", type="primary", use_container_width=True)

    if generate:
        if not api_key:
            st.error("⚠️ Please enter your API key in the sidebar.")
        elif not resume_text or resume_text.startswith("Error"):
            st.error("⚠️ Please upload a valid PDF resume.")
        elif not job_description.strip():
            st.error("⚠️ Please paste a job description.")
        else:
            # Create client
            client_kwargs = {"api_key": api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            client = OpenAI(**client_kwargs)

            progress = st.progress(0)
            status = st.empty()

            try:
                # 1. Analysis
                status.info("📊 Analyzing match score...")
                progress.progress(20)

                analysis_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": get_analysis_prompt(resume_text, job_description)}
                    ],
                    temperature=0.3
                )
                analysis_result = analysis_response.choices[0].message.content

                # 2. Tailored Resume
                status.info("📝 Rewriting your resume...")
                progress.progress(55)

                tailored_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": get_tailored_resume_prompt(resume_text, job_description)}
                    ],
                    temperature=0.4
                )
                tailored_resume = tailored_response.choices[0].message.content

                # 3. Cover Letter
                status.info("✉️ Writing cover letter...")
                progress.progress(85)

                cover_response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": get_cover_letter_prompt(resume_text, job_description, company_name)}
                    ],
                    temperature=0.5
                )
                cover_letter = cover_response.choices[0].message.content

                progress.progress(100)
                status.success("✅ Done! Scroll down to see results.")

                # Count this generation
                increment_usage()

                # Store in session for downloads
                st.session_state["last_analysis"] = analysis_result
                st.session_state["last_resume"] = tailored_resume
                st.session_state["last_cover"] = cover_letter

            except Exception as e:
                st.error(f"❌ Something went wrong: {str(e)}")
                st.info("Common fixes: Check API key, model name, or try a different provider.")

# -----------------------------
# Results Section
# -----------------------------
if "last_analysis" in st.session_state:
    st.markdown("---")
    st.subheader("🎉 Your Results")

    tab1, tab2, tab3 = st.tabs(["📊 Match Analysis", "📝 Tailored Resume", "✉️ Cover Letter"])

    with tab1:
        st.markdown(st.session_state["last_analysis"])

    with tab2:
        st.markdown(st.session_state["last_resume"])

        col_a, col_b = st.columns(2)
        with col_a:
            st.download_button(
                label="⬇️ Download as Markdown",
                data=st.session_state["last_resume"],
                file_name="tailored_resume.md",
                mime="text/markdown",
                use_container_width=True
            )
        with col_b:
            try:
                pdf_bytes = create_pdf_from_text(st.session_state["last_resume"], title="Tailored Resume")
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_bytes,
                    file_name="tailored_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"PDF generation failed: {e}")

    with tab3:
        st.markdown(st.session_state["last_cover"])

        col_c, col_d = st.columns(2)
        with col_c:
            st.download_button(
                label="⬇️ Download as Text",
                data=st.session_state["last_cover"],
                file_name="cover_letter.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_d:
            try:
                pdf_bytes = create_pdf_from_text(st.session_state["last_cover"], title="Cover Letter")
                st.download_button(
                    label="📄 Download as PDF",
                    data=pdf_bytes,
                    file_name="cover_letter.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"PDF generation failed: {e}")
