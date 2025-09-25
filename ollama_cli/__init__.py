"""
Ollama CLI - A Claude Code-like interface for Ollama
"""

import argparse

from .core.cli import OllamaCLI

__all__ = ["OllamaCLI", "main"]


def main():  # pragma: no cover
    """Main entry point for the ollama-agent command."""
    parser = argparse.ArgumentParser(
        description="🤖 Ollama CLI - A Claude Code-like conversational interface for Ollama",  # noqa: E501
        epilog="""
Examples:
  ollama-agent                          # Start with default model (gemma2:9b)
  ollama-agent -m codellama            # Use CodeLlama model
  ollama-agent --url http://server:11434  # Connect to remote Ollama server

Features:
  • Interactive chat with AI models via Ollama
  • File operations (/read, /write, /ls, /cd)
  • Code analysis (/search, /find-func, /find-todo)
  • Shell command execution (/run)
  • Model switching during session (/models, /model)
  • Rich help system (/help, /help examples, /help <command>)

Get started:
  Type /help for all available commands
  Type /help examples for workflow examples
  Start chatting naturally for AI assistance
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        "-m",
        default="gemma2:9b",
        help="Ollama model to use (default: %(default)s). Use 'ollama list' to see available models.",  # noqa: E501
    )
    parser.add_argument(
        "--url",
        default="http://localhost:11434",
        help="Ollama server URL (default: %(default)s)",
    )
    args = parser.parse_args()

    cli = OllamaCLI(model=args.model, base_url=args.url)
    cli.interactive_mode()
