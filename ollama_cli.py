#!/usr/bin/env python3
"""
Ollama CLI - A Claude Code-like interface for Ollama
"""

import json
import os
import subprocess
import sys
import argparse
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
import shlex

class OllamaCLI:
    def __init__(self, model: str = "gemma2:9b", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        self.conversation_history = []
        self.working_directory = Path.cwd()

    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            return []
        except Exception:
            return []

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a chat message to Ollama"""
        url = f"{self.base_url}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            assistant_message = result["message"]["content"]

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def read_file(self, file_path: str) -> str:
        """Read a file and return its contents"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.working_directory / path

            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            return f"File: {path}\n```\n{content}\n```"
        except Exception as e:
            return f"Error reading file {file_path}: {str(e)}"

    def write_file(self, file_path: str, content: str) -> str:
        """Write content to a file"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.working_directory / path

            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file {file_path}: {str(e)}"

    def run_command(self, command: str) -> str:
        """Execute a shell command"""
        try:
            # Change to working directory
            original_cwd = os.getcwd()
            os.chdir(self.working_directory)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
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

    def list_files(self, directory: str = ".") -> str:
        """List files in a directory"""
        try:
            path = Path(directory)
            if not path.is_absolute():
                path = self.working_directory / path

            if not path.exists():
                return f"Directory {path} does not exist"

            if not path.is_dir():
                return f"{path} is not a directory"

            files = []
            for item in sorted(path.iterdir()):
                if item.is_file():
                    files.append(f"📄 {item.name}")
                elif item.is_dir():
                    files.append(f"📁 {item.name}/")

            return f"Contents of {path}:\n" + "\n".join(files)

        except Exception as e:
            return f"Error listing directory: {str(e)}"

    def change_directory(self, directory: str) -> str:
        """Change working directory"""
        try:
            path = Path(directory)
            if not path.is_absolute():
                path = self.working_directory / path

            path = path.resolve()

            if not path.exists():
                return f"Directory {path} does not exist"

            if not path.is_dir():
                return f"{path} is not a directory"

            self.working_directory = path
            return f"Changed directory to {path}"

        except Exception as e:
            return f"Error changing directory: {str(e)}"

    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return f"""You are an AI assistant similar to Claude Code, running locally via Ollama. You help users with programming, file operations, and system tasks.

Current working directory: {self.working_directory}

IMPORTANT: When users ask you to perform actions like:
- "run ls -al", "list files", "show directory contents" -> Execute: COMMAND: ls -al
- "read file.txt", "show me file.txt" -> Execute: READ: file.txt
- "create/write file.txt with content" -> Execute: WRITE: file.txt
- "change to directory", "cd to folder" -> Execute: CD: directory_name

Use these exact formats in your response:
- COMMAND: <shell_command> - to execute shell commands
- READ: <file_path> - to read files
- WRITE: <file_path> - to write files (you'll be prompted for content)
- CD: <directory> - to change directories
- LS: [directory] - to list files

Always execute the requested action immediately, don't just suggest what the user should type. Be helpful and direct."""

    def process_ai_response(self, response: str) -> str:
        """Process AI response and execute any commands found"""
        lines = response.split('\n')
        result_parts = []

        for line in lines:
            line = line.strip()
            if line.startswith('COMMAND: '):
                command = line[9:].strip()
                print(f"🔧 Executing: {command}")
                cmd_result = self.run_command(command)
                result_parts.append(f"Command output:\n{cmd_result}")
            elif line.startswith('READ: '):
                file_path = line[6:].strip()
                print(f"📖 Reading: {file_path}")
                read_result = self.read_file(file_path)
                result_parts.append(read_result)
            elif line.startswith('LS: '):
                directory = line[4:].strip() or "."
                print(f"📁 Listing: {directory}")
                ls_result = self.list_files(directory)
                result_parts.append(ls_result)
            elif line.startswith('CD: '):
                directory = line[4:].strip()
                print(f"📂 Changing to: {directory}")
                cd_result = self.change_directory(directory)
                result_parts.append(cd_result)
            elif line.startswith('WRITE: '):
                file_path = line[7:].strip()
                print(f"✏️ Write to {file_path} - provide content:")
                try:
                    content = sys.stdin.read()
                    write_result = self.write_file(file_path, content)
                    result_parts.append(write_result)
                except KeyboardInterrupt:
                    result_parts.append("❌ Write cancelled")
            else:
                if line:  # Only add non-empty lines
                    result_parts.append(line)

        return '\n'.join(result_parts)

    def interactive_mode(self):
        """Run the interactive CLI"""
        print(f"🤖 Ollama CLI - Claude Code-like Interface")
        print(f"Model: {self.model}")
        print(f"Working Directory: {self.working_directory}")
        print(f"Type /help for commands or start chatting!\n")

        system_prompt = self.get_system_prompt()

        while True:
            try:
                user_input = input("💬 ").strip()

                if not user_input:
                    continue

                # Handle special commands
                if user_input.startswith('/'):
                    parts = shlex.split(user_input[1:])
                    command = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []

                    if command == 'exit':
                        print("👋 Goodbye!")
                        break
                    elif command == 'help':
                        print(self.get_help_text())
                    elif command == 'clear':
                        self.conversation_history = []
                        print("🧹 Conversation history cleared")
                    elif command == 'models':
                        models = self.list_models()
                        print("Available models:")
                        for model in models:
                            marker = " 👈 (current)" if model == self.model else ""
                            print(f"  • {model}{marker}")
                    elif command == 'model' and args:
                        self.model = args[0]
                        self.conversation_history = []  # Clear history when switching models
                        print(f"🔄 Switched to model: {self.model}")
                    elif command == 'read' and args:
                        result = self.read_file(args[0])
                        print(result)
                    elif command == 'write' and args:
                        print(f"Enter content for {args[0]} (Ctrl+D to finish):")
                        try:
                            content = sys.stdin.read()
                            result = self.write_file(args[0], content)
                            print(result)
                        except KeyboardInterrupt:
                            print("\n❌ Write cancelled")
                    elif command == 'run' and args:
                        cmd = ' '.join(args)
                        print(f"🔧 Running: {cmd}")
                        result = self.run_command(cmd)
                        print(result)
                    elif command == 'ls':
                        directory = args[0] if args else "."
                        result = self.list_files(directory)
                        print(result)
                    elif command == 'cd' and args:
                        result = self.change_directory(args[0])
                        print(result)
                    else:
                        print(f"❓ Unknown command: {command}")
                        print("Type /help for available commands")

                else:
                    # Regular chat
                    print("🤔 Thinking...", end="", flush=True)
                    response = self.chat(user_input, system_prompt)
                    print("\r" + " " * 15 + "\r", end="")  # Clear "Thinking..."

                    # Process the response and execute any commands
                    processed_response = self.process_ai_response(response)
                    print(f"🤖 {processed_response}\n")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break

    def get_help_text(self) -> str:
        """Get help text"""
        return """
📖 Ollama CLI Help

Available commands:
  /read <file_path>     - Read and display a file
  /write <file_path>    - Write content to a file
  /run <command>        - Execute a shell command
  /ls [directory]       - List files (default: current directory)
  /cd <directory>       - Change working directory
  /models               - List available Ollama models
  /model <model_name>   - Switch to a different model
  /clear                - Clear conversation history
  /help                 - Show this help
  /exit                 - Exit the program

💡 Tips:
- You can have normal conversations with the AI
- The AI can suggest commands for file operations
- File paths can be relative or absolute
- Use Ctrl+C or Ctrl+D to exit
"""

def main():
    parser = argparse.ArgumentParser(description="Ollama CLI - Claude Code-like Interface")
    parser.add_argument("--model", "-m", default="gemma2:9b", help="Ollama model to use")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama server URL")
    args = parser.parse_args()

    cli = OllamaCLI(model=args.model, base_url=args.url)
    cli.interactive_mode()

if __name__ == "__main__":
    main()