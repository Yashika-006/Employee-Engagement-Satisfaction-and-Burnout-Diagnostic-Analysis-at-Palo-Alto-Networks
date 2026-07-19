import streamlit as st
import pandas as pd
import plotly.express as px

# Load the processed data
df = pd.read_excel('Palo Alto Networks.xlsx')
# [Add the logic from Phase 1 here to create the columns]
df['EngagementIndex'] = (df['JobInvolvement'] + df['JobSatisfaction'] + 
                         df['EnvironmentSatisfaction'] + df['RelationshipSatisfaction']) / 4
df['OverTime_Numeric'] = df['OverTime'].map({'Yes': 1, 'No': 0})
df['BurnoutRisk'] = ((df['OverTime_Numeric'] == 1) & (df['WorkLifeBalance'] <= 2)).astype(int)

st.title("Palo Alto Networks: Employee Experience Diagnostics")

# Filters
dept = st.multiselect("Select Department", df['Department'].unique())
if dept:
    df = df[df['Department'].isin(dept)]

# Module 1: Engagement Overview
st.header("Engagement Health Overview")
fig_engagement = px.histogram(df, x="EngagementIndex", nbins=10, title="Distribution of Engagement Scores")
st.plotly_chart(fig_engagement)

# Module 2: Burnout Risk
st.header("Burnout Risk Dashboard")
st.metric("High-Risk Employees", f"{df['BurnoutRisk'].sum()} / {len(df)}")
fig_burnout = px.scatter(df, x="TotalWorkingYears", y="MonthlyIncome", color="BurnoutRisk", 
                         title="Burnout Risk by Tenure and Income")
st.plotly_chart(fig_burnout)

# Identify which Job Roles have the highest average Burnout Risk
burnout_by_role = df.groupby('JobRole')['BurnoutRisk'].mean().sort_values(ascending=False)
print("Burnout Risk by Job Role:")
print(burnout_by_role)

# Identify which Job Roles have the lowest average Engagement Index
engagement_by_role = df.groupby('JobRole')['EngagementIndex'].mean().sort_values(ascending=True)
print("\nEngagement Index by Job Role:")
print(engagement_by_role)