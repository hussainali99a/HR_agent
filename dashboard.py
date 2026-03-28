import streamlit as st
import pandas as pd
import sqlite3
import os

from config import DATABASE_FILE
from job_manager import create_job, get_all_jobs, save_uploaded_file, download_resume_from_url
from main_agent import HRRecruitmentAgent

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Recruitment System", layout="wide")

def get_db():
    return sqlite3.connect(DATABASE_FILE)


st.title("🤖 AI Recruitment System")

# =========================
# SIDEBAR NAV
# =========================
page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "💼 Jobs", "👤 Candidates", "⚙️ Settings"]
)


# =========================
# 📊 OVERVIEW DASHBOARD
# =========================
if page == "📊 Overview":

    st.header("📊 System Overview")

    conn = get_db()

    candidates = pd.read_sql("SELECT * FROM candidates", conn)
    jobs = get_all_jobs()

    total_jobs = len(jobs)
    total_candidates = len(candidates)
    accepted = len(candidates[candidates["status"] == "ACCEPTED"])
    rejected = len(candidates[candidates["status"] == "REJECTED"])

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Jobs Posted", total_jobs)
    col2.metric("Candidates Screened", total_candidates)
    col3.metric("Accepted", accepted)
    col4.metric("Rejected", rejected)

    st.markdown("---")

    if not candidates.empty:
        st.subheader("📈 Hiring Funnel")
        st.bar_chart(candidates["status"].value_counts())



# =========================
# 💼 JOBS DASHBOARD
# =========================
elif page == "💼 Jobs":

    st.header("💼 Jobs Dashboard")

    # CREATE JOB
    with st.expander("➕ Create Job"):
        job_title = st.text_input("Job Title")
        job_profile = st.text_input("Job Profile")
        jd_text = st.text_area("Job Description")

        if st.button("Create Job", type="primary"):
            job = create_job(job_title, jd_text, job_profile)
            st.success(f"Job Created: {job['job_id']}")

    jobs = get_all_jobs()

    if not jobs:
        st.warning("No jobs available")
        st.stop()

    job_ids = [j["job_id"] for j in jobs]
    selected_job = st.selectbox("Select Job", job_ids)

    conn = get_db()

    df = pd.read_sql(
        "SELECT * FROM candidates WHERE job_id=?",
        conn,
        params=(selected_job,)
    )

    st.subheader("📊 Job Statistics")

    col1, col2, col3 = st.columns(3)

    col1.metric("Candidates", len(df))
    col2.metric("Accepted", len(df[df["status"] == "ACCEPTED"]))
    col3.metric("Rejected", len(df[df["status"] == "REJECTED"]))

    if not df.empty:
        st.bar_chart(df["status"].value_counts())



# =========================
# 👤 CANDIDATES DASHBOARD
# =========================
elif page == "👤 Candidates":

    st.header("👤 Candidates Dashboard")

    conn = get_db()

    jobs = get_all_jobs()
    job_ids = [j["job_id"] for j in jobs]

    selected_job = st.selectbox("Select Job", job_ids)

    job_path = os.path.join("resumes", selected_job)

    # ----------------------
    # UPLOAD
    # ----------------------
    st.subheader("📤 Upload Resumes")

    files = st.file_uploader("Upload", accept_multiple_files=True)

    if files:
        for f in files:
            save_uploaded_file(f, selected_job)
        st.success("Uploaded")

    # ----------------------
    # URL UPLOAD
    # ----------------------
    st.subheader("🌐 Bulk URL Upload")

    urls = st.text_area("Paste URLs")

    if st.button("Download URLs"):
        for url in urls.split("\n"):
            if url.strip():
                download_resume_from_url(url.strip(), selected_job)
        st.success("Downloaded")

    # ----------------------
    # SCREENING
    # ----------------------
    st.subheader("🤖 Screening")

    if st.button("Run Screening"):
        agent = HRRecruitmentAgent(
            job_id=selected_job,
            job_folder=job_path
        )
        agent.process_job_resumes()
        st.success("Done")

    # ----------------------
    # LOAD DATA
    # ----------------------
    df = pd.read_sql(
        "SELECT * FROM candidates WHERE job_id=? ORDER BY match_score DESC",
        conn,
        params=(selected_job,)
    )

    if df.empty:
        st.warning("No candidates yet")
        st.stop()

    df["match_score"] = (df["match_score"] * 100).round(1)

    st.subheader("🏆 Candidates")

    st.dataframe(df[["id", "name", "match_score", "status"]])

    # ----------------------
    # DETAIL VIEW
    # ----------------------
    st.subheader("🔍 Candidate Detail")

    selected_id = st.selectbox("Select Candidate ID", df["id"])

    candidate = df[df["id"] == selected_id].iloc[0]

    st.markdown(f"""
    ### {candidate['name']}

    **Email:** {candidate['email']}  
    **Phone:** {candidate['phone']}  
    **LinkedIn:** {candidate['linkedin']}  

    **Skills:** {candidate['skills']}  
    **Experience:** {candidate['experience']} years  

    **Match Score:** {candidate['match_score']}%  
    **Status:** {candidate['status']}  
    """)

    # ACTIONS
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Shortlist"):
            conn.execute(
                "UPDATE candidates SET status='SHORTLISTED' WHERE id=?",
                (selected_id,)
            )
            conn.commit()
            st.success("Shortlisted")

    with col2:
        if st.button("Reject"):
            conn.execute(
                "UPDATE candidates SET status='REJECTED' WHERE id=?",
                (selected_id,)
            )
            conn.commit()
            st.success("Rejected")



# =========================
# ⚙️ SETTINGS DASHBOARD
# =========================
elif page == "⚙️ Settings":

    st.header("⚙️ System Settings")

    st.subheader("🔌 Connectivity Check")

    try:
        conn = get_db()
        conn.execute("SELECT 1")
        st.success("Database Connected")
    except:
        st.error("Database Error")

    st.subheader("📁 Resume Folder Check")

    if os.path.exists("resumes"):
        st.success("Resumes folder OK")
    else:
        st.error("Resumes folder missing")

    st.subheader("⚡ System Info")

    st.write("Environment: Local")
    st.write("Status: Running")