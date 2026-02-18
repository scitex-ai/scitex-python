"""Scholar GUI - Interactive Flask app for scientific literature management.

Launch via CLI:
    scitex scholar gui
    scitex scholar gui --port 8080

Or from Python:
    from scitex.scholar.gui import launch
    launch(port=5051)
"""

from pathlib import Path
from typing import Optional


def launch(
    port: int = 5051,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    db_path: Optional[str] = None,
):
    """Launch the Scholar GUI in a browser.

    Parameters
    ----------
    port : int
        Port to serve on (default: 5051).
    host : str
        Host to bind to (default: 127.0.0.1).
    open_browser : bool
        Whether to open a browser tab automatically.
    db_path : str, optional
        Path to CrossRef SQLite database. Auto-detected if not given.
    """
    from ._app import create_app

    app = create_app(db_path=db_path)
    url = f"http://{host}:{port}"

    if open_browser:
        import threading
        import webbrowser

        threading.Timer(1.0, webbrowser.open, args=[url]).start()

    print(f"Scholar GUI running at {url}")
    print("Press Ctrl+C to stop.")

    app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)


__all__ = ["launch"]

# EOF
