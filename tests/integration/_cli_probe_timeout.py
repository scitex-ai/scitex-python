"""Bounded diagnostics for the isolated operator-policy test subprocess."""

import sys


def annotate_timeout(error):
    """Keep the original timeout while retaining bounded child-only stderr."""
    stderr = error.stderr or ""
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    stderr = stderr.encode("utf-8", errors="replace")
    if len(stderr) > 8192:
        stderr = stderr[:4096] + b"\n[child stderr truncated]\n" + stderr[-4096:]
    detail = stderr.decode("utf-8", errors="replace") or "No child stack was captured."
    note = "Operator-policy probe exceeded its original 50-second deadline.\n" + detail
    if hasattr(error, "add_note"):
        error.add_note(note)
    else:  # Python 3.10 lacks BaseException.add_note.
        sys.stderr.write(note + "\n")
