import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
# Risk Scoring Function
# ------------------------------
def assign_risk_reason(row):
    salary_gap = (row['market_salary'] - row['current_salary']) / row['market_salary']
    engagement = row['engagement_score']
    recognition = row['recognition_count']

    if salary_gap > 0.12 or engagement < 60 or recognition < 2:
        return "High", "Significant salary gap, low engagement or recognition"
    elif (0.05 < salary_gap <= 0.12) or (60 <= engagement < 75) or (2 <= recognition <= 3):
        return "Medium", "Some salary gap or moderate engagement/recognition"
    else:
        return "Low", "Good salary alignment and strong engagement"

# ------------------------------
# Mock AI Recommendations
# ------------------------------
def generate_recommendations(risk):
    if risk == "High":
        return [
            "Define a clear career progression roadmap.",
            "Offer targeted skill development workshops.",
            "Monitor workload and redistribute tasks."
        ]
    elif risk == "Medium":
        return [
            "Schedule regular mentorship sessions.",
            "Implement monthly recognition for small wins.",
            "Adjust workload to prevent burnout."
        ]
    else:  # Low
        return [
            "Continue regular recognition for contributions.",
            "Offer small stretch projects for growth.",
            "Maintain strong team engagement practices."
        ]

# ------------------------------
# Fancy Employee Drill-Down
# ------------------------------
def show_employee_details(selected_employee, risk, reason, recommendations):
    st.markdown("### 👤 Employee Drill-Down")  # smaller heading

    # Risk badge
    risk_colors = {"High": "red", "Medium": "orange", "Low": "green"}
    st.markdown(
        f"<div style='background-color:{risk_colors.get(risk, 'gray')};"
        f"color:white;padding:8px;border-radius:10px;width:120px;text-align:center;'>"
        f"{risk} Risk</div>",
        unsafe_allow_html=True
    )

    st.write("---")
    # Key metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("📉 Salary Gap", f"{selected_employee['Salary Gap (%)']:.1f}%")
    col2.metric("🎯 Engagement", f"{selected_employee['engagement_score']}/100")
    col3.metric("📊 Attendance", f"{selected_employee['attendance_rate']}%")

    st.write("---")
    # Grouped Info
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
    # Survey Response
    st.subheader("💬 Employee Feedback")
    st.markdown(
        f"<div style='padding:10px;border-left:5px solid #999;background-color:#f9f9f9;"
        f"border-radius:5px;font-style:italic;'>“{selected_employee['survey_response']}”</div>",
        unsafe_allow_html=True
    )

    # AI Reason
    st.subheader("📝 AI Retention Risk Analysis")
    st.info(reason)

    # AI Recommendations
    st.subheader("💡 AI Retention Recommendations")
    for rec in recommendations:
        st.markdown(f"- {rec}")

# ------------------------------
# Streamlit App
# ------------------------------
def main():
    st.set_page_config(page_title="Employee Retention Dashboard", layout="wide")
    st.title("📊 AI-Powered Employee Retention Predictor")

    # Upload CSV or use default
    uploaded_file = st.file_uploader("Upload HR/Employee CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.success("✅ Uploaded CSV loaded successfully!")
    else:
        try:
            df = pd.read_csv("HR_Data.csv")
            st.info("Using default CSV (demo data)")
        except FileNotFoundError:
            st.error("❌ Default file 'HR_Data.csv' not found. Please upload a CSV to continue.")
            return

    df['Salary Gap (%)'] = ((df['market_salary'] - df['current_salary']) / df['market_salary']) * 100

    # Assign risk + reason + top recommendation
    risk_data = []
    for _, row in df.iterrows():
        risk, reason = assign_risk_reason(row)
        recs = generate_recommendations(risk)
        risk_data.append({
            "name": row['name'],
            "risk_level": risk,
            "reason": reason,
            "top_recommendation": recs[0]  # for summary table
        })
    risk_summary = pd.DataFrame(risk_data)

    # ------------------------------
    # Page selection
    # ------------------------------
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
            dept_risk = merged.groupby(['department', 'risk_level']).size().unstack(fill_value=0)
            fig2, ax2 = plt.subplots()
            dept_risk.plot(kind="bar", stacked=True, ax=ax2)
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig2)

    else:
        st.markdown("## Individual Employee Analysis")
        st.sidebar.header("🔍 Select Employee")
        selected_employee_name = st.sidebar.selectbox("Choose an employee", df['name'].tolist())

        if selected_employee_name:
            employee_data = df[df['name'] == selected_employee_name].iloc[0]
            risk_row = risk_summary[risk_summary['name'] == selected_employee_name].iloc[0]
            recs = generate_recommendations(risk_row['risk_level'])
            show_employee_details(employee_data, risk_row['risk_level'], risk_row['reason'], recs)

if __name__ == "__main__":
    main()
