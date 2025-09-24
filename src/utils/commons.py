from dataclasses import dataclass



@dataclass
class ToolCallParameters:
    tool_call_id:str
    tool_name:str
    tool_input:str


@dataclass
class ToolOutput:
    """Output from LLM tool implementation
    Attributes:
    """