"""
Unit tests for ResponseProcessor class
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from ollama_cli.ai.response_processor import ResponseProcessor


class TestResponseProcessor:
    """Test cases for ResponseProcessor class"""

    @pytest.fixture
    def mock_components(self):
        """Create mock components for testing"""
        return {
            "ai_client": Mock(),
            "command_executor": Mock(),
            "file_reader": Mock(),
            "file_writer": Mock(),
            "directory_navigator": Mock(),
            "code_searcher": Mock(),
            "function_finder": Mock(),
            "todo_finder": Mock(),
            "import_finder": Mock(),
        }

    @pytest.fixture
    def processor(self, mock_components):
        """Create a ResponseProcessor instance with mocked components"""
        return ResponseProcessor(**mock_components)

    def test_init(self, mock_components):
        """Test ResponseProcessor initialization"""
        processor = ResponseProcessor(**mock_components)

        assert processor.ai_client == mock_components["ai_client"]
        assert processor.command_executor == mock_components["command_executor"]
        assert processor.file_reader == mock_components["file_reader"]
        assert processor.file_writer == mock_components["file_writer"]
        assert processor.directory_navigator == mock_components["directory_navigator"]
        assert processor.code_searcher == mock_components["code_searcher"]
        assert processor.function_finder == mock_components["function_finder"]
        assert processor.todo_finder == mock_components["todo_finder"]
        assert processor.import_finder == mock_components["import_finder"]

    def test_process_command_execution(self, processor, mock_components):
        """Test COMMAND: processing"""
        response = "COMMAND: ls -la"
        mock_components["command_executor"].run_command.return_value = (
            "file1.txt\nfile2.txt"
        )

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["command_executor"].run_command.assert_called_once_with(
            "ls -la"
        )
        mock_print.assert_called_with("🔧 Executing: ls -la")
        assert "Command output:" in result
        assert "file1.txt" in result

    def test_process_read_file(self, processor, mock_components):
        """Test READ: processing"""
        response = "READ: test.py"
        mock_components["file_reader"].read_file.return_value = "print('hello')"

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["file_reader"].read_file.assert_called_once_with("test.py")
        mock_print.assert_called_with("📖 Reading: test.py")
        assert "print('hello')" in result

    def test_process_list_directory(self, processor, mock_components):
        """Test LS: processing"""
        response = "LS: /home/user"
        mock_components["directory_navigator"].list_files.return_value = (
            "📄 file1.txt\n📁 dir1/"
        )

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)
        mock_components["directory_navigator"].list_files.assert_called_once_with(
            "/home/user"
        )
        mock_print.assert_called_with("📁 Listing: /home/user")
        assert "📄 file1.txt" in result

    def test_process_change_directory(self, processor, mock_components):
        """Test CD: processing"""
        response = "CD: /home/user"
        new_path = Path("/home/user")
        mock_components["directory_navigator"].change_directory.return_value = (
            "Changed directory to /home/user",
            new_path,
        )

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["directory_navigator"].change_directory.assert_called_once_with(
            "/home/user"
        )
        mock_print.assert_called_with("📂 Changing to: /home/user")
        assert "Changed directory to /home/user" in result

    def test_process_change_directory_updates_working_dir(
        self, processor, mock_components
    ):
        """Test CD: processing updates working directory for all components"""
        response = "CD: /home/user"
        new_path = Path("/home/user")
        mock_components["directory_navigator"].change_directory.return_value = (
            "Changed directory to /home/user",
            new_path,
        )

        processor.process_ai_response(response)

        # Verify all components got their working directory updated
        assert processor.file_reader.working_directory == new_path
        assert processor.file_writer.working_directory == new_path
        assert processor.directory_navigator.working_directory == new_path
        assert processor.code_searcher.working_directory == new_path
        assert processor.function_finder.working_directory == new_path
        assert processor.todo_finder.working_directory == new_path
        assert processor.import_finder.working_directory == new_path
        assert processor.command_executor.working_directory == new_path

    def test_process_write_ai_generated(self, processor, mock_components):
        """Test WRITE: processing with AI-generated content"""
        response = "WRITE: test.py"
        mock_components["ai_client"].chat.return_value = "print('hello world')"
        mock_components["file_writer"].write_file.return_value = (
            "File written successfully"
        )

        with patch("builtins.print") as mock_print:  # noqa: F841
            result = processor.process_ai_response(response)

        mock_components["ai_client"].chat.assert_called_once()
        mock_components["file_writer"].write_file.assert_called_once_with(
            "test.py", "print('hello world')"
        )
        assert "File written successfully" in result

    def test_process_write_ai_generated_with_markdown(self, processor, mock_components):
        """Test WRITE: processing with AI-generated content containing markdown"""
        response = "WRITE: test.py"
        mock_components["ai_client"].chat.return_value = (
            "```python\nprint('hello world')\n```"
        )
        mock_components["file_writer"].write_file.return_value = (
            "File written successfully"
        )

        processor.process_ai_response(response)

        # Verify markdown was stripped
        mock_components["file_writer"].write_file.assert_called_once_with(
            "test.py", "print('hello world')"
        )

    def test_process_write_content_inline(self, processor, mock_components):
        """Test WRITE_CONTENT: processing with inline content"""
        response = """WRITE_CONTENT: test.py
CONTENT: print('hello world')
END_CONTENT"""
        mock_components["file_writer"].write_file.return_value = (
            "File written successfully"
        )

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["file_writer"].write_file.assert_called_once_with(
            "test.py", "print('hello world')"
        )
        mock_print.assert_called_with("✏️ Writing to test.py")
        assert "File written successfully" in result

    def test_process_write_content_multiline(self, processor, mock_components):
        """Test WRITE_CONTENT: processing with multiline content"""
        response = """WRITE_CONTENT: test.py
CONTENT:
def hello():
    print('hello world')
    return True
END_CONTENT"""
        mock_components["file_writer"].write_file.return_value = (
            "File written successfully"
        )

        processor.process_ai_response(response)

        expected_content = """def hello():
    print('hello world')
    return True"""
        mock_components["file_writer"].write_file.assert_called_once_with(
            "test.py", expected_content
        )

    def test_process_write_content_no_content(self, processor, mock_components):
        """Test WRITE_CONTENT: processing with no content found"""
        response = """WRITE_CONTENT: test.py
END_CONTENT"""

        result = processor.process_ai_response(response)

        assert "❌ No content found for WRITE_CONTENT" in result
        mock_components["file_writer"].write_file.assert_not_called()

    def test_process_search_code(self, processor, mock_components):
        """Test SEARCH: processing"""
        response = "SEARCH: function_name"
        mock_components["code_searcher"].search_code.return_value = (
            "Found in file.py:10"
        )

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["code_searcher"].search_code.assert_called_once_with(
            "function_name"
        )
        mock_print.assert_called_with("🔍 Searching for: function_name")
        assert "Found in file.py:10" in result

    def test_process_search_functions(self, processor, mock_components):
        """Test SEARCH_FUNC: processing"""
        response = "SEARCH_FUNC: main"
        mock_components["function_finder"].find_functions.return_value = "def main():"

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["function_finder"].find_functions.assert_called_once_with(
            "main"
        )
        mock_print.assert_called_with("🔍 Finding functions: main")
        assert "def main():" in result

    def test_process_find_todos(self, processor, mock_components):
        """Test FIND_TODO: processing"""
        response = "FIND_TODO:"
        mock_components["todo_finder"].find_todos.return_value = "TODO: Fix this bug"

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["todo_finder"].find_todos.assert_called_once()
        mock_print.assert_called_with("🔍 Finding TODO comments")
        assert "TODO: Fix this bug" in result

    def test_process_find_imports(self, processor, mock_components):
        """Test FIND_IMPORT: processing"""
        response = "FIND_IMPORT: requests"
        mock_components["import_finder"].find_imports.return_value = "import requests"

        with patch("builtins.print") as mock_print:
            result = processor.process_ai_response(response)

        mock_components["import_finder"].find_imports.assert_called_once_with(
            "requests"
        )
        mock_print.assert_called_with("🔍 Finding imports of: requests")
        assert "import requests" in result

    def test_process_mixed_response(self, processor, mock_components):
        """Test processing response with multiple commands"""
        response = """Here is some text
COMMAND: ls
READ: file.py
More text here"""

        mock_components["command_executor"].run_command.return_value = "file1.txt"
        mock_components["file_reader"].read_file.return_value = "print('test')"

        with patch("builtins.print"):
            result = processor.process_ai_response(response)

        assert "Here is some text" in result
        assert "Command output:" in result
        assert "file1.txt" in result
        assert "print('test')" in result
        assert "More text here" in result

    def test_process_empty_lines_filtered(self, processor):
        """Test that empty lines are filtered out"""
        response = """
Line 1

Line 3
"""
        result = processor.process_ai_response(response)

        result.split("\n")
        # Should only contain non-empty lines
        assert "Line 1" in result
        assert "Line 3" in result
        # Empty lines should be filtered out
        assert result.count("\n") == 1  # Only one newline between the two lines

    def test_process_content_markers_filtered(self, processor):
        """Test that standalone CONTENT: and END_CONTENT markers are filtered"""
        response = """Text before
CONTENT:
Some content
END_CONTENT
Text after"""

        result = processor.process_ai_response(response)

        assert "Text before" in result
        assert "Some content" in result
        assert "Text after" in result
        assert "CONTENT:" not in result
        assert "END_CONTENT" not in result

    def test_debug_output_for_write_content(self, processor, mock_components):
        """Test that debug output is printed for WRITE_CONTENT commands"""
        response = "WRITE_CONTENT: test.py\nCONTENT: hello\nEND_CONTENT"
        mock_components["file_writer"].write_file.return_value = "Success"

        with patch("builtins.print") as mock_print:
            processor.process_ai_response(response)

        # Check if debug print was called
        debug_calls = [
            call
            for call in mock_print.call_args_list
            if "DEBUG - Full AI response:" in str(call)
        ]
        assert len(debug_calls) == 1

    def test_update_working_directory(self, processor, mock_components):
        """Test _update_working_directory method"""
        new_path = Path("/new/path")

        processor._update_working_directory(new_path)

        assert processor.file_reader.working_directory == new_path
        assert processor.file_writer.working_directory == new_path
        assert processor.directory_navigator.working_directory == new_path
        assert processor.code_searcher.working_directory == new_path
        assert processor.function_finder.working_directory == new_path
        assert processor.todo_finder.working_directory == new_path
        assert processor.import_finder.working_directory == new_path
        assert processor.command_executor.working_directory == new_path


class TestResponseProcessorEdgeCases:
    """Test edge cases and error conditions"""

    @pytest.fixture
    def processor_with_mocks(self):
        """Create processor with mock components for edge case testing"""
        mock_components = {
            "ai_client": Mock(),
            "command_executor": Mock(),
            "file_reader": Mock(),
            "file_writer": Mock(),
            "directory_navigator": Mock(),
            "code_searcher": Mock(),
            "function_finder": Mock(),
            "todo_finder": Mock(),
            "import_finder": Mock(),
        }
        return ResponseProcessor(**mock_components), mock_components

    def test_malformed_write_content(self, processor_with_mocks):
        """Test handling of malformed WRITE_CONTENT blocks"""
        processor, mock_components = processor_with_mocks
        mock_components["file_writer"].write_file.return_value = (
            "File written successfully"
        )

        # Missing END_CONTENT
        response = """WRITE_CONTENT: test.py
CONTENT: some content"""

        processor.process_ai_response(response)

        # Should still write the content even without END_CONTENT
        mock_components["file_writer"].write_file.assert_called_once_with(
            "test.py", "some content"
        )

    def test_write_content_with_indentation_preserved(self, processor_with_mocks):
        """Test that indentation is preserved in WRITE_CONTENT"""
        processor, mock_components = processor_with_mocks
        mock_components["file_writer"].write_file.return_value = "Success"

        response = """WRITE_CONTENT: test.py
CONTENT:
    def function():
        print("indented")
        if True:
            return "nested"
END_CONTENT"""

        processor.process_ai_response(response)

        expected_content = """    def function():
        print("indented")
        if True:
            return "nested\""""
        mock_components["file_writer"].write_file.assert_called_once_with(
            "test.py", expected_content
        )

    def test_markdown_cleanup_edge_cases(self, processor_with_mocks):
        """Test edge cases in markdown cleanup for WRITE: commands"""
        processor, mock_components = processor_with_mocks
        mock_components["file_writer"].write_file.return_value = "Success"

        # Test with only opening markdown
        mock_components["ai_client"].chat.return_value = "```python\nprint('test')"
        processor.process_ai_response("WRITE: test.py")
        mock_components["file_writer"].write_file.assert_called_with(
            "test.py", "print('test')"
        )

        # Reset and test with only closing markdown (on separate line)
        mock_components["file_writer"].write_file.reset_mock()
        mock_components["ai_client"].chat.return_value = "```python\nprint('test')\n```"
        processor.process_ai_response("WRITE: test2.py")
        mock_components["file_writer"].write_file.assert_called_with(
            "test2.py", "print('test')"
        )

        # Test with closing markdown that won't be stripped (not on separate line)
        mock_components["file_writer"].write_file.reset_mock()
        mock_components["ai_client"].chat.return_value = "print('test')```"
        processor.process_ai_response("WRITE: test3.py")
        mock_components["file_writer"].write_file.assert_called_with(
            "test3.py", "print('test')```"
        )

    def test_command_stripping_whitespace(self, processor_with_mocks):
        """Test that commands properly strip whitespace"""
        processor, mock_components = processor_with_mocks
        mock_components["command_executor"].run_command.return_value = "output"

        response = "COMMAND:   ls -la   "

        with patch("builtins.print"):
            processor.process_ai_response(response)

        mock_components["command_executor"].run_command.assert_called_once_with(
            "ls -la"
        )
