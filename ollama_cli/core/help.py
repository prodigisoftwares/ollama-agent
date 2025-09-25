"""
Comprehensive help system for Ollama CLI
"""

from typing import Dict, List


class HelpSystem:
    """Manages help content and documentation for the CLI"""

    def __init__(self):
        self.commands = self._init_commands()
        self.examples = self._init_examples()
        self.tips = self._init_tips()

    def _init_commands(self) -> Dict[str, Dict[str, str]]:
        """Initialize command documentation"""
        return {
            # File Operations
            "read": {
                "description": "Read and display a file's contents",
                "usage": "/read <file_path>",
                "examples": [
                    "/read main.py",
                    "/read config/settings.json",
                    "/read ../README.md",
                ],
                "notes": "Supports relative and absolute paths",
            },
            "write": {
                "description": "Write content to a file (interactive mode)",
                "usage": "/write <file_path>",
                "examples": ["/write test.py", "/write docs/api.md"],
                "notes": "Enter content, then Ctrl+D to finish. Ctrl+C to cancel.",
            },
            # Directory Operations
            "ls": {
                "description": "List files and directories",
                "usage": "/ls [directory]",
                "examples": ["/ls", "/ls src/", "/ls /home/user/projects"],
                "notes": "Defaults to current directory if no path specified",
            },
            "cd": {
                "description": "Change working directory",
                "usage": "/cd <directory>",
                "examples": ["/cd src", "/cd ..", "/cd /absolute/path"],
                "notes": "Updates working directory for all operations",
            },
            # Code Analysis
            "search": {
                "description": "Search for code patterns in files",
                "usage": "/search <query>",
                "examples": [
                    "/search function main",
                    "/search import requests",
                    "/search TODO",
                    "/search class.*Exception",
                ],
                "notes": "Supports regex patterns. Searches all readable files.",
            },
            "find-func": {
                "description": "Find function and class definitions",
                "usage": "/find-func [name]",
                "examples": ["/find-func", "/find-func main", "/find-func Calculator"],
                "notes": "Without name, shows all functions. Primarily for Python files.",  # noqa: E501
            },
            "find-todo": {
                "description": "Find TODO comments in codebase",
                "usage": "/find-todo",
                "examples": ["/find-todo"],
                "notes": "Searches for TODO, FIXME, HACK, NOTE comments",
            },
            "find-import": {
                "description": "Find files that import a specific module",
                "usage": "/find-import <module>",
                "examples": [
                    "/find-import requests",
                    "/find-import numpy",
                    "/find-import .config",
                ],
                "notes": "Finds both direct imports and from-imports",
            },
            # Command Execution
            "run": {
                "description": "Execute shell commands",
                "usage": "/run <command>",
                "examples": ["/run ls -la", "/run python test.py", "/run git status"],
                "notes": "⚠️  Be careful with destructive commands",
            },
            # AI/Model Management
            "models": {
                "description": "List available Ollama models",
                "usage": "/models",
                "examples": ["/models"],
                "notes": "Shows all models with current model marked",
            },
            "model": {
                "description": "Switch to a different model",
                "usage": "/model <model_name>",
                "examples": ["/model codellama", "/model gemma2:9b", "/model llama3.1"],
                "notes": "Model must be available in Ollama",
            },
            # Session Management
            "clear": {
                "description": "Clear conversation history",
                "usage": "/clear",
                "examples": ["/clear"],
                "notes": "Keeps command history intact",
            },
            "clear-history": {
                "description": "Clear command input history",
                "usage": "/clear-history",
                "examples": ["/clear-history"],
                "notes": "Clears arrow-key navigation history",
            },
            "cls": {
                "description": "Clear screen and conversation history",
                "usage": "/cls",
                "examples": ["/cls"],
                "notes": "Fresh start - clears both screen and conversation",
            },
            # System
            "help": {
                "description": "Show help information",
                "usage": "/help [command]",
                "examples": ["/help", "/help search", "/help find-func"],
                "notes": "Without command, shows overview. With command, shows details.",  # noqa: E501
            },
            "exit": {
                "description": "Exit the program",
                "usage": "/exit",
                "examples": ["/exit"],
                "notes": "Also: Ctrl+C or Ctrl+D",
            },
        }

    def _init_examples(self) -> List[Dict[str, str]]:
        """Initialize usage examples"""
        return [
            {
                "scenario": "Exploring a new codebase",
                "commands": ["/ls", "/find-func", "/search main", "/find-todo"],
                "description": "Get oriented in an unfamiliar project",
            },
            {
                "scenario": "Code review workflow",
                "commands": [
                    "/search FIXME",
                    "/find-import requests",
                    "/read src/main.py",
                    "Can you review this code for potential issues?",
                ],
                "description": "Systematic code review with AI assistance",
            },
            {
                "scenario": "Debugging session",
                "commands": [
                    "/run python debug.py",
                    "/search except.*Error",
                    "/find-func handle_error",
                    "The error logs show X, what might be causing this?",
                ],
                "description": "Investigate and debug issues",
            },
            {
                "scenario": "Documentation writing",
                "commands": [
                    "/find-func public",
                    "/read api.py",
                    "/write docs/api.md",
                    "Generate API documentation for these functions",
                ],
                "description": "Create documentation with AI help",
            },
        ]

    def _init_tips(self) -> List[str]:
        """Initialize helpful tips"""
        return [
            "Use arrow keys (↑/↓) to navigate command history",
            "Tab completion works for file paths and commands",
            "Ctrl+A jumps to beginning of line, Ctrl+E to end",
            "Ctrl+K deletes from cursor to end of line",
            "You can combine slash commands with natural conversation",
            "The AI remembers context from previous commands in the session",
            "File paths can be relative (./file) or absolute (/path/to/file)",
            "Use regex patterns with /search for powerful code searching",
            "Model switching preserves conversation history",
            "Use /cls for a completely fresh start",
            "Commands are case-insensitive (/HELP works like /help)",
            "Most commands show helpful output even when no results found",
        ]

    def get_overview_help(self) -> str:
        """Get the main help overview"""
        help_text = "📖 Ollama CLI - Comprehensive Help\n\n"

        # Group commands by category
        categories = {
            "📁 File Operations": ["read", "write", "ls", "cd"],
            "🔍 Code Analysis": ["search", "find-func", "find-todo", "find-import"],
            "⚙️ Command Execution": ["run"],
            "🤖 AI/Model Management": ["models", "model"],
            "🗂️ Session Management": ["clear", "clear-history", "cls"],
            "❓ System": ["help", "exit"],
        }

        for category, commands in categories.items():
            help_text += f"{category}:\n"
            for cmd in commands:
                if cmd in self.commands:
                    cmd_info = self.commands[cmd]
                    help_text += (
                        f"  {cmd_info['usage']:<20} - {cmd_info['description']}\n"
                    )
            help_text += "\n"

        help_text += "💡 Quick Tips:\n"
        for tip in self.tips[:5]:  # Show first 5 tips
            help_text += f"• {tip}\n"

        help_text += f"\n💬 Natural Conversation:\n"
        help_text += "• Ask questions: 'What does this function do?'\n"
        help_text += "• Request actions: 'Create a test file for main.py'\n"
        help_text += "• Get suggestions: 'How can I optimize this code?'\n"
        help_text += "• Code generation: 'Write a function that sorts a list'\n\n"

        help_text += "📚 For detailed command help: /help <command>\n"
        help_text += "🚀 Quick start examples: /help examples\n"

        return help_text

    def get_command_help(self, command: str) -> str:
        """Get detailed help for a specific command"""
        command = command.lower()

        if command not in self.commands:
            return f"❓ Unknown command: {command}\nType /help to see all available commands."  # noqa: E501

        cmd_info = self.commands[command]
        help_text = f"📖 Help for /{command}\n\n"
        help_text += f"Description: {cmd_info['description']}\n"
        help_text += f"Usage: {cmd_info['usage']}\n\n"

        if cmd_info.get("examples"):
            help_text += "Examples:\n"
            for example in cmd_info["examples"]:
                help_text += f"  {example}\n"
            help_text += "\n"

        if cmd_info.get("notes"):
            help_text += f"Notes: {cmd_info['notes']}\n"

        return help_text

    def get_examples_help(self) -> str:
        """Get workflow examples"""
        help_text = "🚀 Ollama CLI - Usage Examples\n\n"

        for example in self.examples:
            help_text += f"📋 {example['scenario'].title()}:\n"
            help_text += f"{example['description']}\n\n"

            for i, cmd in enumerate(example["commands"], 1):
                if cmd.startswith("/"):
                    help_text += f"  {i}. {cmd}\n"
                else:
                    help_text += f'  {i}. "{cmd}"\n'
            help_text += "\n"

        return help_text

    def get_tips_help(self) -> str:
        """Get all tips and tricks"""
        help_text = "💡 Ollama CLI - Tips & Tricks\n\n"

        categories = {
            "⌨️ Keyboard Shortcuts": [
                "↑/↓ arrows: Navigate command history",
                "←/→ arrows: Move cursor within input",
                "Ctrl+A: Jump to beginning of line",
                "Ctrl+E: Jump to end of line",
                "Ctrl+K: Delete from cursor to end",
                "Ctrl+C or Ctrl+D: Exit program",
            ],
            "📂 File Operations": [
                "File paths can be relative (./file) or absolute (/path/to/file)",
                "Tab completion works for file paths",
                "Most commands handle missing files gracefully",
            ],
            "🔍 Search & Analysis": [
                "Use regex patterns with /search for powerful searching",
                "/search supports standard regex: *, +, ?, [], etc.",
                "/find-func without arguments shows all functions",
                "Code analysis works best with Python files",
            ],
            "🤖 AI Interaction": [
                "Ask questions in natural language",
                "The AI remembers context from the current session",
                "You can reference files by name in conversation",
                "Combine slash commands with conversation for best results",
            ],
            "⚡ Productivity": [
                "Use /cls for a completely fresh start",
                "Model switching preserves conversation history",
                "/clear only clears conversation, not command history",
                "Commands are case-insensitive",
            ],
        }

        for category, tips in categories.items():
            help_text += f"{category}:\n"
            for tip in tips:
                help_text += f"  • {tip}\n"
            help_text += "\n"

        return help_text

    def get_contextual_help(self, error_type: str = None) -> str:
        """Get contextual help based on error or situation"""
        if error_type == "file_not_found":
            return (
                "💡 File not found? Try:\n"
                "• /ls to see available files\n"
                "• Use absolute paths: /read /full/path/to/file\n"
                "• Check spelling and case sensitivity"
            )

        elif error_type == "command_not_found":
            return (
                "💡 Command not recognized? Try:\n"
                "• /help to see all commands\n"
                "• Check command spelling (case insensitive)\n"
                "• Use natural language for AI assistance"
            )

        elif error_type == "model_error":
            return (
                "💡 Model issues? Try:\n"
                "• /models to see available models\n"
                "• Check if Ollama is running\n"
                "• Verify the model name spelling"
            )

        return "💡 Type /help for assistance or ask me a question!"

    def search_help(self, query: str) -> List[str]:
        """Search help content for relevant commands"""
        query = query.lower()
        results = []

        for cmd, info in self.commands.items():
            if (
                query in cmd.lower()
                or query in info["description"].lower()
                or any(query in example.lower() for example in info.get("examples", []))
            ):
                results.append(cmd)

        return results
