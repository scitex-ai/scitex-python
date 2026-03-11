#!/usr/bin/env python3
# Timestamp: 2026-02-02
# File: scitex/_dev/_dashboard/_routes.py

"""Flask routes for the dashboard."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask


def register_routes(app: Flask) -> None:
    """Register dashboard routes with Flask app."""
    from flask import jsonify, request

    from ._templates import get_dashboard_html, get_error_html

    @app.route("/")
    def index():
        """Serve the main dashboard page."""
        try:
            return get_dashboard_html()
        except Exception as e:
            return get_error_html(str(e)), 500

    @app.route("/json")
    @app.route("/api/versions")
    def api_versions():
        """Get version data as JSON (also available at /json)."""
        try:
            data = _get_all_version_data()
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/ecosystem")
    def api_ecosystem():
        """Get ecosystem registry (repos, paths, clone URLs) for AI agents."""
        from .._ecosystem import ECOSYSTEM

        repos = []
        for name, info in ECOSYSTEM.items():
            repos.append(
                {
                    "name": name,
                    "github_repo": info["github_repo"],
                    "clone_url": f"git@github.com:{info['github_repo']}.git",
                    "local_path": info["local_path"],
                    "pypi_name": info.get("pypi_name", name),
                    "import_name": info.get("import_name", ""),
                }
            )
        return jsonify({"ecosystem": repos})

    @app.route("/api/packages")
    def api_packages():
        """Get local package versions only (fast)."""
        try:
            from .._versions import list_versions

            return jsonify(list_versions())
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/fix_mismatches", methods=["POST"])
    def api_fix_mismatches():
        """Detect and fix version mismatches. POST with confirm=true to execute."""
        try:
            from .._fix import fix_mismatches

            data = request.get_json(silent=True) or {}
            result = fix_mismatches(
                hosts=data.get("hosts"),
                packages=data.get("packages"),
                local=data.get("local", True),
                remote=data.get("remote", True),
                confirm=data.get("confirm", False),
            )
            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/config")
    def api_config():
        """Get current configuration."""
        try:
            from .._config import config_to_dict, get_config_path, load_config

            config = load_config()
            return jsonify(config_to_dict(config, config_path=get_config_path()))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/refresh", methods=["POST"])
    def api_refresh():
        """Trigger a data refresh."""
        try:
            data = _get_all_version_data(force_refresh=True)
            return jsonify({"status": "ok", "data": data})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/hosts")
    def api_hosts():
        """Get host version data."""
        try:
            packages = request.args.getlist("package") or None
            hosts = request.args.getlist("host") or None
            from .._config import get_enabled_hosts, load_config
            from .._ssh import check_all_hosts

            config = load_config()
            data = check_all_hosts(packages=packages, hosts=hosts, config=config)

            # Add host metadata (hostname/IP) for display
            enabled_hosts = get_enabled_hosts(config)
            data["_meta"] = {
                h.name: {"hostname": h.hostname, "role": h.role} for h in enabled_hosts
            }
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/remotes")
    def api_remotes():
        """Get GitHub remote version data."""
        try:
            packages = request.args.getlist("package") or None
            remotes = request.args.getlist("remote") or None
            from .._github import check_all_remotes

            data = check_all_remotes(packages=packages, remotes=remotes)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/rtd")
    def api_rtd():
        """Get Read the Docs build status."""
        try:
            packages = request.args.getlist("package") or None
            versions = request.args.getlist("version") or None
            from .._rtd import check_all_rtd

            data = check_all_rtd(packages=packages, versions=versions)
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)}), 500


def _get_all_version_data(force_refresh: bool = False) -> dict[str, Any]:
    """Get all version data from all sources.

    Parameters
    ----------
    force_refresh : bool
        If True, bypass any caching.

    Returns
    -------
    dict
        Combined version data.
    """
    from .._config import get_enabled_hosts, get_enabled_remotes, load_config
    from .._github import check_all_remotes
    from .._ssh import check_all_hosts
    from .._versions import list_versions

    config = load_config()

    # Get local versions
    packages_data = list_versions()

    # Get host versions (if any hosts configured)
    hosts_data = {}
    enabled_hosts = get_enabled_hosts(config)
    if enabled_hosts:
        try:
            hosts_data = check_all_hosts(config=config)
        except Exception:
            pass

    # Get remote versions (if any remotes configured)
    remotes_data = {}
    enabled_remotes = get_enabled_remotes(config)
    if enabled_remotes:
        try:
            remotes_data = check_all_remotes(config=config)
        except Exception:
            pass

    return {
        "packages": packages_data,
        "hosts": hosts_data,
        "remotes": remotes_data,
    }


# EOF
