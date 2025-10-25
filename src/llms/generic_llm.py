"""Generic LLM wrapper with support for multiple providers."""

import requests
import time
from typing import Optional, Dict, Any


class GenericLLM:
    """Unified interface for different LLM providers."""
    
    def __init__(
        self,
        model_name: str,
        api_key: str,
        base_url: str,
        provider: str,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """Initialize the LLM wrapper.
        
        Args:
            model_name: Name of the model (e.g., 'gemini-2.0-flash', 'gpt-4')
            api_key: API key for the provider
            base_url: Base URL for the API
            provider: Provider name ('gemini', 'openai', 'groq')
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.model_name = model_name
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.provider = provider.lower()
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Validate provider
        if self.provider not in ['gemini', 'openai', 'groq']:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """Generate text from the LLM.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Generated text
        """
        return self._generate_with_retry(
            lambda p, t, m, **kw: self._generate_internal(p, t, m, **kw),
            prompt,
            temperature,
            max_tokens,
            **kwargs
        )
    
    def _generate_with_retry(
        self,
        generate_func,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Execute generation with retry logic."""
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return generate_func(prompt, temperature, max_tokens, **kwargs)
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                    print(f"   Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        raise RuntimeError(f"Generation failed after {self.max_retries} attempts: {last_error}") from last_error
    
    def _generate_internal(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Internal generation method that routes to the correct provider."""
        if self.provider == 'gemini':
            return self._generate_gemini(prompt, temperature, max_tokens, **kwargs)
        elif self.provider in ['openai', 'groq']:
            return self._generate_openai_compatible(prompt, temperature, max_tokens, **kwargs)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _generate_gemini(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using Google Gemini API."""
        # Gemini uses a different URL structure
        # Format: POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
        url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
        
        # Gemini request format
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": kwargs.get("top_p", 0.95),
                "topK": kwargs.get("top_k", 40),
            }
        }
        
        # Add system instruction if provided
        if "system_prompt" in kwargs:
            payload["systemInstruction"] = {
                "parts": [{
                    "text": kwargs["system_prompt"]
                }]
            }
        
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            # Check for errors
            if response.status_code != 200:
                error_detail = response.text
                raise RuntimeError(
                    f"Gemini API error {response.status_code}: {error_detail}"
                )
            
            # Parse response
            data = response.json()
            
            # Extract text from Gemini response format
            if "candidates" not in data or not data["candidates"]:
                raise RuntimeError(f"No candidates in Gemini response: {data}")
            
            candidate = data["candidates"][0]
            if "content" not in candidate:
                raise RuntimeError(f"No content in candidate: {candidate}")
            
            parts = candidate["content"].get("parts", [])
            if not parts:
                raise RuntimeError(f"No parts in content: {candidate['content']}")
            
            text = parts[0].get("text", "")
            if not text:
                raise RuntimeError(f"Empty text in response: {parts}")
            
            return text.strip()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Gemini API request failed: {e}") from e
    
    def _generate_openai_compatible(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using OpenAI-compatible API (OpenAI, Groq, etc.)."""
        url = f"{self.base_url}/chat/completions"
        
        # Build messages
        messages = []
        if "system_prompt" in kwargs:
            messages.append({
                "role": "system",
                "content": kwargs["system_prompt"]
            })
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        # OpenAI-compatible request format
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        
        # Add optional parameters
        if "top_p" in kwargs:
            payload["top_p"] = kwargs["top_p"]
        if "frequency_penalty" in kwargs:
            payload["frequency_penalty"] = kwargs["frequency_penalty"]
        if "presence_penalty" in kwargs:
            payload["presence_penalty"] = kwargs["presence_penalty"]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            # Check for errors
            if response.status_code != 200:
                error_detail = response.text
                raise RuntimeError(
                    f"{self.provider.upper()} API error {response.status_code}: {error_detail}"
                )
            
            # Parse response
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"No choices in response: {data}")
            
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")
            
            if not content:
                raise RuntimeError(f"Empty content in response: {data}")
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"{self.provider.upper()} API request failed: {e}") from e
    
    def __repr__(self):
        return f"GenericLLM(model={self.model_name}, provider={self.provider})"