"""Unit tests for LLM components."""

import pytest
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import after path is set
from src.config import Config
from src.llms import (
    GenericAdapter,
    OrchestratorLLM,
    CodeWriter,
    LLMFactory
)


@pytest.fixture
def test_llm():
    """Create a test LLM instance."""
    return LLMFactory.create_orchestrator()


class TestGenericAdapter:
    """Tests for GenericAdapter."""
    
    def test_initialization(self):
        """Test LLM initialization."""
        config = Config.get_model_config(Config.ORCHESTRATOR_MODEL)
        llm = GenericAdapter(
            model_name=Config.ORCHESTRATOR_MODEL,
            api_key=config['api_key'],
            base_url=config['base_url'],
            provider=config['provider']
        )
        assert llm.model_name == Config.ORCHESTRATOR_MODEL
        assert llm.provider == config['provider']
    
    def test_generate_basic(self, test_llm):
        """Test basic text generation."""
        response = test_llm.generate(
            "Say 'test' and nothing else",
            temperature=0.3,
            max_tokens=10
        )
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_generate_with_system_prompt(self, test_llm):
        """Test generation with system prompt."""
        response = test_llm.generate(
            "What is 2+2?",
            temperature=0.1,
            max_tokens=20,
            system_prompt="You are a calculator. Answer only with numbers."
        )
        assert isinstance(response, str)
        # Response should contain "4"
        assert '4' in response


class TestOrchestratorLLM:
    """Tests for OrchestratorLLM."""
    
    def test_plan_generation(self, test_llm):
        """Test plan generation."""
        orchestrator = OrchestratorLLM(test_llm)
        plan = orchestrator.plan("Create a function to add two numbers")
        
        assert isinstance(plan, dict)
        assert 'task' in plan
        assert 'tests' in plan
        assert 'constraints' in plan
        assert len(plan['task']) > 0
    
    def test_reason(self, test_llm):
        """Test general reasoning."""
        orchestrator = OrchestratorLLM(test_llm)
        response = orchestrator.reason(
            "Should I use a list or a dictionary to store key-value pairs?"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_decide(self, test_llm):
        """Test decision making."""
        orchestrator = OrchestratorLLM(test_llm)
        options = ["Use a for loop", "Use list comprehension", "Use map()"]
        context = "Need to transform a list of numbers by doubling them"
        
        choice = orchestrator.decide(options, context)
        
        assert choice in options
    
    def test_analyze(self, test_llm):
        """Test code analysis."""
        orchestrator = OrchestratorLLM(test_llm)
        code = "def add(a, b):\n    return a + b"
        question = "What does this function do?"
        
        analysis = orchestrator.analyze(code, question)
        
        assert isinstance(analysis, str)
        assert len(analysis) > 0


class TestCodeWriter:
    """Tests for CodeWriter."""
    
    def test_single_generation(self, test_llm):
        """Test code generation with single temperature."""
        writer = CodeWriter(test_llm, temps=[0.5], max_tokens=200)
        result = writer.generate_and_pick("Write: def hello(): pass")
        
        assert 'best' in result
        assert 'candidates' in result
        assert result['best']['temperature'] == 0.5
        assert isinstance(result['best']['text'], str)
    
    def test_multi_temperature(self, test_llm):
        """Test code generation with multiple temperatures."""
        writer = CodeWriter(test_llm, temps=[0.3, 0.7], max_tokens=200)
        result = writer.generate_and_pick("Write: def add(a, b): return a + b")
        
        assert len(result['candidates']) == 2
        assert result['candidates'][0]['temperature'] == 0.3
        assert result['candidates'][1]['temperature'] == 0.7


class TestLLMFactory:
    """Tests for LLMFactory."""
    
    def test_create_llm_default(self):
        """Test creating LLM with defaults."""
        llm = LLMFactory.create_llm()
        assert llm.model_name == Config.ORCHESTRATOR_MODEL
    
    def test_create_llm_custom(self):
        """Test creating LLM with custom model."""
        llm = LLMFactory.create_llm(model_name=Config.CODEWRITER_MODEL)
        assert llm.model_name == Config.CODEWRITER_MODEL
    
    def test_create_orchestrator(self):
        """Test orchestrator creation."""
        llm = LLMFactory.create_orchestrator()
        assert llm.model_name == Config.ORCHESTRATOR_MODEL
    
    def test_create_code_writer(self):
        """Test code writer creation."""
        llm = LLMFactory.create_code_writer()
        assert llm.model_name == Config.CODEWRITER_MODEL
    
    def test_list_available_models(self):
        """Test listing available models."""
        models = LLMFactory.list_available_models()
        assert isinstance(models, dict)
        assert Config.ORCHESTRATOR_MODEL in models
        assert Config.CODEWRITER_MODEL in models


# Integration Tests
class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_plan_and_generate(self, test_llm):
        """Test complete plan → generate workflow."""
        # Step 1: Plan
        orchestrator = OrchestratorLLM(test_llm)
        plan = orchestrator.plan("Create a fibonacci function")
        
        assert 'task' in plan
        
        # Step 2: Generate code
        code_llm = LLMFactory.create_code_writer()
        writer = CodeWriter(code_llm, temps=[0.5], max_tokens=300)
        
        prompt = f"Task: {plan['task']}\n\nCode:"
        result = writer.generate_and_pick(prompt)
        
        assert result['best']['text']
        assert not result['best'].get('error')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])