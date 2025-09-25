"""
Code search functionality
"""

from pathlib import Path


class CodeSearcher:
    def __init__(self, working_directory: Path):
        self.working_directory = working_directory

    def search_code(self, query: str, file_pattern: str = "*") -> str:
        """Search for code patterns in files"""
        try:
            # Handle empty or whitespace-only queries immediately
            if not query or not query.strip():
                return "Error: Search query cannot be empty"

            results = []
            search_path = self.working_directory

            # Search for different file types based on pattern
            if file_pattern == "*":
                patterns = ["*.py", "*.js", "*.ts", "*.java", "*.cpp", "*.c", "*.h"]
            else:
                patterns = [file_pattern]

            for pattern in patterns:
                for file_path in search_path.rglob(pattern):
                    if file_path.is_file():
                        try:
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()
                                lines = content.split("\n")

                            for line_num, line in enumerate(lines, 1):
                                if query.lower() in line.lower():
                                    relative_path = file_path.relative_to(search_path)
                                    results.append(
                                        f"{relative_path}:{line_num}: {line.strip()}"
                                    )
                        except Exception:
                            continue

            if results:
                # Limit to first 20 results
                return f"Search results for '{query}':\n" + "\n".join(results[:20])
            else:
                return f"No results found for '{query}'"

        except Exception as e:
            return f"Error searching code: {str(e)}"
