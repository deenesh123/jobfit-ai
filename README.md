# 🎯 JobFit AI – Smart Resume Tailor (Upgraded)

A complete AI-powered resume tailoring tool that you can deploy and monetize.

### What it does
- Upload any PDF resume
- Paste a job description
- Get:
  - Match Score + detailed analysis
  - Fully rewritten tailored resume
  - Professional cover letter
- Download both as **Markdown** and **real PDF**

### New Features in this version
- ✅ Real PDF download (Resume + Cover Letter)
- ✅ Free daily usage limit (3 generations / day) – ready for monetization
- ✅ Support for Groq, OpenAI & OpenRouter
- ✅ Clean modern UI
- ✅ Session-based results (no re-generation needed for downloads)

---

## Quick Start (Local)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL and put your API key in the sidebar.

**Recommended API**: Groq (console.groq.com) → free + very fast.

---

## Deploy for Free (Public Link)

### Streamlit Community Cloud (Easiest)

1. Create a new public GitHub repository
2. Upload all files from this folder
3. Go to → https://share.streamlit.io
4. Click **New app** → select your repo → Main file: `app.py`
5. Deploy

Your live link will be: `https://your-username-jobfit-ai.streamlit.app`

---

## Project Structure

```
jobfit-ai/
├── app.py              # Main application (with limits + PDF)
├── prompts.py          # High-quality AI prompts
├── utils.py            # PDF extraction + PDF generation
├── requirements.txt
├── .gitignore
└── README.md
```

---

## How to Monetize Later

1. Keep the free limit at 3/day
2. Add a "Upgrade to Pro" button (Stripe / Lemon Squeezy)
3. Pro users get unlimited generations + better models
4. Price recommendation: **$9 – $12 / month**

---

## License
MIT – You can use, modify, and sell this freely.
