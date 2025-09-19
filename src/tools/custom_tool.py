# Custom_tool
# tools.py
import subprocess
import os

def read_file(path: str) -> str:
    """Reads the content of a file at the given path."""
    print(f"--- Reading file: {path} ---")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file at the given path."""
    print(f"--- Writing to file: {path} ---")
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error writing file: {e}"

def run_bash(command: str) -> str:
    """Executes a bash command and returns its output."""
    print(f"--- Running bash command: {command} ---")
    try:
        result = subprocess.run(
            command,
            shell=True,
            text=True,
            capture_output=True,
            check=False # Do not raise exception on non-zero exit codes
        )
        output = f"STDOUT:\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        return output
    except Exception as e:
        return f"Error running command: {e}"

# A dictionary to map tool names to functions
AVAILABLE_TOOLS = {
    "read_file": read_file,
    "write_file": write_file,
    "run_bash": run_bash,
}
