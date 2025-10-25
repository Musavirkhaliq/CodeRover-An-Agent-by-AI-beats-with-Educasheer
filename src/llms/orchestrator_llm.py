"""Enhanced Orchestrator LLM with flexible methods for integration."""

import json
from typing import Dict, Any, List, Optional


class OrchestratorLLM:
    """High-level planner and reasoning LLM for orchestration."""
    
    def __init__(self, llm, system_prompt: Optional[str] = None):
        """Initialize orchestrator.
        
        Args:
            llm: GenericAdapter instance
            system_prompt: System prompt for the orchestrator
        """
        self.llm = llm
        self.system_prompt = system_prompt or "You are an expert coding assistant and planner."
    
    def plan(self, user_request: str) -> Dict[str, Any]:
        """Create a structured plan for a coding request.
        
        Args:
            user_request: The user's coding task description
            
        Returns:
            Dictionary with 'task', 'tests', and 'constraints'
        """
        prompt = f"""Given this coding request, create a detailed plan.

USER REQUEST:
{user_request}

Provide a JSON response with:
1. "task": A clear, specific description of what needs to be coded
2. "tests": Specific test cases or validation criteria
3. "constraints": Any technical constraints or requirements

Example format:
{{
    "task": "Create a function that...",
    "tests": "Should handle edge cases like...",
    "constraints": "Must use only standard library..."
}}

Your response (JSON only):"""
        
        try:
            response = self.llm.generate(
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000,
                system_prompt=self.system_prompt
            )
            
            # Extract JSON from response
            response = response.strip()
            if '{' in response:
                start = response.find('{')
                end = response.rfind('}') + 1
                json_str = response[start:end]
                plan = json.loads(json_str)
            else:
                plan = self._create_fallback_plan(user_request)
            
            # Validate and fill missing fields
            plan.setdefault('task', user_request)
            plan.setdefault('tests', 'Test with various inputs')
            plan.setdefault('constraints', 'Use Python best practices')
            
            return plan
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Planning error: {e}")
            return self._create_fallback_plan(user_request)
    
    def reason(self, prompt: str, temperature: float = 0.3, **kwargs) -> str:
        """General reasoning without structured format.
        
        Useful for: decision making, analysis, explanations
        
        Args:
            prompt: The reasoning prompt
            temperature: Sampling temperature (lower = more focused)
            **kwargs: Additional generation parameters
            
        Returns:
            Reasoning response as text
        """
        return self.llm.generate(
            prompt=prompt,
            temperature=temperature,
            system_prompt=self.system_prompt,
            **kwargs
        )
    
    def decide(
        self, 
        options: List[str], 
        context: str,
        temperature: float = 0.2
    ) -> str:
        """Choose the best option given context.
        
        Args:
            options: List of possible choices
            context: Context for the decision
            temperature: Sampling temperature
            
        Returns:
            Selected option (one of the input options)
        """
        options_text = "\n".join(f"{i+1}. {opt}" for i, opt in enumerate(options))
        
        prompt = f"""Given this context, choose the best option.

CONTEXT:
{context}

OPTIONS:
{options_text}

Respond with ONLY the number of your choice (1-{len(options)}).
Your choice:"""
        
        response = self.llm.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=10,
            system_prompt=self.system_prompt
        )
        
        # Extract number from response
        try:
            choice_num = int(''.join(c for c in response if c.isdigit()))
            if 1 <= choice_num <= len(options):
                return options[choice_num - 1]
        except (ValueError, IndexError):
            pass
        
        # Fallback: return first option
        return options[0]
    
    def analyze(self, code: str, question: str) -> str:
        """Analyze code and answer questions about it.
        
        Args:
            code: Code to analyze
            question: Question about the code
            
        Returns:
            Analysis response
        """
        prompt = f"""Analyze this code and answer the question.

CODE:
```python
{code}
```

QUESTION:
{question}

Your analysis:"""
        
        return self.llm.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=500,
            system_prompt=self.system_prompt
        )
    
    def _create_fallback_plan(self, user_request: str) -> Dict[str, Any]:
        """Create a basic plan when JSON parsing fails."""
        return {
            "task": user_request,
            "tests": "Test with various inputs and edge cases",
            "constraints": "Use Python standard library and best practices"
        }
    
    def __repr__(self):
        return f"OrchestratorLLM(llm={self.llm})"