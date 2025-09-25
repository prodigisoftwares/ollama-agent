"""
Shell command execution
"""

import os
import subprocess
from pathlib import Path


class CommandExecutor:
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def run_command(self, command: str) -> str:
        """Execute a shell command"""
        try:
            # Change to working directory
            original_cwd = os.getcwd()
            os.chdir(self.working_directory)

            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )

            os.chdir(original_cwd)

            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            output += f"Return code: {result.returncode}"

            return output

        except subprocess.TimeoutExpired:
            return "Command timed out after 30 seconds"
        except Exception as e:
            return f"Error running command: {str(e)}"
