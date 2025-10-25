"""Simple unit tests for LLM components (without LLMFactory)."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.config import Config
from src.llms import (
    GenericAdapter,
    OrchestratorLLM,
    CodeWriter
)


def create_test_llm():
    """Helper to create a test LLM instance."""
    config = Config.get_model_config(Config.ORCHESTRATOR_MODEL)
    return GenericAdapter(
        model_name=Config.ORCHESTRATOR_MODEL,
        api_key=config['api_key'],
        base_url=config['base_url'],
        provider=config['provider'],
        timeout=30,
        max_retries=2
    )


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
        print(f"✅ Initialized: {llm}")
    
    def test_generate_basic(self):
        """Test basic text generation."""
        llm = create_test_llm()
        response = llm.generate(
            "Say 'test' and nothing else",
            temperature=0.3,
            max_tokens=10
        )
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"✅ Generated: {response[:50]}...")
    
    def test_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        llm = create_test_llm()
        response = llm.generate(
            "What is 2+2?",
            temperature=0.1,
            max_tokens=20,
            system_prompt="You are a calculator. Answer only with numbers."
        )
        assert isinstance(response, str)
        assert '4' in response
        print(f"✅ Generated with system prompt: {response[:50]}...")


class TestOrchestratorLLM:
    """Tests for OrchestratorLLM."""
    
    def test_plan_generation(self):
        """Test plan generation."""
        llm = create_test_llm()
        orchestrator = OrchestratorLLM(llm)
        plan = orchestrator.plan("Create a function to add two numbers")
        
        assert isinstance(plan, dict)
        assert 'task' in plan
        assert 'tests' in plan
        assert 'constraints' in plan
        assert len(plan['task']) > 0
        print(f"✅ Plan generated: {plan['task'][:50]}...")
    
    def test_reason(self):
        """Test general reasoning."""
        llm = create_test_llm()
        orchestrator = OrchestratorLLM(llm)
        response = orchestrator.reason(
            "Should I use a list or a dictionary to store key-value pairs?"
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        print(f"✅ Reasoning: {response[:50]}...")
    
    def test_decide(self):
        """Test decision making."""
        llm = create_test_llm()
        orchestrator = OrchestratorLLM(llm)
        options = ["Use a for loop", "Use list comprehension", "Use map()"]
        context = "Need to transform a list of numbers by doubling them"
        
        choice = orchestrator.decide(options, context)
        
        assert choice in options
        print(f"✅ Decision: {choice}")


class TestCodeWriter:
    """Tests for CodeWriter."""
    
    def test_single_generation(self):
        """Test code generation with single temperature."""
        llm = create_test_llm()
        writer = CodeWriter(llm, temps=[0.5], max_tokens=200)
        result = writer.generate_and_pick("Write: def hello(): pass")
        
        assert 'best' in result
        assert 'candidates' in result
        assert result['best']['temperature'] == 0.5
        assert isinstance(result['best']['text'], str)
        print(f"✅ Code generated: {result['best']['text'][:50]}...")
    
    def test_multi_temperature(self):
        """Test code generation with multiple temperatures."""
        llm = create_test_llm()
        writer = CodeWriter(llm, temps=[0.3, 0.7], max_tokens=200)
        result = writer.generate_and_pick("Write: def add(a, b): return a + b")
        
        assert len(result['candidates']) == 2
        assert result['candidates'][0]['temperature'] == 0.3
        assert result['candidates'][1]['temperature'] == 0.7
        print(f"✅ Multi-temp code generated, best temp: {result['best']['temperature']}")


def test_integration():
    """Integration test for complete workflow."""
    print("\n" + "="*60)
    print("INTEGRATION TEST: Plan → Generate")
    print("="*60)
    
    # Step 1: Plan
    llm = create_test_llm()
    orchestrator = OrchestratorLLM(llm)
    plan = orchestrator.plan("Create a fibonacci function")
    
    print(f"\n📋 Plan: {plan['task'][:80]}...")
    assert 'task' in plan
    
    # Step 2: Generate code
    code_config = Config.get_model_config(Config.CODEWRITER_MODEL)
    code_llm = GenericAdapter(
        model_name=Config.CODEWRITER_MODEL,
        api_key=code_config['api_key'],
        base_url=code_config['base_url'],
        provider=code_config['provider'],
        timeout=60,
        max_retries=2
    )
    writer = CodeWriter(code_llm, temps=[0.5], max_tokens=300)
    
    prompt = f"Task: {plan['task']}\n\nCode:"
    result = writer.generate_and_pick(prompt)
    
    print(f"\n💻 Code Preview:")
    print(result['best']['text'][:150] + "...")
    
    assert result['best']['text']
    assert not result['best'].get('error')
    print("\n✅ Integration test passed!")


if __name__ == "__main__":
    # Run tests manually
    print("\n🧪 Running LLM Component Tests\n")
    
    try:
        # Test 1
        print("TEST 1: GenericAdapter initialization")
        t = TestGenericAdapter()
        t.test_initialization()
        
        # Test 2
        print("\nTEST 2: Basic generation")
        t.test_generate_basic()
        
        # Test 3
        print("\nTEST 3: Orchestrator planning")
        t = TestOrchestratorLLM()
        t.test_plan_generation()
        
        # Test 4
        print("\nTEST 4: Code generation")
        t = TestCodeWriter()
        t.test_single_generation()
        
        # Test 5
        print("\nTEST 5: Integration")
        test_integration()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()