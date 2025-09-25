# Demo Scripts

This folder contains demonstration scripts for testing and showcasing features of the Ollama CLI.

**Note**: These scripts are for demonstration purposes only and are not part of the test suite.

## Available Demos

### help_system_demo.py
Demonstrates the enhanced help system features including:
- Overview help (`/help`)
- Command-specific help (`/help <command>`)
- Examples help (`/help examples`)
- Tips help (`/help tips`)
- Help search functionality
- Contextual error help

Run with:
```bash
cd demo
python help_system_demo.py
```

### interactive_demo.sh
Shows how to test the interactive help features by running commands in the actual CLI.

Run with:
```bash
cd demo
bash interactive_demo.sh
```

## Testing the CLI Help System

To test the help system interactively:

1. **Command-line help**:
   ```bash
   python ../ollama_cli.py --help
   ```

2. **Interactive help**:
   ```bash
   python ../ollama_cli.py
   # Then try these commands:
   /help
   /help search
   /help examples
   /help tips
   /help nonexistent  # Test error handling
   ```
