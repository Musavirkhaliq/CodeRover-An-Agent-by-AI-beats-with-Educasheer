
"""LLM interface protocol for type safety and modularity."""

from typing import Protocol


class LLMInterface(Protocol):
    """Protocol defining the interface for LLM implementations."""

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
        **kwargs
    ) -> str:
        """Generate text from the LLM.

        Args:
            prompt: The input prompt
            temperature: Sampling temperature (0.0 = deterministic, higher = more random)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text string

        Raises:
            RuntimeError: If API key is missing or API call fails
        """
        ...
