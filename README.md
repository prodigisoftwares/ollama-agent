# Ollama Agent

An intelligent agent CLI for Ollama that provides natural language interaction with your local AI models, similar to Claude Code.

## Overview

Ollama Agent bridges the gap between conversational AI and system operations, allowing you to interact with your locally-hosted Ollama models in a way similar to Claude Code. It combines chat functionality with direct system integration, enabling file operations, command execution, and directory navigation through natural language requests.

## Features

- **Interactive Chat Interface**: Natural conversation with any Ollama model
- **Direct Command Execution**: Ask "run ls -al" and it executes automatically
- **File Operations**: Read and write files through conversation
- **Directory Navigation**: Change directories and list contents
- **Model Management**: Switch between available Ollama models
- **Conversation History**: Maintains context throughout your session
- **Slash Commands**: Traditional command interface for direct control
- **Code Analysis Tools**: Search code patterns, find functions/classes, TODO comments, and imports

## Requirements

- Python 3.12+
- Ollama installed and running locally
- At least one Ollama model downloaded

## Installation

1. Clone or download this project
2. Install dependencies:
   ```bash
   uv add requests
   ```
3. Make the script executable:
   ```bash
   chmod +x ollama_cli.py
   ```

## Usage

### Basic Usage

Run the CLI directly:
```bash
./ollama_cli.py
```

Or with Python:
```bash
uv run python ollama_cli.py
```

### Command Line Options

```bash
./ollama_cli.py --model codestral:22b    # Use specific model
./ollama_cli.py --url http://localhost:11434  # Custom Ollama URL
./ollama_cli.py --help                   # Show help
```

### Natural Language Commands

The AI understands and executes natural language requests:

- **"run ls -al"** - Executes shell commands
- **"read config.py"** - Displays file contents
- **"list the files in src/"** - Shows directory contents
- **"change to the src directory"** - Changes working directory
- **"show me the current directory"** - Displays current path

### Slash Commands

For direct control, use slash commands:

- `/run <command>` - Execute shell command
- `/read <file>` - Read file contents
- `/write <file>` - Write to file (prompts for content)
- `/ls [directory]` - List files in directory
- `/cd <directory>` - Change working directory
- `/models` - List available Ollama models
- `/model <name>` - Switch to different model
- `/search <query>` - Search for code patterns in files
- `/find-func [name]` - Find function/class definitions (optional name filter)
- `/find-todo` - Find TODO comments in the codebase
- `/find-import <module>` - Find files that import a specific module
- `/clear` - Clear conversation history
- `/help` - Show help information
- `/exit` - Exit the program

## Examples

### File Operations
```
You: Can you show me what's in the config file?
AI: READ: config.py
[File contents displayed]

You: /write settings.json
[Prompts for content, then writes file]
```

### Command Execution
```
You: What Python files are in this directory?
AI: COMMAND: find . -name "*.py"
[Command output displayed]

You: /run git status
[Git status output displayed]
```

### Model Management
```
You: /models
Available models:
  " gemma2:9b (current)
  " codestral:22b
  " llama3.2:latest

You: /model codestral:22b
Switched to model: codestral:22b
```

### Code Analysis
```
You: /search "def main"
Search results for 'def main':
  ollama_cli.py:612: def main():

You: /find-func search
Functions/Classes found:
  ollama_cli/code_analysis/searcher.py:12: class CodeSearcher:

You: /find-todo
TODO comments found:
  src/utils.py:25: # TODO: Add error handling

You: /find-import requests
Files importing 'requests':
  ollama_cli/ai/client.py:6: import requests
```

## Configuration

Ollama Agent uses these defaults:
- **Model**: gemma2:9b (or first available model)
- **Ollama URL**: http://localhost:11434
- **Working Directory**: Current directory where script is run

All can be overridden via command line options.

## How It Works

1. **Natural Language Processing**: The AI is trained to recognize requests for system operations
2. **Command Translation**: Requests are translated to structured commands (COMMAND:, READ:, etc.)
3. **Automatic Execution**: The agent detects these patterns and executes them automatically
4. **Result Integration**: Command outputs are integrated into the conversation flow

## Project Structure

```
agent/
├── ollama_cli.py              # Main CLI entry point
├── ollama_cli/                # Package modules
│   ├── core/                  # Core CLI functionality
│   ├── ai/                    # AI integration and communication
│   ├── file_ops/             # File operations (read, write, navigate)
│   ├── code_analysis/        # Code analysis tools
│   └── commands/             # Command execution
├── tests/                     # Test suite
├── pyproject.toml            # Project configuration and dependencies
├── README.md                 # This file
├── DEVELOPMENT.md            # Developer documentation
├── .gitignore               # Git ignore patterns
└── uv.lock                  # Dependency lock file
```

## Development

This project uses `uv` for dependency management. For detailed development information, see [DEVELOPMENT.md](DEVELOPMENT.md).

```bash
# Add new dependency
uv add package_name

# Run script with dependencies
uv run python ollama_cli.py

# Run tests
python -m pytest tests/ -v

# Install as editable package
uv pip install -e .
```

## Limitations

- Commands have a 30-second timeout
- File operations use UTF-8 encoding
- Requires Ollama server to be running locally
- Some models may not follow the command format consistently

## Troubleshooting

**"No module named 'requests'"**
- Install dependencies with `uv add requests`

**"Error communicating with Ollama"**
- Ensure Ollama is running: `ollama serve`
- Check if models are available: `ollama list`

**AI not executing commands**
- Try using slash commands instead: `/run ls`
- Some models may need explicit instruction to use command formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with multiple Ollama models
5. Submit a pull request

## License

This project is open source. Use and modify as needed.
