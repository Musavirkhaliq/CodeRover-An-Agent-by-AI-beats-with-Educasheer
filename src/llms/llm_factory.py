"""Factory for creating LLM instances."""

from typing import Optional, Dict, Any
from src.config import Config
from .generic_adapter import GenericAdapter


class LLMFactory:
    """Factory class for creating LLM instances."""
    
    @staticmethod
    def create_llm(
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = None
    ) -> GenericAdapter:
        """
        Create a generic LLM instance.
        
        Args:
            model_name: Model identifier (defaults to ORCHESTRATOR_MODEL)
            api_key: API key (fetched from config if not provided)
            base_url: Base URL for API (fetched from config if not provided)
            provider: Provider name (fetched from config if not provided)
            
        Returns:
            GenericAdapter instance
        """
        # Use default model if not specified
        if model_name is None:
            model_name = Config.ORCHESTRATOR_MODEL
        
        # Get config for the model
        config = Config.get_model_config(model_name)
        
        # Use provided values or fall back to config
        api_key = api_key or config['api_key']
        base_url = base_url or config['base_url']
        provider = provider or config['provider']
        
        return GenericAdapter(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            provider=provider
        )
    
    @staticmethod
    def create_orchestrator() -> GenericAdapter:
        """
        Create an orchestrator LLM instance.
        
        Returns:
            GenericAdapter configured for orchestration
        """
        return LLMFactory.create_llm(model_name=Config.ORCHESTRATOR_MODEL)
    
    @staticmethod
    def create_code_writer() -> GenericAdapter:
        """
        Create a code writer LLM instance.
        
        Returns:
            GenericAdapter configured for code writing
        """
        return LLMFactory.create_llm(model_name=Config.CODEWRITER_MODEL)
    
    @staticmethod
    def list_available_models() -> Dict[str, Dict[str, Any]]:
        """
        List all available models and their configurations.
        
        Returns:
            Dictionary mapping model names to their configurations
        """
        models = {}
        
        # Get orchestrator model
        try:
            models[Config.ORCHESTRATOR_MODEL] = {
                'provider': Config.get_model_config(Config.ORCHESTRATOR_MODEL)['provider'],
                'role': 'orchestrator'
            }
        except Exception:
            pass
        
        # Get code writer model
        try:
            models[Config.CODEWRITER_MODEL] = {
                'provider': Config.get_model_config(Config.CODEWRITER_MODEL)['provider'],
                'role': 'code_writer'
            }
        except Exception:
            pass
        
        return models