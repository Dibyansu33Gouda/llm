import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

from weather_tool import get_weather_decl, TOOLS

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

declaration = types.FunctionDeclaration(**get_weather_decl)
config = types.GenerateContentConfig(
    tools=[types.Tool(function_declarations=[declaration])]
)


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


question = "Should I carry an umbrella in Berhampur today?"
user_msg = types.Content(role="user", parts=[types.Part(text=question)])

# Call 1: the model decides whether it needs a tool
response = ask([user_msg])

calls = response.function_calls
if not calls:
    print("answer:", response.text)  # model answered without any tool
    raise SystemExit

if not response.candidates:
    raise SystemExit("No candidates returned")

call = calls[0]
model_msg = response.candidates[0].content

# Your Python code does the real work
result = TOOLS[call.name](**(call.args or {}))
print("tool result:", result)

# Call 2: replay the story so far, plus the tool result
tool_msg = types.Content(
    role="user",
    parts=[types.Part.from_function_response(
        name=call.name,
        response={"result": result},
    )],
)
final = ask([user_msg, model_msg, tool_msg])
print("answer:", final.text)