import os
import streamlit as st
from crew_v2 import run_full_crew
from tools import FUNCS, read_pdf

st.set_page_config(
    page_title="Placement Prep Crew v2",
    page_icon=":briefcase:"
)

st.title("Placement Prep Crew v2")

pdf = st.file_uploader("Your resume (PDF)", type="pdf")
jd = st.text_area("Job description", height=200)

if st.button("Run the crew") and pdf and jd:
    with st.spinner("Five agents at work..."):
        st.session_state.out = run_full_crew(read_pdf(pdf), jd)

out = st.session_state.get("out")

if out:
    st.metric(
        "Match score",
        f"{out['report'].get('match_score', 0)}/100"
    )

    sections = {
        "Coach": "advice",
        "Interviewer": "questions",
        "Study Planner": "plan",
        "Cover Letter Writer": "letter",
        "HR Interview Coach": "hr_advice",
        "Project Recommender": "project_ideas"
    }

    for title, key in sections.items():
        with st.expander(title):
            st.markdown(out[key])
    st.subheader("Waiting for your approval")

    for i, action in enumerate(out["pending"]):
        st.write(f"**{action['tool']}**")
        st.json(action["args"], expanded=False)

        if st.button("Confirm", key=f"ok{i}"):
            out["done"].append(
                FUNCS[action["tool"]](**action["args"])
            )
            out["pending"].pop(i)
            st.rerun()

    for result in out["done"]:
        if "saved" in result:
            name = os.path.basename(result["saved"])

            with open(result["saved"], "rb") as f:
                st.download_button(
                    f"Download {name}",
                    f.read(),
                    file_name=name
                )
        else:
            st.error(result.get("error", "Something went wrong."))