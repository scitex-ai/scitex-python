"""Flask app factory for Scholar GUI."""

import os
from pathlib import Path
from typing import Optional

from flask import Flask


def _find_crossref_db(db_path: Optional[str] = None) -> Optional[str]:
    """Auto-detect CrossRef database path."""
    if db_path and Path(db_path).exists():
        return db_path

    # Check environment variable (Docker / explicit config)
    env_path = os.environ.get("CROSSREF_DB_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # Static candidates
    candidates = [
        Path.home() / ".scitex" / "scholar" / "crossref.db",
        Path.home() / "proj" / "crossref_local" / "data" / "crossref.db",
        Path.home() / "proj" / "crossref-local" / "data" / "crossref.db",
        Path.home() / ".proj" / "crossref_local" / "data" / "crossref.db",
    ]
    for p in candidates:
        if p.exists():
            return str(p)

    # Try crossref_local module info as last resort
    try:
        import crossref_local

        info = crossref_local.info()
        p = info.get("db_path")
        if p and Path(p).exists():
            return str(p)
    except Exception:
        pass

    return None


def create_app(db_path: Optional[str] = None) -> Flask:
    """Create and configure the Flask application.

    Parameters
    ----------
    db_path : str, optional
        Path to CrossRef database. Auto-detected if not given.
    """
    static_dir = Path(__file__).parent / "static"
    template_dir = Path(__file__).parent / "templates"

    app = Flask(
        __name__,
        static_folder=str(static_dir),
        static_url_path="/static",
        template_folder=str(template_dir),
    )

    # Store DB path in app config
    resolved_db = _find_crossref_db(db_path)
    app.config["CROSSREF_DB_PATH"] = resolved_db

    # Register routes
    from ._routes_graph import register_graph_routes

    register_graph_routes(app)

    @app.route("/")
    def index():
        from flask import render_template

        return render_template(
            "scholar.html",
            db_available=resolved_db is not None,
            db_path=resolved_db or "Not found",
        )

    @app.route("/api/health")
    def health():
        from flask import jsonify

        return jsonify(
            {
                "status": "ok",
                "db_available": resolved_db is not None,
                "db_path": resolved_db,
            }
        )

    return app


# EOF
