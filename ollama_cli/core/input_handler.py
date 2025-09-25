"""
Enhanced input handler with arrow key support and command history
"""

import os
import readline
from typing import List, Optional


class InputHandler:  # pragma: no cover
    """Enhanced input handler with arrow key navigation and history support"""

    def __init__(self, history_file: Optional[str] = None):
        self.history_file = history_file or os.path.expanduser("~/.ollama_cli_history")
        self.setup_readline()

    def setup_readline(self):
        """Configure readline for enhanced input handling"""
        # Enable arrow key navigation and editing
        readline.parse_and_bind("tab: complete")
        readline.parse_and_bind("set editing-mode emacs")  # Enable emacs-style editing

        # Enable history navigation with arrow keys
        readline.parse_and_bind('"\\e[A": history-search-backward')  # Up arrow
        readline.parse_and_bind('"\\e[B": history-search-forward')  # Down arrow
        readline.parse_and_bind('"\\e[C": forward-char')  # Right arrow
        readline.parse_and_bind('"\\e[D": backward-char')  # Left arrow

        # Additional helpful bindings
        readline.parse_and_bind(
            '"\\e[1;5C": forward-word'
        )  # Ctrl+Right (word forward)  noqa: E501
        readline.parse_and_bind(
            '"\\e[1;5D": backward-word'
        )  # Ctrl+Left (word backward) noqa: E501
        readline.parse_and_bind('"\\C-a": beginning-of-line')  # Ctrl+A (beginning)
        readline.parse_and_bind('"\\C-e": end-of-line')  # Ctrl+E (end)
        readline.parse_and_bind('"\\C-k": kill-line')  # Ctrl+K (kill to end)
        readline.parse_and_bind(
            '"\\C-u": unix-line-discard'
        )  # Ctrl+U (kill to beginning) noqa: E501

        # Load history if it exists
        self.load_history()

    def load_history(self):
        """Load command history from file"""
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)
                # Limit history size
                readline.set_history_length(1000)
        except Exception:
            # Silently ignore history loading errors
            pass

    def save_history(self):
        """Save command history to file"""
        try:
            readline.write_history_file(self.history_file)
        except Exception:
            # Silently ignore history saving errors
            pass

    def get_input(self, prompt: str = "") -> str:
        """Get user input with arrow key support and history"""
        try:
            user_input = input(prompt)
            # Save non-empty commands to history
            if user_input.strip():
                readline.add_history(user_input)
                self.save_history()
            return user_input
        except (EOFError, KeyboardInterrupt):
            raise

    def clear_history(self):
        """Clear command history"""
        readline.clear_history()
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
        except Exception:
            pass

    def get_history(self) -> List[str]:
        """Get current command history"""
        history = []
        for i in range(readline.get_current_history_length()):
            history.append(readline.get_history_item(i + 1))
        return history
