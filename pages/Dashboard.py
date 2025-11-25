import streamlit as st
import pandas as pd
import plotly.express as px

# Importing our database actions
from app.data.incidents import get_all_incidents, insert_incident

# 1️⃣ Page Configuration
st.set_page_config(
    page_title="Threat Feed",
    page_icon="📡",
    layout="wide"
)

# 2️⃣ Security Gatekeeper
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⛔ Access Restricted. Please log in first.")
    if st.button("Back to Login"):
        st.switch_page("Home.py")
    st.stop()

# 3️⃣ Sidebar
with st.sidebar:
    st.header("👤 User Profile")
    st.write(f"**Analyst:** {st.session_state.username}")
    st.write("**Role:** Cyber Analyst")
    st.divider()
    if st.button("🚪 Log Out", type="secondary"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.switch_page("Home.py")

# 4️⃣ Main Title
st.title("📡 Live Threat Intelligence Feed")
st.markdown(f"Welcome back, **{st.session_state.username}**. Here is the current security posture.")

# 5️⃣ Fetch Data
incidents_df = get_all_incidents()

# 6️⃣ KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total Incidents", len(incidents_df))
with kpi2:
    open_cases = len(incidents_df[incidents_df['status'] == 'Open']) if 'status' in incidents_df.columns else 0
    st.metric("Active / Open", open_cases, delta="Action Required", delta_color="inverse")
with kpi3:
    crit_cases = len(incidents_df[incidents_df['severity'] == 'Critical']) if 'severity' in incidents_df.columns else 0
    st.metric("Critical Threats", crit_cases, delta_color="inverse")
with kpi4:
    resolved_cases = len(incidents_df[incidents_df['status'] == 'Resolved']) if 'status' in incidents_df.columns else 0
    st.metric("Resolved", resolved_cases)

st.divider()

# 7️⃣ Visualisations
chart_col_left, chart_col_right = st.columns(2)

with chart_col_left:
    st.subheader("🔍 Incidents by Category")
    if 'category' in incidents_df.columns and not incidents_df.empty:
        type_counts = incidents_df['category'].value_counts().reset_index()
        type_counts.columns = ['category', 'count']
        fig_bar = px.bar(type_counts, x='count', y='category', orientation='h', color='count',
                         color_continuous_scale='Blues')
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No incident category data available.")

with chart_col_right:
    st.subheader("⚠️ Severity Distribution")
    if 'severity' in incidents_df.columns and not incidents_df.empty:
        fig_pie = px.pie(incidents_df, names='severity', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No severity data available.")

# 8️⃣ Data Entry Form
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
            insert_incident(
                date=str(i_date),
                severity=i_sev,
                category=i_type,
                status=i_status,
                description=i_desc
            )
            st.success("New incident logged successfully!")
            st.rerun()

# 9️⃣ Data Table
st.subheader("📋 Incident Logs")
if not incidents_df.empty:
    st.dataframe(incidents_df, use_container_width=True, hide_index=True)
else:
    st.info("No incidents to display.")
