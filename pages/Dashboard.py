import streamlit as st
import pandas as pd
import plotly.express as px

# Importing our database actions
from app.data.incidents import get_all_incidents, insert_incident

# 1. Page Configuration
st.set_page_config(
    page_title="Threat Feed", 
    page_icon="📡", 
    layout="wide"
)

# 2. Security Gatekeeper
# We need to bounce the user back to Home if they aren't logged in.
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Access Restricted. Please log in first.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

# 3. Sidebar (User Profile & Actions)
with st.sidebar:
    st.header("👤 User Profile")
    st.write(f"**Analyst:** {st.session_state.username}")
    st.write("**Role:** Cyber Analyst") # Placeholder for now
    
    st.divider()
    
    if st.button("🚪 Log Out", type="secondary"):
        # Clear session and redirect
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")

# 4. Main Title Area
st.title("📡 Live Threat Intelligence Feed")
st.markdown(f"Welcome back, **{st.session_state.username}**. Here is the current security posture.")

# 5. Fetch Data from Database
# We get the dataframe once and use it for all charts/tables
incidents_df = get_all_incidents()

# 6. Key Performance Indicators (KPIs)
# Let's show some quick numbers at the top
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric(label="Total Incidents", value=len(incidents_df))
with kpi2:
    # calculating open cases dynamically
    open_cases = len(incidents_df[incidents_df['status'] == 'Open'])
    st.metric(label="Active / Open", value=open_cases, delta="Action Required", delta_color="inverse")
with kpi3:
    crit_cases = len(incidents_df[incidents_df['severity'] == 'Critical'])
    st.metric(label="Critical Threats", value=crit_cases, delta_color="inverse")
with kpi4:
    # Just a placeholder for resolved percentage
    resolved_cases = len(incidents_df[incidents_df['status'] == 'Resolved'])
    st.metric(label="Resolved", value=resolved_cases)

st.divider()

# 7. Visualisations
# I'll put charts side-by-side
chart_col_left, chart_col_right = st.columns(2)

with chart_col_left:
    st.subheader("🔍 Incidents by Category")
    if not incidents_df.empty:
        # Grouping data for the chart
        type_counts = incidents_df['category'].value_counts().reset_index()
        type_counts.columns = ['category', 'count']
        
        # Horizontal bar chart is often easier to read for categories
        fig_bar = px.bar(
            type_counts, 
            x='count', 
            y='category', 
            orientation='h', 
            color='count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with chart_col_right:
    st.subheader("⚠️ Severity Distribution")
    if not incidents_df.empty:
        # Using a Donut chart (hole=.4) looks a bit more modern
        fig_pie = px.pie(
            incidents_df, 
            names='severity', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# 8. Data Management (Add New)
# I'll hide this in an expander so it doesn't take up space constantly
with st.expander("➕ Log New Security Event"):
    st.write("Fill out the details below to log a new threat into the database.")
    
    with st.form("incident_entry_form"):
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            i_date = st.date_input("Date of Occurrence")
            i_type = st.selectbox("Threat Type", ["Phishing", "Malware", "DDoS", "Ransomware", "Insider", "Other"])
            i_sev = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
            
        with f_col2:
            i_status = st.selectbox("Current Status", ["Open", "Investigating", "Resolved", "Closed"])
            i_desc = st.text_area("Incident Details / Description")
            
        submit_incident = st.form_submit_button("📥 Save to Database")
        
        if submit_incident:
            # Calling the Week 8 backend function
            insert_incident(
                date=str(i_date),
                incident_type=i_type,
                severity=i_sev,
                status=i_status,
                description=i_desc
            )

            st.success("New incident logged successfully!")
            st.rerun() # Refresh the page to update the charts and table

# 9. Detailed Data View
st.subheader("📋 Incident Logs")
st.dataframe(
    incidents_df, 
    use_container_width=True, 
    hide_index=True # Hides the row numbers for a cleaner look
)

