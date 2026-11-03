from agents import Agent

mentor = Agent(
    "Mentor",
    "You are a placement mentor for engineering students. "
    "Answer in at most 3 short bullet points.",
)

print(mentor.speak("What should a 3rd-year CSE student learn first "
                   "for an AI engineering internship?"))