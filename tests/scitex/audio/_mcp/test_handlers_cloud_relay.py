#!/usr/bin/env python3
"""Tests for cloud relay mode in scitex/audio/_mcp/handlers.py

When the environment variable SCITEX_CLOUD=true is set, speak_handler()
must emit an OSC escape sequence to stderr instead of playing audio locally:
    \\x1b]9999;speak:<base64-text>\\x07

Source file: src/scitex/audio/_mcp/handlers.py
"""

import asyncio
import base64
import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _decode_osc_text(stderr_output: str) -> str:
    """Extract and base64-decode the text carried in an OSC 9999 escape."""
    prefix = "\x1b]9999;speak:"
    suffix = "\x07"
    assert prefix in stderr_output, f"OSC prefix not found in: {repr(stderr_output)}"
    start = stderr_output.index(prefix) + len(prefix)
    end = stderr_output.index(suffix, start)
    b64 = stderr_output[start:end]
    return base64.b64decode(b64.encode()).decode()


def _run(coro):
    """Run a coroutine synchronously."""
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Tests for _emit_browser_speech
# ---------------------------------------------------------------------------


class TestEmitBrowserSpeech:
    """Unit tests for the _emit_browser_speech helper."""

    def test_emits_osc_escape_sequence(self):
        """_emit_browser_speech must write the OSC 9999 escape to stderr."""
        from scitex_audio._mcp.handlers import _emit_browser_speech

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            _emit_browser_speech("hello")

        output = stderr_capture.getvalue()
        assert "\x1b]9999;speak:" in output
        assert output.endswith("\x07")

    def test_emitted_text_is_base64_encoded(self):
        """The text embedded in the OSC escape must be valid base64 for the input."""
        from scitex_audio._mcp.handlers import _emit_browser_speech

        input_text = "test payload"
        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            _emit_browser_speech(input_text)

        decoded = _decode_osc_text(stderr_capture.getvalue())
        assert decoded == input_text

    def test_emits_to_stderr_not_stdout(self):
        """Output must go to stderr so as not to corrupt MCP stdio protocol."""
        from scitex_audio._mcp.handlers import _emit_browser_speech

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        with patch("sys.stdout", stdout_capture), patch("sys.stderr", stderr_capture):
            _emit_browser_speech("check stream")

        assert "\x1b]9999;speak:" not in stdout_capture.getvalue()
        assert "\x1b]9999;speak:" in stderr_capture.getvalue()


# ---------------------------------------------------------------------------
# Tests for speak_handler in cloud relay mode
# ---------------------------------------------------------------------------


class TestSpeakHandlerCloudRelayMode:
    """speak_handler cloud relay: SCITEX_CLOUD=true path."""

    def test_cloud_relay_emits_osc_escape(self, monkeypatch):
        """With SCITEX_CLOUD=true, stderr must contain the OSC escape for the text."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            result = _run(speak_handler(text="hello cloud"))

        output = stderr_capture.getvalue()
        assert "\x1b]9999;speak:" in output
        decoded = _decode_osc_text(output)
        assert decoded == "hello cloud"

    def test_cloud_relay_returns_browser_relay_backend(self, monkeypatch):
        """Result dict must have backend='browser_relay' in cloud relay mode."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            result = _run(speak_handler(text="check backend"))

        assert result["backend"] == "browser_relay"

    def test_cloud_relay_returns_cloud_relay_mode(self, monkeypatch):
        """Result dict must have mode='cloud_relay' in cloud relay mode."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            result = _run(speak_handler(text="check mode"))

        assert result["mode"] == "cloud_relay"

    def test_cloud_relay_returns_success_true(self, monkeypatch):
        """Result dict must have success=True in cloud relay mode."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            result = _run(speak_handler(text="check success"))

        assert result["success"] is True

    def test_cloud_relay_returns_played_true(self, monkeypatch):
        """Result dict must mark played=True even though audio is relayed, not local."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            result = _run(speak_handler(text="check played"))

        assert result["played"] is True

    def test_cloud_relay_with_signature_prepends_to_emitted_text(self, monkeypatch):
        """When signature=True, the emitted OSC text must start with the signature."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")

        fake_sig = "myhost. myproject. main. "
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("scitex_audio._mcp.handlers._get_signature", return_value=fake_sig):
            with patch("sys.stderr", stderr_capture):
                result = _run(speak_handler(text="important message", signature=True))

        decoded = _decode_osc_text(stderr_capture.getvalue())
        assert decoded.startswith(fake_sig)
        assert "important message" in decoded

    def test_cloud_relay_with_signature_populates_result_fields(self, monkeypatch):
        """When signature=True, result must include 'signature' and 'full_text' keys."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")

        fake_sig = "myhost. myproject. main. "
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("scitex_audio._mcp.handlers._get_signature", return_value=fake_sig):
            with patch("sys.stderr", stderr_capture):
                result = _run(speak_handler(text="sig test", signature=True))

        assert "signature" in result
        assert "full_text" in result
        assert result["signature"] == fake_sig
        assert result["full_text"] == fake_sig + "sig test"

    def test_cloud_relay_without_signature_no_sig_keys(self, monkeypatch):
        """When signature=False (default), result must not include 'signature' key."""
        monkeypatch.setenv("SCITEX_CLOUD", "true")
        from scitex_audio._mcp.handlers import speak_handler

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            result = _run(speak_handler(text="no sig test"))

        assert "signature" not in result
        assert "full_text" not in result


# ---------------------------------------------------------------------------
# Tests for speak_handler in local mode
# ---------------------------------------------------------------------------


class TestSpeakHandlerLocalMode:
    """speak_handler local mode: SCITEX_CLOUD not set."""

    def test_local_mode_does_not_emit_osc_escape(self, monkeypatch):
        """Without SCITEX_CLOUD, no OSC escape must appear on stderr."""
        monkeypatch.delenv("SCITEX_CLOUD", raising=False)
        from scitex_audio._mcp.handlers import speak_handler

        mock_speak_result = {
            "success": True,
            "backend": "gtts",
            "played": True,
            "mode": "local",
        }

        stderr_capture = io.StringIO()
        with patch("sys.stderr", stderr_capture):
            with patch(
                "scitex_audio._mcp.handlers.asyncio.get_event_loop"
            ) as mock_loop_fn:
                mock_loop = MagicMock()
                mock_loop.run_in_executor = AsyncMock(return_value=mock_speak_result)
                mock_loop_fn.return_value = mock_loop
                _run(speak_handler(text="local speech"))

        output = stderr_capture.getvalue()
        assert "\x1b]9999;speak:" not in output

    def test_local_mode_does_not_return_cloud_relay_mode(self, monkeypatch):
        """Local mode result must not have mode='cloud_relay'."""
        monkeypatch.delenv("SCITEX_CLOUD", raising=False)
        from scitex_audio._mcp.handlers import speak_handler

        local_result = {
            "success": True,
            "backend": "gtts",
            "played": True,
            "mode": "local",
        }

        with patch("scitex_audio._mcp.handlers.asyncio.get_event_loop") as mock_loop_fn:
            mock_loop = MagicMock()
            mock_loop.run_in_executor = AsyncMock(return_value=local_result)
            mock_loop_fn.return_value = mock_loop
            result = _run(speak_handler(text="local mode check"))

        assert result.get("mode") != "cloud_relay"


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
