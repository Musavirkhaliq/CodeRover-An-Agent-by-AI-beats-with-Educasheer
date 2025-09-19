# agent.py
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

from prompts.prompts import SYSTEM_PROMPT
from tools.custom_tool import AVAILABLE_TOOLS

# Load API key from .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

class Agent:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.messages = [{"role": "user", "parts": [SYSTEM_PROMPT]}]
        # The model expects a specific format, we start with the system prompt
        # and then alternate between 'model' and 'user' roles.
        # The 'user' role will contain our requests and tool outputs.
        # The 'model' role will contain the LLM's thoughts and tool calls.

    def run(self, user_request: str):
        print(f"USER REQUEST: {user_request}\n")
        self.messages.append({"role": "user", "parts": [user_request]})

        while True:
            # 1. Call the LLM
            response = self.model.generate_content(self.messages)
            response_text = response.parts[0].text
            self.messages.append({"role": "model", "parts": [response_text]})
            print(f"AGENT: {response_text}\n")

            # 2. Check for a tool call
            tool_call = self._parse_tool_call(response_text)
            print(f"TOOL CALL: {tool_call}\n")
            if tool_call:
                tool_name = tool_call.get("tool_name")
                parameters = tool_call.get("parameters", {})

                if tool_name in AVAILABLE_TOOLS:
                    # 3. Execute the tool
                    tool_function = AVAILABLE_TOOLS[tool_name]
                    tool_output = tool_function(**parameters)
                    
                    # 4. Add tool output to messages for the next loop
                    tool_result_message = f"<tool_result>\n{tool_output}\n</tool_result>"
                    self.messages.append({"role": "user", "parts": [tool_result_message]})
                    print(f"TOOL RESULT:\n{tool_output}\n")
                else:
                    self.messages.append({"role": "user", "parts": [f"Tool '{tool_name}' not found."]})
            else:
                # 5. No tool call, so it's the final answer
                print("--- Task Complete ---")
                break

    def _parse_tool_call(self, text: str):
        """Parses a tool call from the LLM's response."""
        if "<tool_code>" in text and "</tool_code>" in text:
            try:
                # Extract the JSON string between the tags
                json_str = text.split("<tool_code>")[1].split("</tool_code>")[0]
                return json.loads(json_str)
            except (json.JSONDecodeError, IndexError) as e:
                print(f"Error parsing tool code: {e}")
                return None
        return None
