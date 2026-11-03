import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "openai/gpt-oss-20b"


class Agent:
    def __init__(self, name, role):
        self.name = name
        self.role = role

    def speak(self, message):
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": message},
            ],
            temperature=0.3,
            reasoning_effort="low",
            max_completion_tokens=1500,
        )
        return response.choices[0].message.content.strip()

def as_dict(msg):
    calls = [
        {
            "id": c.id,
            "type": "function",
            "function": {
                "name": c.function.name,
                "arguments": c.function.arguments
            }
        }
        for c in msg.tool_calls
    ]

    return {
        "role": "assistant",
        "content": msg.content or "",
        "tool_calls": calls
    }


class ToolAgent(Agent):
    def __init__(self, name, role, tools, funcs, gated=()):
        super().__init__(name, role)
        self.tools = tools
        self.funcs = funcs
        self.gated = set(gated)  
    def run(self, message, max_steps=5):
        messages = [
            {"role": "system", "content": self.role},
            {"role": "user", "content": message}
        ]

        pending = []

        for _ in range(max_steps):
            msg = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=self.tools,
                reasoning_effort="low",
                max_completion_tokens=3000,
            ).choices[0].message

            if not msg.tool_calls:
                return msg.content, pending

            messages.append(as_dict(msg))

            for call in msg.tool_calls:
                result = self.handle(call, pending)
                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": json.dumps(result)
                })

        return "Stopped: too many steps.", pending
    
    def handle(self, call, pending):
        name = call.function.name

        try:
            args = json.loads(call.function.arguments or "{}")
        except json.JSONDecodeError:
            return {"error": "arguments were not valid JSON"}

        if name not in self.funcs:
            return {"error": f"unknown tool {name}"}

        if name in self.gated:
            pending.append({
                "tool": name,
                "args": args
            })
            return {"status": "proposed. The student must confirm it."}

        return self.funcs[name](**args)