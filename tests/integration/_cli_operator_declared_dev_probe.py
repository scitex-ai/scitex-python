"""Real owned installed declarations for the existing canonical Dev composition."""

import importlib
import json
import os
import sys
from importlib.metadata import distribution
from pathlib import Path


def main():
    source, directory, case = sys.argv[1:]
    owned = Path(directory).resolve()
    for key in tuple(os.environ):
        if key.startswith("SCITEX_"):
            del os.environ[key]
    os.environ.update(
        HOME=str(owned), SCITEX_DIR=str(owned / "state"), XDG_RUNTIME_DIR=str(owned)
    )
    sys.path.insert(0, source)
    config, state = owned / "config.yaml", owned / "knobs.json"
    config.write_text("packages: []\n")
    state.write_text(
        json.dumps({"cli": {"scitex-dev": False}}) if case == "owner_false" else "{}"
    )
    os.environ.update(SCITEX_DEV_CONFIG=str(config), SCITEX_DEV_KNOB_STATE=str(state))
    site = owned / "metadata"
    site.mkdir()
    target = "scitex_dev._cli:main"
    if case == "none":
        target = "none"
    elif case == "invalid":
        target = "not/a:target"
    elif case == "other_target":
        target = "scitex_dev._cli:unrelated"
    owner = "scitex-foreign-developer" if case == "foreign_owner" else "scitex-dev"
    module = "scitex_dev/_cli/__init__.py"
    # Real owner source bytes, recorded in an isolated metadata fixture. They
    # are never put on sys.path: invocation uses the actual installed Dev.
    original = Path(distribution("scitex-dev").locate_file(module))
    copied = site / module
    copied.parent.mkdir(parents=True)
    copied.write_bytes(original.read_bytes())
    for suffix in range(2 if case == "ambiguous" else 1):
        info = site / f"{owner.replace('-', '_')}-{suffix + 1}.0.dist-info"
        info.mkdir()
        (info / "METADATA").write_text(
            f"Metadata-Version: 2.1\nName: {owner}\nVersion: {suffix + 1}.0\n"
        )
        explicit = "" if case == "legacy" else f"[scitex.cli]\ndev = {target}\n"
        (info / "entry_points.txt").write_text(
            f"[console_scripts]\n{owner} = scitex_dev._cli:main\n{explicit}"
        )
        (info / "RECORD").write_text(module + ",,\n")

    def guard(event, args):
        if event in {"socket.connect", "socket.bind", "subprocess.Popen"}:
            raise AssertionError("Dev declaration inspection attempted provider work")
        if event == "open" and not isinstance(args[0], int):
            mode, flags = args[1:3]
            write = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int)
                and flags
                & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            if write and not Path(args[0]).resolve().is_relative_to(owned):
                raise AssertionError(
                    "Dev declaration inspection attempted an unowned write"
                )

    sys.addaudithook(guard)
    from click.testing import CliRunner
    from scitex_dev.cli_providers import list_cli_providers
    from scitex_dev.exposure import load_exposure_policy

    from scitex.cli._exposure import CliExposureSnapshot
    from scitex.cli._lazy_subcommands import build_lazy_subcommands
    from scitex.cli.main import LazyGroup

    rows = tuple(list_cli_providers(path=[site]))
    snapshot = CliExposureSnapshot(
        rows, load_exposure_policy(config, knob_state_path=state), frozenset()
    )
    specs = build_lazy_subcommands(str(Path(source) / "scitex/cli"), snapshot=snapshot)
    expected = case in {"legacy", "declared"}
    assert ("dev" in specs) is expected, (case, rows, specs.get("dev"))
    if expected:
        group = LazyGroup(
            name="owned-root",
            lazy_subcommands={"dev": specs["dev"]},
            exposure_snapshot=snapshot,
        )
        actual = importlib.import_module("scitex_dev._cli").main
        before = (actual.name, tuple(actual.commands.items()))
        projected = group.get_command(None, "dev")
        assert projected._owner is actual
        assert projected._upkeep is actual.get_command(None, "dev")
        assert projected.get_command(None, "ci") is actual.get_command(None, "ci")
        result = CliRunner().invoke(group, ["dev", "--help"])
        assert result.exit_code == 0, (result.output, repr(result.exception))
        assert before == (actual.name, tuple(actual.commands.items()))
    sys.stdout.write(
        json.dumps(
            {"case": case, "admitted": expected, "statuses": [r.status for r in rows]}
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
