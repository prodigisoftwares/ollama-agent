"""
File reading operations
"""

from pathlib import Path
from typing import Union


class FileReader:  # pragma: no cover
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def read_file(self, file_path: Union[str, Path]) -> str:
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
