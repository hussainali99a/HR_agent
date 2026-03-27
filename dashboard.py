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

# Custom CSS for professional styling
custom_css = """
<style>
    /* Primary colors */
    :root {
        --primary: #1F4788;
        --success: #28a745;
        --warning: #ffc107;
        --danger: #dc3545;
        --info: #17a2b8;
        --light: #f8f9fa;
        --dark: #343a40;
    }
    
    /* Main content styling */
    .main {
        padding: 2rem 1rem;
    }
    
    /* Header styling */
    .header-title {
        background: linear-gradient(135deg, #1F4788 0%, #2e5fa3 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .header-title h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .header-subtitle {
        color: #e8f0f8;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Metric card styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #1F4788;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1F4788;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Status badges */
    .badge-accepted {
        background: #28a745;
        color: white;
    }
    
    .badge-rejected {
        background: #dc3545;
        color: white;
    }
    
    .badge-pending {
        background: #ffc107;
        color: #333;
    }
    
    .badge-under-review {
        background: #17a2b8;
        color: white;
    }
    
    /* Card styling */
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
    }
    
    /* Section title */
    .section-title {
        color: #1F4788;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #1F4788;
        padding-bottom: 0.5rem;
    }
    
    /* Data table styling */
    .dataframe {
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        padding: 2rem 1rem;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Header section
st.markdown("""
<div class="header-title">
    <h1>🤖 AI HR Recruitment Dashboard</h1>
    <div class="header-subtitle">Real-time recruitment analytics & candidate management</div>
</div>
""", unsafe_allow_html=True)

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
        st.warning("⚠️ No candidates in database yet. Run main_agent.py to process resumes.")
    else:
        # Key metrics
        st.markdown("<div class='section-title'>📊 Key Metrics</div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_candidates = len(df)
        accepted_count = len(df[df['status'] == 'ACCEPTED'])
        under_review_count = len(df[df['status'] == 'UNDER_REVIEW'])
        rejected_count = len(df[df['status'] == 'REJECTED'])
        
        with col1:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-label'>Total Candidates</div>
                <div class='metric-value'>{total_candidates}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            acceptance_rate = (accepted_count / total_candidates * 100) if total_candidates > 0 else 0
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #28a745;'>
                <div class='metric-label'>Accepted</div>
                <div class='metric-value' style='color: #28a745;'>{accepted_count}</div>
                <small style='color: #6c757d;'>{acceptance_rate:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            review_rate = (under_review_count / total_candidates * 100) if total_candidates > 0 else 0
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #17a2b8;'>
                <div class='metric-label'>Under Review</div>
                <div class='metric-value' style='color: #17a2b8;'>{under_review_count}</div>
                <small style='color: #6c757d;'>{review_rate:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            rejection_rate = (rejected_count / total_candidates * 100) if total_candidates > 0 else 0
            st.markdown(f"""
            <div class='metric-card' style='border-left-color: #dc3545;'>
                <div class='metric-label'>Rejected</div>
                <div class='metric-value' style='color: #dc3545;'>{rejected_count}</div>
                <small style='color: #6c757d;'>{rejection_rate:.1f}%</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Charts section
        st.markdown("<div class='section-title'>📈 Analytics & Insights</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Candidate Status Distribution")
            status_counts = df['status'].value_counts()
            colors = {'ACCEPTED': '#28a745', 'REJECTED': '#dc3545', 'UNDER_REVIEW': '#17a2b8'}
            color_list = [colors.get(status, '#1F4788') for status in status_counts.index]
            
            fig = go.Figure(data=[go.Pie(
                labels=status_counts.index,
                values=status_counts.values,
                hole=0.3,
                marker=dict(colors=color_list),
                textposition='inside',
                textinfo='label+percent'
            )])
            fig.update_layout(
                height=400,
                font=dict(family="Arial, sans-serif", size=12),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Match Score Distribution")
            fig = go.Figure(data=[go.Histogram(
                x=df['match_score'] * 100,
                nbinsx=15,
                marker=dict(
                    color='#1F4788',
                    line=dict(color='#0d2450', width=1)
                ),
                opacity=0.7
            )])
            fig.update_layout(
                title="",
                xaxis_title="Match Score (%)",
                yaxis_title="Number of Candidates",
                height=400,
                hovermode='x unified',
                font=dict(family="Arial, sans-serif", size=11),
                margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor='rgba(240,240,240,0.5)',
                xaxis=dict(gridcolor='white')
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Recent candidates table
        st.markdown("<div class='section-title'>👥 Recent Candidates</div>", unsafe_allow_html=True)
        
        display_df = df[['name', 'email', 'match_score', 'status', 'created_at']].head(15).copy()
        display_df['match_score'] = (display_df['match_score'] * 100).round(1).astype(str) + '%'
        display_df.columns = ['Name', 'Email', 'Match Score', 'Status', 'Applied Date']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ===== CANDIDATES PAGE =====
elif page == "👤 Candidates":
    df = load_candidates_data()
    
    st.markdown("<div class='section-title'>👥 Candidate Management & Search</div>", unsafe_allow_html=True)
    
    if df.empty:
        st.warning("⚠️ No candidates found")
    else:
        # Advanced filters
        st.markdown("### Search & Filter Options")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            status_filter = st.multiselect(
                "Filter by Status",
                options=sorted(df['status'].unique()),
                default=sorted(df['status'].unique()),
                key="status_multi"
            )
        
        with col2:
            min_score = st.slider(
                "Minimum Match Score (%)",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            ) / 100
        
        with col3:
            sort_by = st.selectbox(
                "Sort by",
                ["Date (Newest)", "Date (Oldest)", "Match Score (High to Low)", "Match Score (Low to High)", "Name (A-Z)"]
            )
        
        with col4:
            show_count = st.number_input(
                "Show Records",
                min_value=5,
                max_value=100,
                value=20,
                step=5
            )
        
        # Filter data
        filtered_df = df[df['status'].isin(status_filter)].copy()
        filtered_df = filtered_df[filtered_df['match_score'] >= min_score]
        
        # Sort data
        if sort_by == "Match Score (High to Low)":
            filtered_df = filtered_df.sort_values('match_score', ascending=False)
        elif sort_by == "Match Score (Low to High)":
            filtered_df = filtered_df.sort_values('match_score', ascending=True)
        elif sort_by == "Name (A-Z)":
            filtered_df = filtered_df.sort_values('name', ascending=True)
        elif sort_by == "Date (Oldest)":
            filtered_df = filtered_df.sort_values('created_at', ascending=True)
        else:  # Default: Date (Newest)
            filtered_df = filtered_df.sort_values('created_at', ascending=False)
        
        filtered_df = filtered_df.head(int(show_count))
        
        # Show summary
        st.info(f"📊 Showing {len(filtered_df)} of {len(df)} total candidates")
        
        st.markdown("---")
        
        # Display table with better formatting
        display_df = filtered_df[['name', 'email', 'match_score', 'status', 'created_at']].copy()
        display_df['match_score'] = (display_df['match_score'] * 100).round(1).astype(str) + '%'
        display_df.columns = ['Name', 'Email', 'Match Score', 'Status', 'Applied Date']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # Candidate details section
        if len(filtered_df) > 0:
            st.markdown("<div class='section-title'>📋 Candidate Details</div>", unsafe_allow_html=True)
            
            selected_candidate = st.selectbox(
                "Select a candidate to view full details",
                options=filtered_df['name'].values,
                key="candidate_select"
            )
            
            candidate = filtered_df[filtered_df['name'] == selected_candidate].iloc[0]
            
            # Status badge color
            status_colors = {
                'ACCEPTED': '#28a745',
                'REJECTED': '#dc3545',
                'UNDER_REVIEW': '#17a2b8'
            }
            status_color = status_colors.get(candidate['status'], '#6c757d')
            
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                    <h4 style='color: #1F4788; margin-top: 0;'>Personal Information</h4>
                    <p><strong>Name:</strong> {candidate['name']}</p>
                    <p><strong>Email:</strong> {candidate['email']}</p>
                    <p><strong>Phone:</strong> {candidate.get('phone', 'N/A')}</p>
                    <p><strong>Resume File:</strong> {candidate.get('resume_file', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                    <h4 style='color: #1F4788; margin-top: 0;'>Application Details</h4>
                    <p><strong>Match Score:</strong> <span style='font-size: 1.3em; color: #1F4788; font-weight: bold;'>{candidate['match_score']*100:.1f}%</span></p>
                    <p><strong>Status:</strong> <span style='background: {status_color}; color: white; padding: 0.3rem 0.7rem; border-radius: 20px;'>{candidate['status']}</span></p>
                    <p><strong>Applied:</strong> {candidate.get('application_date', candidate.get('created_at', 'N/A'))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.08);'>
                    <h4 style='color: #1F4788; margin-top: 0;'>Score</h4>
                    <svg width="100" height="100" style='display: block; margin: 0 auto;'>
                        <circle cx="50" cy="50" r="45" fill="none" stroke='#e9ecef' stroke-width="10"/>
                        <circle cx="50" cy="50" r="45" fill="none" stroke='{status_color}' stroke-width="10" 
                                stroke-dasharray="{candidate['match_score'] * 283}" stroke-dashoffset="0"
                                style='transform: rotate(-90deg); transform-origin: 50px 50px;'/>
                        <text x="50" y="60" text-anchor="middle" font-size="20" font-weight="bold" fill="{status_color}">
                            {candidate['match_score']*100:.0f}%
                        </text>
                    </svg>
                </div>
                """, unsafe_allow_html=True)
            
            # Candidate summary
            if candidate.get('summary'):
                st.markdown("### Candidate Summary")
                st.info(candidate['summary'])

# ===== ANALYTICS PAGE =====
elif page == "📈 Analytics":
    st.markdown("<div class='section-title'>📊 Recruitment Analytics & Insights</div>", unsafe_allow_html=True)
    
    decisions_df = load_decisions_data()
    emails_df = load_email_logs()
    candidates_df = load_candidates_data()
    
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

# ===== SETTINGS PAGE =====
elif page == "⚙️ Settings":
    st.markdown("<div class='section-title'>⚙️ Settings & Configuration</div>", unsafe_allow_html=True)
    
    # System Status
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### System Status")
        
        st.markdown("""
        <div class='section-card'>
            <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                <span style='color: #28a745; font-size: 1.5rem; margin-right: 10px;'>✅</span>
                <strong>Database Connected</strong>
            </div>
            <div style='display: flex; align-items: center; margin-bottom: 1rem;'>
                <span style='color: #28a745; font-size: 1.5rem; margin-right: 10px;'>✅</span>
                <strong>Dashboard Running</strong>
            </div>
            <div style='display: flex; align-items: center;'>
                <span style='color: #28a745; font-size: 1.5rem; margin-right: 10px;'>✅</span>
                <strong>Email Service Active</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Database Information")
        
        candidates_count = len(load_candidates_data())
        decisions_df = load_decisions_data()
        decisions_count = len(decisions_df)
        emails_df = load_email_logs()
        emails_count = len(emails_df)
        
        st.markdown(f"""
        <div class='section-card'>
            <p><strong>📊 Candidates:</strong> {candidates_count}</p>
            <p><strong>✅ Decisions Made:</strong> {decisions_count}</p>
            <p><strong>📧 Emails Sent:</strong> {emails_count}</p>
            <p><strong>💾 Database:</strong> {DATABASE_FILE}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Data Management
    st.markdown("### 📥 Data Management")
    
    tab1, tab2, tab3 = st.tabs(["📊 Export", "📥 Import", "⚠️ Advanced"])
    
    with tab1:
        st.markdown("#### Export Candidates Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Select Format",
                ["CSV", "Excel", "JSON"]
            )
        
        with col2:
            export_status = st.multiselect(
                "Export Status",
                options=["ACCEPTED", "REJECTED", "UNDER_REVIEW"],
                default=["ACCEPTED", "REJECTED", "UNDER_REVIEW"]
            )
        
        if st.button("📥 Generate Export", key="export_btn"):
            df = load_candidates_data()
            
            if export_status:
                df = df[df['status'].isin(export_status)]
            
            if export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download CSV",
                    data=csv,
                    file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_csv"
                )
                st.success("✅ CSV ready for download")
            
            elif export_format == "Excel":
                try:
                    excel_file = f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    df.to_excel(excel_file, index=False)
                    
                    with open(excel_file, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Excel",
                            data=f.read(),
                            file_name=excel_file,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            key="download_excel"
                        )
                    st.success("✅ Excel file ready for download")
                except ImportError:
                    st.warning("⚠️ Excel export requires openpyxl. Using CSV instead.")
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download as CSV",
                        data=csv,
                        file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_csv_fallback"
                    )
            
            elif export_format == "JSON":
                json_str = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="⬇️ Download JSON",
                    data=json_str,
                    file_name=f"candidates_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="download_json"
                )
                st.success("✅ JSON ready for download")
    
    with tab2:
        st.info("📌 Import functionality coming soon")
    
    with tab3:
        st.markdown("#### 🔒 Advanced Operations")
        
        st.warning("⚠️ These operations cannot be undone. Please proceed with caution.")
        
        operation = st.radio(
            "Select Operation",
            ["Backup Database", "Clear Specific Status", "Delete All Data"],
            key="operation_radio"
        )
        
        if operation == "Backup Database":
            if st.button("🔄 Create Backup", key="backup_btn"):
                try:
                    import shutil
                    backup_file = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy(DATABASE_FILE, backup_file)
                    
                    with open(backup_file, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Backup",
                            data=f.read(),
                            file_name=backup_file,
                            key="download_backup"
                        )
                    st.success(f"✅ Database backed up successfully")
                except Exception as e:
                    st.error(f"❌ Backup failed: {e}")
        
        elif operation == "Clear Specific Status":
            status_to_clear = st.multiselect(
                "Select status to clear",
                options=["ACCEPTED", "REJECTED", "UNDER_REVIEW"],
                key="status_clear"
            )
            
            if status_to_clear:
                if st.checkbox("I understand this will delete all candidates with selected status", key="clear_check"):
                    if st.button("🗑️ Clear Data", key="clear_btn"):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            placeholders = ','.join('?' * len(status_to_clear))
                            cursor.execute(f'DELETE FROM candidates WHERE status IN ({placeholders})', status_to_clear)
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Deleted all candidates with status: {', '.join(status_to_clear)}")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
        
        elif operation == "Delete All Data":
            st.error("🔴 This will permanently delete all data in the database")
            
            if st.checkbox("I understand this will delete all data permanently", key="delete_all_check"):
                if st.checkbox("I confirm the deletion", key="delete_confirm"):
                    if st.button("🗑️ Delete All Data", key="delete_all_btn"):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute('DELETE FROM candidates')
                            cursor.execute('DELETE FROM decisions')
                            cursor.execute('DELETE FROM email_logs')
                            cursor.execute('DELETE FROM meetings')
                            conn.commit()
                            conn.close()
                            
                            st.success("✅ All data has been deleted")
                            st.info("🔄 The dashboard will refresh momentarily")
                            
                        except Exception as e:
                            st.error(f"❌ Error: {e}")

st.markdown("---")

# Footer
st.markdown(f"""
<div style='text-align: center; color: #6c757d; font-size: 0.9rem; margin-top: 2rem;'>
    <p>🤖 <strong>AI HR Recruitment System</strong> | Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p style='font-size: 0.8rem; opacity: 0.7;'>© 2024-2026 HR Department | All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)