"""
Ollama API client
"""

import subprocess
from typing import List, Optional

import requests


class OllamaClient:
    def __init__(
        self,
        model: str = "gemma2:9b",
        base_url: str = "http://localhost:11434",  # noqa: E501
    ):
        self.model = model
        self.base_url = base_url
        self.conversation_history = []

    def list_models(self) -> List[str]:
        """List available Ollama models"""
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if result.returncode == 0:
                # Skip header
                lines = result.stdout.strip().split("\n")[1:]
                models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]
                        models.append(model_name)
                return models
            return []
        except Exception:
            return []

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """Send a chat message to Ollama"""
        url = f"{self.base_url}/api/chat"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # Add conversation history
        messages.extend(self.conversation_history)

        # Add current message
        messages.append({"role": "user", "content": message})

        payload = {"model": self.model, "messages": messages, "stream": False}

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()

            assistant_message = result["message"]["content"]

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            return assistant_message

        except Exception as e:
            return f"Error communicating with Ollama: {str(e)}"

    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []

    def set_model(self, model: str):
        """Change the model and clear conversation history"""
        self.model = model
        self.conversation_history = []
