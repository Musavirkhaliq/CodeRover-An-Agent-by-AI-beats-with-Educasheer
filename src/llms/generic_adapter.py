"""Adapter for GenericLLM to maintain interface compatibility."""

from typing import Optional
from .generic_llm import GenericLLM


class GenericAdapter:
    """Adapter that wraps GenericLLM to provide a consistent interface."""
    
    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        provider: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize the adapter.
        
        Args:
            model_name: Name of the model
            api_key: API key for authentication (optional if in config)
            base_url: Base URL for the API (optional if in config)
            provider: Provider name ('gemini', 'openai', 'groq')
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        # Auto-detect provider if not specified
        if provider is None:
            provider = self._detect_provider(model_name, base_url)
        
        # Validate required parameters
        if api_key is None:
            raise ValueError(f"api_key is required for {model_name}")
        if base_url is None:
            raise ValueError(f"base_url is required for {model_name}")
        
        self.llm = GenericLLM(
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
            provider=provider,
            timeout=timeout,
            max_retries=max_retries
        )
        self.model_name = model_name
        self.provider = provider
    
    @staticmethod
    def _detect_provider(model_name: str, base_url: Optional[str] = None) -> str:
        """Auto-detect provider from model name or base URL."""
        model_lower = model_name.lower()
        
        if "gemini" in model_lower:
            return "gemini"
        elif "gpt" in model_lower or "openai" in model_lower:
            return "openai"
        elif base_url and "groq" in base_url.lower():
            return "groq"
        elif any(x in model_lower for x in ["llama", "mixtral", "qwen"]):
            return "groq"
        else:
            # Default to openai-compatible
            return "openai"
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate text using the underlying LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters (e.g., system_prompt)
            
        Returns:
            Generated text
        """
        return self.llm.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def __repr__(self):
        return f"GenericAdapter(model={self.model_name}, provider={self.provider})"