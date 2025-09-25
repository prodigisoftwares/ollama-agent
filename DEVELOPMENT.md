# Development Guide

This document contains detailed information for developers working on the Ollama CLI project.

## Recent Refactoring

The project was recently refactored from a monolithic `ollama_cli.py` file into a well-structured package. This refactoring improved:

- **Maintainability**: Separated concerns into logical modules
- **Testability**: Individual components can be tested in isolation
- **Extensibility**: Easy to add new features or modify existing ones
- **Code Organization**: Clear structure for new developers

### Migration Summary

The original 630-line monolithic file was broken down into focused modules:

**Before**: Single `ollama_cli.py` with all functionality
**After**: Organized package structure with separation of concerns

## Package Architecture

### Core Structure

```
ollama_cli/
├── __init__.py                    # Main package exports
├── core/                          # Core functionality
│   ├── __init__.py
│   └── cli.py                     # Main CLI orchestrator class
├── ai/                           # AI integration
│   ├── __init__.py
│   ├── client.py                  # Ollama API client
│   ├── prompt_manager.py          # System prompt management
│   └── response_processor.py      # AI response parsing and execution
├── file_ops/                     # File operations
│   ├── __init__.py
│   ├── reader.py                  # File reading functionality
│   ├── writer.py                  # File writing functionality
│   └── navigator.py               # Directory navigation
├── code_analysis/                # Code analysis tools
│   ├── __init__.py
│   ├── searcher.py               # Code pattern searching
│   ├── function_finder.py        # Function/class definition finder
│   ├── todo_finder.py            # TODO comment finder
│   └── import_finder.py          # Import analysis
└── commands/                     # Command execution
    ├── __init__.py
    └── executor.py               # Shell command execution
```

### Design Principles

1. **Single Responsibility**: Each module handles one specific concern
2. **Dependency Injection**: Components receive their dependencies in constructors
3. **Composition over Inheritance**: Main CLI class composes functionality from modules
4. **Type Safety**: All modules use proper type hints
5. **Error Handling**: Consistent error handling patterns across modules

## Module Responsibilities

### `core/cli.py` - Main Orchestrator
- Initializes and coordinates all other modules
- Handles interactive mode and user input
- Manages working directory updates across components
- Provides backward-compatible API

### `ai/` - AI Integration
- **`client.py`**: Ollama API communication, model management, conversation history
- **`prompt_manager.py`**: System prompt generation and management
- **`response_processor.py`**: Parses AI responses for commands and executes them

### `file_ops/` - File Operations
- **`reader.py`**: File reading with path resolution
- **`writer.py`**: File writing with directory creation
- **`navigator.py`**: Directory listing and navigation

### `code_analysis/` - Code Analysis Tools
- **`searcher.py`**: Generic code pattern searching
- **`function_finder.py`**: Function and class definition discovery
- **`todo_finder.py`**: TODO comment extraction
- **`import_finder.py`**: Import statement analysis

### `commands/` - System Integration
- **`executor.py`**: Shell command execution with timeout and error handling

## Testing

### Test Suite Structure

```
tests/
└── test_ollama_cli.py            # Main test suite
```

### Running Tests

```bash
# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=ollama_cli --cov-report=html

# Run specific test class
python -m pytest tests/test_ollama_cli.py::TestOllamaCLI -v
```

### Test Categories

1. **Initialization Tests**: Verify proper setup of CLI components
2. **Code Analysis Tests**: Test search, function finding, TODO detection
3. **Integration Tests**: Verify component interaction
4. **Edge Case Tests**: Handle empty queries, missing files, etc.

### Current Test Coverage

- **13 tests** covering core functionality including `/cls` command
- **100% pass rate** maintained during refactoring
- Tests focus on public API to ensure backward compatibility
- Integration tests verify command execution through subprocess simulation

### Adding New Tests

When adding new functionality:

1. **Unit Tests**: Test individual modules in isolation
2. **Integration Tests**: Test component interactions
3. **Regression Tests**: Ensure existing functionality still works
4. **Edge Cases**: Test error conditions and boundary cases

Example test structure:
```python
class TestNewFeature:
    def test_basic_functionality(self):
        """Test basic feature operation"""
        cli = OllamaCLI()
        result = cli.new_feature("input")
        assert isinstance(result, str)
        assert "expected_content" in result

    def test_error_handling(self):
        """Test error conditions"""
        cli = OllamaCLI()
        result = cli.new_feature("")
        assert "error" in result.lower()
```

## Code Quality

### Linting and Formatting

The project uses standard Python code quality tools:

```bash
# Check code style
python -m flake8 ollama_cli/ --max-line-length=88

# Format code (if using black)
python -m black ollama_cli/

# Type checking (if using mypy)
python -m mypy ollama_cli/
```

### Code Style Guidelines

1. **Line Length**: Maximum 88 characters (Black default)
2. **Type Hints**: Use type hints for all function parameters and returns
3. **Docstrings**: Document all public methods and classes
4. **Error Handling**: Use explicit exception handling, avoid bare except
5. **Imports**: Group imports (standard library, third-party, local)

## Development Workflow

### Setting Up Development Environment

1. **Clone Repository**:
   ```bash
   git clone <repository-url>
   cd agent
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Install Pre-commit Hooks** (if available):
   ```bash
   pre-commit install
   ```

### Making Changes

1. **Create Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**: Follow the architecture patterns established
3. **Run Tests**: Ensure all tests pass
   ```bash
   python -m pytest tests/ -v
   ```

4. **Test Manually**: Run the CLI to verify functionality
   ```bash
   python ollama_cli.py --help
   ```

5. **Commit Changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

### Adding New Features

When adding new functionality:

1. **Identify Module**: Determine which module should contain the feature
2. **Follow Patterns**: Use existing patterns for consistency
3. **Add Tests**: Write tests before or alongside implementation
4. **Update Documentation**: Update relevant documentation
5. **Maintain API**: Ensure backward compatibility

### Example: Adding New Code Analysis Feature

1. **Create new module** in `code_analysis/`:
   ```python
   # ollama_cli/code_analysis/new_analyzer.py
   class NewAnalyzer:
       def __init__(self, working_directory: Path):
           self.working_directory = working_directory

       def analyze(self, query: str) -> str:
           # Implementation here
           pass
   ```

2. **Update `__init__.py`**:
   ```python
   from .new_analyzer import NewAnalyzer
   __all__ = ["CodeSearcher", "FunctionFinder", "TodoFinder", "ImportFinder", "NewAnalyzer"]
   ```

3. **Integrate in main CLI**:
   ```python
   # In cli.py __init__
   self.new_analyzer = NewAnalyzer(self.working_directory)

   # Add method
   def new_analysis(self, query: str) -> str:
       return self.new_analyzer.analyze(query)
   ```

4. **Add tests**:
   ```python
   def test_new_analysis_basic(self):
       cli = OllamaCLI()
       result = cli.new_analysis("test query")
       assert isinstance(result, str)
   ```

## Troubleshooting

### Common Issues

**Import Errors After Refactoring**:
- Ensure all `__init__.py` files are present
- Check import paths are correct
- Verify package is installed properly

**Tests Failing**:
- Check if working directory affects tests
- Verify all dependencies are installed
- Ensure Ollama is not required for unit tests

**Performance Issues**:
- Profile code analysis functions with large codebases
- Consider adding caching for repeated operations
- Monitor memory usage with large file operations

### Debugging

1. **Enable Debug Output**: Add debug prints in response processor
2. **Test Individual Modules**: Import and test modules separately
3. **Use IDE Debugger**: Set breakpoints in key functions
4. **Check File Permissions**: Ensure proper access to files/directories

## Contributing

### Pull Request Process

1. **Fork Repository** and create feature branch
2. **Implement Changes** following architecture patterns
3. **Add Tests** for new functionality
4. **Run Full Test Suite** and ensure all pass
5. **Update Documentation** as needed
6. **Submit Pull Request** with clear description

### Review Criteria

- [ ] All tests pass
- [ ] Code follows established patterns
- [ ] Documentation is updated
- [ ] Backward compatibility maintained
- [ ] Performance impact considered

## Future Improvements

### Potential Enhancements

1. **Plugin System**: Allow external modules to extend functionality
2. **Configuration Files**: Support for user preferences and settings
3. **Command History**: Persistent command history across sessions
4. **Async Operations**: Non-blocking command execution for long tasks
5. **Web Interface**: Optional web UI alongside CLI
6. **Multiple AI Providers**: Support for other AI services beyond Ollama

### Architecture Considerations

- Consider dependency injection container for complex setups
- Evaluate event system for loose coupling between modules
- Plan for internationalization if expanding user base
- Consider CLI framework (Click, Typer) for advanced command handling

## Test Performance Best Practices

Based on the optimizations implemented for Issue #11, here are best practices for maintaining fast test execution:

### 1. Validate Input Early
- **Before**: Tests with invalid inputs (like empty search queries) would process through entire codebase
- **After**: Validate inputs at the beginning of functions to fail fast
- **Example**: Check for empty strings before expensive file system operations

### 2. Minimize Integration Test Overhead
- **Use minimal test scenarios**: Only test what's necessary to validate functionality
- **Reduce timeouts**: Use the shortest timeout that reliably works
- **Avoid redundant operations**: Don't send unnecessary commands in subprocess tests

### 3. Profile Slow Tests Regularly
```bash
# Identify slow tests
python -m pytest tests/ --durations=0

# Run specific slow tests to debug
python -m pytest tests/test_file.py::TestClass::test_slow_method -v
```

### 4. Optimize File System Operations
- **Avoid recursive file searches with broad patterns**: Especially with empty or very general queries
- **Limit result sets early**: Don't process more data than needed
- **Cache expensive operations**: Consider caching file system lookups in tests

### 5. Target Execution Times
- **Unit tests**: Aim for <0.1s per test
- **Integration tests**: Aim for <1s per test
- **Full test suite**: Should complete in under 10s
- **Critical threshold**: If any single test takes >5s, investigate immediately

### Performance Monitoring
Monitor test performance over time:
```bash
# Run tests with timing and save to file
python -m pytest tests/ --durations=0 > test_timings.txt

# Compare with previous runs to catch performance regressions
```

## Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ollama API Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
