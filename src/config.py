import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration for CodeRover multi-model agent."""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # If you want to use Groq models
    
    # Model Selection
    ORCHESTRATOR_MODEL = os.getenv("ORCHESTRATOR_MODEL", "gemini-2.0-flash")
    CODEWRITER_MODEL = os.getenv("CODEWRITER_MODEL", "openai/gpt-oss-120b")  # Changed to standard OpenAI model
    
    # API Base URLs
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    # OPENAI_BASE_URL = "https://api.openai.com/v1"
    GROQ_BASE_URL = "https://api.groq.com/openai/v1"
    
    # LLM Settings
    LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))
    LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
    
    # Code Writer Settings
    CODE_WRITER_TEMPS = [0.2, 0.7, 1.0]
    CODE_WRITER_MAX_TOKENS = int(os.getenv("CODE_WRITER_MAX_TOKENS", "2000"))
    
    @classmethod
    def validate_config(cls):
        """Validate that required API keys are present."""
        errors = []
        
        # Check which models are being used
        if "gemini" in cls.ORCHESTRATOR_MODEL.lower():
            if not cls.GEMINI_API_KEY:
                errors.append("GEMINI_API_KEY required for Gemini orchestrator model")
        
        # if "gemini" in cls.CODEWRITER_MODEL.lower():
        #     if not cls.GEMINI_API_KEY:
        #         errors.append("GEMINI_API_KEY required for Gemini code writer model")
        
        # if "gpt" in cls.CODEWRITER_MODEL.lower() or "openai" in cls.CODEWRITER_MODEL.lower():
        #     if not cls.OPENAI_API_KEY:
        #         errors.append("OPENAI_API_KEY required for OpenAI code writer model")
        
        if "groq" in cls.ORCHESTRATOR_MODEL.lower() or "groq" in cls.CODEWRITER_MODEL.lower():
            if not cls.GROQ_API_KEY:
                errors.append("GROQ_API_KEY required for Groq models")
        
        if errors:
            raise ValueError("\n  - ".join([""] + errors))
    
    @classmethod
    def get_model_config(cls, model_name: str) -> dict:
        """Get the appropriate API key and base URL for a model."""
        model_lower = model_name.lower()
        
        if "gemini" in model_lower:
            return {
                "api_key": cls.GEMINI_API_KEY,
                "base_url": cls.GEMINI_BASE_URL,
                "provider": "gemini"
            }
        # elif "gpt" in model_lower or "openai" in model_lower:
        #     return {
        #         "api_key": cls.OPENAI_API_KEY,
        #         "base_url": cls.OPENAI_BASE_URL,
        #         "provider": "openai"
        #     }
        elif "groq" in model_lower or any(x in model_lower for x in ["openai/gpt-oss-120b", "mixtral"]):
            return {
                "api_key": cls.GROQ_API_KEY,
                "base_url": cls.GROQ_BASE_URL,
                "provider": "groq"
            }
        else:
            raise ValueError(f"Unknown model provider for: {model_name}")
    
    @classmethod
    def get_gemini_key(cls):
        """Get Gemini API key (legacy method)."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set")
        return cls.GEMINI_API_KEY

    @classmethod
    def get_openai_key(cls):
        """Get OpenAI API key (legacy method)."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set")
        return cls.OPENAI_API_KEY