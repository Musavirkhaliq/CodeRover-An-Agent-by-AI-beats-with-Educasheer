# main.py
import sys
from agent import Agent

if __name__ == "__main__":
    # Check if a request was provided
    if len(sys.argv) < 2:
        print("Usage: python main.py \"<your request>\"")
        sys.exit(1)

    # The user's request is the first command-line argument
    user_request = sys.argv[1]

    # Initialize and run the agent
    coding_agent = Agent()
    coding_agent.run(user_request)
