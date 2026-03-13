#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_audio._relay module."""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from unittest.mock import MagicMock, patch

import pytest


class TestRelayClient:
    """Tests for RelayClient class."""

    def test_init_with_url(self):
        """Test client initialization with explicit URL."""
        from scitex_audio._relay import RelayClient

        client = RelayClient("http://localhost:9999")
        assert client.base_url == "http://localhost:9999"
        assert client.timeout == 30

    def test_init_with_trailing_slash(self):
        """Test URL trailing slash is stripped."""
        from scitex_audio._relay import RelayClient

        client = RelayClient("http://localhost:9999/")
        assert client.base_url == "http://localhost:9999"

    def test_init_with_custom_timeout(self):
        """Test client initialization with custom timeout."""
        from scitex_audio._relay import RelayClient

        client = RelayClient("http://localhost:9999", timeout=60)
        assert client.timeout == 60

    @patch("scitex_audio._relay.get_relay_url")
    def test_init_auto_detect_url(self, mock_get_url):
        """Test client auto-detects URL from environment."""
        from scitex_audio._relay import RelayClient

        mock_get_url.return_value = "http://auto-detected:31293"
        client = RelayClient()
        assert client.base_url == "http://auto-detected:31293"


class TestRelayClientMethods:
    """Tests for RelayClient methods with mock server."""

    @pytest.fixture
    def mock_server(self):
        """Create a simple mock HTTP server."""
        responses = {}

        class MockHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass  # Suppress logging

            def do_GET(self):
                if self.path == "/health":
                    self._respond(200, {"status": "healthy"})
                elif self.path == "/list_backends":
                    self._respond(200, {"backends": ["gtts", "pyttsx3"]})
                else:
                    self._respond(404, {"error": "not found"})

            def do_POST(self):
                if self.path == "/speak":
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = json.loads(self.rfile.read(content_length))
                    self._respond(200, {"success": True, "text": body.get("text")})
                else:
                    self._respond(404, {"error": "not found"})

            def _respond(self, status, data):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())

        server = HTTPServer(("127.0.0.1", 0), MockHandler)
        port = server.server_address[1]
        thread = Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()

        yield f"http://127.0.0.1:{port}"

        server.shutdown()

    def test_health_check(self, mock_server):
        """Test health check endpoint."""
        from scitex_audio._relay import RelayClient

        client = RelayClient(mock_server, timeout=5)
        result = client.health()
        assert result["status"] == "healthy"

    def test_is_available(self, mock_server):
        """Test availability check."""
        from scitex_audio._relay import RelayClient

        client = RelayClient(mock_server, timeout=5)
        assert client.is_available() is True

    def test_is_available_unreachable(self):
        """Test availability check for unreachable server."""
        from scitex_audio._relay import RelayClient

        # Mock the health method to raise an exception
        client = RelayClient("http://127.0.0.1:59999", timeout=1)
        with patch.object(client, "health", side_effect=ConnectionError("unreachable")):
            assert client.is_available() is False

    def test_speak(self, mock_server):
        """Test speak request."""
        from scitex_audio._relay import RelayClient

        client = RelayClient(mock_server, timeout=5)
        result = client.speak("Hello test")
        assert result["success"] is True
        assert result["text"] == "Hello test"

    def test_list_backends(self, mock_server):
        """Test list backends request."""
        from scitex_audio._relay import RelayClient

        client = RelayClient(mock_server, timeout=5)
        result = client.list_backends()
        assert "backends" in result


class TestModuleFunctions:
    """Tests for module-level functions."""

    def test_get_relay_client_singleton(self):
        """Test relay client singleton."""
        from scitex_audio._relay import get_relay_client, reset_relay_client

        reset_relay_client()
        client1 = get_relay_client("http://test:1234")
        client2 = get_relay_client()
        assert client1 is client2

    def test_reset_relay_client(self):
        """Test relay client reset."""
        from scitex_audio._relay import get_relay_client, reset_relay_client

        client1 = get_relay_client("http://test:1234")
        reset_relay_client()
        client2 = get_relay_client("http://test:5678")
        assert client1 is not client2
        assert client2.base_url == "http://test:5678"


class TestBrandingFunctions:
    """Tests for _branding module relay functions."""

    def test_get_ssh_client_ip_with_ssh_client(self):
        """Test SSH client IP extraction from SSH_CLIENT."""
        from scitex_audio._branding import get_ssh_client_ip

        with patch.dict(os.environ, {"SSH_CLIENT": "192.168.1.100 54321 22"}):
            assert get_ssh_client_ip() == "192.168.1.100"

    def test_get_ssh_client_ip_with_ssh_connection(self):
        """Test SSH client IP extraction from SSH_CONNECTION."""
        from scitex_audio._branding import get_ssh_client_ip

        with patch.dict(
            os.environ, {"SSH_CONNECTION": "10.0.0.50 54321 10.0.0.1 22"}, clear=True
        ):
            # Clear SSH_CLIENT to test SSH_CONNECTION fallback
            os.environ.pop("SSH_CLIENT", None)
            assert get_ssh_client_ip() == "10.0.0.50"

    def test_get_ssh_client_ip_not_in_ssh(self):
        """Test SSH client IP when not in SSH session."""
        from scitex_audio._branding import get_ssh_client_ip

        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("SSH_CLIENT", None)
            os.environ.pop("SSH_CONNECTION", None)
            assert get_ssh_client_ip() is None

    def test_get_relay_url_from_env(self):
        """Test relay URL from environment variable."""
        from scitex_audio._branding import get_relay_url

        with patch.dict(os.environ, {"SCITEX_AUDIO_RELAY_URL": "http://custom:8080"}):
            assert get_relay_url() == "http://custom:8080"

    def test_get_relay_url_from_host_port(self):
        """Test relay URL built from host and port."""
        from scitex_audio._branding import get_relay_url

        env = {
            "SCITEX_AUDIO_RELAY_HOST": "myhost",
            "SCITEX_AUDIO_RELAY_PORT": "9999",
        }
        # Clear RELAY_URL to test host/port
        with patch.dict(os.environ, env):
            os.environ.pop("SCITEX_AUDIO_RELAY_URL", None)
            result = get_relay_url()
            assert result == "http://myhost:9999"


class TestSpeakHandlers:
    """Tests for speak handlers."""

    @pytest.mark.asyncio
    async def test_speak_local_handler_success(self):
        """Test local speak handler with play=False (skips sink check)."""
        from scitex_audio._mcp.speak_handlers import speak_local_handler

        # Mock the speak function and ensure SCITEX_AUDIO_MODE is not "remote"
        mock_result = {
            "success": True,
            "played": False,
            "play_requested": False,
            "backend": "gtts",
            "mode": "local",
        }
        with patch.dict(os.environ, {"SCITEX_AUDIO_MODE": "local"}, clear=False):
            with patch("scitex_audio.speak", return_value=mock_result):
                result = await speak_local_handler("Test text", play=False)
                assert result["success"] is True
                assert result["text"] == "Test text"
                assert result["played_on"] == "server"

    @pytest.mark.asyncio
    async def test_speak_local_handler_fails_when_mode_remote(self):
        """Test local speak handler fails when SCITEX_AUDIO_MODE=remote."""
        from scitex_audio._mcp.speak_handlers import speak_local_handler

        with patch.dict(os.environ, {"SCITEX_AUDIO_MODE": "remote"}, clear=False):
            result = await speak_local_handler("Test text")
            assert result["success"] is False
            assert "SCITEX_AUDIO_MODE=remote" in result["error"]

    @pytest.mark.asyncio
    async def test_speak_local_handler_fails_when_sink_suspended(self):
        """Test local speak handler fails when sink is SUSPENDED."""
        from scitex_audio._mcp.speak_handlers import speak_local_handler

        mock_sink = {"available": False, "state": "SUSPENDED", "reason": "No output"}
        with patch.dict(os.environ, {"SCITEX_AUDIO_MODE": "local"}, clear=False):
            with patch(
                "scitex_audio._mcp.speak_handlers.check_audio_sink_state",
                return_value=mock_sink,
            ):
                result = await speak_local_handler("Test text", play=True)
                assert result["success"] is False
                assert "SUSPENDED" in result.get("sink_state", "")

    @pytest.mark.asyncio
    async def test_speak_relay_handler_no_url(self):
        """Test relay handler when no URL configured."""
        from scitex_audio._mcp.speak_handlers import speak_relay_handler

        with patch("scitex_audio._branding.get_relay_url", return_value=None):
            with patch("scitex_audio._branding.get_ssh_client_ip", return_value=None):
                result = await speak_relay_handler("Test")
                assert result["success"] is False
                assert "not configured" in result["error"]
                assert "instructions" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
