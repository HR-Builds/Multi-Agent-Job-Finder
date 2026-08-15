import streamlit as st
import pandas as pd
import tempfile
from pathlib import Path
import time

from src.pipeline import run_pipeline


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Resume → Job Matcher",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: #0f172a;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 17px;
        color: #94a3b8;
        margin-bottom: 30px;
    }

    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 800;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 14px;
    }

    .job-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 15px;
    }

    .job-title {
        font-size: 21px;
        font-weight: 700;
    }

    .job-company {
        color: #60a5fa;
        font-size: 15px;
        margin-top: 4px;
    }

    .job-description {
        color: #cbd5e1;
        line-height: 1.6;
        margin-top: 12px;
    }

    .status-box {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 8px;
    }

    .success-text {
        color: #4ade80;
    }

    .running-text {
        color: #facc15;
    }

    .waiting-text {
        color: #94a3b8;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🚀 Resume → Job Matcher</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="subtitle">
    Upload your resume and let AI discover relevant job opportunities
    from the web based on your real skills and experience.
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("⚙️ Search Settings")

    max_jobs = st.slider(
        "Maximum Jobs",
        min_value=5,
        max_value=30,
        value=10,
        step=5,
        help="Maximum number of jobs to process.",
    )

    search_results = st.slider(
        "Search Results",
        min_value=3,
        max_value=10,
        value=5,
        step=1,
        help="Number of Tavily results per search.",
    )

    st.divider()

    st.markdown("### 🔎 Pipeline")

    st.markdown(
        """
        **1.** 📄 Resume Reader  
        **2.** 🧠 Resume Analyzer  
        **3.** 🔎 Tavily Job Search  
        **4.** 🕷️ Job Scraper  
        **5.** 🧹 Result Processor  
        **6.** 📊 Final Results
        """
    )

    st.divider()

    st.caption(
        "Powered by Python, LangChain, LangGraph, "
        "Gemini and Tavily."
    )


# =========================================================
# RESUME UPLOAD
# =========================================================

st.subheader("📄 Upload Resume")

uploaded_file = st.file_uploader(
    "Drop your resume here",
    type=["pdf", "docx"],
    help="Supported formats: PDF and DOCX",
)


# =========================================================
# START BUTTON
# =========================================================

start_search = st.button(
    "🚀 Find Matching Jobs",
    type="primary",
    use_container_width=True,
)


# =========================================================
# PIPELINE UI
# =========================================================

if start_search:

    if uploaded_file is None:

        st.warning(
            "⚠️ Please upload a PDF or DOCX resume first."
        )

        st.stop()

    # -----------------------------------------------------
    # Save uploaded resume temporarily
    # -----------------------------------------------------

    suffix = Path(uploaded_file.name).suffix

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
    ) as tmp:

        tmp.write(
            uploaded_file.getbuffer()
        )

        resume_path = tmp.name

    # -----------------------------------------------------
    # Progress UI
    # -----------------------------------------------------

    st.divider()

    st.subheader("🔄 Pipeline Progress")

    progress = st.progress(0)

    status_container = st.container()

    stage_placeholders = []

    stages = [
        "📄 Resume Reader",
        "🧠 Resume Analyzer",
        "🔎 Job Search Agent",
        "🕷️ Job Scraper Agent",
        "🧹 Result Processor",
        "📊 Final Results",
    ]

    for stage in stages:

        placeholder = status_container.empty()

        placeholder.markdown(
            f"""
            <div class="status-box">
                <span class="waiting-text">
                ○ {stage} — Waiting...
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        stage_placeholders.append(
            placeholder
        )

    # -----------------------------------------------------
    # Helper for updating stages
    # -----------------------------------------------------

    def update_stage(index, message, state="running"):

        if state == "success":

            icon = "✓"
            css = "success-text"

        elif state == "running":

            icon = "●"
            css = "running-text"

        else:

            icon = "○"
            css = "waiting-text"

        stage_placeholders[index].markdown(
            f"""
            <div class="status-box">
                <span class="{css}">
                {icon} {stages[index]} — {message}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -----------------------------------------------------
    # Stage 1
    # -----------------------------------------------------

    update_stage(
        0,
        "Reading uploaded resume...",
        "running",
    )

    progress.progress(5)

    time.sleep(0.3)

    # -----------------------------------------------------
    # IMPORTANT
    #
    # Current pipeline runs all stages internally.
    # Therefore we show progress around the pipeline.
    # -----------------------------------------------------

    try:

        update_stage(
            0,
            "Resume uploaded successfully.",
            "success",
        )

        progress.progress(15)

        update_stage(
            1,
            "Analyzing skills and generating search queries...",
            "running",
        )

        progress.progress(25)

        # -------------------------------------------------
        # Run pipeline
        # -------------------------------------------------

        result = run_pipeline(
            resume_path=resume_path,
            max_jobs=max_jobs,
        )

        # -------------------------------------------------
        # Stage completion
        # -------------------------------------------------

        update_stage(
            1,
            "Candidate profile analyzed.",
            "success",
        )

        progress.progress(40)

        update_stage(
            2,
            "Relevant jobs discovered through Tavily.",
            "success",
        )

        progress.progress(55)

        update_stage(
            3,
            "Job pages scraped successfully.",
            "success",
        )

        progress.progress(75)

        update_stage(
            4,
            "Duplicate jobs removed and results processed.",
            "success",
        )

        progress.progress(90)

        update_stage(
            5,
            "Final job matches ready.",
            "success",
        )

        progress.progress(100)

        # -------------------------------------------------
        # Save result
        # -------------------------------------------------

        st.session_state["pipeline_result"] = result

        st.success(
            "🎉 Job matching completed successfully!"
        )

    except Exception as e:

        st.error(
            "❌ Pipeline failed."
        )

        st.exception(e)

        st.stop()


# =========================================================
# DISPLAY RESULTS
# =========================================================

if "pipeline_result" in st.session_state:

    result = st.session_state[
        "pipeline_result"
    ]

    candidate = result.get(
        "candidate",
        {},
    )

    jobs = result.get(
        "jobs",
        [],
    )

    statistics = result.get(
        "statistics",
        {},
    )

    st.divider()

    # =====================================================
    # CANDIDATE PROFILE
    # =====================================================

    st.subheader("👤 Candidate Profile")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Primary Role",
            candidate.get(
                "role",
                "N/A",
            ),
        )

    with col2:

        st.metric(
            "Experience",
            candidate.get(
                "experience_level",
                "N/A",
            ),
        )

    with col3:

        st.metric(
            "Location",
            candidate.get(
                "location",
                "N/A",
            ),
        )

    with col4:

        st.metric(
            "Skills",
            len(
                candidate.get(
                    "skills",
                    [],
                )
            ),
        )

    # =====================================================
    # SEARCH QUERIES
    # =====================================================

    search_queries = candidate.get(
        "search_queries",
        [],
    )

    if search_queries:

        with st.expander(
            "🔎 View Generated Search Queries"
        ):

            for index, query in enumerate(
                search_queries,
                start=1,
            ):

                st.write(
                    f"**{index}.** {query}"
                )

    # =====================================================
    # STATISTICS
    # =====================================================

    st.subheader("📊 Job Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Total Jobs",
            statistics.get(
                "total_jobs",
                len(jobs),
            ),
        )

    with col2:

        st.metric(
            "With Date",
            statistics.get(
                "jobs_with_date",
                0,
            ),
        )

    with col3:

        st.metric(
            "Date Unavailable",
            statistics.get(
                "jobs_without_date",
                0,
            ),
        )

    with col4:

        st.metric(
            "Companies",
            statistics.get(
                "unique_companies",
                0,
            ),
        )

    # =====================================================
    # JOB RESULTS
    # =====================================================

    st.subheader(
        f"🎯 Matching Jobs ({len(jobs)})"
    )

    if not jobs:

        st.info(
            "No relevant jobs were found."
        )

    else:

        # -------------------------------------------------
        # Convert jobs to dataframe
        # -------------------------------------------------

        dataframe_rows = []

        for job in jobs:

            dataframe_rows.append(
                {
                    "Job": job.get(
                        "title",
                        "N/A",
                    ),
                    "Company": job.get(
                        "company",
                        "N/A",
                    ),
                    "Location": job.get(
                        "location",
                        "N/A",
                    ),
                    "Employment": job.get(
                        "employment_type",
                        "N/A",
                    ),
                    "Posting Date": job.get(
                        "posting_date",
                        "date not available",
                    ),
                    "URL": job.get(
                        "url",
                        "",
                    ),
                }
            )

        df = pd.DataFrame(
            dataframe_rows
        )

        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        csv_data = df.to_csv(
            index=False
        )

        st.download_button(
            label="📥 Download Jobs CSV",
            data=csv_data,
            file_name="job_matches.csv",
            mime="text/csv",
        )

        st.write("")

        # -------------------------------------------------
        # Job cards
        # -------------------------------------------------

        for index, job in enumerate(
            jobs,
            start=1,
        ):

            title = job.get(
                "title",
                "Untitled Job",
            )

            company = job.get(
                "company",
                "Company not available",
            )

            location = job.get(
                "location",
                "Location not available",
            )

            employment = job.get(
                "employment_type",
                "Not specified",
            )

            posting_date = job.get(
                "posting_date",
                "date not available",
            )

            description = job.get(
                "description",
                "No description available.",
            )

            url = job.get(
                "url",
                "",
            )

            st.markdown(
                f"""
                <div class="job-card">

                    <div class="job-title">
                        {index}. {title}
                    </div>

                    <div class="job-company">
                        🏢 {company}
                    </div>

                    <br>

                    📍 <b>Location:</b> {location}
                    &nbsp;&nbsp;&nbsp;

                    💼 <b>Employment:</b> {employment}
                    &nbsp;&nbsp;&nbsp;

                    📅 <b>Posted:</b> {posting_date}

                    <div class="job-description">
                        {description}
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            if url:

                st.link_button(
                    "🔗 Open Job Posting",
                    url,
                )

            st.divider()

    # =====================================================
    # CLEAR RESULTS
    # =====================================================

    if st.button(
        "🗑️ Clear Results",
        use_container_width=True,
    ):

        del st.session_state[
            "pipeline_result"
        ]

        st.rerun()