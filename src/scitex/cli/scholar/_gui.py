"""CLI command for launching Scholar GUI."""

from __future__ import annotations

import click


@click.command()
@click.option("--port", type=int, default=5051, help="Port to serve on (default: 5051)")
@click.option("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1)")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
@click.option("--db", type=click.Path(), default=None, help="CrossRef database path")
def gui(port, host, no_browser, db):
    r"""Launch Scholar GUI in browser.

    \b
    Interactive web interface for:
      - Citation graph visualization
      - Paper library management
      - Literature search
      - Metadata enrichment

    \b
    Examples:
      scitex scholar gui
      scitex scholar gui --port 8080
      scitex scholar gui --db /path/to/crossref.db
    """
    try:
        from flask import Flask as _  # noqa: F401
    except ImportError:
        click.secho("Flask is required: pip install flask", fg="red", err=True)
        raise SystemExit(1)

    from scitex.scholar.gui import launch

    launch(
        port=port,
        host=host,
        open_browser=not no_browser,
        db_path=db,
    )


# EOF
