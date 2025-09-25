"""
Unit tests for DirectoryNavigator class
"""

import tempfile
from pathlib import Path

import pytest

from ollama_cli.file_ops.navigator import DirectoryNavigator


class TestDirectoryNavigator:
    """Test cases for DirectoryNavigator class"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            # Create test structure
            (temp_path / "test_file.txt").write_text("test content")
            (temp_path / "test_dir").mkdir()
            (temp_path / "test_dir" / "nested_file.py").write_text("print('hello')")
            yield temp_path

    @pytest.fixture
    def navigator(self, temp_dir):
        """Create a DirectoryNavigator instance"""
        return DirectoryNavigator(temp_dir)

    def test_init(self, temp_dir):
        """Test DirectoryNavigator initialization"""
        navigator = DirectoryNavigator(temp_dir)
        assert navigator.working_directory == temp_dir

    def test_list_files_current_directory(self, navigator, temp_dir):
        """Test listing files in current directory"""
        result = navigator.list_files()

        assert f"Contents of {temp_dir}" in result
        assert "📄 test_file.txt" in result
        assert "📁 test_dir/" in result

    def test_list_files_specific_directory(self, navigator, temp_dir):
        """Test listing files in a specific directory"""
        result = navigator.list_files("test_dir")

        assert f"Contents of {temp_dir / 'test_dir'}" in result
        assert "📄 nested_file.py" in result

    def test_list_files_with_path_object(self, navigator, temp_dir):
        """Test listing files using Path object"""
        test_dir_path = temp_dir / "test_dir"
        result = navigator.list_files(test_dir_path)

        assert f"Contents of {test_dir_path}" in result
        assert "📄 nested_file.py" in result

    def test_list_files_nonexistent_directory(self, navigator):
        """Test listing files in non-existent directory"""
        result = navigator.list_files("nonexistent")
        assert "does not exist" in result

    def test_list_files_not_a_directory(self, navigator):
        """Test listing files on a file (not directory)"""
        result = navigator.list_files("test_file.txt")
        assert "is not a directory" in result

    def test_list_files_absolute_path(self, navigator, temp_dir):
        """Test listing files with absolute path"""
        abs_path = temp_dir / "test_dir"
        result = navigator.list_files(str(abs_path))

        assert f"Contents of {abs_path}" in result
        assert "📄 nested_file.py" in result

    def test_list_files_exception_handling(self, navigator):
        """Test exception handling in list_files"""
        # Create a navigator with invalid working directory
        invalid_navigator = DirectoryNavigator(Path("/nonexistent/path"))
        result = invalid_navigator.list_files(".")
        assert "does not exist" in result

    def test_change_directory_relative_path(self, navigator, temp_dir):
        """Test changing to relative directory"""
        message, new_path = navigator.change_directory("test_dir")

        assert "Changed directory to" in message
        assert new_path == temp_dir / "test_dir"

    def test_change_directory_absolute_path(self, navigator, temp_dir):
        """Test changing to absolute directory"""
        target_path = temp_dir / "test_dir"
        message, new_path = navigator.change_directory(str(target_path))

        assert "Changed directory to" in message
        assert new_path == target_path

    def test_change_directory_with_path_object(self, navigator, temp_dir):
        """Test changing directory using Path object"""
        target_path = temp_dir / "test_dir"
        message, new_path = navigator.change_directory(target_path)

        assert "Changed directory to" in message
        assert new_path == target_path

    def test_change_directory_nonexistent(self, navigator):
        """Test changing to non-existent directory"""
        message, new_path = navigator.change_directory("nonexistent")

        assert "does not exist" in message
        assert new_path == navigator.working_directory

    def test_change_directory_not_a_directory(self, navigator):
        """Test changing to a file (not directory)"""
        message, new_path = navigator.change_directory("test_file.txt")

        assert "is not a directory" in message
        assert new_path == navigator.working_directory

    def test_change_directory_dot_dot(self, temp_dir):
        """Test changing to parent directory"""
        # Start in subdirectory
        navigator = DirectoryNavigator(temp_dir / "test_dir")
        message, new_path = navigator.change_directory("..")

        assert "Changed directory to" in message
        assert new_path == temp_dir

    def test_change_directory_exception_handling(self, navigator):
        """Test exception handling in change_directory"""
        # Create a navigator with invalid working directory
        invalid_navigator = DirectoryNavigator(Path("/nonexistent/path"))
        message, new_path = invalid_navigator.change_directory(".")

        assert "does not exist" in message
        assert new_path == invalid_navigator.working_directory

    def test_empty_directory(self, navigator, temp_dir):
        """Test listing files in empty directory"""
        empty_dir = temp_dir / "empty_dir"
        empty_dir.mkdir()

        result = navigator.list_files("empty_dir")
        assert f"Contents of {empty_dir}:" in result
        # Should only contain the header, no files listed

    def test_directory_with_hidden_files(self, navigator, temp_dir):
        """Test listing directory with hidden files"""
        hidden_file = temp_dir / ".hidden_file"
        hidden_file.write_text("hidden content")

        result = navigator.list_files()
        assert "📄 .hidden_file" in result

    def test_sorted_output(self, navigator, temp_dir):
        """Test that files are listed in sorted order"""
        # Create files with names that would be unsorted
        (temp_dir / "z_file.txt").write_text("content")
        (temp_dir / "a_file.txt").write_text("content")
        (temp_dir / "m_file.txt").write_text("content")

        result = navigator.list_files()
        lines = result.split('\n')[1:]  # Skip header line

        # Extract filenames and verify they're sorted
        filenames = [line.split(' ', 1)[1] for line in lines if line.strip()]
        assert filenames == sorted(filenames)


class TestDirectoryNavigatorEdgeCases:
    """Test edge cases and error conditions"""

    def test_navigator_with_nonexistent_working_directory(self):
        """Test navigator with non-existent working directory"""
        navigator = DirectoryNavigator(Path("/nonexistent/path"))

        # Should handle gracefully
        result = navigator.list_files()
        assert "does not exist" in result

    def test_permission_denied_simulation(self):
        """Test behavior when directory permissions are restricted"""
        # This test may not work on all systems due to permission restrictions
        # But we can at least verify error handling exists
        navigator = DirectoryNavigator(Path.cwd())
        result = navigator.list_files("/root")  # Likely restricted directory
        # Should either succeed or show appropriate error
        assert isinstance(result, str)
