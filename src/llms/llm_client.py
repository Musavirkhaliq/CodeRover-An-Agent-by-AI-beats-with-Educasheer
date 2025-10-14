from dataclasses import dataclass
from typing import List,Any, Tuple
from dataclasses_json import DataClassJsonMixin
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types



@dataclass
class ToolParameters(DataClassJsonMixin):
    name: str
    description: str
    input_schema: dict[str,Any]

@dataclass
class ToolCall(DataClassJsonMixin):
    tool_call_id: str
    name: str
    tool_input: Any

@dataclass
class ToolCallResult(DataClassJsonMixin):
    tool_call_id: str
    tool_name: str
    output: Any

@dataclass
class ToolFormattedResult(DataClassJsonMixin):
    tool_call_id: str
    tool_name: str
    output: Any

@dataclass
class TextPrompt(DataClassJsonMixin):
    text: str

@dataclass
class TextResponse(DataClassJsonMixin):
    text: str


AssistantContentBlock = (TextResponse | ToolCall)
UserContentBlock = TextPrompt | ToolFormattedResult
GeneralContentBlock = AssistantContentBlock | UserContentBlock
Conversation = List[List[GeneralContentBlock]]


class LLMClient:
    def generate(
            self,
            messages: Conversation,
            max_tokens: int,
            system_prompt: str | None = None,
            temperature: float = 0.0,
            tools: List[ToolParameters] =[],
            tool_choice : dict[str,str] | None = None,
            thinking_tokens: int | None = None
    )-> Tuple[AssistantContentBlock,dict[str,Any]]:
        

        raise NotImplementedError()
    

class GoogleGemini(LLMClient):
    def __init__(self,model_name:str = 'gemini-2.5-flash',max_retries:int =3):
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        self.model_name = model_name
        self.max_retries = max_retries

    def generate(
                self,
                messages:Conversation,
                max_tokens: int,
                system_prompt: str | None = None,
                temperature: float = 0.0,
                tools: List[ToolParameters] =[],
                tool_choice : dict[str,str] | None = None,
                thinking_tokens: int | None = None
        )-> Tuple[AssistantContentBlock,dict[str,Any]]:

        # gemini_messages = []
        # for idx,message_list in enumerate(messages):
        #     role = 'user' if idx % 2 == 0 else 'assistant'
        #     message_content_list = []
        #     for message in message_list:
                

        client = genai.Client()
        response = client.models.generate_content(
            model=self.model_name,
            config=types.GenerateContentConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                system_instruction=system_prompt
                ),
            contents=messages
        )
        print(response.candidates[0].content.parts[0].text
)
g = GoogleGemini()
g.generate("What is 2+2?",max_tokens=1000)

