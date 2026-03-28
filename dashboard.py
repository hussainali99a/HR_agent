import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

from config import DATABASE_FILE
from job_manager import (
    create_job,
    get_all_jobs,
    save_uploaded_file,
    download_resume_from_url
)
from main_agent import HRRecruitmentAgent

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="AI HR Dashboard",
    layout="wide"
)

st.title("🤖 AI Recruitment Dashboard")

# =========================
# DB CONNECTION
# =========================
def get_db():
    return sqlite3.connect(DATABASE_FILE)


# =========================
# SIDEBAR
# =========================
page = st.sidebar.radio(
    "Navigation",
    ["📂 Job Management", "👤 Candidates", "📊 Analytics"]
)


# =========================
# JOB MANAGEMENT PAGE
# =========================
if page == "📂 Job Management":

    st.header("📂 Job Management")

    # CREATE JOB
    with st.expander("➕ Create Job"):
        job_id = st.text_input("Job ID (01, 02...)")
        jd_text = st.text_area("Job Description")

        if st.button("Create Job"):
            try:
                create_job(job_id, jd_text)
                st.success(f"Job {job_id} created")
            except Exception as e:
                st.error(str(e))

    jobs = get_all_jobs()

    if not jobs:
        st.warning("No jobs found")
        st.stop()

    job_ids = [job["job_id"] for job in jobs]
    selected_job = st.selectbox("Select Job", job_ids)

    job_path = os.path.join("resumes", selected_job)

    st.info(f"📁 {job_path}")

    # UPLOAD
    st.subheader("📤 Upload Resumes")
    files = st.file_uploader("Upload resumes", accept_multiple_files=True)

    if files:
        for f in files:
            save_uploaded_file(f, selected_job)
        st.success(f"{len(files)} resumes uploaded")

    # DOWNLOAD
    st.subheader("🌐 Download Resume")
    url = st.text_input("Resume URL")

    if st.button("Download"):
        try:
            path = download_resume_from_url(url, selected_job)
            st.success(f"Saved: {path}")
        except Exception as e:
            st.error(str(e))

    # SCREEN
    st.subheader("🤖 Screening")

    if st.button("Run Screening"):

        with st.spinner("Processing..."):

            agent = HRRecruitmentAgent(
                job_id=selected_job,
                job_folder=job_path
            )

            agent.process_job_resumes()

        st.success("Screening complete")

    # FILE LIST
    st.subheader("📄 Files")
    for f in os.listdir(job_path):
        if f.endswith((".pdf", ".docx")):
            st.write(f"📄 {f}")


# =========================
# CANDIDATES PAGE
# =========================
elif page == "👤 Candidates":

    st.header("👤 Candidates")

    conn = get_db()

    jobs = get_all_jobs()
    job_ids = [job["job_id"] for job in jobs]

    selected_job = st.selectbox("Filter by Job", job_ids)

    df = pd.read_sql_query(
        "SELECT * FROM candidates WHERE job_id = ? ORDER BY match_score DESC",
        conn,
        params=(selected_job,)
    )

    if df.empty:
        st.warning("No candidates found")
        st.stop()

    # FORMAT
    df["match_score"] = (df["match_score"] * 100).round(1)

    st.subheader("🏆 Ranked Candidates")

    st.dataframe(
        df[["name", "email", "match_score", "status"]],
        use_container_width=True
    )

    # ACTION PANEL
    st.subheader("⚡ Take Action")

    selected_candidate = st.selectbox(
        "Select Candidate",
        df["id"]
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Shortlist"):
            conn.execute(
                "UPDATE candidates SET status='SHORTLISTED' WHERE id=?",
                (selected_candidate,)
            )
            conn.commit()
            st.success("Shortlisted")

    with col2:
        if st.button("❌ Reject"):
            conn.execute(
                "UPDATE candidates SET status='REJECTED' WHERE id=?",
                (selected_candidate,)
            )
            conn.commit()
            st.success("Rejected")


# =========================
# ANALYTICS PAGE
# =========================
elif page == "📊 Analytics":

    st.header("📊 Analytics")

    conn = get_db()

    jobs = get_all_jobs()
    job_ids = [job["job_id"] for job in jobs]

    selected_job = st.selectbox("Select Job", job_ids)

    df = pd.read_sql_query(
        "SELECT * FROM candidates WHERE job_id = ?",
        conn,
        params=(selected_job,)
    )

    if df.empty:
        st.warning("No data")
        st.stop()

    # METRICS
    total = len(df)
    accepted = len(df[df["status"] == "ACCEPTED"])
    rejected = len(df[df["status"] == "REJECTED"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Total", total)
    col2.metric("Accepted", accepted)
    col3.metric("Rejected", rejected)

    # DISTRIBUTION
    st.subheader("📈 Score Distribution")
    st.bar_chart(df["match_score"])

    # STATUS BREAKDOWN
    st.subheader("📊 Status Breakdown")
    st.bar_chart(df["status"].value_counts())