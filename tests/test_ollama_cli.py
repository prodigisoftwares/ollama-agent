"""
Basic tests for ollama_cli module
"""

from pathlib import Path

from ollama_cli import OllamaCLI


class TestOllamaCLI:
    """Test cases for OllamaCLI class"""

    def test_init(self):
        """Test CLI initialization"""
        cli = OllamaCLI()
        assert cli.model == "gemma2:9b"
        assert cli.base_url == "http://localhost:11434"
        assert cli.conversation_history == []
        assert isinstance(cli.working_directory, Path)

    def test_init_with_custom_params(self):
        """Test CLI initialization with custom parameters"""
        cli = OllamaCLI(model="custom:model", base_url="http://example.com")
        assert cli.model == "custom:model"
        assert cli.base_url == "http://example.com"

    def test_search_code_basic(self):
        """Test basic code search functionality"""
        cli = OllamaCLI()
        result = cli.search_code("def")
        assert isinstance(result, str)
        assert "Search results for 'def'" in result or "No results found" in result

    def test_find_functions_basic(self):
        """Test basic function finding"""
        cli = OllamaCLI()
        result = cli.find_functions()
        assert isinstance(result, str)
        assert (
            "Functions/Classes found" in result
            or "No functions/classes found" in result
        )

    def test_find_todos_basic(self):
        """Test basic TODO finding"""
        cli = OllamaCLI()
        result = cli.find_todos()
        assert isinstance(result, str)
        assert "TODO comments found" in result or "No TODO comments found" in result

    def test_find_imports_basic(self):
        """Test basic import finding"""
        cli = OllamaCLI()
        result = cli.find_imports("requests")
        assert isinstance(result, str)
        assert (
            "Files importing 'requests'" in result
            or "No files found importing" in result
        )

    def test_get_help_text(self):
        """Test help text generation"""
        cli = OllamaCLI()
        help_text = cli.get_help_text()
        assert isinstance(help_text, str)
        assert "Ollama CLI Help" in help_text
        assert "/search" in help_text
        assert "/find-func" in help_text
        assert "/find-todo" in help_text
        assert "/find-import" in help_text

    def test_get_system_prompt(self):
        """Test system prompt generation"""
        cli = OllamaCLI()
        prompt = cli.get_system_prompt()
        assert isinstance(prompt, str)
        assert "AI assistant" in prompt
        assert "SEARCH:" in prompt
        assert "FIND_TODO:" in prompt


class TestSearchFunctionality:
    """Test search functionality with edge cases"""

    def test_search_empty_query(self):
        """Test search with empty query"""
        cli = OllamaCLI()
        result = cli.search_code("")
        assert isinstance(result, str)

    def test_find_functions_with_filter(self):
        """Test finding functions with name filter"""
        cli = OllamaCLI()
        result = cli.find_functions("main")
        assert isinstance(result, str)

    def test_find_imports_nonexistent(self):
        """Test finding imports for non-existent module"""
        cli = OllamaCLI()
        result = cli.find_imports("nonexistent_module_12345")
        assert "No files found importing" in result
