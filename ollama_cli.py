#!/usr/bin/env python3
"""
Ollama CLI - A Claude Code-like interface for Ollama
"""

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import requests


class OllamaCLI:
    def __init__(
        self, model: str = "gemma2:9b", base_url: str = "http://localhost:11434"
    ):
        self.model = model
        self.base_url = base_url
        self.conversation_history = []
        self.working_directory = Path.cwd()

    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                # Skip header
                lines = result.stdout.strip().split("\n")[1:]
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

        payload = {"model": self.model, "messages": messages, "stream": False}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            assistant_message = result["message"]["content"]

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            return assistant_message

        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def read_file(self, file_path: str) -> str:
        """Read a file and return its contents"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.working_directory / path

            with open(path, "r", encoding="utf-8") as f:
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

            with open(path, "w", encoding="utf-8") as f:
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

    def search_code(self, query: str, file_pattern: str = "*") -> str:
        """Search for code patterns in files"""
        try:
            results = []
            search_path = self.working_directory

            # Search for different file types based on pattern
            if file_pattern == "*":
                patterns = ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.h"]
            else:
                patterns = [file_pattern]

            for pattern in patterns:
                for file_path in search_path.rglob(pattern):
                    if file_path.is_file():
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                lines = content.split("\n")

                            for line_num, line in enumerate(lines, 1):
                                if query.lower() in line.lower():
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                        except Exception:
                            continue

            if results:
                # Limit to first 20 results
                return f"Search results for '{query}':\n" + "\n".join(results[:20])
            else:
                return f"No results found for '{query}'"

        except Exception as e:
            return f"Error searching code: {str(e)}"

    def find_functions(
        self, function_name: str = "", file_pattern: str = "*.py"
    ) -> str:
        """Find function definitions"""
        try:
            results = []
            search_path = self.working_directory

            for file_path in search_path.rglob(file_pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                        for line_num, line in enumerate(lines, 1):
                            # Look for function definitions
                            if re.match(r"\s*def\s+\w+", line):
                                if (
                                    not function_name
                                    or function_name.lower() in line.lower()
                                ):
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                            # Look for class definitions too
                            elif re.match(r"\s*class\s+\w+", line):
                                if (
                                    not function_name
                                    or function_name.lower() in line.lower()
                                ):
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                    except Exception:
                        continue

            if results:
                return f"Functions/Classes found:\n" + "\n".join(results[:20])
            else:
                return f"No functions/classes found"

        except Exception as e:
            return f"Error finding functions: {str(e)}"

    def find_todos(self) -> str:
        """Find TODO comments in the codebase"""
        try:
            results = []
            search_path = self.working_directory
            todo_patterns = [r"#\s*TODO", r"//\s*TODO", r"/\*\s*TODO", r"<!--\s*TODO"]

            for file_path in search_path.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith("."):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                        for line_num, line in enumerate(lines, 1):
                            for pattern in todo_patterns:
                                if re.search(pattern, line, re.IGNORECASE):
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                                    break
                    except Exception:
                        continue

            if results:
                return f"TODO comments found:\n" + "\n".join(results)
            else:
                return "No TODO comments found"

        except Exception as e:
            return f"Error finding TODOs: {str(e)}"

    def find_imports(self, import_name: str) -> str:
        """Find files that import a specific module"""
        try:
            results = []
            search_path = self.working_directory

            for file_path in search_path.rglob("*.py"):
                if file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                        for line_num, line in enumerate(lines, 1):
                            if (
                                "import " + import_name in line
                                or "from " + import_name in line
                            ):
                                relative_path = file_path.relative_to(search_path)
                                results.append(
                                    f"{relative_path}:{line_num}: {line.strip()}"
                                )
                    except Exception:
                        continue

            if results:
                return f"Files importing '{import_name}':\n" + "\n".join(results)
            else:
                return f"No files found importing '{import_name}'"

        except Exception as e:
            return f"Error finding imports: {str(e)}"

    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return f"""You are an AI assistant similar to Claude Code, running \
locally via Ollama. You help users with programming, file operations, and \
system tasks.

Current working directory: {self.working_directory}

IMPORTANT: When users ask you to perform actions like:
- "run ls -al", "list files", "show directory contents" -> Execute: COMMAND: ls -al
- "read file.txt", "show me file.txt" -> Execute: READ: file.txt
- "create/write file.txt with content" -> Execute: WRITE: file.txt
- "change to directory", "cd to folder" -> Execute: CD: directory_name
- "find functions with 'database'", "search for functions" -> Execute: SEARCH_FUNC: database
- "find TODO comments" -> Execute: FIND_TODO:
- "search for 'error handling'" -> Execute: SEARCH: error handling
- "find files importing requests" -> Execute: FIND_IMPORT: requests

Use these exact formats in your response:
- COMMAND: <shell_command> - to execute shell commands
- READ: <file_path> - to read files
- WRITE: <file_path> - to write files (you'll be prompted for content)
- WRITE_CONTENT: <file_path> (then on next line) CONTENT: (then content) \
(then on final line) END_CONTENT - to write content directly
- CD: <directory> - to change directories
- LS: [directory] - to list files
- SEARCH: <query> - to search for code patterns
- SEARCH_FUNC: [function_name] - to find function/class definitions
- FIND_TODO: - to find TODO comments
- FIND_IMPORT: <module_name> - to find files importing a module

Always execute the requested action immediately, don't just suggest what the \
user should type. Be helpful and direct."""

    def process_ai_response(self, response: str) -> str:
        """Process AI response and execute any commands found"""
        # Debug: print the raw response
        if "WRITE_CONTENT:" in response:
            print(f"DEBUG - Full AI response:\n{repr(response)}")

        lines = response.split("\n")
        result_parts = []

        i = 0
        while i < len(lines):
            line = lines[i]
            line = line.strip()
            if line.startswith("COMMAND: "):
                command = line[9:].strip()
                print(f"🔧 Executing: {command}")
                cmd_result = self.run_command(command)
                result_parts.append(f"Command output:\n{cmd_result}")
            elif line.startswith("READ: "):
                file_path = line[6:].strip()
                print(f"📖 Reading: {file_path}")
                read_result = self.read_file(file_path)
                result_parts.append(read_result)
            elif line.startswith("LS: "):
                directory = line[4:].strip() or "."
                print(f"📁 Listing: {directory}")
                ls_result = self.list_files(directory)
                result_parts.append(ls_result)
            elif line.startswith("CD: "):
                directory = line[4:].strip()
                print(f"📂 Changing to: {directory}")
                cd_result = self.change_directory(directory)
                result_parts.append(cd_result)
            elif line.startswith("WRITE: "):
                file_path = line[7:].strip()
                print(f"✏️ Generating content for {file_path}")

                # Ask the AI to generate the content for this file
                content_prompt = f"Generate the content for the file {file_path}. Only output the file content, nothing else."  # noqa: E501
                generated_content = self.chat(content_prompt)

                # Clean up the response - remove any markdown code blocks
                if generated_content.startswith("```"):
                    lines = generated_content.split("\n")
                    # Remove first and last lines if they're markdown markers
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    generated_content = "\n".join(lines)

                print(f"✏️ Writing to {file_path}")
                write_result = self.write_file(file_path, generated_content)
                result_parts.append(write_result)
            elif line.startswith("WRITE_CONTENT: "):
                file_path = line[15:].strip()
                print(f"✏️ Writing to {file_path}")
                # Look for content between CONTENT: and END_CONTENT
                content_lines = []
                i += 1  # Move to next line
                collecting_content = False

                while i < len(lines):
                    current_line = lines[i].strip()
                    if current_line.startswith("CONTENT:"):
                        collecting_content = True
                        # Extract content from same line if present
                        content_after_colon = current_line[
                            8:
                        ].strip()  # Remove "CONTENT:"
                        if content_after_colon:
                            content_lines.append(content_after_colon)
                        i += 1
                        continue
                    elif current_line.startswith("END_CONTENT"):
                        break
                    elif collecting_content:
                        content_lines.append(lines[i])  # Keep original indentation
                    i += 1

                if content_lines:
                    content = "\n".join(content_lines)
                    write_result = self.write_file(file_path, content)
                    result_parts.append(write_result)
                else:
                    result_parts.append("❌ No content found for WRITE_CONTENT")
            elif line.startswith("SEARCH: "):
                query = line[8:].strip()
                print(f"🔍 Searching for: {query}")
                search_result = self.search_code(query)
                result_parts.append(search_result)
            elif line.startswith("SEARCH_FUNC: "):
                func_name = line[13:].strip()
                print(f"🔍 Finding functions: {func_name}")
                func_result = self.find_functions(func_name)
                result_parts.append(func_result)
            elif line.startswith("FIND_TODO:"):
                print(f"🔍 Finding TODO comments")
                todo_result = self.find_todos()
                result_parts.append(todo_result)
            elif line.startswith("FIND_IMPORT: "):
                import_name = line[13:].strip()
                print(f"🔍 Finding imports of: {import_name}")
                import_result = self.find_imports(import_name)
                result_parts.append(import_result)
            elif line == "CONTENT:" or line == "END_CONTENT":
                # Skip these markers when they appear as standalone lines
                pass
            else:
                if line:  # Only add non-empty lines
                    result_parts.append(line)

            i += 1

        return "\n".join(result_parts)

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
                if user_input.startswith("/"):
                    parts = shlex.split(user_input[1:])
                    command = parts[0].lower()
                    args = parts[1:] if len(parts) > 1 else []

                    if command == "exit":
                        print("👋 Goodbye!")
                        break
                    elif command == "help":
                        print(self.get_help_text())
                    elif command == "clear":
                        self.conversation_history = []
                        print("🧹 Conversation history cleared")
                    elif command == "models":
                        models = self.list_models()
                        print("Available models:")
                        for model in models:
                            marker = " 👈 (current)" if model == self.model else ""
                            print(f"  • {model}{marker}")
                    elif command == "model" and args:
                        self.model = args[0]
                        # Clear history when switching models
                        self.conversation_history = []
                        print(f"🔄 Switched to model: {self.model}")
                    elif command == "read" and args:
                        result = self.read_file(args[0])
                        print(result)
                    elif command == "write" and args:
                        print(f"Enter content for {args[0]} (Ctrl+D to finish):")
                        try:
                            content = sys.stdin.read()
                            result = self.write_file(args[0], content)
                            print(result)
                        except KeyboardInterrupt:
                            print("\n❌ Write cancelled")
                    elif command == "run" and args:
                        cmd = " ".join(args)
                        print(f"🔧 Running: {cmd}")
                        result = self.run_command(cmd)
                        print(result)
                    elif command == "ls":
                        directory = args[0] if args else "."
                        result = self.list_files(directory)
                        print(result)
                    elif command == "cd" and args:
                        result = self.change_directory(args[0])
                        print(result)
                    elif command == "search" and args:
                        query = " ".join(args)
                        result = self.search_code(query)
                        print(result)
                    elif command == "find-func":
                        func_name = args[0] if args else ""
                        result = self.find_functions(func_name)
                        print(result)
                    elif command == "find-todo":
                        result = self.find_todos()
                        print(result)
                    elif command == "find-import" and args:
                        result = self.find_imports(args[0])
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
  /search <query>       - Search for code patterns in files
  /find-func [name]     - Find function/class definitions (optional name filter)
  /find-todo            - Find TODO comments in the codebase
  /find-import <module> - Find files that import a specific module
  /models               - List available Ollama models
  /model <model_name>   - Switch to a different model
  /clear                - Clear conversation history
  /help                 - Show this help
  /exit                 - Exit the program

💡 Tips:
- You can have normal conversations with the AI
- The AI can suggest commands for file operations
- New code analysis features help you navigate codebases
- File paths can be relative or absolute
- Use Ctrl+C or Ctrl+D to exit
"""


def main():
    parser = argparse.ArgumentParser(
        description="Ollama CLI - Claude Code-like Interface"
    )
    parser.add_argument(
        "--model", "-m", default="gemma2:9b", help="Ollama model to use"
    )
    parser.add_argument(
        "--url", default="http://localhost:11434", help="Ollama server URL"
    )
    args = parser.parse_args()

    cli = OllamaCLI(model=args.model, base_url=args.url)
    cli.interactive_mode()


if __name__ == "__main__":
    main()
