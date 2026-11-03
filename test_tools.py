from tools import read_pdf, get_today, save_study_plan, save_cover_letter

print(read_pdf("sample_resume.pdf")[:80])

print(get_today())

print(save_study_plan([
    {"date": "2026-11-10", "topic": "FastAPI basics", "hours": 2}
]))

print(save_study_plan([
    {"date": "next monday", "topic": "Docker", "hours": 1}
]))

print(save_cover_letter(
    "Pragati Labs",
    "Dear Hiring Team, ..."
))