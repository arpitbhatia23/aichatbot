import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load API key
load_dotenv()
gemini_key = os.getenv("api_key")
client = genai.Client(api_key=gemini_key)

# --- Tool implementation ---
def get_weatherData(city=""):
    if city.lower() == 'patiala': return '10C'
    if city.lower() == 'mohali': return '12C'
    if city.lower() == 'chandigarh': return '25C'
    if city.lower() == 'kangra': return '18C'
    return "Unknown city"

# --- Helper to safely load JSON ---
def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                return {"type": "error", "raw": text}
        return {"type": "error", "raw": text}

# --- System prompt for tool-use reasoning ---
system_prompt = """
You are an AI assistant with START, PLAN, ACTION, Observation, and OUTPUT states.
Always respond in JSON only.

Available tool:
- function get_weatherData(city: string): string

Rules:
1. First make a PLAN.
2. Then request ACTION if a tool is needed.
3. Wait for an Observation after ACTION.
4. Finally return OUTPUT.

Example flow:
{"type":"user","user":"what is the sum of weather of patiala and mohali?"}
{"type":"plan","plan":"I will call get_weatherData for patiala"}
{"type":"action","function":"get_weatherData","input":"patiala"}
{"type":"observation","observation":"10C"}
{"type":"plan","plan":"I will call get_weatherData for mohali"}
{"type":"action","function":"get_weatherData"c,"input":"mohali"}
{"type":"observation","observation":"12C"}
{"type":"output","output":"The sum of weather of patiala and mohali is 22C"}
"""

# --- Create chat session ---
chat_session = client.chats.create(
    model="gemini-2.0-flash",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json"
    ),
)

# --- Chat loop ---
def chat():
    print("Welcome to the AI chatbot")
    while True:
        user_input = input("You: ")
        if user_input.lower().strip() == "exit":
            print("Goodbye!")
            break

        # Send user query
        response = chat_session.send_message(user_input)
        msg = safe_json_loads(response.text)

        # Loop until OUTPUT is returned
        while msg.get("type") != "output":
            if msg.get("type") == "action" and msg.get("function") == "get_weatherData":
                # Call the tool
                city = msg.get("input", "")
                obs = get_weatherData(city)
                # Send observation back to model
                response = chat_session.send_message(json.dumps({
                    "type": "observation",
                    "observation": obs
                }))
                msg = safe_json_loads(response.text)
            else:
                # Ask model to continue reasoning
                response = chat_session.send_message(json.dumps({"type": "continue"}))
                msg = safe_json_loads(response.text)

        # Final output
        if msg.get("type") == "output":
            print("🤖:", msg.get("output"))

# --- Run bot ---
if __name__ == "__main__":
    chat()
