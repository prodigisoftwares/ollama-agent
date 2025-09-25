"""
Import analysis functionality
"""

from pathlib import Path


class ImportFinder:
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def find_imports(self, import_name: str) -> str:
        """Find files that import a specific module"""
        try:
            results = []
            search_path = self.working_directory

            for file_path in search_path.rglob("*.py"):
                if file_path.is_file():
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                            lines = content.split("\n")

                        for line_num, line in enumerate(lines, 1):
                            if (
                                "import " + import_name in line
                                or "from " + import_name in line
                            ):
                                relative_path = file_path.relative_to(search_path)
                                results.append(
                                    f"{relative_path}:{line_num}: {line.strip()}"
                                )
                    except Exception:
                        continue

            if results:
                return f"Files importing '{import_name}':\n" + "\n".join(results)
            else:
                return f"No files found importing '{import_name}'"

        except Exception as e:
            return f"Error finding imports: {str(e)}"
