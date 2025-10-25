"""LLM interfaces and adapters."""

# Import base interfaces
from .llm_interfaces import LLMInterface

# Import adapters
from .generic_adapter import GenericAdapter

# Import specialized LLMs
from .orchestrator_llm import OrchestratorLLM
from .code_writer import CodeWriter

# Only import LLMFactory if the file exists
try:
    from .llm_factory import LLMFactory
except ImportError:
    # If llm_factory doesn't exist, create a simple inline factory
    from src.config import Config
    
    class LLMFactory:
        """Simple factory for creating LLM instances."""
        
        @staticmethod
        def create_llm(model_name=None):
            model_name = model_name or Config.ORCHESTRATOR_MODEL
            config = Config.get_model_config(model_name)
            return GenericAdapter(
                model_name=model_name,
                api_key=config['api_key'],
                base_url=config['base_url'],
                provider=config['provider']
            )
        
        @staticmethod
        def create_orchestrator():
            return LLMFactory.create_llm(Config.ORCHESTRATOR_MODEL)
        
        @staticmethod
        def create_code_writer():
            return LLMFactory.create_llm(Config.CODEWRITER_MODEL)
        
        @staticmethod
        def list_available_models():
            return {
                Config.ORCHESTRATOR_MODEL: {'role': 'orchestrator'},
                Config.CODEWRITER_MODEL: {'role': 'code_writer'}
            }

__all__ = [
    'LLMInterface',
    'GenericAdapter',
    'OrchestratorLLM',
    'CodeWriter',
    'LLMFactory'
]