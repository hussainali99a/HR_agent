"""
HR Recruitment Dashboard
Interactive Streamlit UI for monitoring recruitment process
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_FILE
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="HR Recruitment Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🤖 AI HR Recruitment Dashboard")
st.markdown("Real-time recruitment analytics and candidate management")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select View",
    ["📊 Overview", "👤 Candidates", "📈 Analytics", "⚙️ Settings"]
)

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_FILE)
    return conn

def load_candidates_data():
    """Load all candidates from database"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('SELECT * FROM candidates ORDER BY created_at DESC', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def load_decisions_data():
    """Load all decisions from database"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('''
            SELECT d.*, c.name, c.email 
            FROM decisions d
            LEFT JOIN candidates c ON d.candidate_id = c.id
            ORDER BY d.made_at DESC
        ''', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

def load_email_logs():
    """Load email logs"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query('''
            SELECT e.*, c.name, c.email 
            FROM email_logs e
            LEFT JOIN candidates c ON e.candidate_id = c.id
            ORDER BY e.sent_at DESC
        ''', conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ===== OVERVIEW PAGE =====
if page == "📊 Overview":
    df = load_candidates_data()
    
    if df.empty:
        st.warning("No candidates in database yet. Run main_agent.py to process resumes.")
    else:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Candidates", len(df))
        
        with col2:
            accepted = len(df[df['status'] == 'ACCEPTED'])
            st.metric("Accepted", accepted, f"({accepted/len(df)*100:.1f}%)")
        
        with col3:
            under_review = len(df[df['status'] == 'UNDER_REVIEW'])
            st.metric("Under Review", under_review, f"({under_review/len(df)*100:.1f}%)")
        
        with col4:
            rejected = len(df[df['status'] == 'REJECTED'])
            st.metric("Rejected", rejected, f"({rejected/len(df)*100:.1f}%)")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Candidate Status Distribution")
            status_counts = df['status'].value_counts()
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                hole=0.3
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Match Score Distribution")
            fig = px.histogram(
                df,
                x='match_score',
                nbins=10,
                title="Score Distribution",
                labels={'match_score': 'Score', 'count': 'Number of Candidates'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent candidates
        st.subheader("Recent Candidates")
        display_df = df[['name', 'email', 'match_score', 'status', 'created_at']].head(10)
        display_df['match_score'] = (display_df['match_score'] * 100).round(1).astype(str) + '%'
        st.dataframe(display_df, use_container_width=True)

# ===== CANDIDATES PAGE =====
elif page == "👤 Candidates":
    df = load_candidates_data()
    
    st.subheader("Candidate Management")
    
    if df.empty:
        st.warning("No candidates found")
    else:
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=df['status'].unique(),
                default=df['status'].unique()
            )
        
        with col2:
            min_score = st.number_input(
                "Minimum Score (%)",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=5.0
            ) / 100
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Created Date", "Match Score", "Name"]
            )
        
        # Filter data
        filtered_df = df[df['status'].isin(status_filter)]
        filtered_df = filtered_df[filtered_df['match_score'] >= min_score]
        
        # Sort data
        if sort_by == "Match Score":
            filtered_df = filtered_df.sort_values('match_score', ascending=False)
        elif sort_by == "Name":
            filtered_df = filtered_df.sort_values('name')
        
        # Display table
        display_df = filtered_df[['name', 'email', 'match_score', 'status', 'created_at']].copy()
        display_df['match_score'] = (display_df['match_score'] * 100).round(1).astype(str) + '%'
        
        st.dataframe(display_df, use_container_width=True)
        
        # Candidate details
        if len(filtered_df) > 0:
            st.subheader("Candidate Details")
            selected_candidate = st.selectbox(
                "Select candidate to view details",
                options=filtered_df['name'].values
            )
            
            candidate = filtered_df[filtered_df['name'] == selected_candidate].iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Name:** {candidate['name']}")
                st.write(f"**Email:** {candidate['email']}")
                st.write(f"**Phone:** {candidate['phone']}")
                st.write(f"**Resume:** {candidate['resume_file']}")
            
            with col2:
                st.write(f"**Match Score:** {candidate['match_score']*100:.1f}%")
                st.write(f"**Status:** {candidate['status']}")
                st.write(f"**Applied:** {candidate['application_date']}")
                st.write(f"**Summary:** {candidate['summary']}")

# ===== ANALYTICS PAGE =====
elif page == "📈 Analytics":
    st.subheader("Recruitment Analytics")
    
    decisions_df = load_decisions_data()
    emails_df = load_email_logs()
    candidates_df = load_candidates_data()
    
    if decisions_df.empty:
        st.info("No decision data yet")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Decision Distribution**")
            decision_counts = decisions_df['decision'].value_counts()
            st.bar_chart(decision_counts)
        
        with col2:
            st.write("**Email Status**")
            if not emails_df.empty:
                email_counts = emails_df['status'].value_counts()
                st.bar_chart(email_counts)
    
    # Timeline
    if not decisions_df.empty:
        st.subheader("Decision Timeline")
        decisions_df['made_at'] = pd.to_datetime(decisions_df['made_at'])
        decisions_by_date = decisions_df.groupby(decisions_df['made_at'].dt.date).size()
        st.line_chart(decisions_by_date)
    
    # Score statistics
    if not candidates_df.empty:
        st.subheader("Score Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Score", f"{candidates_df['match_score'].mean()*100:.1f}%")
        with col2:
            st.metric("Max Score", f"{candidates_df['match_score'].max()*100:.1f}%")
        with col3:
            st.metric("Min Score", f"{candidates_df['match_score'].min()*100:.1f}%")
        with col4:
            st.metric("Std Dev", f"{candidates_df['match_score'].std()*100:.2f}%")

# ===== SETTINGS PAGE =====
elif page == "⚙️ Settings":
    st.subheader("Settings & Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("### System Status")
        st.info("✅ Database connected")
        st.info("📊 Dashboard running")
    
    with col2:
        st.write("### Database Info")
        candidates_count = len(load_candidates_data())
        st.info(f"Candidates: {candidates_count}")
        st.info(f"Database: {DATABASE_FILE}")
    
    # Data export
    st.subheader("Export Data")
    if st.button("Export Candidates to CSV"):
        df = load_candidates_data()
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    # Clear database (with confirmation)
    st.subheader("⚠️ Dangerous Operations")
    if st.checkbox("I understand the risks"):
        if st.button("Delete All Data", key="delete_all"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM candidates')
                cursor.execute('DELETE FROM decisions')
                cursor.execute('DELETE FROM email_logs')
                cursor.execute('DELETE FROM meetings')
                conn.commit()
                conn.close()
                st.success("All data deleted")
            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.markdown("---")
st.markdown("🤖 **AI HR Recruitment System** | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))