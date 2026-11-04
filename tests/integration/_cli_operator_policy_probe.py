"""Guarded real Click/installed-metadata fixtures for CLI operator preferences."""

import importlib
import json
import os
import re
import sys
from pathlib import Path


def provider(
    site, name="owned", owner="scitex-owned-cli", declaration="owned_cli:main"
):
    site.mkdir(exist_ok=True)
    module = site / "owned_cli.py"
    module.write_text(
        "import click\nfrom pathlib import Path\n"
        f"Path({str(site / 'imported')!r}).touch()\n"
        "@click.group()\ndef main():\n    pass\n"
        "@main.command()\n@click.argument('value',required=False,default='owned-default')\n"
        "@click.option('--exit-code',type=int,default=0)\ndef echo(value,exit_code):\n"
        "    click.echo(value)\n    raise SystemExit(exit_code)\n"
    )
    info = site / (owner.replace("-", "_") + "-1.0.dist-info")
    info.mkdir()
    (info / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {owner}\nVersion: 1.0\n"
    )
    (info / "entry_points.txt").write_text(
        f"[console_scripts]\n{owner} = owned_cli:main\n[scitex.cli]\n{name} = {declaration}\n"
    )
    (info / "RECORD").write_text("owned_cli.py,,\n")


def names(result, mode):
    if mode == "json":
        return set(json.loads(result.output)["data"]["commands"])
    if mode == "completion":
        return {
            line.split(",", 1)[1]
            for line in result.output.splitlines()
            if line.startswith("plain,")
        }
    return set(re.findall(r"^  ([a-z][a-z0-9-]*)\s{2,}\S", result.output, re.MULTILINE))


def main():
    source, directory, operation = sys.argv[1:]
    owned = Path(directory).resolve()
    sys.path.insert(0, source)
    for key in tuple(os.environ):
        if key.startswith("SCITEX_"):
            del os.environ[key]
    os.environ.update(
        HOME=str(owned),
        TMPDIR=str(owned),
        XDG_RUNTIME_DIR=str(owned),
        SCITEX_DIR=str(owned / "state"),
    )
    config, state = owned / "config.yaml", owned / "knobs.json"
    config.write_text("packages: []\n")
    state.write_text("{}")
    os.environ.update(SCITEX_DEV_CONFIG=str(config), SCITEX_DEV_KNOB_STATE=str(state))
    site = owned / "installed"
    provider(
        site,
        name="ci" if operation == "owner_collision" else "owned",
        declaration="none" if operation == "metadata_none" else "owned_cli:main",
    )
    # A real Python-only installed distribution cannot acquire a CLI by enablement.
    absent = site / "scitex_owned_library-1.0.dist-info"
    absent.mkdir()
    (absent / "METADATA").write_text(
        "Metadata-Version: 2.1\nName: scitex-owned-library\nVersion: 1.0\n"
    )
    (absent / "RECORD").write_text("")
    sys.path.insert(0, str(site))
    importlib.invalidate_caches()
    if operation in {"declined", "reverse_snapshot"}:
        config.write_text(
            json.dumps(
                {"packages": [{"name": "scitex-owned-cli", "cli_enabled": True}]}
            )
        )
        state.write_text(
            json.dumps(
                {
                    "cli": {
                        "scitex-sdk": False,
                        "scitex-dev": False,
                        "scitex-owned-cli": False,
                        "scitex-owned-library": True,
                    }
                }
            )
        )
    elif operation == "owner_collision":
        state.write_text(json.dumps({"cli": {"scitex-owned-cli": False}}))
    elif operation == "cross_surface":
        state.write_text(
            json.dumps(
                {
                    "mcp": {
                        "scitex-sdk": False,
                        "scitex-dev": False,
                        "scitex-owned-cli": False,
                    },
                    "skills": {
                        "scitex-sdk": False,
                        "scitex-dev": False,
                        "scitex-owned-cli": False,
                    },
                }
            )
        )
    elif operation == "config_declined":
        config.write_text(
            json.dumps(
                {"packages": [{"name": "scitex-owned-cli", "cli_enabled": False}]}
            )
        )
    elif operation == "metadata_none":
        state.write_text(json.dumps({"cli": {"scitex-owned-cli": True}}))
    elif operation == "malformed_config":
        config.write_text("packages: not-a-list\n")
    elif operation == "malformed":
        state.write_text(json.dumps({"cli": {"scitex-owned-cli": "false"}}))

    def guard(event, arguments):
        if event in {"socket.connect", "socket.bind", "subprocess.Popen"}:
            raise AssertionError("CLI inspection attempted an external operation")
        if event == "open" and not isinstance(arguments[0], int):
            mode, flags = arguments[1:3]
            write = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int)
                and flags
                & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            if write and not Path(arguments[0]).resolve().is_relative_to(owned):
                raise AssertionError(
                    f"CLI inspection attempted an unowned write: {arguments[0]}"
                )
        if event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.chown"}:
            if not isinstance(arguments[0], int) and not Path(
                arguments[0]
            ).resolve().is_relative_to(owned):
                raise AssertionError("CLI inspection attempted an unowned mutation")

    sys.addaudithook(guard)
    from click.testing import CliRunner

    import scitex

    peers = (
        "scitex_sdk",
        "scitex_cards",
        "scitex_clew",
        "scitex_ssh",
        "scitex_writer",
        "owned_cli.py",
    )
    events, reads = [], []

    def profile(frame, event, value):
        if event != "call":
            return
        filename = frame.f_code.co_filename.replace("\\", "/")
        if frame.f_code.co_name == "<module>" and any(
            "/" + name + "/" in filename or filename.endswith("/" + name)
            for name in peers
        ):
            events.append(filename)
        if (
            filename.endswith("/scitex_dev/exposure/__init__.py")
            and frame.f_code.co_name == "load_exposure_policy"
        ):
            reads.append(filename)

    sys.setprofile(profile)
    try:
        module = importlib.import_module("scitex.cli.main")
    except (ValueError, TypeError) as error:
        assert operation in {"malformed", "malformed_config"}
        assert not events and not (site / "imported").exists()
        sys.setprofile(None)
        sys.stdout.write(
            json.dumps({"malformed_refused": True, "error": type(error).__name__})
            + "\n"
        )
        return
    cli = module.cli
    runner = CliRunner()

    def invoke(group, arguments, **kwargs):
        return runner.invoke(group, arguments, prog_name="scitex", **kwargs)

    def inspect(group):
        result = {}
        for mode, arguments in [
            ("help", ["--help"]),
            ("json", ["--json"]),
            ("completion", []),
        ]:
            options = (
                {
                    "env": {
                        "_SCITEX_COMPLETE": "bash_complete",
                        "COMP_WORDS": "scitex ",
                        "COMP_CWORD": "1",
                    }
                }
                if mode == "completion"
                else {}
            )
            value = invoke(group, arguments, **options)
            assert value.exit_code == 0, value.output
            result[mode] = names(value, mode)
        assert result["help"] == result["json"] == result["completion"]
        return result["json"]

    initial = inspect(cli)
    assert not events and len(reads) == 1
    from scitex_dev.cli_providers import list_cli_providers

    raw = list_cli_providers(package="scitex-owned-cli")
    assert any(
        row.status == ("none" if operation == "metadata_none" else "declared")
        for row in raw
    )
    assert "owned-library" not in initial
    if operation in {"declined", "reverse_snapshot"}:
        assert not {"sdk", "dev", "owned"}.intersection(initial)
        for path in [
            ["app", "--help"],
            ["ui", "--help"],
            ["skills", "--help"],
            ["dev", "skills", "--help"],
            ["dev", "dev", "skills", "--help"],
        ]:
            assert invoke(cli, path).exit_code != 0
        assert not (site / "imported").exists()
        # CLI admission never disables an independent explicit Python import.
        if operation == "declined":
            assert importlib.import_module("owned_cli").main.name == "main"
            assert importlib.import_module("scitex.app") is importlib.import_module(
                "scitex_sdk.app"
            )
        if operation == "reverse_snapshot":
            state.write_text("{}")
            updated = importlib.reload(module).cli
            assert {"sdk", "dev", "owned"}.issubset(inspect(updated))
            assert inspect(cli) == initial
            dev = updated.get_command(None, "dev")
            assert dev._exposure_snapshot is updated._exposure_snapshot
            legacy = invoke(updated, ["dev", "dev", "skills", "--help"])
            assert legacy.exit_code == 0, (legacy.output, repr(legacy.exception))
            assert invoke(cli, ["dev", "dev", "skills", "--help"]).exit_code != 0
            assert len(reads) == 2
    elif operation in {"metadata_none", "config_declined"}:
        assert "owned" not in initial
        assert invoke(cli, ["owned", "--help"]).exit_code != 0
        assert not (site / "imported").exists()
    elif operation == "owner_collision":
        assert "ci" not in initial
        dev = cli.get_command(None, "dev")
        assert dev.get_command(None, "ci") is dev._owner.get_command(None, "ci")
        assert dev.get_command(None, "ci") is not None
        assert invoke(cli, ["dev", "ci", "--help"]).exit_code == 0
    else:
        assert {"sdk", "dev", "owned"}.issubset(initial)
        assert invoke(cli, ["owned", "--help"]).exit_code == 0
        import owned_cli

        assert cli.get_command(None, "owned") is owned_cli.main
        assert owned_cli.main.name == "main"
        echoed = invoke(cli, ["owned", "echo", "--exit-code", "7"])
        assert (echoed.exit_code, echoed.output) == (7, "owned-default\n")
        if operation == "snapshot":
            first_dev = cli.get_command(None, "dev")
            first_owner = first_dev._owner
            assert first_dev.get_command(None, "introspect") is not None
            assert len(reads) == 1
            state.write_text(
                json.dumps(
                    {
                        "cli": {
                            "scitex-sdk": False,
                            "scitex-owned-cli": False,
                            "scitex-introspect": False,
                        }
                    }
                )
            )
            assert inspect(cli) == initial
            updated = importlib.reload(module).cli
            assert len(reads) == 2
            new_names = inspect(updated)
            assert (
                "sdk" not in new_names
                and "owned" not in new_names
                and "dev" in new_names
            )
            second_dev = updated.get_command(None, "dev")
            assert second_dev is not first_dev and second_dev._owner is first_owner
            assert second_dev._exposure_snapshot is updated._exposure_snapshot
            assert second_dev.get_command(None, "introspect") is None
            assert first_dev.get_command(None, "introspect") is not None
            for path in [
                ["introspect", "--help"],
                ["dev", "introspect", "--help"],
                ["dev", "dev", "introspect", "--help"],
            ]:
                assert invoke(updated, path).exit_code != 0
                original = invoke(cli, path)
                assert original.exit_code == 0, (
                    path,
                    original.output,
                    repr(original.exception),
                )
            state.write_text(json.dumps({"cli": {"scitex-dev": False}}))
            third = importlib.reload(module).cli
            assert len(reads) == 3 and "dev" not in inspect(third)
            for path in [
                ["skills", "--help"],
                ["dev", "skills", "--help"],
                ["dev", "dev", "skills", "--help"],
            ]:
                assert invoke(third, path).exit_code != 0
            for group, expected in [
                (updated, new_names),
                (cli, initial),
                (updated, new_names),
            ]:
                assert inspect(group) == expected
            assert first_dev.get_command(
                None, "skills"
            ) is first_dev._upkeep.get_command(None, "skills")
            assert second_dev.get_command(
                None, "skills"
            ) is first_dev._upkeep.get_command(None, "skills")
            assert len(reads) == 3
    sys.setprofile(None)
    sys.stdout.write(
        json.dumps(
            {
                "operation": operation,
                "names": sorted(initial),
                "construction_reads": len(reads),
                "metadata_peer_execution": [],
            }
        )
        + "\n"
    )


if __name__ == "__main__":
    main()
