# app.py
import streamlit as st
import pandas as pd
from openai import OpenAI

# -------------------------------
# Streamlit App Title
# -------------------------------
st.set_page_config(page_title="AI Employee Retention Predictor", layout="wide")
st.title("AI Employee Retention Predictor 🚀")

# -------------------------------
# CSV Upload
# -------------------------------
uploaded_file = st.file_uploader("Upload your HR CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("✅ CSV loaded successfully!")
    st.dataframe(df.head())

    # -------------------------------
    # Calculate Salary Gap
    # -------------------------------
    df['salary_gap_pct'] = ((df['market_salary'] - df['current_salary']) / df['market_salary']) * 100
    st.success("✅ Salary gap calculated for each employee")

    # -------------------------------
    # Employee Selection & Details
    # -------------------------------
    st.subheader("Employee Details")
    employee_name = st.selectbox("Select Employee", df['name'])
    emp_data = df[df['name'] == employee_name].iloc[0]

    st.write(f"**Department:** {emp_data['department']}")
    st.write(f"**Current Salary:** ${emp_data['current_salary']}")
    st.write(f"**Market Salary:** ${emp_data['market_salary']}")
    st.write(f"**Salary Gap:** {emp_data['salary_gap_pct']:.2f}%")
    st.write(f"**Recognition Count:** {emp_data['recognition_count']}")
    st.write(f"**Tenure:** {emp_data['tenure']} years")
    st.write(f"**Engagement Score:** {emp_data['engagement_score']}")
    st.write(f"**Attendance Rate:** {emp_data['attendance_rate']}%")
    st.write(f"**Survey Response:** {emp_data['survey_response']}")

    # -------------------------------
    # AI-Predicted Retention Risk
    # -------------------------------
    st.subheader("AI-Predicted Retention Risk")
    openai_api_key = "your_api_key_here"  # replace with your key
    client = OpenAI(api_key=openai_api_key)

    risk_prompt = f"""
    You are an HR analytics assistant. 
    Based on the following employee data, classify retention risk as Low, Medium, or High.
    Also provide a short explanation.

    Employee Data:
    Name: {emp_data['name']}
    Department: {emp_data['department']}
    Current Salary: {emp_data['current_salary']}
    Market Salary: {emp_data['market_salary']}
    Salary Gap (%): {emp_data['salary_gap_pct']:.2f}
    Recognition Count: {emp_data['recognition_count']}
    Tenure: {emp_data['tenure']}
    Engagement Score: {emp_data['engagement_score']}
    Attendance Rate: {emp_data['attendance_rate']}
    Survey Response: {emp_data['survey_response']}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": risk_prompt}],
            temperature=0.5
        )
        retention_risk = response.choices[0].message.content.strip()
        st.write(retention_risk)
    except Exception as e:
        st.error(f"Error generating AI retention risk: {e}")

    # -------------------------------
    # AI Recommendations
    # -------------------------------
    st.subheader("AI Retention Recommendations")
    recommendation_prompt = f"""
    Based on the following employee data, suggest 3 actionable recommendations to reduce retention risk.

    Employee Data:
    Name: {emp_data['name']}
    Department: {emp_data['department']}
    Current Salary: {emp_data['current_salary']}
    Market Salary: {emp_data['market_salary']}
    Salary Gap (%): {emp_data['salary_gap_pct']:.2f}
    Recognition Count: {emp_data['recognition_count']}
    Tenure: {emp_data['tenure']}
    Engagement Score: {emp_data['engagement_score']}
    Attendance Rate: {emp_data['attendance_rate']}
    Survey Response: {emp_data['survey_response']}
    """

    try:
        response_rec = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": recommendation_prompt}],
            temperature=0.5
        )
        recommendations = response_rec.choices[0].message.content.strip()
        st.write(recommendations)
    except Exception as e:
        st.error(f"Error generating AI recommendations: {e}")
