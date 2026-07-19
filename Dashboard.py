import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- Page Setup ---
st.set_page_config(layout="wide", page_title="Palo Alto Networks HR Diagnostic")
st.title("🛡️ Employee Engagement, Satisfaction, and Burnout Diagnostic Analysis")

# --- Load & Prep Data ---
@st.cache_data
def load_data():
    df = pd.read_excel('Palo Alto Networks.xlsx')
    
    # Core Logic
    df['EngagementIndex'] = (df['JobInvolvement'] * 0.25 + df['JobSatisfaction'] * 0.35 + 
                             df['EnvironmentSatisfaction'] * 0.20 + df['RelationshipSatisfaction'] * 0.20)
    df['OverTime_Numeric'] = df['OverTime'].map({'Yes': 1, 'No': 0})
    df['BurnoutScore'] = (df['OverTime_Numeric'] * 0.6) + ((5 - df['WorkLifeBalance']) * 0.4)
    df['AttritionRisk'] = (4 - df['EngagementIndex']) * 0.4 + (df['BurnoutScore']) * 0.4 + (df['YearsSinceLastPromotion'] > 3).astype(int) * 0.2
    return df

df = load_data()

# --- Sidebar Controls (User Capabilities) ---
st.sidebar.header("🔍 Dashboard Controls")
dept_filter = st.sidebar.multiselect("Department", df['Department'].unique())
role_filter = st.sidebar.multiselect("Job Role", df['JobRole'].unique())
ot_toggle = st.sidebar.selectbox("Overtime Status", ["All", "Yes", "No"])
engagement_slider = st.sidebar.slider("Minimum Engagement Threshold", 1.0, 4.0, 2.0)
tenure_selector = st.sidebar.slider("Tenure Range (Years)", 0, int(df['YearsAtCompany'].max()), (0, int(df['YearsAtCompany'].max())))

# --- Apply Filters ---
dff = df[(df['Department'].isin(dept_filter) if dept_filter else True) &
         (df['JobRole'].isin(role_filter) if role_filter else True) &
         (df['OverTime'] == ot_toggle if ot_toggle != "All" else True) &
         (df['EngagementIndex'] >= engagement_slider) &
         (df['YearsAtCompany'].between(tenure_selector[0], tenure_selector[1]))]

# --- Dashboard Modules ---
tabs = st.tabs(["Overview", "Burnout Risk", "Role & Career Analysis", "Manager Action Panel"])

with tabs[0]: # Engagement Health Overview
    st.subheader("Organization-wide Engagement Health")
    c1, c2 = st.columns(2)
    c1.metric("Avg Engagement Index", f"{dff['EngagementIndex'].mean():.2f}")
    c2.metric("Total Employees", len(dff))
    st.plotly_chart(px.histogram(dff, x="EngagementIndex", color="Department", title="Satisfaction Distribution"), use_container_width=True)

with tabs[1]: # Burnout Risk Dashboard
    st.subheader("High-Risk Segments & Imbalance")
    c1, c2 = st.columns(2)
    c1.plotly_chart(px.pie(dff, names='OverTime', title="Overtime vs. Work-Life Imbalance"), use_container_width=True)
    c2.plotly_chart(px.scatter(dff, x="TotalWorkingYears", y="MonthlyIncome", color="BurnoutScore", title="Burnout Intensity by Experience"), use_container_width=True)

with tabs[2]: # Role & Career Stage Analysis
    st.subheader("Engagement by Role and Tenure")
    st.plotly_chart(px.box(dff, x="JobRole", y="EngagementIndex", color="JobLevel", title="Engagement by Role and Level"), use_container_width=True)
    st.plotly_chart(px.scatter(dff, x="YearsAtCompany", y="EngagementIndex", trendline="ols", title="Tenure vs Engagement Trend"), use_container_width=True)

with tabs[3]: # Manager Action Panel
    st.subheader("⚠️ Priority Intervention Areas")
    
    # Logic for high-risk alert
    high_alert = dff[dff['AttritionRisk'] >= 0.6].sort_values('AttritionRisk', ascending=False)
    
    # Display the filtered dataframe
    st.dataframe(high_alert[['JobRole', 'Department', 'AttritionRisk', 'EngagementIndex', 'MonthlyIncome', 'YearsAtCompany']], use_container_width=True)
    
    # CSV Download capability for HR managers
    if not high_alert.empty:
        csv = high_alert.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Priority Intervention List", csv, "intervention_list.csv", "text/csv")
    else:
        st.success("No high-risk intervention alerts detected in this segment.")