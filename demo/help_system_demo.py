#!/usr/bin/env python3
"""
Demo script to showcase the new help system features
"""

import os
import sys

# Add the parent directory to Python path to import ollama_cli
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ollama_cli.core.help import HelpSystem  # noqa: E402


def print_separator(title):
    """Print a separator with title"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print("=" * 60)


def demo_help_system():
    """Demonstrate the help system features"""
    help_system = HelpSystem()

    print_separator("1. OVERVIEW HELP - /help")
    overview = help_system.get_overview_help()
    # Show first 20 lines to keep demo manageable
    lines = overview.split("\n")[:20]
    print("\n".join(lines))
    print("... (truncated for demo)")

    print_separator("2. COMMAND-SPECIFIC HELP - /help search")
    print(help_system.get_command_help("search"))

    print_separator("3. COMMAND-SPECIFIC HELP - /help read")
    print(help_system.get_command_help("read"))

    print_separator("4. EXAMPLES HELP - /help examples")
    examples = help_system.get_examples_help()
    # Show first example
    lines = examples.split("\n")[:15]
    print("\n".join(lines))
    print("... (more examples available)")

    print_separator("5. TIPS HELP - /help tips")
    tips = help_system.get_tips_help()
    # Show first section
    lines = tips.split("\n")[:15]
    print("\n".join(lines))
    print("... (more tips available)")

    print_separator("6. HELP SEARCH - Finding file-related commands")
    file_commands = help_system.search_help("file")
    print(f"Commands related to 'file': {file_commands}")

    print_separator("7. CONTEXTUAL HELP - Error assistance")
    print("File not found error help:")
    print(help_system.get_contextual_help("file_not_found"))

    print("\nCommand not found error help:")
    print(help_system.get_contextual_help("command_not_found"))

    print_separator("8. INVALID COMMAND HELP")
    print(help_system.get_command_help("nonexistent"))

    print_separator("DEMO COMPLETE")
    print("🎉 All help system features demonstrated!")
    print("💡 Try these commands interactively with: python ../ollama_cli.py")


if __name__ == "__main__":
    demo_help_system()
