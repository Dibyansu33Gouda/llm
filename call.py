import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from weather_tool import DECLS, TOOLS

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

declarations = [types.FunctionDeclaration(**d) for d in DECLS]
config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=declarations)]
)

MAX_STEPS = 6


def ask(contents):
    for attempt in range(4):
        try:
            return client.models.generate_content(
                model="gemini-3.8-flash",
                contents=contents,
                config=config,
            )
        except errors.ServerError:
            wait = 2 ** attempt
            print(f"server busy, retrying in {wait}s")
            time.sleep(wait)
    raise SystemExit("Gave up after 4 tries")


def run_tool(call):
    func = TOOLS.get(call.name)
    if func is None:
        return f"Unknown tool: {call.name}"
    try:
        return func(**(call.args or {}))
    except Exception as e:
        return f"Tool error: {e}"


def run_agent(question):
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    for step in range(MAX_STEPS):
        response = ask(contents)
        if not response.candidates:
            return "No response from model"

        calls = response.function_calls
        if not calls:
            return response.text  # model has what it needs, done

        contents.append(response.candidates[0].content)

        result_parts = []
        for call in calls:
            print(f"step {step + 1}: {call.name}({call.args})")
            result = run_tool(call)
            print(f"   -> {result}")
            result_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result},
                )
            )
        contents.append(types.Content(role="user", parts=result_parts))

    return "Stopped: too many steps"


question = "Which is warmer right now, Berhampur or Hyderabad? Give me the warmer one's temperature in Fahrenheit."
print("answer:", run_agent(question))