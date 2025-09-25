"""
Ollama CLI - A Claude Code-like interface for Ollama
"""

import argparse

from .core.cli import OllamaCLI

__all__ = ["OllamaCLI", "main"]


def main():
    """Main entry point for the ollama-agent command."""
    parser = argparse.ArgumentParser(
        description="Ollama CLI - Claude Code-like Interface"
    )
    parser.add_argument(
        "--model", "-m", default="gemma2:9b", help="Ollama model to use"
    )
    parser.add_argument(
        "--url", default="http://localhost:11434", help="Ollama server URL"
    )
    args = parser.parse_args()

    cli = OllamaCLI(model=args.model, base_url=args.url)
    cli.interactive_mode()
