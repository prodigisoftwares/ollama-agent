#!/usr/bin/env python3
"""
Ollama CLI - A Claude Code-like interface for Ollama
"""

import argparse

from ollama_cli import OllamaCLI


def main():
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


if __name__ == "__main__":
    main()
