#!/usr/bin/env python3
# Timestamp: "2026-02-26 11:12:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-python/src/scitex/_dev/_dashboard/_app.py

# Timestamp: 2026-02-02

"""Flask application factory for the dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application.

    Returns
    -------
    Flask
        Configured Flask application.
    """
    try:
        from flask import Flask
    except ImportError as e:
        raise ImportError(
            "Flask is required for the dashboard. Install with: pip install flask"
        ) from e

    from pathlib import Path

    static_folder = Path(__file__).parent / "static"
    app = Flask(__name__, static_folder=str(static_folder), static_url_path="/static")

    # Disable JSON key sorting to preserve insertion order (Flask 2.2+)
    app.json.sort_keys = False

    # Register routes
    from ._routes import register_routes

    register_routes(app)

    return app


def _kill_process_on_port(port: int) -> None:
    """Kill any process using the specified port.

    Parameters
    ----------
    port : int
        Port number to free up.
    """
    import subprocess
    import sys

    try:
        if sys.platform == "win32":
            # Windows: use netstat and taskkill
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                check=False,
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(
                        ["taskkill", "/F", "/PID", pid],
                        capture_output=True,
                        check=False,
                    )
                    print(f"Killed process {pid} on port {port}")
        else:
            # Unix: use lsof
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.stdout.strip():
                pids = result.stdout.strip().split("\n")
                for pid in pids:
                    subprocess.run(
                        ["kill", "-9", pid], capture_output=True, check=False
                    )
                    print(f"Killed process {pid} on port {port}")
    except Exception as e:
        print(f"Warning: Could not kill process on port {port}: {e}")


def run_dashboard(
    host: str = "127.0.0.1",
    port: int = 5000,
    debug: bool = False,
    open_browser: bool = True,
    force: bool = False,
) -> None:
    """Run the Flask dashboard server.

    Parameters
    ----------
    host : str
        Host to bind to. Default "127.0.0.1".
    port : int
        Port to listen on. Default 5000.
    debug : bool
        Enable Flask debug mode.
    open_browser : bool
        Open browser automatically.
    force : bool
        Kill existing process using the port if any.
    """
    if force:
        _kill_process_on_port(port)

    app = create_app()

    url = f"http://{host}:{port}"
    print(f"Starting SciTeX Version Dashboard at {url}")
    print("Press Ctrl+C to stop.")

    if open_browser:
        import threading
        import webbrowser

        def open_url():
            import time

            time.sleep(1)  # Wait for server to start
            webbrowser.open(url)

        threading.Thread(target=open_url, daemon=True).start()

    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped.")


def run_background(
    host: str = "127.0.0.1",
    port: int = 5000,
    force: bool = False,
) -> None:
    """Launch the dashboard as a detached background subprocess.

    Parameters
    ----------
    host : str
        Host to bind to. Default "127.0.0.1".
    port : int
        Port to listen on. Default 5000.
    force : bool
        Kill existing process using the port if any.
    """
    import subprocess
    import sys
    from pathlib import Path

    cache_dir = Path.home() / ".cache" / "scitex"
    cache_dir.mkdir(parents=True, exist_ok=True)

    log_path = cache_dir / "dashboard.log"
    pid_path = cache_dir / "dashboard.pid"

    inline_script = (
        f"from scitex._dev._dashboard._app import run_dashboard; "
        f"run_dashboard(host={host!r}, port={port!r}, debug=False, open_browser=False, force={force!r})"
    )

    log_file = open(log_path, "a")
    proc = subprocess.Popen(
        [sys.executable, "-c", inline_script],
        stdout=log_file,
        stderr=log_file,
        start_new_session=True,
    )

    pid_path.write_text(str(proc.pid))

    # print("Dashboard started in background.")
    # print(f"  PID:  {proc.pid}")
    # print(f"  URL:  http://{host}:{port}")
    # print(f"  Log:  {log_path}")
    # print(f"  PID file: {pid_path}")


def stop_dashboard() -> bool:
    """Stop a running background dashboard process.

    Returns
    -------
    bool
        True if the process was successfully stopped, False otherwise.
    """
    import os
    import signal
    from pathlib import Path

    pid_path = Path.home() / ".cache" / "scitex" / "dashboard.pid"

    if not pid_path.exists():
        print("No dashboard PID file found. Is the dashboard running in background?")
        return False

    try:
        pid = int(pid_path.read_text().strip())
        os.kill(pid, signal.SIGTERM)
        pid_path.unlink()
        print(f"Dashboard (PID {pid}) stopped.")
        return True
    except ProcessLookupError:
        print("Process not found. Removing stale PID file.")
        pid_path.unlink(missing_ok=True)
        return False
    except Exception as e:
        print(f"Error stopping dashboard: {e}")
        return False


# EOF
