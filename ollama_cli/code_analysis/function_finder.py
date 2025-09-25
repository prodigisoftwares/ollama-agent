"""
Function and class definition finder
"""

import re
from pathlib import Path


class FunctionFinder:  # pragma: no cover
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def find_functions(
        self, function_name: str = "", file_pattern: str = "*.py"
    ) -> str:
        """Find function definitions"""
        try:
            results = []
            search_path = self.working_directory

            for file_path in search_path.rglob(file_pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                        for line_num, line in enumerate(lines, 1):
                            # Look for function definitions
                            if re.match(r"\s*def\s+\w+", line):
                                if (
                                    not function_name
                                    or function_name.lower() in line.lower()
                                ):
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                            # Look for class definitions too
                            elif re.match(r"\s*class\s+\w+", line):
                                if (
                                    not function_name
                                    or function_name.lower() in line.lower()
                                ):
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                    except Exception:
                        continue

            if results:
                return f"Functions/Classes found:\n" + "\n".join(results[:20])
            else:
                return f"No functions/classes found"

        except Exception as e:
            return f"Error finding functions: {str(e)}"
