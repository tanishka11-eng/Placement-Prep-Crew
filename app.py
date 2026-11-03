import streamlit as st
from crew import run_crew

st.set_page_config(page_title="Placement Prep Crew", page_icon=":briefcase:")
st.title("Placement Prep Crew")

col1, col2 = st.columns(2)
resume = col1.text_area("Your resume (text)", height=300)
jd = col2.text_area("Job description", height=300)

if st.button("Run the crew") and resume and jd:
    with st.spinner("The crew is reading..."):
        report, advice, questions = run_crew(resume, jd)

    st.metric("Match score", f"{report.get('match_score', 0)}/100")
    st.write("**Missing skills:**", ", ".join(report.get("missing_skills", [])))
    st.caption(report.get("summary", ""))

    st.subheader("Coach: how to improve")
    st.markdown(advice)
    st.subheader("Interviewer: practise these")
    st.markdown(questions)