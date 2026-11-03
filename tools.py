import datetime
import os
import re
from pypdf import PdfReader

OUT = "outputs"


def read_pdf(file):
    reader = PdfReader(file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# READ tool
def get_today():
    return {"today": datetime.date.today().isoformat()}


# COMMIT tools
def ics_text(s):
    return s.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;")
def save_study_plan(sessions):
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//PrepCrew//EN"]

    for i, s in enumerate(sessions):
        try:
            day = datetime.date.fromisoformat(s["date"]).strftime("%Y%m%d")
        except (KeyError, ValueError):
            return {"error": f"session {i + 1} needs a date like 2026-11-10"}

        topic = str(s.get("topic", "revision"))[:45]
        title = ics_text(f"Study: {topic} ({s.get('hours', 1)}h)")

        lines += [
            "BEGIN:VEVENT",
            f"UID:prepcrew-{day}-{i}",
            f"DTSTAMP:{stamp}",
            f"DTSTART;VALUE=DATE:{day}",
            f"SUMMARY:{title}",
            "END:VEVENT"
        ]

    lines.append("END:VCALENDAR")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "study_plan.ics")

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")

    return {"saved": path, "sessions": len(sessions)}
def save_cover_letter(company, text):
    name = re.sub(r"[^a-z0-9]+", "_", company.lower()).strip("_") or "company"

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"cover_letter_{name}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

    return {"saved": path}


FUNCS = {
    "get_today": get_today,
    "save_study_plan": save_study_plan,
    "save_cover_letter": save_cover_letter
}
# Tool schemas

def tool(name, description, properties, required=()):
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": list(required)
            }
        }
    }


SESSION = {
    "type": "object",
    "properties": {
        "date": {
            "type": "string",
            "description": "YYYY-MM-DD"
        },
        "topic": {
            "type": "string"
        },
        "hours": {
            "type": "integer",
            "minimum": 1,
            "maximum": 3
        },
    },
    "required": ["date", "topic", "hours"],
}


PLANNER_TOOLS = [
    tool(
        "get_today",
        "Today's date. Call it before choosing dates.",
        {}
    ),
    tool(
        "save_study_plan",
        "Save the study sessions as a calendar file.",
        {"sessions": {"type": "array", "items": SESSION}},
        ["sessions"]
    ),
]


WRITER_TOOLS = [
    tool(
        "save_cover_letter",
        "Save the finished cover letter as a file.",
        {
            "company": {"type": "string"},
            "text": {"type": "string"}
        },
        ["company", "text"]
    ),
]