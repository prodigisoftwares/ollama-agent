"""
Unit tests for OllamaClient class
"""

from unittest.mock import Mock, patch

import requests

from ollama_cli.ai.client import OllamaClient


class TestOllamaClient:
    """Test cases for OllamaClient class"""

    def test_init_default_values(self):
        """Test OllamaClient initialization with default values"""
        client = OllamaClient()

        assert client.model == "gemma2:9b"
        assert client.base_url == "http://localhost:11434"
        assert client.conversation_history == []

    def test_init_custom_values(self):
        """Test OllamaClient initialization with custom values"""
        client = OllamaClient(model="llama2:7b", base_url="http://custom-host:8080")

        assert client.model == "llama2:7b"
        assert client.base_url == "http://custom-host:8080"
        assert client.conversation_history == []

    @patch("subprocess.run")
    def test_list_models_success(self, mock_run):
        """Test successful model listing"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NAME\tID\tSIZE\tMODIFIED\ngemma2:9b\tabc123\t5.4GB\t2 days ago\nllama2:7b\tdef456\t3.8GB\t1 week ago\n",  # noqa: E501
        )

        client = OllamaClient()
        models = client.list_models()

        assert models == ["gemma2:9b", "llama2:7b"]
        mock_run.assert_called_once_with(
            ["ollama", "list"], capture_output=True, text=True
        )

    @patch("subprocess.run")
    def test_list_models_empty_output(self, mock_run):
        """Test model listing with only header"""
        mock_run.return_value = Mock(returncode=0, stdout="NAME\tID\tSIZE\tMODIFIED\n")

        client = OllamaClient()
        models = client.list_models()

        assert models == []

    @patch("subprocess.run")
    def test_list_models_with_empty_lines(self, mock_run):
        """Test model listing with empty lines"""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NAME\tID\tSIZE\tMODIFIED\ngemma2:9b\tabc123\t5.4GB\t2 days ago\n\nllama2:7b\tdef456\t3.8GB\t1 week ago\n\n",  # noqa: E501
        )

        client = OllamaClient()
        models = client.list_models()

        assert models == ["gemma2:9b", "llama2:7b"]

    @patch("subprocess.run")
    def test_list_models_subprocess_failure(self, mock_run):
        """Test model listing when subprocess fails"""
        mock_run.return_value = Mock(returncode=1)

        client = OllamaClient()
        models = client.list_models()

        assert models == []

    @patch("subprocess.run")
    def test_list_models_exception(self, mock_run):
        """Test model listing when subprocess raises exception"""
        mock_run.side_effect = FileNotFoundError("ollama command not found")

        client = OllamaClient()
        models = client.list_models()

        assert models == []

    @patch("requests.post")
    def test_chat_basic_message(self, mock_post):
        """Test basic chat functionality"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {"content": "Hello! How can I help you?"}
        }
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.chat("Hello")

        assert result == "Hello! How can I help you?"
        assert len(client.conversation_history) == 2
        assert client.conversation_history[0] == {"role": "user", "content": "Hello"}
        assert client.conversation_history[1] == {
            "role": "assistant",
            "content": "Hello! How can I help you?",
        }

        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json={
                "model": "gemma2:9b",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False,
            },
        )

    @patch("requests.post")
    def test_chat_with_system_prompt(self, mock_post):
        """Test chat with system prompt"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {"content": "I understand the system prompt."}
        }
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.chat("Hello", system_prompt="You are a helpful assistant.")

        assert result == "I understand the system prompt."

        expected_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
        ]
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json={"model": "gemma2:9b", "messages": expected_messages, "stream": False},
        )

    @patch("requests.post")
    def test_chat_with_conversation_history(self, mock_post):
        """Test chat with existing conversation history"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"message": {"content": "Second response"}}
        mock_post.return_value = mock_response

        client = OllamaClient()
        # Simulate existing conversation history
        client.conversation_history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
        ]

        result = client.chat("Second message")

        assert result == "Second response"

        expected_messages = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
        ]
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json={"model": "gemma2:9b", "messages": expected_messages, "stream": False},
        )

    @patch("requests.post")
    def test_chat_with_system_prompt_and_history(self, mock_post):
        """Test chat with both system prompt and conversation history"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {"content": "Response with system and history"}
        }
        mock_post.return_value = mock_response

        client = OllamaClient()
        client.conversation_history = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
        ]

        client.chat("Current message", system_prompt="Be helpful")

        expected_messages = [
            {"role": "system", "content": "Be helpful"},
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
            {"role": "user", "content": "Current message"},
        ]
        mock_post.assert_called_once_with(
            "http://localhost:11434/api/chat",
            json={"model": "gemma2:9b", "messages": expected_messages, "stream": False},
        )

    @patch("requests.post")
    def test_chat_http_error(self, mock_post):
        """Test chat when HTTP error occurs"""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.chat("Hello")

        assert "Error communicating with Ollama: 404 Not Found" in result
        assert (
            client.conversation_history == []
        )  # History should not be updated on error

    @patch("requests.post")
    def test_chat_connection_error(self, mock_post):
        """Test chat when connection error occurs"""
        mock_post.side_effect = requests.ConnectionError("Connection refused")

        client = OllamaClient()
        result = client.chat("Hello")

        assert "Error communicating with Ollama: Connection refused" in result
        assert client.conversation_history == []

    @patch("requests.post")
    def test_chat_json_decode_error(self, mock_post):
        """Test chat when response is not valid JSON"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.chat("Hello")

        assert "Error communicating with Ollama: Invalid JSON" in result
        assert client.conversation_history == []

    @patch("requests.post")
    def test_chat_malformed_response(self, mock_post):
        """Test chat when response has unexpected structure"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"unexpected": "structure"}
        mock_post.return_value = mock_response

        client = OllamaClient()
        result = client.chat("Hello")

        assert "Error communicating with Ollama:" in result
        assert client.conversation_history == []

    @patch("requests.post")
    def test_chat_custom_base_url(self, mock_post):
        """Test chat with custom base URL"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {"content": "Response from custom URL"}
        }
        mock_post.return_value = mock_response

        client = OllamaClient(base_url="http://custom-host:8080")
        client.chat("Hello")

        mock_post.assert_called_once_with(
            "http://custom-host:8080/api/chat",
            json={
                "model": "gemma2:9b",
                "messages": [{"role": "user", "content": "Hello"}],
                "stream": False,
            },
        )

    @patch("requests.post")
    def test_chat_custom_model(self, mock_post):
        """Test chat with custom model"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "message": {"content": "Response from custom model"}
        }
        mock_post.return_value = mock_response

        client = OllamaClient(model="llama2:7b")
        client.chat("Hello")

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[1]["json"]["model"] == "llama2:7b"

    def test_clear_conversation(self):
        """Test clearing conversation history"""
        client = OllamaClient()
        client.conversation_history = [
            {"role": "user", "content": "Message 1"},
            {"role": "assistant", "content": "Response 1"},
            {"role": "user", "content": "Message 2"},
            {"role": "assistant", "content": "Response 2"},
        ]

        client.clear_conversation()

        assert client.conversation_history == []

    def test_set_model(self):
        """Test setting a new model"""
        client = OllamaClient()
        client.conversation_history = [
            {"role": "user", "content": "Previous message"},
            {"role": "assistant", "content": "Previous response"},
        ]

        client.set_model("llama2:7b")

        assert client.model == "llama2:7b"
        assert client.conversation_history == []  # Should be cleared

    def test_set_model_same_model(self):
        """Test setting the same model clears history"""
        client = OllamaClient(model="gemma2:9b")
        client.conversation_history = [
            {"role": "user", "content": "Message"},
            {"role": "assistant", "content": "Response"},
        ]

        client.set_model("gemma2:9b")

        assert client.model == "gemma2:9b"
        assert client.conversation_history == []


class TestOllamaClientIntegration:
    """Integration-style tests for OllamaClient"""

    @patch("requests.post")
    def test_multiple_chat_messages(self, mock_post):
        """Test multiple chat messages build conversation history correctly"""
        # Setup responses for multiple calls
        responses = [
            {"message": {"content": "First response"}},
            {"message": {"content": "Second response"}},
            {"message": {"content": "Third response"}},
        ]

        mock_responses = []
        for response_data in responses:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = response_data
            mock_responses.append(mock_response)

        mock_post.side_effect = mock_responses

        client = OllamaClient()

        # Send multiple messages
        result1 = client.chat("First message")
        result2 = client.chat("Second message")
        result3 = client.chat("Third message")

        assert result1 == "First response"
        assert result2 == "Second response"
        assert result3 == "Third response"

        # Check conversation history builds correctly
        expected_history = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
            {"role": "assistant", "content": "Second response"},
            {"role": "user", "content": "Third message"},
            {"role": "assistant", "content": "Third response"},
        ]
        assert client.conversation_history == expected_history

        # Verify the third call included all previous messages
        third_call = mock_post.call_args_list[2]
        expected_messages_in_third_call = [
            {"role": "user", "content": "First message"},
            {"role": "assistant", "content": "First response"},
            {"role": "user", "content": "Second message"},
            {"role": "assistant", "content": "Second response"},
            {"role": "user", "content": "Third message"},
        ]
        assert third_call[1]["json"]["messages"] == expected_messages_in_third_call

    @patch("subprocess.run")
    def test_list_models_various_formats(self, mock_run):
        """Test list_models with various output formats"""
        # Test with different spacing and formatting
        mock_run.return_value = Mock(
            returncode=0,
            stdout="NAME             \tID      \tSIZE    \tMODIFIED     \ngemma2:9b        \txyz789  \t5.4GB   \t2 days ago   \nllama2:7b:latest \tabc123  \t3.8GB   \t1 week ago   \n",  # noqa: E501
        )

        client = OllamaClient()
        models = client.list_models()

        assert models == ["gemma2:9b", "llama2:7b:latest"]
