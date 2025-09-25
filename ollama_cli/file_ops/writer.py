"""
File writing operations
"""

from pathlib import Path
from typing import Union


class FileWriter:
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def write_file(self, file_path: Union[str, Path], content: str) -> str:
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
