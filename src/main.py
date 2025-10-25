"""Main entry point for CodeRover agent with multi-model support."""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.config import Config
from src.llms import GenericAdapter, OrchestratorLLM, CodeWriter


def main():
    """Run the CodeRover coding agent with separate models."""

    print("\n" + "="*60)
    print("🤖 CodeRover - AI Coding Agent (Multi-Model)")
    print("="*60)

    # Validate configuration
    try:
        Config.validate_config()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease set up your .env file with required API keys.")
        sys.exit(1)

    # Initialize LLM components
    print("\n🚀 Initializing CodeRover components...")

    try:
        # ============================================================
        # ORCHESTRATOR: Use a fast, cheap model for planning
        # ============================================================
        orchestrator_model = Config.ORCHESTRATOR_MODEL
        orchestrator_config = Config.get_model_config(orchestrator_model)
        
        orchestrator_llm = GenericAdapter(
            model_name=orchestrator_model,
            api_key=orchestrator_config['api_key'],
            base_url=orchestrator_config['base_url'],
            provider=orchestrator_config['provider'],
            timeout=Config.LLM_TIMEOUT,
            max_retries=Config.LLM_MAX_RETRIES
        )
        print(f"✓ Orchestrator LLM: {orchestrator_model} ({orchestrator_config['provider']})")

        orchestrator = OrchestratorLLM(
            llm=orchestrator_llm,
            system_prompt="You are an expert coding assistant and planner."
        )
        print("✓ Orchestrator initialized")

        # ============================================================
        # CODE WRITER: Use a powerful model for code generation
        # ============================================================
        codewriter_model = Config.CODEWRITER_MODEL
        codewriter_config = Config.get_model_config(codewriter_model)
        
        codewriter_llm = GenericAdapter(
            model_name=codewriter_model,
            api_key=codewriter_config['api_key'],
            base_url=codewriter_config['base_url'],
            provider=codewriter_config['provider'],
            timeout=Config.LLM_TIMEOUT,
            max_retries=Config.LLM_MAX_RETRIES
        )
        print(f"✓ Code Writer LLM: {codewriter_model} ({codewriter_config['provider']})")

        code_writer = CodeWriter(
            llm=codewriter_llm,
            temps=Config.CODE_WRITER_TEMPS,
            max_tokens=Config.CODE_WRITER_MAX_TOKENS
        )
        print(f"✓ Code Writer initialized with temps: {Config.CODE_WRITER_TEMPS}")

        # Summary
        print("\n" + "="*60)
        print("📊 Model Configuration:")
        print(f"   Planning:     {orchestrator_model} ({orchestrator_config['provider']})")
        print(f"   Coding:       {codewriter_model} ({codewriter_config['provider']})")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Initialization Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Interactive loop
    print("\nReady! Enter your coding requests below.")
    print("Type 'quit' or 'exit' to stop.")
    print("="*60)

    while True:
        # Get user input
        print("\n📝 Your coding request:")
        try:
            user_request = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 Goodbye!")
            break

        if user_request.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break

        if not user_request:
            print("⚠️  Please enter a request.")
            continue

        try:
            # Step 1: Generate plan (using orchestrator_model)
            print(f"\n🧠 Planning with {orchestrator_model}...")
            plan = orchestrator.plan(user_request)
            print(f"\n📋 Plan:")
            print(f"  Task: {plan['task']}")
            if plan.get('tests'):
                print(f"  Tests: {plan['tests']}")
            if plan.get('constraints'):
                print(f"  Constraints: {plan['constraints']}")

            # Step 2: Generate code (using codewriter_model)
            print(f"\n💻 Generating code with {codewriter_model}...")
            print(f"    (testing {len(Config.CODE_WRITER_TEMPS)} temperatures)")
            
            code_prompt = f"""Task: {plan['task']}
Constraints: {plan.get('constraints', 'None')}
Tests: {plan.get('tests', 'None')}

Write complete, working Python code to solve this task. Include:
1. Function implementation
2. Proper error handling
3. Docstrings
4. Example usage

Code:"""

            # Use retry logic to handle truncated outputs
            result = code_writer.generate_with_retry(
                code_prompt,
                max_attempts=2
            )
            best = result['best']

            # Display best result
            if best.get('error'):
                print(f"\n❌ Generation issue: {best['error']}")
                print("Please try again with a different request.")
                continue
            
            # Warn if code seems incomplete
            if best['score'] < 0.6:
                print(f"\n⚠️  Warning: Generated code quality is low (score={best['score']:.2f})")
                print("    The code may be incomplete or have issues.")

            print(f"\n✅ Best code (temperature={best['temperature']}, score={best['score']:.2f}):")
            print("-" * 60)
            print(best['text'])
            print("-" * 60)

            # Show all candidates
            print(f"\n📊 All candidates ({len(result['candidates'])}):")
            for i, candidate in enumerate(result['candidates'], 1):
                status = "❌ ERROR" if candidate.get('error') else "✓"
                score_str = f"{candidate['score']:.2f}" if not candidate.get('error') else "N/A"
                print(f"  {i}. {status} temp={candidate['temperature']}, score={score_str}")

        except KeyboardInterrupt:
            print("\n\n⚠️  Generation interrupted.")
            continue
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print("Please try again with a different request.")


if __name__ == "__main__":
    main()