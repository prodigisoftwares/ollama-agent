"""
AI response processing and command execution
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..ai.client import OllamaClient
    from ..code_analysis import CodeSearcher, FunctionFinder, ImportFinder, TodoFinder
    from ..commands.executor import CommandExecutor
    from ..file_ops import DirectoryNavigator, FileReader, FileWriter


class ResponseProcessor:
    def __init__(
        self,
        ai_client: "OllamaClient",
        command_executor: "CommandExecutor",
        file_reader: "FileReader",
        file_writer: "FileWriter",
        directory_navigator: "DirectoryNavigator",
        code_searcher: "CodeSearcher",
        function_finder: "FunctionFinder",
        todo_finder: "TodoFinder",
        import_finder: "ImportFinder",
    ):
        self.ai_client = ai_client
        self.command_executor = command_executor
        self.file_reader = file_reader
        self.file_writer = file_writer
        self.directory_navigator = directory_navigator
        self.code_searcher = code_searcher
        self.function_finder = function_finder
        self.todo_finder = todo_finder
        self.import_finder = import_finder

    def process_ai_response(self, response: str) -> str:
        """Process AI response and execute any commands found"""
        # Debug: print the raw response
        if "WRITE_CONTENT:" in response:
            print(f"DEBUG - Full AI response:\n{repr(response)}")

        lines = response.split("\n")
        result_parts = []

        i = 0
        while i < len(lines):
            line = lines[i]
            line = line.strip()
            if line.startswith("COMMAND: "):
                command = line[9:].strip()
                print(f"🔧 Executing: {command}")
                cmd_result = self.command_executor.run_command(command)
                result_parts.append(f"Command output:\n{cmd_result}")
            elif line.startswith("READ: "):
                file_path = line[6:].strip()
                print(f"📖 Reading: {file_path}")
                read_result = self.file_reader.read_file(file_path)
                result_parts.append(read_result)
            elif line.startswith("LS: "):
                directory = line[4:].strip() or "."
                print(f"📁 Listing: {directory}")
                ls_result = self.directory_navigator.list_files(directory)
                result_parts.append(ls_result)
            elif line.startswith("CD: "):
                directory = line[4:].strip()
                print(f"📂 Changing to: {directory}")
                cd_result, new_directory = self.directory_navigator.change_directory(
                    directory
                )  # noqa: E501
                # Update working directory for all components
                self._update_working_directory(new_directory)
                result_parts.append(cd_result)
            elif line.startswith("WRITE: "):
                file_path = line[7:].strip()
                print(f"✏️ Generating content for {file_path}")

                # Ask the AI to generate the content for this file
                content_prompt = f"Generate the content for the file {file_path}. Only output the file content, nothing else."  # noqa: E501
                generated_content = self.ai_client.chat(content_prompt)

                # Clean up the response - remove any markdown code blocks
                if generated_content.startswith("```"):
                    lines = generated_content.split("\n")
                    # Remove first and last lines if they're markdown markers
                    if lines[0].startswith("```"):
                        lines = lines[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    generated_content = "\n".join(lines)

                print(f"✏️ Writing to {file_path}")
                write_result = self.file_writer.write_file(file_path, generated_content)
                result_parts.append(write_result)
            elif line.startswith("WRITE_CONTENT: "):
                file_path = line[15:].strip()
                print(f"✏️ Writing to {file_path}")
                # Look for content between CONTENT: and END_CONTENT
                content_lines = []
                i += 1  # Move to next line
                collecting_content = False

                while i < len(lines):
                    current_line = lines[i].strip()
                    if current_line.startswith("CONTENT:"):
                        collecting_content = True
                        # Extract content from same line if present
                        content_after_colon = current_line[
                            8:
                        ].strip()  # Remove "CONTENT:"
                        if content_after_colon:
                            content_lines.append(content_after_colon)
                        i += 1
                        continue
                    elif current_line.startswith("END_CONTENT"):
                        break
                    elif collecting_content:
                        content_lines.append(lines[i])  # Keep original indentation
                    i += 1

                if content_lines:
                    content = "\n".join(content_lines)
                    write_result = self.file_writer.write_file(file_path, content)
                    result_parts.append(write_result)
                else:
                    result_parts.append("❌ No content found for WRITE_CONTENT")
            elif line.startswith("SEARCH: "):
                query = line[8:].strip()
                print(f"🔍 Searching for: {query}")
                search_result = self.code_searcher.search_code(query)
                result_parts.append(search_result)
            elif line.startswith("SEARCH_FUNC: "):
                func_name = line[13:].strip()
                print(f"🔍 Finding functions: {func_name}")
                func_result = self.function_finder.find_functions(func_name)
                result_parts.append(func_result)
            elif line.startswith("FIND_TODO:"):
                print(f"🔍 Finding TODO comments")
                todo_result = self.todo_finder.find_todos()
                result_parts.append(todo_result)
            elif line.startswith("FIND_IMPORT: "):
                import_name = line[13:].strip()
                print(f"🔍 Finding imports of: {import_name}")
                import_result = self.import_finder.find_imports(import_name)
                result_parts.append(import_result)
            elif line == "CONTENT:" or line == "END_CONTENT":
                # Skip these markers when they appear as standalone lines
                pass
            else:
                if line:  # Only add non-empty lines
                    result_parts.append(line)

            i += 1

        return "\n".join(result_parts)

    def _update_working_directory(self, new_directory: Path):
        """Update working directory for all components"""
        self.file_reader.working_directory = new_directory
        self.file_writer.working_directory = new_directory
        self.directory_navigator.working_directory = new_directory
        self.code_searcher.working_directory = new_directory
        self.function_finder.working_directory = new_directory
        self.todo_finder.working_directory = new_directory
        self.import_finder.working_directory = new_directory
        self.command_executor.working_directory = new_directory
