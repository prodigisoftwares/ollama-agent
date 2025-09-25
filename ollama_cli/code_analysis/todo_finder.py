"""
TODO comment finder
"""

import re
from pathlib import Path


class TodoFinder:
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

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
