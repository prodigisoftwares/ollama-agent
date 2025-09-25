"""
Main CLI class orchestrating all components
"""

import shlex
import sys
from pathlib import Path
from typing import List

from ..ai import OllamaClient, PromptManager, ResponseProcessor
from ..code_analysis import CodeSearcher, FunctionFinder, ImportFinder, TodoFinder
from ..commands import CommandExecutor
from ..file_ops import DirectoryNavigator, FileReader, FileWriter


class OllamaCLI:
    def __init__(
        self, model: str = "gemma2:9b", base_url: str = "http://localhost:11434"
    ):
        self.working_directory = Path.cwd()

        # Initialize all components
        self.ai_client = OllamaClient(model, base_url)
        self.prompt_manager = PromptManager(self.working_directory)
        self.command_executor = CommandExecutor(self.working_directory)

        # File operations
        self.file_reader = FileReader(self.working_directory)
        self.file_writer = FileWriter(self.working_directory)
        self.directory_navigator = DirectoryNavigator(self.working_directory)

        # Code analysis
        self.code_searcher = CodeSearcher(self.working_directory)
        self.function_finder = FunctionFinder(self.working_directory)
        self.todo_finder = TodoFinder(self.working_directory)
        self.import_finder = ImportFinder(self.working_directory)

        # Response processor
        self.response_processor = ResponseProcessor(
            self.ai_client,
            self.command_executor,
            self.file_reader,
            self.file_writer,
            self.directory_navigator,
            self.code_searcher,
            self.function_finder,
            self.todo_finder,
            self.import_finder,
        )

    @property
    def model(self) -> str:
        """Get current model"""
        return self.ai_client.model

    @property
    def base_url(self) -> str:
        """Get Ollama base URL"""
        return self.ai_client.base_url

    @property
    def conversation_history(self) -> List[dict]:
        """Get conversation history"""
        return self.ai_client.conversation_history

    def list_models(self) -> List[str]:
        """List available Ollama models"""
        return self.ai_client.list_models()

    def chat(self, message: str, system_prompt: str = None) -> str:
        """Send a chat message to Ollama"""
        return self.ai_client.chat(message, system_prompt)

    def read_file(self, file_path: str) -> str:
        """Read a file and return its contents"""
        return self.file_reader.read_file(file_path)

    def write_file(self, file_path: str, content: str) -> str:
        """Write content to a file"""
        return self.file_writer.write_file(file_path, content)

    def run_command(self, command: str) -> str:
        """Execute a shell command"""
        return self.command_executor.run_command(command)

    def list_files(self, directory: str = ".") -> str:
        """List files in a directory"""
        return self.directory_navigator.list_files(directory)

    def change_directory(self, directory: str) -> str:
        """Change working directory"""
        cd_result, new_directory = self.directory_navigator.change_directory(directory)
        if new_directory != self.working_directory:
            self.working_directory = new_directory
            self._update_all_working_directories(new_directory)
        return cd_result

    def search_code(self, query: str, file_pattern: str = "*") -> str:
        """Search for code patterns in files"""
        return self.code_searcher.search_code(query, file_pattern)

    def find_functions(
        self, function_name: str = "", file_pattern: str = "*.py"
    ) -> str:
        """Find function definitions"""
        return self.function_finder.find_functions(function_name, file_pattern)

    def find_todos(self) -> str:
        """Find TODO comments in the codebase"""
        return self.todo_finder.find_todos()

    def find_imports(self, import_name: str) -> str:
        """Find files that import a specific module"""
        return self.import_finder.find_imports(import_name)

    def get_system_prompt(self) -> str:
        """Get the system prompt for the AI assistant"""
        return self.prompt_manager.get_system_prompt()

    def process_ai_response(self, response: str) -> str:
        """Process AI response and execute any commands found"""
        return self.response_processor.process_ai_response(response)

    def _update_all_working_directories(self, new_directory: Path):
        """Update working directory for all components"""
        self.prompt_manager.working_directory = new_directory
        self.command_executor.working_directory = new_directory
        self.file_reader.working_directory = new_directory
        self.file_writer.working_directory = new_directory
        self.directory_navigator.working_directory = new_directory
        self.code_searcher.working_directory = new_directory
        self.function_finder.working_directory = new_directory
        self.todo_finder.working_directory = new_directory
        self.import_finder.working_directory = new_directory

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
                        self.ai_client.clear_conversation()
                        print("🧹 Conversation history cleared")
                    elif command == "cls":
                        # Clear terminal screen
                        print("\033[H\033[2J\033[3J", end="", flush=True)
                        # Clear conversation history
                        self.ai_client.clear_conversation()
                        # Show welcome message again
                        print(f"🤖 Ollama CLI - Claude Code-like Interface")
                        print(f"Model: {self.model}")
                        print(f"Working Directory: {self.working_directory}")
                        print(f"Type /help for commands or start chatting!\n")
                    elif command == "models":
                        models = self.list_models()
                        print("Available models:")
                        for model in models:
                            marker = " 👈 (current)" if model == self.model else ""
                            print(f"  • {model}{marker}")
                    elif command == "model" and args:
                        self.ai_client.set_model(args[0])
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
  /cls                  - Clear screen and conversation history
  /help                 - Show this help
  /exit                 - Exit the program

💡 Tips:
- You can have normal conversations with the AI
- The AI can suggest commands for file operations
- New code analysis features help you navigate codebases
- File paths can be relative or absolute
- Use Ctrl+C or Ctrl+D to exit
"""
