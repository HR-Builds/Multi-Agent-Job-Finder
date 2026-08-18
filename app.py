import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import html

from src.pipeline import run_pipeline


# ============================================================
# CONTACT INFO — edit these three lines
# ============================================================

GITHUB_URL = "https://github.com/HR-Builds"
LINKEDIN_URL = "https://www.linkedin.com/in/hassan-rashid-a325883aa/"
EMAIL_ADDRESS = "dev.hassanrashid@gmail.com"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="CareerLens — AI Career Intelligence",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# HTML RENDER HELPER
# ------------------------------------------------------------
# st.markdown parses input as Markdown BEFORE applying
# unsafe_allow_html. Any line indented 4+ spaces is read as a
# fenced code block by Markdown, so deeply nested <div> blocks
# get printed as raw text instead of rendered. Stripping each
# line's own leading/trailing whitespace (not just the shared
# prefix, which is all textwrap.dedent removes) avoids this
# entirely. CSS/HTML don't care about indentation, so this is
# always safe.
# ============================================================

def render_html(content: str) -> None:
    lines = content.strip("\n").split("\n")
    cleaned = "\n".join(line.strip() for line in lines)
    st.markdown(cleaned, unsafe_allow_html=True)


# ============================================================
# GLOBAL CSS — OBSIDIAN / AURORA NEON / GOLD-THREAD LUXURY
# ============================================================

render_html("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

:root{
    --void:#05060d;
    --panel:#0c0e1c;
    --panel-2:#10132a;
    --line:rgba(255,255,255,0.08);
    --line-strong:rgba(255,255,255,0.14);
    --text:#f3f4fb;
    --muted:#8992ad;
    --cyan:#2fe6ff;
    --violet:#8b6bff;
    --magenta:#f45fc0;
    --gold:#f0c46b;
    --emerald:#3ee6a8;
    --rose:#ff6b7a;
}

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background:
        radial-gradient(circle at 8% 0%, rgba(47,230,255,0.10), transparent 26%),
        radial-gradient(circle at 92% 8%, rgba(139,107,255,0.16), transparent 30%),
        radial-gradient(circle at 50% 100%, rgba(244,95,192,0.06), transparent 32%),
        var(--void);
    color: var(--text);
}

.block-container { max-width: 1180px !important; padding-top: 1.6rem !important; padding-bottom: 5rem !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { background: #070811; border-right: 1px solid var(--line); }

/* ---------- NAV ---------- */
.lux-nav {
    height: 72px; display: flex; align-items: center; justify-content: space-between;
    padding: 0 22px; border: 1px solid var(--line); border-radius: 18px;
    background: linear-gradient(135deg, rgba(16,19,42,0.9), rgba(7,8,17,0.82));
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 55px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.05);
    margin-bottom: 46px;
}
.brand { display: flex; align-items: center; gap: 12px; }
.brand-mark {
    width: 38px; height: 38px; display: flex; align-items: center; justify-content: center;
    border-radius: 11px; font-size: 18px; color: #05060d; font-weight: 800;
    background: linear-gradient(135deg, var(--cyan), var(--violet) 55%, var(--magenta));
    box-shadow: 0 0 24px rgba(47,230,255,0.28);
}
.brand-name { font-family: 'Space Grotesk', sans-serif; font-size: 18px; font-weight: 700; letter-spacing: -0.4px; }
.brand-name span { background: linear-gradient(90deg, var(--cyan), var(--violet)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.nav-right { display: flex; gap: 9px; }
.nav-pill { padding: 8px 14px; border-radius: 999px; border: 1px solid rgba(240,196,107,0.22); background: rgba(240,196,107,0.05); color: var(--gold); font-size: 11px; font-weight: 700; letter-spacing: 0.6px; }
.nav-pill.live { border-color: rgba(62,230,168,0.25); background: rgba(62,230,168,0.05); color: var(--emerald); }

/* ---------- HERO ---------- */
.hero {
    position: relative; padding: 76px 60px; border-radius: 28px; overflow: hidden;
    border: 1px solid var(--line);
    background:
        radial-gradient(circle at 12% 18%, rgba(47,230,255,0.14), transparent 30%),
        radial-gradient(circle at 88% 12%, rgba(139,107,255,0.20), transparent 34%),
        linear-gradient(135deg, rgba(12,14,28,0.97), rgba(10,7,22,0.98));
    box-shadow: 0 35px 100px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.04);
    margin-bottom: 40px;
}
.hero-scanline {
    position: absolute; left: 0; right: 0; top: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--cyan), var(--violet), var(--magenta), transparent);
    opacity: 0.55; filter: blur(0.4px);
}
.hero-orb-a { position: absolute; width: 280px; height: 280px; right: -90px; top: -110px; border-radius: 50%; background: rgba(139,107,255,0.14); filter: blur(75px); }
.hero-orb-b { position: absolute; width: 220px; height: 220px; left: -80px; bottom: -100px; border-radius: 50%; background: rgba(47,230,255,0.10); filter: blur(65px); }
.hero-content { position: relative; z-index: 2; }
.hero-kicker {
    display: inline-flex; align-items: center; gap: 8px; padding: 8px 13px; border-radius: 999px;
    border: 1px solid rgba(240,196,107,0.28); background: rgba(240,196,107,0.06);
    color: var(--gold); font-size: 11px; font-weight: 700; letter-spacing: 1.8px; text-transform: uppercase;
    margin-bottom: 26px;
}
.hero-title { font-family: 'Space Grotesk', sans-serif; font-size: clamp(46px, 6.4vw, 78px); line-height: 0.98; letter-spacing: -3px; font-weight: 700; margin-bottom: 24px; max-width: 820px; }
.gradient-text { background: linear-gradient(90deg, var(--cyan) 0%, var(--violet) 55%, var(--magenta) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-description { max-width: 660px; color: var(--muted); font-size: 16px; line-height: 1.8; margin-bottom: 28px; }
.hero-badges { display: flex; flex-wrap: wrap; gap: 9px; }
.hero-badge { padding: 9px 14px; border-radius: 999px; background: rgba(255,255,255,0.03); border: 1px solid var(--line); color: #cbd1e6; font-size: 12px; font-weight: 600; }

/* ---------- SECTION TITLES ---------- */
.section-kicker { color: var(--cyan); font-size: 10px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }
.section-title { font-family: 'Space Grotesk', sans-serif; font-size: 27px; font-weight: 700; letter-spacing: -0.6px; margin-bottom: 6px; }
.section-subtitle { color: var(--muted); font-size: 13.5px; margin-bottom: 22px; }

/* ---------- MODE CARDS ---------- */
.mode-card {
    min-height: 176px; padding: 26px; border-radius: 20px; border: 1px solid var(--line);
    background: linear-gradient(150deg, rgba(16,19,42,0.85), rgba(7,8,17,0.9));
    box-shadow: 0 16px 42px rgba(0,0,0,0.24), inset 0 1px 0 rgba(255,255,255,0.03);
}
.mode-icon { font-size: 22px; margin-bottom: 16px; }
.mode-title { font-family: 'Space Grotesk', sans-serif; font-size: 17px; font-weight: 700; margin-bottom: 7px; }
.mode-text { color: var(--muted); font-size: 12.5px; line-height: 1.6; }

/* ---------- TABS ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: transparent; border-bottom: 1px solid var(--line); }
.stTabs [data-baseweb="tab"] {
    height: 44px; border-radius: 10px 10px 0 0; background: rgba(255,255,255,0.02);
    color: var(--muted); font-weight: 700; font-size: 13px; padding: 0 18px;
}
.stTabs [aria-selected="true"] { color: var(--text) !important; background: rgba(47,230,255,0.06) !important; border-bottom: 2px solid var(--cyan) !important; }

/* ---------- INPUTS ---------- */
[data-testid="stFileUploader"] { border: 1px dashed rgba(47,230,255,0.3) !important; border-radius: 16px !important; background: rgba(47,230,255,0.02) !important; padding: 10px !important; }
[data-testid="stFileUploader"]:hover { border-color: rgba(47,230,255,0.6) !important; }
.stTextInput input, .stTextArea textarea {
    background: var(--panel) !important; border: 1px solid var(--line) !important; color: var(--text) !important; border-radius: 12px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus { border-color: rgba(47,230,255,0.5) !important; box-shadow: 0 0 0 1px rgba(47,230,255,0.25) !important; }
.stSlider [data-baseweb="slider"] { padding-top: 6px; }

/* ---------- BUTTONS ---------- */
.stButton > button, .stDownloadButton > button, .stLinkButton > a {
    border-radius: 12px !important; min-height: 47px !important; font-weight: 700 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    background: linear-gradient(100deg, var(--cyan), var(--violet), var(--magenta)) !important;
    color: #05060d !important; box-shadow: 0 10px 32px rgba(139,107,255,0.22) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover, .stDownloadButton > button:hover, .stLinkButton > a:hover {
    transform: translateY(-2px) !important; box-shadow: 0 15px 42px rgba(47,230,255,0.24), 0 10px 36px rgba(244,95,192,0.18) !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.03) !important; color: var(--text) !important; box-shadow: none !important;
}

/* ---------- EXPANDER ---------- */
[data-testid="stExpander"] { border: 1px solid var(--line) !important; border-radius: 14px !important; background: rgba(255,255,255,0.015) !important; }

/* ---------- METRICS ---------- */
[data-testid="stMetric"] {
    padding: 20px !important; border-radius: 16px !important;
    background: linear-gradient(150deg, rgba(16,19,42,0.88), rgba(6,7,16,0.94)) !important;
    border: 1px solid var(--line) !important; box-shadow: 0 14px 36px rgba(0,0,0,0.22) !important;
}
[data-testid="stMetricLabel"] { color: var(--muted) !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { font-family: 'Space Grotesk', sans-serif !important; color: var(--text) !important; font-weight: 700 !important; }

/* ---------- JOB CARDS ---------- */
.job-card {
    position: relative; padding: 26px; margin: 14px 0; border-radius: 20px;
    border: 1px solid var(--line);
    background: linear-gradient(150deg, rgba(15,18,36,0.94), rgba(7,8,17,0.96));
    box-shadow: 0 16px 46px rgba(0,0,0,0.28);
    display: flex; gap: 22px; align-items: flex-start;
}
.job-main { flex: 1; min-width: 0; }
.job-number { color: var(--cyan); font-size: 10.5px; font-weight: 800; letter-spacing: 1.4px; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace; }
.job-title { font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; color: var(--text); margin-bottom: 5px; }
.job-company { color: var(--violet); font-size: 13.5px; font-weight: 600; margin-bottom: 15px; }
.job-meta { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px; }
.job-tag { padding: 6px 10px; border-radius: 7px; background: rgba(255,255,255,0.03); border: 1px solid var(--line); color: #9aa2c0; font-size: 11px; }
.job-tag.source { border-color: rgba(240,196,107,0.25); color: var(--gold); background: rgba(240,196,107,0.045); }
.job-description { color: #a4abc6; font-size: 12.8px; line-height: 1.7; max-width: 760px; }

/* ---------- SCORE RING (signature element) ---------- */
.score-ring-wrap { flex-shrink: 0; display: flex; flex-direction: column; align-items: center; gap: 6px; width: 84px; }
.score-ring {
    width: 76px; height: 76px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    position: relative;
}
.score-ring::before {
    content: ""; position: absolute; inset: 0; border-radius: 50%;
    background: conic-gradient(var(--ring-color) calc(var(--score) * 1%), rgba(255,255,255,0.06) 0);
    -webkit-mask: radial-gradient(farthest-side, transparent calc(100% - 7px), #000 calc(100% - 6px));
    mask: radial-gradient(farthest-side, transparent calc(100% - 7px), #000 calc(100% - 6px));
    filter: drop-shadow(0 0 8px var(--ring-color));
}
.score-value { font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; color: var(--text); z-index: 1; }
.score-label { font-size: 9.5px; font-weight: 700; letter-spacing: 1px; color: var(--muted); text-transform: uppercase; }

/* ---------- CONTACT ---------- */
.contact-card {
    display: flex; align-items: center; gap: 15px; padding: 20px 22px; border-radius: 18px;
    border: 1px solid var(--line);
    background: linear-gradient(150deg, rgba(16,19,42,0.85), rgba(7,8,17,0.9));
    text-decoration: none !important; height: 100%;
    transition: all 0.2s ease;
}
.contact-card:hover { border-color: rgba(47,230,255,0.35); box-shadow: 0 18px 46px rgba(0,0,0,0.3), 0 0 28px rgba(47,230,255,0.08); transform: translateY(-3px); }
.contact-icon {
    width: 42px; height: 42px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
    border-radius: 12px; font-size: 18px; color: #05060d; font-weight: 800;
    background: linear-gradient(135deg, var(--cyan), var(--violet) 55%, var(--magenta));
}
.contact-label { color: var(--muted); font-size: 10.5px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 3px; }
.contact-value { color: var(--text); font-size: 14px; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }

/* ---------- FOOTER ---------- */
.lux-footer { margin-top: 80px; padding-top: 26px; border-top: 1px solid var(--line); display: flex; align-items: center; justify-content: space-between; color: #4a5170; font-size: 11px; }
.footer-brand { color: var(--muted); font-weight: 700; }
.footer-gradient { background: linear-gradient(90deg, var(--cyan), var(--violet)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

@media (max-width: 768px) {
    .block-container { padding-left: 16px !important; padding-right: 16px !important; }
    .hero { padding: 40px 24px; }
    .hero-title { font-size: 42px; letter-spacing: -2px; }
    .lux-nav { margin-bottom: 28px; }
    .job-card { flex-direction: column; }
    .score-ring-wrap { flex-direction: row; width: auto; }
    .lux-footer { flex-direction: column; gap: 8px; text-align: center; }
}

</style>
""")


# ============================================================
# NAVIGATION
# ============================================================

render_html("""
<div class="lux-nav">
    <div class="brand">
        <div class="brand-mark">✦</div>
        <div class="brand-name">Career<span>Lens</span></div>
    </div>
    <div class="nav-right">
        <div class="nav-pill">AI CAREER INTELLIGENCE</div>
        <div class="nav-pill live">● LIVE DISCOVERY</div>
    </div>
</div>
""")


# ============================================================
# HERO
# ============================================================

render_html("""
<section class="hero">
    <div class="hero-scanline"></div>
    <div class="hero-orb-a"></div>
    <div class="hero-orb-b"></div>
    <div class="hero-content">
        <div class="hero-kicker">✦ AI-Powered Career Intelligence</div>
        <div class="hero-title">
            Discover.
            <br>
            <span class="gradient-text">Match. Grow.</span>
        </div>
        <div class="hero-description">
            CareerLens transforms your resume, skills and experience
            into a precise, scored stream of relevant career
            opportunities — pulled live from the web and ranked by
            an actual matching engine, not guesswork.
        </div>
        <div class="hero-badges">
            <div class="hero-badge">✦ Scored Matching</div>
            <div class="hero-badge">⚡ Live Discovery</div>
            <div class="hero-badge">◈ Multi-Source Jobs</div>
            <div class="hero-badge">◎ Zero Fabricated Data</div>
        </div>
    </div>
</section>
""")


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

with st.sidebar:
    render_html("""
    <div style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:16px;margin-bottom:4px;">✦ Search Controls</div>
    <div style="color:#8992ad;font-size:12px;margin-bottom:18px;">Tune how deep CareerLens searches.</div>
    """)
    max_jobs = st.slider("Maximum jobs", min_value=5, max_value=30, value=10, step=5)
    st.caption("Search depth is fixed server-side to control API usage.")


# ============================================================
# DISCOVERY MODE OVERVIEW
# ============================================================

render_html("""
<div class="section-kicker">CAREER DISCOVERY</div>
<div class="section-title">Choose your discovery mode</div>
<div class="section-subtitle">Start from your complete resume, or search directly by role and skills.</div>
""")

col1, col2 = st.columns(2)
with col1:
    render_html("""
    <div class="mode-card">
        <div class="mode-icon">◈</div>
        <div class="mode-title">Resume Intelligence</div>
        <div class="mode-text">Upload a PDF or DOCX resume. One AI pass extracts your role, skills and experience, then CareerLens discovers and scores matching jobs.</div>
    </div>
    """)
with col2:
    render_html("""
    <div class="mode-card">
        <div class="mode-icon">⌁</div>
        <div class="mode-title">Skill Intelligence</div>
        <div class="mode-text">No resume needed. Enter a target role, skills and location — CareerLens searches live with zero LLM analysis calls.</div>
    </div>
    """)

st.write("")


# ============================================================
# TABS — RESUME / SKILL
# ============================================================

resume_tab, skill_tab = st.tabs(["◈  Resume Intelligence", "⌁  Skill Intelligence"])

with resume_tab:
    render_html("""
    <div class="section-title">Upload your professional profile</div>
    <div class="section-subtitle">PDF or DOCX · Your resume stays within the current session.</div>
    """)

    uploaded_file = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx"],
        key="resume_upload",
        label_visibility="collapsed",
    )

    st.write("")

    start_resume = st.button(
        "✦  Find My Opportunities",
        type="primary",
        use_container_width=True,
        key="start_resume",
    )

    if start_resume:
        if uploaded_file is None:
            st.warning("Please upload your PDF or DOCX resume first.")
        else:
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                resume_path = tmp.name

            progress = st.progress(0)
            status = st.empty()
            try:
                status.info("Reading your resume...")
                progress.progress(15)

                status.info("Analyzing role, skills and experience...")
                progress.progress(30)

                result = run_pipeline(
                    resume_path=resume_path,
                    max_jobs=max_jobs,
                    search_mode="resume",
                )

                status.info("Scoring and ranking job matches...")
                progress.progress(90)

                st.session_state["pipeline_result"] = result
                progress.progress(100)
                status.success("✦ Career intelligence complete.")

            except Exception as exc:
                progress.empty()
                status.error("The job search could not be completed.")
                st.exception(exc)

with skill_tab:
    render_html("""
    <div class="section-title">Search by role and skills</div>
    <div class="section-subtitle">Real-time discovery powered by live search. This mode uses zero LLM calls.</div>
    """)

    role = st.text_input("Target role", placeholder="e.g. Python Developer, AI Engineer", key="skill_role")
    skills_input = st.text_input("Skills (comma-separated)", placeholder="e.g. Python, FastAPI, LangChain, PostgreSQL", key="skill_skills")

    loc_col, exp_col, emp_col = st.columns(3)
    with loc_col:
        location = st.text_input("Preferred location", placeholder="e.g. Remote, Lahore, Karachi", key="skill_location")
    with exp_col:
        experience_level = st.text_input("Experience level", placeholder="e.g. entry, mid, senior", key="skill_experience")
    with emp_col:
        employment_type = st.text_input("Employment type", placeholder="e.g. full-time, contract", key="skill_employment")

    st.write("")

    start_skill = st.button(
        "✦  Search Live Opportunities",
        type="primary",
        use_container_width=True,
        key="start_skill",
    )

    if start_skill:
        parsed_skills = [s.strip() for s in skills_input.split(",") if s.strip()]

        if not role.strip():
            st.warning("Enter a target role to search.")
        else:
            progress = st.progress(0)
            status = st.empty()
            try:
                status.info("Building search queries...")
                progress.progress(20)

                result = run_pipeline(
                    resume_path=None,
                    role=role.strip(),
                    skills=parsed_skills,
                    location=location.strip(),
                    experience_level=experience_level.strip(),
                    employment_type=employment_type.strip(),
                    max_jobs=max_jobs,
                    search_mode="manual",
                )

                status.info("Extracting and scoring job listings...")
                progress.progress(75)

                st.session_state["pipeline_result"] = result
                progress.progress(100)
                status.success("✦ Live career intelligence complete.")

            except Exception as exc:
                progress.empty()
                status.error("The live job search could not be completed.")
                st.exception(exc)


# ============================================================
# RESULTS
# ============================================================

def score_color(score: int) -> str:
    if score >= 80:
        return "var(--emerald)"
    if score >= 55:
        return "var(--gold)"
    return "var(--rose)"


if "pipeline_result" in st.session_state:

    result = st.session_state["pipeline_result"]
    candidate = result.get("candidate", {})
    jobs = result.get("jobs", [])
    statistics = result.get("statistics", {})

    st.write("")
    st.write("")

    render_html("""
    <div class="section-kicker">YOUR CAREER PROFILE</div>
    <div class="section-title">Intelligence snapshot</div>
    <div class="section-subtitle">A structured view of the professional profile used to find your matches.</div>
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Primary Role", candidate.get("role", "N/A") or "N/A")
    with col2:
        st.metric("Experience", candidate.get("experience_level", "N/A") or "N/A")
    with col3:
        st.metric("Location", candidate.get("location", "N/A") or "N/A")
    with col4:
        st.metric("Skills", len(candidate.get("skills", []) or []))

    skills = candidate.get("skills", []) or []
    if skills:
        render_html("""
        <br>
        <div class="section-kicker">SKILL INTELLIGENCE</div>
        <div class="section-title">Your strongest signals</div>
        """)
        skill_html = "".join(
            f'<span style="display:inline-block;padding:8px 12px;margin:4px;border-radius:999px;'
            f'background:rgba(47,230,255,0.045);border:1px solid rgba(47,230,255,0.16);'
            f'color:#a7f3ff;font-size:12px;font-weight:600;">{html.escape(str(skill))}</span>'
            for skill in skills
        )
        render_html(f"<div>{skill_html}</div>")

    search_queries = candidate.get("search_queries", []) or []
    if search_queries:
        with st.expander("⌁ View AI-generated search intelligence"):
            for index, query in enumerate(search_queries, start=1):
                st.write(f"**{index}.** {query}")

    # -------------------- STATISTICS --------------------

    st.write("")
    st.write("")

    render_html("""
    <div class="section-kicker">MARKET DISCOVERY</div>
    <div class="section-title">Search intelligence</div>
    <div class="section-subtitle">Overview of the opportunities discovered and scored by CareerLens.</div>
    """)

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Opportunities", statistics.get("total_jobs", len(jobs)))
    with col2:
        st.metric("Avg. Match", f"{statistics.get('average_match_score', 0)}%")
    with col3:
        st.metric("Strong Matches", statistics.get("high_match_jobs", 0))
    with col4:
        st.metric("Companies", statistics.get("unique_companies", 0))
    with col5:
        st.metric("Dated Postings", statistics.get("jobs_with_date", 0))

    sources = statistics.get("sources", {}) or {}
    if sources:
        source_html = "".join(
            f'<span class="job-tag source" style="margin:4px;">{html.escape(str(src))} · {count}</span>'
            for src, count in sorted(sources.items(), key=lambda item: item[1], reverse=True)
        )
        render_html(f'<div style="margin-top:6px;">{source_html}</div>')

    # -------------------- JOB RESULTS --------------------

    st.write("")
    st.write("")

    render_html("""
    <div class="section-kicker">CURATED OPPORTUNITIES</div>
    <div class="section-title">Your career matches</div>
    <div class="section-subtitle">Ranked by match score, then verified posting date.</div>
    """)

    if not jobs:
        st.info("No relevant opportunities were found. Try widening your skills or location.")
    else:
        dataframe_rows = []
        for job in jobs:
            dataframe_rows.append({
                "Job": job.get("title", "N/A"),
                "Company": job.get("company", "N/A"),
                "Location": job.get("location", "N/A"),
                "Employment": job.get("employment_type", "N/A"),
                "Match Score": job.get("match_score", 0),
                "Source": job.get("source", "N/A"),
                "Posting Date": job.get("posting_date", "date not available"),
                "URL": job.get("url", ""),
            })

        df = pd.DataFrame(dataframe_rows)
        csv_data = df.to_csv(index=False)

        st.download_button(
            label="↓  Export Opportunities",
            data=csv_data,
            file_name="careerlens_job_matches.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.write("")

        for index, job in enumerate(jobs, start=1):
            title = html.escape(str(job.get("title", "Untitled Position")))
            company = html.escape(str(job.get("company", "Company unavailable")))
            location = html.escape(str(job.get("location", "Location unavailable")))
            employment = html.escape(str(job.get("employment_type", "Not specified")))
            posting_date = html.escape(str(job.get("posting_date", "date not available")))
            description = html.escape(str(job.get("description", "No description available.")))
            source = html.escape(str(job.get("source", "Company / Other")))
            url = job.get("url", "")

            score = job.get("match_score", 0)
            try:
                score = int(score)
            except (TypeError, ValueError):
                score = 0
            ring_color = score_color(score)

            render_html(f"""
            <div class="job-card">
                <div class="score-ring-wrap">
                    <div class="score-ring" style="--score:{score};--ring-color:{ring_color};">
                        <span class="score-value">{score}</span>
                    </div>
                    <span class="score-label">MATCH</span>
                </div>
                <div class="job-main">
                    <div class="job-number">OPPORTUNITY {index:02d}</div>
                    <div class="job-title">{title}</div>
                    <div class="job-company">✦ {company}</div>
                    <div class="job-meta">
                        <div class="job-tag">📍 {location}</div>
                        <div class="job-tag">◈ {employment}</div>
                        <div class="job-tag">◷ {posting_date}</div>
                        <div class="job-tag source">⌁ {source}</div>
                    </div>
                    <div class="job-description">{description}</div>
                </div>
            </div>
            """)

            if url:
                st.link_button("↗  View Opportunity", url, use_container_width=True)

            st.write("")

    st.write("")
    if st.button("Clear Current Search", use_container_width=True):
        st.session_state.pop("pipeline_result", None)
        st.rerun()


# ============================================================
# CONTACT SECTION
# ============================================================

st.write("")
st.write("")

render_html("""
<div class="section-kicker">GET IN TOUCH</div>
<div class="section-title">Let's connect</div>
<div class="section-subtitle">Built and maintained by me — reach out through any of these channels.</div>
""")

c1, c2, c3 = st.columns(3)

with c1:
    render_html(f"""
    <a href="{GITHUB_URL}" target="_blank" class="contact-card">
        <div class="contact-icon">GH</div>
        <div>
            <div class="contact-label">GitHub</div>
            <div class="contact-value">View my work</div>
        </div>
    </a>
    """)

with c2:
    render_html(f"""
    <a href="{LINKEDIN_URL}" target="_blank" class="contact-card">
        <div class="contact-icon">in</div>
        <div>
            <div class="contact-label">LinkedIn</div>
            <div class="contact-value">Let's connect</div>
        </div>
    </a>
    """)

with c3:
    render_html(f"""
    <a href="mailto:{EMAIL_ADDRESS}" class="contact-card">
        <div class="contact-icon">✉</div>
        <div>
            <div class="contact-label">Email</div>
            <div class="contact-value">{html.escape(EMAIL_ADDRESS)}</div>
        </div>
    </a>
    """)


# ============================================================
# FOOTER
# ============================================================

render_html("""
<div class="lux-footer">
    <div><span class="footer-brand">CareerLens</span> &nbsp;·&nbsp; AI Career Intelligence</div>
    <div><span class="footer-gradient">Python · LangChain · LangGraph · Gemini · Tavily</span></div>
</div>
""")