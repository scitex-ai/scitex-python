#!/usr/bin/env python3
"""Tests for CrossProcessLock module."""

import os
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scitex_audio._cross_process_lock import AudioPlaybackLock, acquire_audio_lock


class TestAudioPlaybackLockInit:
    """Tests for AudioPlaybackLock initialization."""

    def test_init_creates_instance(self):
        """AudioPlaybackLock should initialize without errors."""
        lock = AudioPlaybackLock()
        assert lock is not None

    def test_init_uses_default_lock_file(self):
        """Should use default LOCK_FILE when none provided."""
        lock = AudioPlaybackLock()
        assert lock.lock_file is not None
        assert "audio" in str(lock.lock_file)

    def test_init_uses_custom_lock_file(self):
        """Should use custom lock file when provided."""
        custom_path = Path("/tmp/custom.lock")
        lock = AudioPlaybackLock(lock_file=custom_path)
        assert lock.lock_file == custom_path

    def test_init_sets_fd_to_none(self):
        """Should initialize _fd to None."""
        lock = AudioPlaybackLock()
        assert lock._fd is None

    def test_init_sets_acquired_to_false(self):
        """Should initialize _acquired to False."""
        lock = AudioPlaybackLock()
        assert lock._acquired is False


class TestEnsureLockDir:
    """Tests for _ensure_lock_dir method."""

    def test_creates_parent_directory(self):
        """Should create parent directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "subdir" / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock._ensure_lock_dir()
            assert lock_path.parent.exists()

    def test_handles_existing_directory(self):
        """Should not raise if directory already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            # Should not raise
            lock._ensure_lock_dir()
            lock._ensure_lock_dir()  # Call again


class TestAcquire:
    """Tests for acquire method."""

    def test_acquire_returns_true(self):
        """Should return True when lock acquired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            result = lock.acquire()
            assert result is True
            lock.release()

    def test_acquire_sets_acquired_flag(self):
        """Should set _acquired to True after acquiring."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            assert lock._acquired is True
            lock.release()

    def test_acquire_creates_lock_file(self):
        """Should create lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            assert lock_path.exists()
            lock.release()

    def test_acquire_writes_pid_to_file(self):
        """Should write PID to lock file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            content = lock_path.read_text()
            assert str(os.getpid()) in content
            lock.release()

    def test_acquire_with_timeout_returns_false_on_timeout(self):
        """Should return False when timeout expires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            # First lock holds it
            lock1 = AudioPlaybackLock(lock_file=lock_path)
            lock1.acquire()

            # Second lock times out
            lock2 = AudioPlaybackLock(lock_file=lock_path)
            result = lock2.acquire(timeout=0.2)

            assert result is False
            lock1.release()

    def test_acquire_sets_fd(self):
        """Should set _fd to valid file descriptor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            assert lock._fd is not None
            assert isinstance(lock._fd, int)
            lock.release()


class TestRelease:
    """Tests for release method."""

    def test_release_clears_acquired_flag(self):
        """Should clear _acquired flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            lock.release()
            assert lock._acquired is False

    def test_release_clears_fd(self):
        """Should clear _fd to None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            lock.release()
            assert lock._fd is None

    def test_release_allows_another_process_to_acquire(self):
        """Should allow another lock to acquire after release."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            lock1 = AudioPlaybackLock(lock_file=lock_path)
            lock1.acquire()
            lock1.release()

            lock2 = AudioPlaybackLock(lock_file=lock_path)
            result = lock2.acquire(timeout=0.5)
            assert result is True
            lock2.release()

    def test_release_without_acquire_is_safe(self):
        """Should not raise when releasing without acquiring."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            # Should not raise
            lock.release()


class TestCleanup:
    """Tests for _cleanup method."""

    def test_cleanup_closes_fd(self):
        """Should close file descriptor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            lock.acquire()
            fd = lock._fd
            lock._cleanup()
            assert lock._fd is None
            # Verify fd is closed by trying to use it
            with pytest.raises(OSError):
                os.read(fd, 1)

    def test_cleanup_handles_none_fd(self):
        """Should handle None _fd gracefully."""
        lock = AudioPlaybackLock()
        # Should not raise
        lock._cleanup()


class TestContextManager:
    """Tests for context manager support."""

    def test_enter_acquires_lock(self):
        """__enter__ should acquire the lock."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            with lock:
                assert lock._acquired is True

    def test_exit_releases_lock(self):
        """__exit__ should release the lock."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            with lock:
                pass
            assert lock._acquired is False
            assert lock._fd is None

    def test_exit_releases_on_exception(self):
        """__exit__ should release lock even on exception."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            try:
                with lock:
                    raise ValueError("Test exception")
            except ValueError:
                pass
            assert lock._acquired is False

    def test_exit_returns_false(self):
        """__exit__ should return False (not suppress exceptions)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            lock = AudioPlaybackLock(lock_file=lock_path)
            result = lock.__exit__(None, None, None)
            assert result is False


class TestAcquireAudioLock:
    """Tests for acquire_audio_lock context manager function."""

    def test_yields_true_when_acquired(self):
        """Should yield True when lock is acquired."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch(
                "scitex_audio._cross_process_lock.LOCK_FILE",
                Path(tmpdir) / "test.lock",
            ):
                with acquire_audio_lock() as result:
                    assert result is True

    def test_raises_timeout_error_on_timeout(self):
        """Should raise TimeoutError when timeout expires."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            # Hold the lock
            holding_lock = AudioPlaybackLock(lock_file=lock_path)
            holding_lock.acquire()

            try:
                with patch(
                    "scitex_audio._cross_process_lock.LOCK_FILE",
                    lock_path,
                ):
                    with pytest.raises(TimeoutError) as excinfo:
                        with acquire_audio_lock(timeout=0.2):
                            pass
                    assert "0.2s" in str(excinfo.value)
            finally:
                holding_lock.release()

    def test_releases_lock_after_context(self):
        """Should release lock after context exits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            with patch(
                "scitex_audio._cross_process_lock.LOCK_FILE",
                lock_path,
            ):
                with acquire_audio_lock():
                    pass

            # Should be able to acquire again
            lock = AudioPlaybackLock(lock_file=lock_path)
            result = lock.acquire(timeout=0.5)
            assert result is True
            lock.release()

    def test_default_timeout_is_60_seconds(self):
        """Should use 60 second default timeout."""
        # This is a specification test - we verify the function signature
        import inspect

        sig = inspect.signature(acquire_audio_lock)
        timeout_param = sig.parameters["timeout"]
        assert timeout_param.default == 60.0


class TestConcurrency:
    """Tests for concurrent lock acquisition."""

    def test_sequential_acquisition(self):
        """Locks should be acquired sequentially."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"
            results = []

            def acquire_and_record(name):
                lock = AudioPlaybackLock(lock_file=lock_path)
                if lock.acquire(timeout=2.0):
                    results.append(f"{name}_acquired")
                    time.sleep(0.1)
                    results.append(f"{name}_released")
                    lock.release()

            # Start first thread
            t1 = threading.Thread(target=acquire_and_record, args=("t1",))
            t2 = threading.Thread(target=acquire_and_record, args=("t2",))

            t1.start()
            time.sleep(0.05)  # Ensure t1 starts first
            t2.start()

            t1.join()
            t2.join()

            # Both should complete
            assert len(results) == 4
            # t1 should acquire and release before t2 acquires
            assert results[0] == "t1_acquired"


class TestIntegration:
    """Integration tests for AudioPlaybackLock."""

    def test_full_lifecycle(self):
        """Test complete lock lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            # Create and acquire
            lock = AudioPlaybackLock(lock_file=lock_path)
            assert lock.acquire() is True
            assert lock._acquired is True
            assert lock_path.exists()

            # Release
            lock.release()
            assert lock._acquired is False
            assert lock._fd is None

    def test_context_manager_lifecycle(self):
        """Test complete context manager lifecycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            lock_path = Path(tmpdir) / "test.lock"

            with patch(
                "scitex_audio._cross_process_lock.LOCK_FILE",
                lock_path,
            ):
                with acquire_audio_lock(timeout=5.0) as acquired:
                    assert acquired is True
                    assert lock_path.exists()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
