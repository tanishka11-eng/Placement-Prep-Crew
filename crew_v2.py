import json
from agents import ToolAgent
from crew import run_crew
from tools import FUNCS, PLANNER_TOOLS, WRITER_TOOLS, read_pdf


planner = ToolAgent(
    "Planner",
    "You are a study planner for a college student. First call get_today. "
    "Then plan 6 to 8 study sessions over the next 2 weeks, starting "
    "tomorrow, that cover the missing skills. Call save_study_plan with "
    "them. Finally reply with the plan as a short markdown table.",
    PLANNER_TOOLS, FUNCS, gated=["save_study_plan"],
)

writer = ToolAgent(
    "Writer",
    "You write cover letters for students, under 180 words. Use only facts "
    "from the resume and never invent experience. Call save_cover_letter "
    "with the company name and the letter, then reply with the letter.",
    WRITER_TOOLS, FUNCS, gated=["save_cover_letter"],
)
hr_coach = ToolAgent(
"HR Interview Coach",
"You are an expert HR interview coach for college students. "
"Analyse the student's resume and job description. "
"Generate 10 relevant HR interview questions with short, "
"simple and practical sample answers. Include self-introduction, "
"strengths, weaknesses, career goals and why the student "
"wants this role. Never invent personal experience.",
[],
FUNCS,
gated=[],
)
project_recommender = ToolAgent(
    "Project Recommender",
    "You are a project mentor for college students. Based on the student's "
    "resume, skills, missing skills and target job description, suggest 3 "
    "realistic projects. For each project, provide its title, problem it "
    "solves, key features, suggested tech stack, and a short step-by-step "
    "roadmap. Keep ideas appropriate to the student's current level. "
    "Do not claim the student has already built these projects.",
    [],
    FUNCS,
    gated=[],
)
def run_full_crew(resume, jd):
    report, advice, questions = run_crew(resume, jd)

    missing = ", ".join(report.get("missing_skills", []))

    # Agent 4: Study Planner
    plan, plan_actions = planner.run(
        f"MISSING SKILLS: {missing}"
    )

    # Agent 5: Cover Letter Writer
    letter, letter_actions = writer.run(
        f"REPORT:\n{json.dumps(report)}\n\nRESUME:\n{resume}\n\nJOB:\n{jd}"
    )
   # Agent 6: HR Interview Coach
    hr_advice, _ = hr_coach.run(
    f"RESUME:\n{resume}\n\nJOB DESCRIPTION:\n{jd}\n\n"
    f"MATCH REPORT:\n{json.dumps(report)}"
)

# Agent 7: Project Recommender
    project_ideas, _ = project_recommender.run(
    f"RESUME:\n{resume}\n\n"
    f"MISSING SKILLS: {missing}\n\n"
    f"JOB DESCRIPTION:\n{jd}"
)
    return {
        "report": report,
        "advice": advice,
        "questions": questions,
        "plan": plan,
        "letter": letter,
        "hr_advice": hr_advice,
        "project_ideas": project_ideas,
        "pending": plan_actions + letter_actions,
        "done": []
    }
if __name__ == "__main__":
    resume = read_pdf("sample_resume.pdf")
    jd = open("sample_jd.txt", encoding="utf-8").read()

    out = run_full_crew(resume, jd)

    print("MATCH SCORE:", out["report"].get("match_score"))
    print("\n--- PLANNER ---\n" + out["plan"])
    print("\n--- WRITER ---\n" + out["letter"])

    for action in out["pending"]:
        answer = input(f"\nRun {action['tool']}? (y/n) ")

        if answer.strip().lower() == "y":
            print(FUNCS[action["tool"]](**action["args"]))
        else:
            print("Skipped. Nothing was saved.")