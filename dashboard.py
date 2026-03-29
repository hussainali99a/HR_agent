import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from config import DATABASE_FILE
from job_manager import create_job, get_all_jobs, save_uploaded_file, download_resume_from_url
from main_agent import HRRecruitmentAgent
from auth_service import signup_user, login_user, verify_user_token
from database import db
from meet_scheduler import scheduler

# =========================
# EMAIL VERIFICATION HANDLER
# =========================
def handle_email_verification():
    query_params = st.query_params

    if "u" in query_params and "token" in query_params:
        user_id = query_params["u"]
        token = query_params["token"]

        res = verify_user_token(user_id, token)

        st.title("🔐 Email Verification")

        if res["success"]:
            st.success("✅ Email verified successfully!")

            st.markdown("""
                <meta http-equiv="refresh" content="2;url=/?page=login">
            """, unsafe_allow_html=True)

        else:
            st.error(f"❌ {res['message']}")

        return True

    return False

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="AI Recruitment Platform", layout="wide")


def get_conn():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# SESSION INIT
# =========================
if "user_id" not in st.session_state:
    st.session_state.user_id = None


# =========================
# AUTH SCREEN
# =========================
# Handle verification FIRST
if handle_email_verification():
    st.stop()

if not st.session_state.user_id:

    st.title("🚀 AI Recruitment Platform")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # LOGIN
    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            res = login_user(email, password)

            if res["success"]:
                st.session_state.user_id = res["user_id"]
                st.session_state.hr_email = res["email"]
                st.rerun()
            else:
                st.error(res["message"])

    # SIGNUP
    with tab2:
        name = st.text_input("Name")
        company = st.text_input("Company")
        email = st.text_input("Your Email")
        password = st.text_input("Your Password", type="password")

        if st.button("Signup"):
            res = signup_user(name, company,email, password)

            if res["success"]:
                st.success("Verification Email sent. Check your Inbox")
            else:
                st.error(res["message"])

    st.stop()

def load_candidates_data(user_id):
    """Load all candidates from database"""
    try:
        conn = get_conn()
        df = pd.read_sql_query('SELECT * FROM candidates WHERE user_id=? ORDER BY created_at DESC', conn, params=(user_id,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def load_decisions_data(user_id):
    """Load all decisions from database"""
    try:
        conn = get_conn()
        df = pd.read_sql_query('''
            SELECT d.*, c.name, c.email 
            FROM decisions d
            LEFT JOIN candidates c ON d.candidate_id = c.id
            WHERE d.user_id = ?
            ORDER BY d.made_at DESC
        ''', conn, params=(user_id,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def load_email_logs(user_id):
    """Load email logs"""
    try:
        conn = get_conn()
        df = pd.read_sql_query('''
            SELECT e.*, c.name, c.email 
            FROM email_logs e
            LEFT JOIN candidates c ON e.candidate_id = c.id
            WHERE e.user_id = ?
            ORDER BY e.sent_at DESC
        ''', conn, params=(user_id,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

def load_meetings(user_id):
    """Load meetings for the HR"""
    try:
        conn = get_conn()
        df = pd.read_sql_query('''
            SELECT * 
            FROM meetings
            WHERE hr_id = ?
            ORDER BY created_at DESC
        ''', conn, params=(user_id,))
        conn.close()
        return df
    except:
        return pd.DataFrame()

# =========================
# MAIN DASHBOARD
# =========================
st.title("🤖 AI Recruitment Dashboard")

user_id = st.session_state.user_id

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "💼 Jobs", "👤 Candidates", "📈 Analytics", "⚙️ Settings"]
)


# =========================
# 📊 OVERVIEW
# =========================
if page == "📊 Overview":

    conn = get_conn()

    candidates = pd.read_sql(
        "SELECT * FROM candidates WHERE user_id=?",
        conn,
        params=(user_id,)
    )

    jobs = pd.read_sql(
        "SELECT * FROM jobs WHERE user_id=?",
        conn,
        params=(user_id,)
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Jobs", len(jobs))
    col2.metric("Candidates", len(candidates))
    col3.metric("Accepted", len(candidates[candidates["status"] == "ACCEPTED"]))
    col4.metric("Rejected", len(candidates[candidates["status"] == "REJECTED"]))

    if not candidates.empty:
        st.bar_chart(candidates["status"].value_counts())


# =========================
# 💼 JOBS
# =========================
elif page == "💼 Jobs":

    st.header("Jobs")

    # CREATE JOB
    with st.expander("Create Job"):
        title = st.text_input("Title")
        profile = st.text_input("Profile")
        desc = st.text_area("Description")

        if st.button("Create Job"):
            job = create_job(title, desc, profile)

            db.add_job(
                job["job_id"],
                user_id,
                title,
                profile,
                desc,
                job["folder_path"]
            )

            st.success("Job created")

    conn = get_conn()

    jobs = pd.read_sql(
        "SELECT * FROM jobs WHERE user_id=?",
        conn,
        params=(user_id,),
        index_col="id"
    )
    jobs = jobs.drop(columns=["folder_path", "user_id"])
    st.subheader("Your Jobs")
    st.dataframe(jobs)


# =========================
# 👤 CANDIDATES
# =========================
elif page == "👤 Candidates":

    st.header("Candidates")

    conn = get_conn()

    jobs = pd.read_sql(
        "SELECT * FROM jobs WHERE user_id=?",
        conn,
        params=(user_id,)
    )

    if jobs.empty:
        st.warning("Create a job first")
        st.stop()

    job_id = st.selectbox("Select Job", jobs["id"])

    job_path = f"resumes/{job_id}"

    # UPLOAD
    files = st.file_uploader("Upload resumes", accept_multiple_files=True)

    if files:
        for f in files:
            save_uploaded_file(f, job_id)

        st.success("Uploaded")

    # URL
    urls = st.text_area("Paste URLs")

    if st.button("Download URLs"):
        for url in urls.split("\n"):
            if url.strip():
                download_resume_from_url(url.strip(), job_id)

    # SCREEN
    if st.button("Run Screening"):
        with st.spinner("Processing..."):
            agent = HRRecruitmentAgent(job_id=job_id, job_folder=job_path)
            agent.process_job_resumes(user_id=user_id, hr_email=st.session_state.hr_email)
        st.success("Screening completed")

    # FILE LIST
    st.subheader("📄 Received Resumes")
    st.dataframe([f for f in os.listdir(job_path) if f.endswith((".pdf", ".docx"))])
    # DATA
    df = pd.read_sql(
        "SELECT * FROM candidates WHERE job_id=? AND user_id=? ORDER BY match_score DESC",
        conn,
        params=(job_id, user_id)
    )

    if df.empty:
        st.warning("No candidates")
        st.stop()

    df["match_score"] = (df["match_score"] * 100).round(1)

    st.dataframe(df[["id", "name", "match_score", "status"]])

    # DETAIL
    cid = st.selectbox("Select Candidate", df["id"])
    c = df[df["id"] == cid].iloc[0]

    st.markdown(f"""
    ### {c['name']}

    Email: {c['email']}  
    Phone: {c['phone']}  
    LinkedIn: {c['linkedin']}  

    Skills: {c['skills']}  
    Experience: {c['experience']}  

    Score: {c['match_score']}%  
    Status: {c['status']}
    """)

    # ACTIONS
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Shortlist"):
            conn.execute(
                "UPDATE candidates SET status='SHORTLISTED' WHERE id=?",
                (cid,)
            )
            conn.commit()

    with col2:
        if st.button("Reject"):
            conn.execute(
                "UPDATE candidates SET status='REJECTED' WHERE id=?",
                (cid,)
            )
            conn.commit()

    # SCHEDULE INTERVIEW
    st.subheader("Schedule Interview")

    time = st.datetime_input("Select time")

    if st.button("Schedule"):
        meeting = scheduler.schedule_interview(
            c["name"],
            c["email"],
            "Job Role",
            time,
            cid
        )

        conn.execute("""
            INSERT INTO meetings (candidate_id, hr_id, meeting_link, meeting_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            cid,
            user_id,
            meeting["link"],
            time,
            "SCHEDULED",
            datetime.now()
        ))

        conn.commit()

        st.success("Interview Scheduled")
    decisions_df = load_decisions_data(user_id)
    emails_df = load_email_logs(user_id)
    st.dataframe(decisions_df) 
    st.dataframe(emails_df) 
    meetings_df = load_meetings(user_id)
    st.dataframe(meetings_df) 


elif page == "📈 Analytics":
    st.markdown("<div class='section-title'>📊 Recruitment Analytics & Insights</div>", unsafe_allow_html=True)
    
    decisions_df = load_decisions_data(user_id)
    emails_df = load_email_logs(user_id)
    candidates_df = load_candidates_data(user_id)
    
    if candidates_df.empty:
        st.info("📊 No data available yet. Process some resumes to see analytics.")
    else:
        # Score Statistics
        st.markdown("### 📈 Score Statistics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        avg_score = candidates_df['match_score'].mean() * 100
        max_score = candidates_df['match_score'].max() * 100
        min_score = candidates_df['match_score'].min() * 100
        median_score = candidates_df['match_score'].median() * 100
        std_score = candidates_df['match_score'].std() * 100
        
        with col1:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #1F4788;'>
                <div class='metric-label'>Average</div>
                <div class='metric-value'>{avg_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #28a745;'>
                <div class='metric-label'>Maximum</div>
                <div class='metric-value' style='color: #28a745;'>{max_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #dc3545;'>
                <div class='metric-label'>Minimum</div>
                <div class='metric-value' style='color: #dc3545;'>{min_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #17a2b8;'>
                <div class='metric-label'>Median</div>
                <div class='metric-value' style='color: #17a2b8;'>{median_score:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #6c757d;'>
                <div class='metric-label'>Std Dev</div>
                <div class='metric-value' style='color: #6c757d;'>{std_score:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Advanced charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Score Distribution (Advanced)")
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=candidates_df['match_score'] * 100,
                nbinsx=20,
                name='Candidates',
                marker=dict(
                    color='#1F4788',
                    line=dict(color='#0d2450', width=1.5)
                ),
                opacity=0.7
            ))
            
            # Add vertical lines for statistics
            fig.add_vline(x=avg_score, line_dash="dash", line_color="#28a745", 
                         annotation_text=f"Avg: {avg_score:.1f}%", annotation_position="top left")
            fig.add_vline(x=median_score, line_dash="dash", line_color="#17a2b8",
                         annotation_text=f"Median: {median_score:.1f}%", annotation_position="top right")
            
            fig.update_layout(
                xaxis_title="Match Score (%)",
                yaxis_title="Number of Candidates",
                height=400,
                hovermode='x unified',
                font=dict(family="Arial, sans-serif", size=11),
                plot_bgcolor='rgba(240,240,240,0.5)',
                xaxis=dict(gridcolor='white'),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Decision Status Breakdown")
            
            if not decisions_df.empty:
                decision_counts = decisions_df['decision'].value_counts()
                decision_colors = {'ACCEPTED': '#28a745', 'REJECTED': '#dc3545', 'PENDING': '#ffc107'}
                decision_color_list = [decision_colors.get(d, '#1F4788') for d in decision_counts.index]
                
                fig = go.Figure(data=[go.Bar(
                    x=decision_counts.index,
                    y=decision_counts.values,
                    marker=dict(
                        color=decision_color_list,
                        line=dict(color='#0d0d0d', width=0.5)
                    ),
                    text=decision_counts.values,
                    textposition='outside'
                )])
                
                fig.update_layout(
                    title="",
                    xaxis_title="Decision",
                    yaxis_title="Count",
                    height=400,
                    font=dict(family="Arial, sans-serif", size=11),
                    plot_bgcolor='rgba(240,240,240,0.5)',
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No decision data available yet")
        
        st.markdown("---")
        
        # Timeline analytics
        st.markdown("### 📅 Timeline Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Candidates Over Time")
            if not candidates_df.empty:
                candidates_df_copy = candidates_df.copy()
                candidates_df_copy['created_at'] = pd.to_datetime(candidates_df_copy['created_at'])
                candidates_by_date = candidates_df_copy.groupby(candidates_df_copy['created_at'].dt.date).size()
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=candidates_by_date.index,
                    y=candidates_by_date.values,
                    mode='lines+markers',
                    name='Applications',
                    line=dict(color='#1F4788', width=3),
                    marker=dict(size=8, color='#1F4788')
                ))
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Number of Applications",
                    height=350,
                    hovermode='x unified',
                    font=dict(family="Arial, sans-serif", size=11),
                    plot_bgcolor='rgba(240,240,240,0.5)',
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Decisions Over Time")
            if not decisions_df.empty:
                decisions_df_copy = decisions_df.copy()
                decisions_df_copy['made_at'] = pd.to_datetime(decisions_df_copy['made_at'])
                decisions_by_date = decisions_df_copy.groupby(decisions_df_copy['made_at'].dt.date).size()
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=decisions_by_date.index,
                    y=decisions_by_date.values,
                    marker=dict(
                        color='#17a2b8',
                        line=dict(color='#0d0d0d', width=0.5)
                    )
                ))
                
                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Number of Decisions",
                    height=350,
                    font=dict(family="Arial, sans-serif", size=11),
                    plot_bgcolor='rgba(240,240,240,0.5)',
                    margin=dict(l=20, r=20, t=20, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No decision data available yet")
        
        st.markdown("---")
        
        # Email statistics
        if not emails_df.empty:
            st.markdown("### 📧 Email Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            total_emails = len(emails_df)
            sent_emails = len(emails_df[emails_df['status'] == 'SENT'])
            failed_emails = len(emails_df[emails_df['status'] == 'FAILED'])
            
            with col1:
                st.markdown(f"""
                <div class='metric-card' style='border-left-color: #1F4788;'>
                    <div class='metric-label'>Total Emails</div>
                    <div class='metric-value'>{total_emails}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                sent_rate = (sent_emails / total_emails * 100) if total_emails > 0 else 0
                st.markdown(f"""
                <div class='metric-card' style='border-left-color: #28a745;'>
                    <div class='metric-label'>Sent</div>
                    <div class='metric-value' style='color: #28a745;'>{sent_emails}</div>
                    <small style='color: #6c757d;'>{sent_rate:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                failed_rate = (failed_emails / total_emails * 100) if total_emails > 0 else 0
                st.markdown(f"""
                <div class='metric-card' style='border-left-color: #dc3545;'>
                    <div class='metric-label'>Failed</div>
                    <div class='metric-value' style='color: #dc3545;'>{failed_emails}</div>
                    <small style='color: #6c757d;'>{failed_rate:.1f}%</small>
                </div>
                """, unsafe_allow_html=True)


# =========================
# ⚙️ SETTINGS
# =========================
elif page == "⚙️ Settings":

    st.header("Profile")
    if st.session_state.user_id:
        conn = get_conn()
        user = pd.read_sql(
            "SELECT * FROM users WHERE id=?",
            conn,
            params=(user_id,)
        ).iloc[0]

        st.markdown(f"""
        ### {user['name']} from {user['company']} | Email: {user['email']}  
        """)
    if st.button("Logout"):
        st.session_state.user_id = None
        st.rerun()

    # SYSTEM CHECK
    try:
        conn = get_conn()
        conn.execute("SELECT 1")
        st.success("DB OK")
    except:
        st.error("DB Error")

    if os.path.exists("resumes"):
        st.success("Resumes folder OK")
    else:
        st.error("Resumes folder missing")