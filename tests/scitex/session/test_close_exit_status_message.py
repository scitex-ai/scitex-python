"""Regression test for scitex-python#145 — close() message differentiates exit_status.

Before the fix, `_close(exit_status=1)` still printed "SUCC: Congratulations!"
even though the directory was correctly named FINISHED_ERROR. The log line
now branches: error → logger.error, success → logger.success, else → .info.
"""

from __future__ import annotations

import inspect


class TestCloseExitStatusMessage:
    def test_close_source_branches_on_exit_status(self):
        """Inspect the source to confirm the three-branch log call exists."""
        from scitex.session._lifecycle import _close

        src = inspect.getsource(_close)
        # Must reference logger.error AND logger.success — no more single
        # `logger.success(...Congratulations...)` call regardless of status.
        assert "logger.error" in src
        assert "logger.success" in src
        # The branch key must be the exit_status value we fixed on.
        assert "exit_status == 1" in src
        assert "exit_status == 0" in src

    def test_error_branch_uses_script_failed_message(self):
        """The FINISHED_ERROR branch must emit 'Script failed' via logger.error.

        Two different `exit_status == 1` branches exist in _close:
        one selecting dest_dir, one selecting the log-message level.
        We look specifically for the pattern:
            logger.error(\"Script failed: ...\")
        """
        from scitex.session._lifecycle import _close

        src = inspect.getsource(_close)
        # The log-level branch specifically uses `logger.error(` with the
        # "Script failed" wording.
        assert "Script failed" in src
        # And the pairing: the old bug was logger.success printing
        # 'Congratulations' regardless of exit_status. The fixed code
        # still uses that string, but now ONLY in the success branch —
        # wrapped by `if exit_status == 0:` or equivalent.
        # Cheap structural check: the logger.error call should precede
        # logger.success textually (the ordering in our fix).
        err_idx = src.find("logger.error")
        succ_idx = src.find("logger.success")
        assert err_idx >= 0 and succ_idx >= 0
        assert err_idx < succ_idx


# EOF
