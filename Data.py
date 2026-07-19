import pandas as pd

# Load the file to inspect the structure
file_path = 'Palo Alto Networks.xlsx'
try:
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    df = pd.read_excel(file_path)
    print(f"Sheets: {sheet_names}")
    print(df.head())
    print(df.info())
except Exception as e:
    print(f"Error: {e}")
# Apply the requested data processing logic
# 1. Engagement Index: Average of JobInvolvement, JobSatisfaction, EnvironmentSatisfaction, RelationshipSatisfaction
df['EngagementIndex'] = (df['JobInvolvement'] + df['JobSatisfaction'] + 
                         df['EnvironmentSatisfaction'] + df['RelationshipSatisfaction']) / 4

# 2. Burnout Risk: OverTime == Yes (1) AND WorkLifeBalance <= 2
# Let's map Yes/No to 1/0 first
df['OverTime_Numeric'] = df['OverTime'].map({'Yes': 1, 'No': 0})
df['BurnoutRisk'] = ((df['OverTime_Numeric'] == 1) & (df['WorkLifeBalance'] <= 2)).astype(int)

# 3. Workload Stress Indicator (Basic form: OverTime + Travel)
# Let's map Travel to a numeric scale
travel_map = {'Non-Travel': 0, 'Travel_Rarely': 1, 'Travel_Frequently': 2}
df['Travel_Numeric'] = df['BusinessTravel'].map(travel_map)
df['WorkloadStressIndicator'] = df['OverTime_Numeric'] + df['Travel_Numeric']

print(df[['EngagementIndex', 'BurnoutRisk', 'WorkloadStressIndicator']].head())
print(df[['EngagementIndex', 'BurnoutRisk', 'WorkloadStressIndicator']].describe())