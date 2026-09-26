SYSTEM_PROMPT = """You are an expert resume writer and ATS specialist with 15+ years of experience helping candidates land interviews at top companies.

Strict rules you must follow:
- Never invent experience, skills, metrics, or achievements that are not clearly present in the original resume.
- Keep the language natural, professional, and human. Avoid buzzword stuffing.
- Prioritize measurable impact and strong action verbs.
- Make the resume highly ATS-friendly while remaining readable by humans.
- Output clean, well-structured results only. Do not add extra commentary unless asked."""

def get_analysis_prompt(resume_text: str, job_description: str) -> str:
    return f"""Analyze the resume against the job description and return the following in clear markdown sections:

1. **Match Score**: Give a score out of 100 with a short justification (2-3 sentences).
2. **Strengths**: List 4-6 strongest matches between the resume and the job.
3. **Missing Keywords & Skills**: List the most important keywords/skills from the job description that are missing or weak in the resume.
4. **Improvement Priority**: Rank the top 5 things the candidate should improve first (be specific and actionable).

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}"""

def get_tailored_resume_prompt(resume_text: str, job_description: str) -> str:
    return f"""Rewrite the entire resume to better match this specific job description while staying 100% truthful to the original content.

Requirements:
- Keep a clean professional structure (Contact Info, Professional Summary, Work Experience, Education, Skills, etc.)
- Rewrite the Professional Summary to target this exact role (3-4 lines maximum)
- Rewrite experience bullets using strong action verbs + measurable impact wherever the original resume supports it
- Naturally incorporate important keywords from the job description
- Keep it concise (ideally suitable for 1 page)
- Return ONLY the full rewritten resume in clean markdown format. No extra explanation.

ORIGINAL RESUME:
{resume_text}

TARGET JOB DESCRIPTION:
{job_description}"""

def get_cover_letter_prompt(resume_text: str, job_description: str, company_name: str = "the company") -> str:
    return f"""Write a professional, concise cover letter (maximum 280 words) for this role.

Rules:
- Address it to the Hiring Manager
- Open with a strong, specific hook that shows genuine interest in the role/company
- Highlight 2-3 most relevant achievements from the resume that match the job
- Show understanding of what the role requires
- Close with a clear call to action
- Tone: confident, professional, and human (not robotic)

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Company Name: {company_name}"""
