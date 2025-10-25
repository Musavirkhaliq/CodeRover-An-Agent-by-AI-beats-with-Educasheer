"""Code writer with multi-temperature sampling and validation."""

from typing import List, Dict, Any, Optional
from .llm_interfaces import LLMInterface
import re


class CodeWriter:
    """Generate code with multiple temperature attempts and pick the best."""
    
    def __init__(
        self,
        llm: LLMInterface,
        temps: List[float] = [0.3, 0.7, 1.0],
        max_tokens: int = 2000,
        min_code_length: int = 50
    ):
        """
        Initialize CodeWriter.
        
        Args:
            llm: LLM instance for generation
            temps: List of temperatures to try
            max_tokens: Maximum tokens per generation
            min_code_length: Minimum acceptable code length
        """
        self.llm = llm
        self.temps = temps
        self.max_tokens = max_tokens
        self.min_code_length = min_code_length
    
    def generate_and_pick(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code at multiple temperatures and pick the best.
        
        Args:
            prompt: Code generation prompt
            system_prompt: Optional system prompt
            
        Returns:
            Dictionary with:
                - 'best': Best candidate dict
                - 'candidates': All candidates list
        """
        if system_prompt is None:
            system_prompt = """You are an expert Python programmer. Generate complete, working code.
            
Requirements:
1. Write COMPLETE implementations - no placeholders or TODO comments
2. Include proper error handling
3. Add comprehensive docstrings
4. Ensure code is syntactically correct
5. DO NOT truncate the code - write the full implementation"""
        
        candidates = []
        
        # Try each temperature
        for temp in self.temps:
            try:
                text = self.llm.generate(
                    prompt=prompt,
                    temperature=temp,
                    max_tokens=self.max_tokens,
                    system_prompt=system_prompt
                )
                
                # Validate generation
                if not text or len(text.strip()) < self.min_code_length:
                    candidates.append({
                        'temperature': temp,
                        'text': text,
                        'score': 0.0,
                        'error': f'Code too short ({len(text)} chars)'
                    })
                    continue
                
                # Check for truncation indicators
                if self._is_truncated(text):
                    candidates.append({
                        'temperature': temp,
                        'text': text,
                        'score': 0.3,  # Low score but not zero
                        'error': 'Code appears truncated'
                    })
                    continue
                
                # Score the code
                score = self._score_code(text)
                
                candidates.append({
                    'temperature': temp,
                    'text': text,
                    'score': score,
                    'error': None
                })
                
            except Exception as e:
                candidates.append({
                    'temperature': temp,
                    'text': '',
                    'score': 0.0,
                    'error': str(e)
                })
        
        # Pick best candidate (highest score, non-error first)
        valid_candidates = [c for c in candidates if not c.get('error')]
        
        if valid_candidates:
            best = max(valid_candidates, key=lambda x: x['score'])
        else:
            # All failed - return least bad
            best = max(candidates, key=lambda x: x['score'])
            if best['score'] == 0.0:
                best['error'] = 'All generations failed'
        
        return {
            'best': best,
            'candidates': candidates
        }
    
    def _is_truncated(self, code: str) -> bool:
        """
        Check if code appears to be truncated.
        
        Args:
            code: Generated code string
            
        Returns:
            True if code appears truncated
        """
        code = code.strip()
        
        # Check for incomplete function/class definitions
        if re.search(r'(def|class)\s+\w+.*:\s*$', code):
            return True
        
        # Check for incomplete docstrings
        if code.count('"""') % 2 != 0:
            return True
        
        # Check for incomplete parentheses/brackets
        if code.count('(') != code.count(')'):
            return True
        if code.count('[') != code.count(']'):
            return True
        if code.count('{') != code.count('}'):
            return True
        
        # Check for trailing incomplete statements
        last_line = code.split('\n')[-1].strip()
        if last_line and not last_line.endswith((':', ',', ')', ']', '}', '"', "'")):
            if re.match(r'^[a-zA-Z_].*[=\.]$', last_line):
                return True
        
        return False
    
    def _score_code(self, code: str) -> float:
        """
        Score generated code quality.
        
        Args:
            code: Code string to score
            
        Returns:
            Score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Has docstrings (+0.1)
        if '"""' in code or "'''" in code:
            score += 0.1
        
        # Has type hints (+0.1)
        if '->' in code or ': ' in code:
            score += 0.1
        
        # Has error handling (+0.1)
        if 'try:' in code or 'except' in code or 'raise' in code:
            score += 0.1
        
        # Has comments (+0.05)
        if '#' in code:
            score += 0.05
        
        # Reasonable length (+0.1 if > 200 chars)
        if len(code) > 200:
            score += 0.1
        
        # Not too long (-0.1 if approaching max_tokens)
        estimated_tokens = len(code.split()) * 1.3
        if estimated_tokens > self.max_tokens * 0.95:
            score -= 0.1
        
        # Complete-looking code (+0.15)
        if not self._is_truncated(code):
            score += 0.15
        
        return min(1.0, max(0.0, score))
    
    def generate_with_retry(
        self,
        prompt: str,
        max_attempts: int = 3,
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code with retry logic for truncated outputs.
        
        Args:
            prompt: Code generation prompt
            max_attempts: Maximum retry attempts
            system_prompt: Optional system prompt
            
        Returns:
            Best result after retries
        """
        for attempt in range(max_attempts):
            result = self.generate_and_pick(prompt, system_prompt)
            
            # If best is good enough, return it
            best = result['best']
            if not best.get('error') and best['score'] > 0.7:
                return result
            
            # If truncated, add instruction and retry
            if best.get('error') == 'Code appears truncated':
                prompt = f"""{prompt}

IMPORTANT: The previous attempt was truncated. Please write the COMPLETE implementation.
Do not leave any function bodies empty or use placeholder comments."""
                continue
            
            # Other errors or low score - return what we have
            return result
        
        return result