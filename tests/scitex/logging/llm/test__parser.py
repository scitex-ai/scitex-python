#!/usr/bin/env python3
# Timestamp: 2026-03-19
# File: /home/ywatanabe/proj/scitex-python/tests/scitex/logging/llm/test__parser.py

"""Tests for scitex.logging.llm parser."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from scitex.logging.llm._parser import (
    ClaudeCodeSession,
    Entry,
    ToolCall,
    ToolResult,
    load,
)


def _write_jsonl(lines: list[dict], path: Path) -> Path:
    """Write JSONL test data."""
    with open(path, "w") as f:
        for line in lines:
            f.write(json.dumps(line) + "\n")
    return path


@pytest.fixture
def sample_session(tmp_path):
    """Create a minimal session JSONL for testing."""
    entries = [
        {
            "type": "user",
            "uuid": "u1",
            "parentUuid": "",
            "timestamp": "2026-03-19T10:00:00Z",
            "sessionId": "test-session-123",
            "slug": "test-slug",
            "version": "2.1.76",
            "gitBranch": "develop",
            "message": {"role": "user", "content": "Hello world"},
        },
        {
            "type": "assistant",
            "uuid": "a1",
            "parentUuid": "u1",
            "timestamp": "2026-03-19T10:00:05Z",
            "sessionId": "test-session-123",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "I will read that file."},
                    {
                        "type": "tool_use",
                        "id": "toolu_abc",
                        "name": "Read",
                        "input": {"file_path": "/tmp/test.py"},
                    },
                ],
                "model": "claude-opus-4-6",
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 50,
                    "cache_creation_input_tokens": 10,
                    "cache_read_input_tokens": 5,
                },
            },
        },
        {
            "type": "user",
            "uuid": "u2",
            "parentUuid": "a1",
            "timestamp": "2026-03-19T10:00:06Z",
            "sessionId": "test-session-123",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_abc",
                        "content": [{"type": "text", "text": "file contents here"}],
                    }
                ],
            },
            "toolUseResult": {
                "stdout": "file contents here",
                "stderr": "",
                "interrupted": False,
                "isImage": False,
            },
        },
        {
            "type": "system",
            "uuid": "s1",
            "timestamp": "2026-03-19T10:01:00Z",
            "sessionId": "test-session-123",
            "subtype": "turn_duration",
            "durationMs": 60000,
            "message": {},
        },
        {
            "type": "progress",
            "data": {"type": "hook_progress"},
            "timestamp": "2026-03-19T10:00:07Z",
        },
    ]
    return _write_jsonl(entries, tmp_path / "test.jsonl")


class TestLoad:
    def test_load_session(self, sample_session):
        session = load(sample_session)
        assert isinstance(session, ClaudeCodeSession)
        assert session.session_id == "test-session-123"
        assert session.slug == "test-slug"
        assert session.version == "2.1.76"
        assert session.git_branch == "develop"

    def test_load_filters_progress(self, sample_session):
        session = load(sample_session)
        types = [e.type for e in session.entries]
        assert "progress" not in types

    def test_load_entry_count(self, sample_session):
        session = load(sample_session)
        # user, assistant, user (tool result), system = 4
        assert len(session.entries) == 4

    def test_load_nonexistent(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load(tmp_path / "nonexistent.jsonl")


class TestEntry:
    def test_user_entry(self, sample_session):
        session = load(sample_session)
        user = session.user_entries[0]
        assert user.type == "user"
        assert user.text == "Hello world"
        assert user.uuid == "u1"

    def test_assistant_entry(self, sample_session):
        session = load(sample_session)
        asst = session.assistant_entries[0]
        assert asst.type == "assistant"
        assert asst.text == "I will read that file."
        assert asst.model == "claude-opus-4-6"
        assert asst.input_tokens == 100
        assert asst.output_tokens == 50

    def test_tool_calls(self, sample_session):
        session = load(sample_session)
        asst = session.assistant_entries[0]
        assert len(asst.tool_calls) == 1
        tc = asst.tool_calls[0]
        assert isinstance(tc, ToolCall)
        assert tc.name == "Read"
        assert tc.id == "toolu_abc"
        assert tc.input == {"file_path": "/tmp/test.py"}

    def test_tool_result(self, sample_session):
        session = load(sample_session)
        # Second user entry has tool result
        user2 = session.entries[2]
        assert user2.tool_result is not None
        assert isinstance(user2.tool_result, ToolResult)
        assert user2.tool_result.stdout == "file contents here"

    def test_system_duration(self, sample_session):
        session = load(sample_session)
        sys_entry = [e for e in session.entries if e.type == "system"][0]
        assert sys_entry.duration_ms == 60000


class TestSummary:
    def test_summary_keys(self, sample_session):
        session = load(sample_session)
        s = session.summary()
        assert "session_id" in s
        assert "total_tokens" in s
        assert "tool_usage" in s

    def test_summary_counts(self, sample_session):
        session = load(sample_session)
        s = session.summary()
        assert s["user_turns"] == 2
        assert s["assistant_turns"] == 1
        assert s["total_tool_calls"] == 1
        assert s["tool_usage"] == {"Read": 1}

    def test_summary_tokens(self, sample_session):
        session = load(sample_session)
        s = session.summary()
        assert s["total_input_tokens"] == 100
        assert s["total_output_tokens"] == 50
        assert s["total_tokens"] == 150


class TestProperties:
    def test_tool_calls_property(self, sample_session):
        session = load(sample_session)
        assert len(session.tool_calls) == 1
        assert session.tool_calls[0].name == "Read"

    def test_total_tokens(self, sample_session):
        session = load(sample_session)
        assert session.total_tokens == 150


# EOF
