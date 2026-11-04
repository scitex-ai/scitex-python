"""Construction-time CLI declarations and independent operator preferences."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CliExposureSnapshot:
    """Keep inert installed evidence separate from configured preference."""

    rows: tuple
    policy: object
    retired: frozenset[str]

    def allows(self, owner: str) -> bool:
        """Consult only the CLI axis, not Python/MCP/skills capability or preference."""
        return self.policy.is_enabled(owner, "cli")


def load_cli_snapshot() -> CliExposureSnapshot:
    """Read one immutable construction view without importing any CLI provider."""
    from scitex_dev._ecosystem._core import ECOSYSTEM
    from scitex_dev.cli_providers import list_cli_providers

    try:
        from scitex_dev.exposure import load_exposure_policy
    except ImportError as error:
        raise RuntimeError(
            "CLI operator policy requires scitex_dev.exposure.load_exposure_policy; "
            "install a SciTeX Dev release providing that public capability"
        ) from error
    retired = {name for name, info in ECOSYSTEM.items() if info.get("archived")}
    retired.update({"scitex-app", "scitex-ui", "scitex-orochi", "scitex-audit"})
    rows = tuple(list_cli_providers())
    try:
        policy = load_exposure_policy()
    except (TypeError, ValueError) as error:
        from click import ClickException

        raise ClickException(
            "CLI exposure preferences are invalid. Check package configuration "
            "and boolean surface settings "
            "in SCITEX_DEV_CONFIG and SCITEX_DEV_KNOB_STATE "
            "(or their SciTeX Dev default files)."
        ) from error
    return CliExposureSnapshot(rows, policy, frozenset(retired))
