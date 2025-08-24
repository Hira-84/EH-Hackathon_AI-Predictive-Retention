import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
import time

# ------------------------------
# OpenAI API setup
# ------------------------------
openai_api_key = "YOUR_OPENAI_KEY_HERE"  # replace with your key
client = OpenAI(api_key=openai_api_key)

# ------------------------------
# Caching AI Calls
# ------------------------------
@st.cache_data(show_spinner=False)
def get_ai_risk_cached(emp_data):
    return get_ai_risk(emp_data)

@st.cache_data(show_spinner=False)
def get_ai_recommendations_cached(emp_data):
    return get_ai_recommendations(emp_data)

# ------------------------------
# OpenAI Risk Prediction
# ------------------------------
def get_ai_risk(emp_data):
    prompt = f"""
    You are an HR analytics assistant. 
    Based on the following employee data, classify retention risk as Low, Medium, or High.
    Also provide a short reason (1-2 sentences).

    Employee Data:
    Name: {emp_data['name']}
    Department: {emp_data['department']}
    Current Salary: {emp_data['current_salary']}
    Market Salary: {emp_data['market_salary']}
    Salary Gap (%): {emp_data['Salary Gap (%)']:.2f}
    Recognition Count: {emp_data['recognition_count']}
    Tenure: {emp_data['tenure']}
    Engagement Score: {emp_data['engagement_score']}
    Attendance Rate: {emp_data['attendance_rate']}
    Survey Response: {emp_data['survey_response']}
    """
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            result = response.choices[0].message.content.strip()
            # Parse risk level
            risk_level = None
            reason = None
            lines = result.split("\n")
            for line in lines:
                line_lower = line.lower()
                if "low" in line_lower:
                    risk_level = "Low"
                    reason = line
                    break
                elif "medium" in line_lower:
                    risk_level = "Medium"
                    reason = line
                    break
                elif "high" in line_lower:
                    risk_level = "High"
                    reason = line
                    break
            if not risk_level:
                risk_level = "Medium"
                reason = result
            return risk_level, reason
        except Exception as e:
            st.warning(f"Retry {attempt+1}/3 for {emp_data['name']} due to error: {e}")
            time.sleep(1)
    return "Medium", "Could not determine risk automatically"

# ------------------------------
# OpenAI Recommendations
# ------------------------------
def get_ai_recommendations(emp_data):
    prompt = f"""
    You are an HR assistant. Suggest 3 actionable recommendations to reduce retention risk based on employee data.
    Employee Data:
    Name: {emp_data['name']}
    Department: {emp_data['department']}
    Current Salary: {emp_data['current_salary']}
    Market Salary: {emp_data['market_salary']}
    Salary Gap (%): {emp_data['Salary Gap (%)']:.2f}
    Recognition Count: {emp_data['recognition_count']}
    Tenure: {emp_data['tenure']}
    Engagement Score: {emp_data['engagement_score']}
    Attendance Rate: {emp_data['attendance_rate']}
    Survey Response: {emp_data['survey_response']}
    """
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            result = response.choices[0].message.content.strip()
            recs = [line.strip("-• ") for line in result.split("\n") if line.strip()]
            return recs[:3]
        except Exception as e:
            st.warning(f"Retry {attempt+1}/3 for recommendations for {emp_data['name']}: {e}")
            time.sleep(1)
    return ["Recommendation unavailable"]*3

# ------------------------------
# Fancy Employee Drill-Down (unchanged)
# ------------------------------
def show_employee_details(selected_employee, risk, reason, recommendations):
    st.markdown("### 👤 Employee Drill-Down")
    risk_colors = {"High": "red", "Medium": "orange", "Low": "green"}
    st.markdown(
        f"<div style='background-color:{risk_colors.get(risk,'gray')};"
        f"color:white;padding:8px;border-radius:10px;width:120px;text-align:center;'>"
        f"{risk} Risk</div>", unsafe_allow_html=True
    )
    st.write("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("📉 Salary Gap", f"{selected_employee['Salary Gap (%)']:.1f}%")
    col2.metric("🎯 Engagement", f"{selected_employee['engagement_score']}/100")
    col3.metric("📊 Attendance", f"{selected_employee['attendance_rate']}%")
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("💼 Job Info")
        st.write(f"**Department:** {selected_employee['department']}")
        st.write(f"**Tenure:** {selected_employee['tenure']} years")
        st.subheader("💰 Compensation")
        st.write(f"**Current Salary:** ${selected_employee['current_salary']}")
        st.write(f"**Market Salary:** ${selected_employee['market_salary']}")
    with col2:
        st.subheader("🌟 Engagement")
        st.progress(int(selected_employee['engagement_score']))
        st.caption(f"Engagement Score: {selected_employee['engagement_score']}/100")
        st.progress(int(selected_employee['attendance_rate']))
        st.caption(f"Attendance Rate: {selected_employee['attendance_rate']}%")
        st.write(f"**Recognition Count:** {selected_employee['recognition_count']}")
    st.write("---")
    st.subheader("💬 Employee Feedback")
    st.markdown(f"<div style='padding:10px;border-left:5px solid #999;background-color:#f9f9f9;"
                f"border-radius:5px;font-style:italic;'>“{selected_employee['survey_response']}”</div>", unsafe_allow_html=True)
    st.subheader("📝 AI Retention Risk Analysis")
    st.info(reason)
    st.subheader("💡 AI Retention Recommendations")
    for rec in recommendations:
        st.markdown(f"- {rec}")

# ------------------------------
# Main App
# ------------------------------
def main():
    st.set_page_config(page_title="AI Employee Retention Dashboard", layout="wide")
    st.title("📊 AI-Powered Employee Retention Predictor")

    uploaded_file = st.file_uploader("Upload HR/Employee CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Uploaded CSV loaded successfully!")
    else:
        try:
            df = pd.read_csv("HR_Data.csv")
            st.info("Using default CSV (demo data)")
        except FileNotFoundError:
            st.error("❌ Default file 'HR_Data.csv' not found. Please upload a CSV.")
            return

    df['Salary Gap (%)'] = ((df['market_salary'] - df['current_salary']) / df['market_salary']) * 100

    st.info("Generating AI risk & recommendations (cached, so reloads are fast)...")
    risk_data = []
    for idx, row in df.iterrows():
        risk, reason = get_ai_risk_cached(row)
        recs = get_ai_recommendations_cached(row)
        risk_data.append({
            "name": row['name'],
            "risk_level": risk,
            "reason": reason,
            "top_recommendation": recs[0]
        })
    risk_summary = pd.DataFrame(risk_data)

    page = st.sidebar.radio("Select Page", ["Overall Insights", "Individual Employee Analysis"])
    if page == "Overall Insights":
        st.markdown("## 🌍 Overall Insights")
        st.dataframe(risk_summary)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Risk Distribution")
            risk_counts = risk_summary['risk_level'].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', startangle=90)
            ax1.axis('equal')
            st.pyplot(fig1)
        with col2:
            st.subheader("Department Risk Breakdown")
            merged = df.merge(risk_summary, on="name")
            dept_risk = merged.groupby(['department','risk_level']).size().unstack(fill_value=0)
            fig2, ax2 = plt.subplots()
            dept_risk.plot(kind="bar", stacked=True, ax=ax2)
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig2)
    else:
        st.markdown("## Individual Employee Analysis")
        st.sidebar.header("🔍 Select Employee")
        selected_employee_name = st.sidebar.selectbox("Choose an employee", df['name'].tolist())
        if selected_employee_name:
            employee_data = df[df['name']==selected_employee_name].iloc[0]
            risk_row = risk_summary[risk_summary['name']==selected_employee_name].iloc[0]
            recs = get_ai_recommendations_cached(employee_data)
            show_employee_details(employee_data, risk_row['risk_level'], risk_row['reason'], recs)

if __name__ == "__main__":
    main()
