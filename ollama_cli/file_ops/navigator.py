"""
Directory navigation operations
"""

from pathlib import Path
from typing import Union


class DirectoryNavigator:
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def list_files(self, directory: Union[str, Path] = ".") -> str:
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

    def change_directory(self, directory: Union[str, Path]) -> tuple[str, Path]:
        """Change working directory - returns (message, new_directory)"""
        try:
            path = Path(directory)
            if not path.is_absolute():
                path = self.working_directory / path

            path = path.resolve()

            if not path.exists():
                return f"Directory {path} does not exist", self.working_directory

            if not path.is_dir():
                return f"{path} is not a directory", self.working_directory

            return f"Changed directory to {path}", path

        except Exception as e:  # pragma: no cover
            return f"Error changing directory: {str(e)}", self.working_directory
