import json
import re
from agents import Agent


def parse_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


screener = Agent(
    "Screener",
    "You are a technical recruiter. Compare the resume with the job description. "
    "Return ONLY valid JSON with these keys: match_score (0-100), "
    "matched_skills (list), missing_skills (list), summary (string). "
    "No other text."
)
coach = Agent(
    "Coach",
    "You are a career coach for college students. Using the screening "
    "report and the resume, rewrite 3 resume bullet points to fit the job, "
    "then list 3 things to learn or build next. Never invent experience "
    "the student does not have.",
)

interviewer = Agent(
    "Interviewer",
    "You are a hiring manager. Using the job description and the "
    "candidate's missing skills, write 5 numbered interview questions, "
    "from easy to hard.",
)
def run_crew(resume, jd):
    # Agent 1: Screener
    report = parse_json(screener.speak(f"JOB:\n{jd}\n\nRESUME:\n{resume}"))
    missing = ", ".join(report.get("missing_skills", []))

    # Agent 2: Coach
    coach_msg = f"REPORT:\n{json.dumps(report, indent=2)}\n\nRESUME:\n{resume}"
    advice = coach.speak(coach_msg)

    # Agent 3: Interviewer
    interviewer_msg = f"JOB:\n{jd}\n\nMISSING SKILLS: {missing}"
    questions = interviewer.speak(interviewer_msg)

    return report, advice, questions
if __name__ == "__main__":
    resume = open("sample_resume.txt", encoding="utf-8").read()
    jd = open("sample_jd.txt", encoding="utf-8").read()
    report, advice, questions = run_crew(resume, jd)
    print("MATCH SCORE:", report.get("match_score"))
    print("MISSING:", report.get("missing_skills"))
    print("\n--- COACH ---\n" + advice)
    print("\n--- INTERVIEWER ---\n" + questions)