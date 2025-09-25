"""
Tests for the help system
"""

from ollama_cli.core.help import HelpSystem


class TestHelpSystem:
    """Test cases for the HelpSystem class"""

    def test_initialization(self):
        """Test help system initialization"""
        help_system = HelpSystem()

        assert help_system.commands is not None
        assert help_system.examples is not None
        assert help_system.tips is not None
        assert len(help_system.commands) > 0
        assert len(help_system.examples) > 0
        assert len(help_system.tips) > 0

    def test_overview_help(self):
        """Test overview help generation"""
        help_system = HelpSystem()
        overview = help_system.get_overview_help()

        assert isinstance(overview, str)
        assert "Ollama CLI" in overview
        assert "📁 File Operations" in overview
        assert "🔍 Code Analysis" in overview
        assert "/read" in overview
        assert "/search" in overview
        assert "/help" in overview
        assert "💡 Quick Tips" in overview

    def test_command_help_valid(self):
        """Test help for valid commands"""
        help_system = HelpSystem()

        # Test a few key commands
        for command in ["read", "search", "help", "models"]:
            help_text = help_system.get_command_help(command)
            assert isinstance(help_text, str)
            assert f"Help for /{command}" in help_text
            assert "Description:" in help_text
            assert "Usage:" in help_text

    def test_command_help_invalid(self):
        """Test help for invalid commands"""
        help_system = HelpSystem()
        help_text = help_system.get_command_help("nonexistent")

        assert isinstance(help_text, str)
        assert "Unknown command" in help_text
        assert "Type /help" in help_text

    def test_examples_help(self):
        """Test examples help"""
        help_system = HelpSystem()
        examples = help_system.get_examples_help()

        assert isinstance(examples, str)
        assert "Usage Examples" in examples
        assert "exploring" in examples.lower() and "codebase" in examples.lower()
        assert "/ls" in examples
        assert "/find-func" in examples

    def test_tips_help(self):
        """Test tips help"""
        help_system = HelpSystem()
        tips = help_system.get_tips_help()

        assert isinstance(tips, str)
        assert "Tips & Tricks" in tips
        assert "⌨️ Keyboard Shortcuts" in tips
        assert "arrow" in tips.lower()
        assert "Ctrl" in tips

    def test_search_help(self):
        """Test help search functionality"""
        help_system = HelpSystem()

        # Test searching for file-related commands
        results = help_system.search_help("file")
        assert isinstance(results, list)
        assert "read" in results
        assert "write" in results

        # Test searching for search-related commands
        results = help_system.search_help("search")
        assert "search" in results

        # Test case insensitive search
        results = help_system.search_help("SEARCH")
        assert "search" in results

    def test_contextual_help(self):
        """Test contextual help"""
        help_system = HelpSystem()

        # Test different error types
        file_help = help_system.get_contextual_help("file_not_found")
        assert "File not found" in file_help
        assert "/ls" in file_help

        cmd_help = help_system.get_contextual_help("command_not_found")
        assert "Command not recognized" in cmd_help
        assert "/help" in cmd_help

        model_help = help_system.get_contextual_help("model_error")
        assert "Model issues" in model_help
        assert "/models" in model_help

        # Test default help
        default_help = help_system.get_contextual_help()
        assert isinstance(default_help, str)
        assert "help" in default_help.lower()

    def test_command_coverage(self):
        """Test that all expected commands are documented"""
        help_system = HelpSystem()

        expected_commands = [
            "read",
            "write",
            "ls",
            "cd",
            "search",
            "find-func",
            "find-todo",
            "find-import",
            "run",
            "models",
            "model",
            "clear",
            "clear-history",
            "cls",
            "help",
            "exit",
        ]

        for command in expected_commands:
            assert (
                command in help_system.commands
            ), f"Command '{command}' not documented"

        # Test that each command has required fields
        for command, info in help_system.commands.items():
            assert "description" in info, f"Command '{command}' missing description"
            assert "usage" in info, f"Command '{command}' missing usage"
            assert "examples" in info, f"Command '{command}' missing examples"

    def test_help_content_quality(self):
        """Test the quality and consistency of help content"""
        help_system = HelpSystem()

        # Test that all commands have meaningful descriptions
        for command, info in help_system.commands.items():
            desc = info["description"]
            assert len(desc) > 10, f"Command '{command}' has too short description"
            assert not desc.endswith(
                "."
            ), f"Command '{command}' description shouldn't end with period"

            # Test usage format
            usage = info["usage"]
            assert usage.startswith(
                f"/{command}"
            ), f"Command '{command}' usage doesn't start with command name"

            # Test examples exist and are realistic
            examples = info["examples"]
            assert len(examples) > 0, f"Command '{command}' has no examples"
            for example in examples:
                assert example.startswith(
                    f"/{command}"
                ), f"Command '{command}' example doesn't start with command"
