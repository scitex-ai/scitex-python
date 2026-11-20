"""Installed CLI identity shared by human and machine discovery."""

from importlib import metadata

from scitex_dev.ecosystem import CliHelp, render_help


def cli_metadata(distribution: str) -> dict[str, str | None]:
    """Return actual installed identity, with explicit unavailable metadata."""
    try:
        installed = metadata.metadata(distribution)
    except metadata.PackageNotFoundError:
        installed = {}
    summary = installed.get("Summary") or "Summary unavailable: no installed Summary"
    return {
        "distribution": distribution,
        "version": installed.get("Version"),
        "summary": summary,
        "header": render_help(CliHelp(summary=summary, version_of=distribution)),
    }
