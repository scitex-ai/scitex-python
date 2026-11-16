"""Owned, real-protocol probes for the umbrella's construction-time admission."""

import asyncio
import hashlib
import importlib
import json
import os
import sys
from pathlib import Path


def _skill_provider(site, owner, module, namespace, text):
    package = site / module
    (package / "_skills" / namespace).mkdir(parents=True)
    (package / "__init__.py").write_text(
        f"from pathlib import Path\nPath({str(package / 'imported-marker')!r}).write_text('imported')\n"
        "raise AssertionError('skill provider imported')\n"
    )
    (package / "_skills" / namespace / "SKILL.md").write_text(
        f"---\nname: {namespace}\ndescription: Owned guide fixture.\n---\n{text}\n"
    )
    metadata = site / (owner.replace("-", "_") + "-1.0.dist-info")
    metadata.mkdir()
    (metadata / "METADATA").write_text(
        f"Metadata-Version: 2.1\nName: {owner}\nVersion: 1.0\n"
    )
    (metadata / "entry_points.txt").write_text(
        f"[scitex_dev.skills]\n{namespace} = {module}\n"
    )
    (metadata / "RECORD").write_text(
        f"{module}/__init__.py,,\n{module}/_skills/{namespace}/SKILL.md,,\n"
    )


def _text(result):
    return "\n".join(getattr(content, "text", "") for content in result.content)


def _files(root):
    return {
        str(path.relative_to(root)): (
            hashlib.sha256(path.read_bytes()).hexdigest(),
            path.stat().st_mtime_ns,
        )
        for path in root.rglob("*")
        if path.is_file()
    }


async def inspect(operation, owned):
    # All real providers are declined before the ordinary umbrella import.
    from scitex_dev._ecosystem import ECOSYSTEM

    disabled = dict.fromkeys([*ECOSYSTEM, "scitex", "scitex-cloud"], False)
    if operation == "schema":
        disabled.update({"scitex": True, "scitex-cloud": True, "figrecipe": True})
        fixture = owned / "providers"
        cloud = fixture / "scitex_cloud"
        cloud.mkdir(parents=True)
        (cloud / "__init__.py").write_text("")
        (cloud / "_mcp_server.py").write_text(
            "from fastmcp import FastMCP\nfrom scitex_dev import RESULT_SCHEMA\nmcp=FastMCP('owned-schema-provider')\n"
            "@mcp.tool(output_schema=RESULT_SCHEMA)\ndef owned_result():\n    return {'success': True, 'data': {'owned': 'result'}}\n"
            "@mcp.tool(output_schema={'type':'object','properties':{'value':{'type':'string'}},'required':['value']})\n"
            "def owned_raw():\n    return {'value': 'owned raw'}\n"
            "@mcp.tool()\ndef owned_untyped_raw():\n    return 'owned untyped raw'\n"
        )
        fig = fixture / "figrecipe"
        (fig / "_mcp").mkdir(parents=True)
        (fig / "__init__.py").write_text("")
        (fig / "_mcp/__init__.py").write_text("")
        (fig / "_mcp/server.py").write_text(
            "from fastmcp import FastMCP\nmcp=FastMCP('owned-fig-bridge')\n"
            "@mcp.tool()\ndef fr_owned_untyped_raw():\n    return 'owned bridged raw'\n"
        )
        sys.path.insert(0, str(fixture))
        importlib.invalidate_caches()
    knobs = owned / "knobs.json"
    knobs.write_text(json.dumps({"mcp": disabled}))
    config = owned / "config.yaml"
    config.write_text("packages: []\n")
    os.environ.update(SCITEX_DEV_CONFIG=str(config), SCITEX_DEV_KNOB_STATE=str(knobs))
    from fastmcp import Client, FastMCP

    from scitex import _mcp as umbrella
    from scitex._mcp._exposure import configure_discovery, load_package_policy
    from scitex._mcp._peer_extras import register_peer_extras
    from scitex._mcp._resources import register_resources
    from scitex._mcp._umbrella_tools import register_umbrella_tools

    async with Client(umbrella.mcp) as client:
        if operation != "schema":
            assert await client.list_tools() == []
            assert await client.list_resources() == []
        else:
            from scitex_dev import RESULT_SCHEMA

            tools = {tool.name: tool for tool in await client.list_tools()}
            assert tools["cloud_owned_result"].outputSchema == RESULT_SCHEMA, tools[
                "cloud_owned_result"
            ].outputSchema
            assert tools["cloud_owned_raw"].outputSchema["required"] == ["value"]
            from click import unstyle
            from click.testing import CliRunner

            from scitex.cli.mcp import _format_signature, list_tools

            assert "Result" not in unstyle(
                _format_signature(tools["cloud_owned_untyped_raw"])
            )
            assert unstyle(_format_signature(tools["cloud_owned_result"])).endswith(
                " -> Result"
            )
            assert unstyle(_format_signature(tools["cloud_owned_raw"])).endswith(
                " -> schema-defined output"
            )
            assert unstyle(
                _format_signature(tools["cloud_owned_untyped_raw"])
            ).endswith(" -> output unspecified")
            catalog = CliRunner().invoke(list_tools, ["--json"])
            assert catalog.exit_code == 0, (catalog.output, repr(catalog.exception))
            payload = json.loads(catalog.output)
            listed = {
                row["name"]: row
                for module in payload["modules"].values()
                for row in module["tools"]
            }
            for name in (
                "cloud_owned_result",
                "cloud_owned_raw",
                "cloud_owned_untyped_raw",
                "plt_stx_owned_untyped_raw",
            ):
                assert listed[name]["output_schema"] == tools[name].outputSchema
            assert (
                payload["result_envelope_scope"]
                == "reference only; each tool retains its own output_schema"
            )
            assert tools["cloud_owned_untyped_raw"].outputSchema is None
            assert tools["plt_stx_owned_untyped_raw"].outputSchema is None, tools[
                "plt_stx_owned_untyped_raw"
            ].outputSchema
            assert "owned bridged raw" in _text(
                await client.call_tool("plt_stx_owned_untyped_raw", {})
            )
            assert "owned raw" in _text(await client.call_tool("cloud_owned_raw", {}))
            return {
                "actual_admitted_result_schema": True,
                "explicit_raw_schema_preserved": True,
            }

    def policy(**enabled):
        return load_package_policy({**disabled, **enabled})

    if operation == "snapshot":
        from scitex_dev.exposure import load_exposure_policy

        knobs.write_text(
            json.dumps(
                {
                    "mcp": {"owned-unknown": False},
                    "cli": {"owned-unknown": True},
                    "skills": {"owned-unknown": True},
                }
            )
        )
        resolved = load_exposure_policy(config, knob_state_path=knobs)
        selected = load_package_policy(resolved)
        knobs.write_text(json.dumps({"mcp": {"owned-unknown": True}}))
        observed = (
            selected.allows("owned-unknown", "unknown"),
            resolved.is_enabled("owned-unknown", "cli"),
            resolved.is_enabled("owned-unknown", "skills"),
        )
        assert observed == (False, True, True)
        knobs.write_text(
            json.dumps(
                {
                    "mcp": {"owned-unknown": True},
                    "cli": {"owned-unknown": False},
                    "skills": {"owned-unknown": False},
                }
            )
        )
        independent = load_exposure_policy(config, knob_state_path=knobs)
        assert load_package_policy(independent).allows("owned-unknown", "unknown")
        assert not independent.is_enabled("owned-unknown", "cli")
        assert not independent.is_enabled("owned-unknown", "skills")
        os.environ["SCITEX_MCP_USE_APP"] = "0"
        snapshot = policy(**{"scitex-sdk": True})
        os.environ["SCITEX_MCP_USE_APP"] = "1"
        assert not snapshot.allows("scitex-sdk", "app")
        assert snapshot.allows("scitex-sdk", "ui")
        assert not policy(**{"scitex-sdk": False}).allows("scitex-sdk", "ui")
        return {
            "snapshot_stable": True,
            "unknown_owner_decline": True,
            "axes_independent": True,
        }

    if operation in {"generic", "search"}:
        fixture = owned / "providers"
        fixture.mkdir()
        allowed = fixture / "owned_allowed_peer"
        allowed.mkdir()
        (allowed / "__init__.py").write_text("")
        (allowed / "_mcp_server.py").write_text(
            "from fastmcp import FastMCP\nmcp=FastMCP('owned-peer')\n"
            "@mcp.tool()\ndef ping() -> str:\n    return 'owned-pong'\n"
        )
        blocked = fixture / "owned_blocked_peer"
        blocked.mkdir()
        (blocked / "__init__.py").write_text(
            f"from pathlib import Path\nPath({str(blocked / 'imported-marker')!r}).write_text('imported')\n"
            "raise AssertionError('declined provider imported')\n"
        )
        sys.path.insert(0, str(fixture))
        importlib.invalidate_caches()
        server = FastMCP("owned-native-mounts")
        selected = policy(**{"scitex-sdk": True})
        registry = lambda: [
            ("scitex-sdk", "owned_allowed_peer", "app"),
            ("scitex-sdk", "owned_allowed_peer", "ui"),
            ("scitex-browser", "owned_blocked_peer", "blocked"),
        ]
        umbrella.register_all_tools(
            server, iter_registry=registry, package_policy=selected
        )
        assert (
            "owned_blocked_peer" not in sys.modules
            and not (blocked / "imported-marker").exists()
        )
        if operation == "search":
            os.environ.update(
                SCITEX_MCP_DISCOVERY="search", SCITEX_MCP_SEARCH_LIMIT="1"
            )
            configure_discovery(server)
        async with Client(server) as client:
            names = {tool.name for tool in await client.list_tools()}
            if operation == "generic":
                assert names == {"app_ping", "ui_ping"}
                assert _text(await client.call_tool("app_ping", {})) == "owned-pong"
            else:
                assert names == {"search_tools", "call_tool"}
                assert "app_ping" in _text(
                    await client.call_tool("search_tools", {"pattern": "app_ping"})
                )
                denied = False
                try:
                    await client.call_tool(
                        "call_tool", {"name": "blocked_ping", "arguments": {}}
                    )
                except Exception:
                    denied = True
                assert denied
        assert not (blocked / "imported-marker").exists()
        return {"names": sorted(names), "blocked_provider_imported": False}

    if operation == "inline":
        server = FastMCP("owned-adapter-preferences")
        selected = policy(scitex=True)
        register_umbrella_tools(server, package_policy=selected)
        register_peer_extras(server, package_policy=selected)
        async with Client(server) as client:
            names = {tool.name for tool in await client.list_tools()}
        assert names == {"usage_show", "usage_list"}
        denied = FastMCP("owned-root-declined")
        register_umbrella_tools(denied, package_policy=policy(**{"scitex-dev": True}))
        register_peer_extras(denied, package_policy=policy(**{"scitex-dev": True}))
        async with Client(denied) as client:
            assert await client.list_tools() == []
        return {"root_only": sorted(names), "root_decline_blocks_adapters": True}

    if operation == "skills":
        site = owned / "skill-providers"
        site.mkdir()
        _skill_provider(
            site, "owned-guide-a", "owned_skill_a", "shared-guide", "OWNED GUIDE A"
        )
        _skill_provider(
            site, "owned-guide-b", "owned_skill_b", "shared-guide", "OWNED GUIDE B"
        )
        sys.path.insert(0, str(site))
        importlib.invalidate_caches()
        server = FastMCP("owned-guide-adapter")
        register_umbrella_tools(
            server, package_policy=policy(scitex=True, **{"scitex-dev": True})
        )
        async with Client(server) as client:
            tools = {tool.name: tool for tool in await client.list_tools()}
            assert "owner" in tools["skills_get"].inputSchema["properties"]
            listing = _text(
                await client.call_tool("skills_list", {"package": "owned-guide-a"})
            )
            assert "owned-guide-a" in listing and "shared-guide" in listing, listing
            for owner, marker in [
                ("owned-guide-a", "OWNED GUIDE A"),
                ("owned-guide-b", "OWNED GUIDE B"),
            ]:
                result = _text(
                    await client.call_tool(
                        "skills_get", {"package": "shared-guide", "owner": owner}
                    )
                )
                assert marker in result
            for arguments in [
                {"package": "shared-guide"},
                {"package": "shared-guide", "owner": "wrong-owner"},
                {
                    "package": "shared-guide",
                    "owner": "owned-guide-a",
                    "name": "../escape",
                },
            ]:
                result = _text(await client.call_tool("skills_get", arguments))
                assert "OWNED GUIDE A" not in result and "OWNED GUIDE B" not in result
        assert "owned_skill_a" not in sys.modules and "owned_skill_b" not in sys.modules
        assert not (site / "owned_skill_a/imported-marker").exists()
        assert not (site / "owned_skill_b/imported-marker").exists()
        return {
            "owner_roundtrip": True,
            "no_provider_import": True,
            "wrong_owner_collision_traversal_refused": True,
        }

    if operation == "docs":
        site = owned / "doc-providers"
        package = site / "owned_docs"
        docs = package / "_sphinx_html"
        docs.mkdir(parents=True)
        (package / "__init__.py").write_text(
            f"from pathlib import Path\nPath({str(package / 'imported-marker')!r}).write_text('imported')\n"
            "raise AssertionError('docs provider imported')\n"
        )
        (docs / "index.html").write_text(
            "<html><title>Owned Documentation</title></html>"
        )
        (docs / "manifest.json").write_text(
            json.dumps(
                {
                    "package": "owned-docs",
                    "version": "1.0",
                    "pages": [
                        {
                            "name": "index",
                            "title": "Owned Documentation",
                            "path": "index.html",
                        }
                    ],
                    "formats": ["html"],
                }
            )
        )
        metadata = site / "owned_docs-1.0.dist-info"
        metadata.mkdir()
        (metadata / "METADATA").write_text(
            "Metadata-Version: 2.1\nName: owned-docs\nVersion: 1.0\n"
        )
        (metadata / "entry_points.txt").write_text(
            "[scitex_dev.docs]\nowned-docs = owned_docs\n"
        )
        (metadata / "RECORD").write_text(
            "owned_docs/__init__.py,,\nowned_docs/_sphinx_html/index.html,,\nowned_docs/_sphinx_html/manifest.json,,\n"
        )
        sys.path.insert(0, str(site))
        importlib.invalidate_caches()
        before = _files(site)
        server = FastMCP("owned-public-docs-reader")
        register_umbrella_tools(
            server, package_policy=policy(scitex=True, **{"scitex-dev": True})
        )
        async with Client(server) as client:
            result = json.loads(
                _text(await client.call_tool("docs_get", {"package": "owned-docs"}))
            )
            assert result["success"] and result["data"]["pages"]
            found = json.loads(
                _text(
                    await client.call_tool(
                        "docs_search",
                        {
                            "query": "Owned Documentation",
                            "scope": "docs",
                            "package": "owned-docs",
                            "max_results": 1,
                        },
                    )
                )
            )
            assert found["success"] and found["data"]
        assert "owned_docs" not in sys.modules and _files(site) == before
        return {
            "real_manifest_read": True,
            "real_page_title_search": True,
            "no_build_or_provider_import": True,
        }

    if operation == "resources":
        state = Path(os.environ["SCITEX_DIR"])
        server = FastMCP("owned-domain-declined")
        register_resources(server, package_policy=policy(scitex=True))
        async with Client(server) as client:
            listed = [str(resource.uri) for resource in await client.list_resources()]
            templates = [
                resource.uriTemplate
                for resource in await client.list_resource_templates()
            ]
            assert not any(uri.startswith("scholar:") for uri in [*listed, *templates])
            denied = False
            try:
                await client.read_resource("scholar://library")
            except Exception:
                denied = True
            assert denied
        assert not (state / "scholar").exists()
        paper = state / "scholar/library/owned-project/owned-paper"
        paper.mkdir(parents=True)
        (paper / "metadata.json").write_text(json.dumps({"title": "OWNED TITLE"}))
        before = _files(state / "scholar")
        selected = FastMCP("owned-domain-admitted")
        register_resources(
            selected, package_policy=policy(scitex=True, **{"scitex-scholar": True})
        )
        async with Client(selected) as client:
            listing = await client.read_resource("scholar://library")
            detail = await client.read_resource("scholar://library/owned-project")
            assert "owned-project" in str(listing) and "OWNED TITLE" in str(detail)
        assert _files(state / "scholar") == before
        return {
            "disabled_uri_unavailable": True,
            "disabled_did_not_create_domain_state": True,
            "admitted_reads_preserve_payload_metadata": True,
        }
    raise ValueError("unsupported owned probe")


def main():
    """Run a selected owned source probe without exposing user state."""
    source, directory, operation = sys.argv[1:]
    owned = Path(directory)
    sys.path.insert(0, source)
    for key in tuple(os.environ):
        if key.startswith("SCITEX_"):
            del os.environ[key]
    os.environ.update(
        HOME=str(owned), SCITEX_DIR=str(owned / "state"), TMPDIR=str(owned)
    )

    def guard(event, arguments):
        if event in {"socket.connect", "socket.bind", "subprocess.Popen"}:
            raise AssertionError("owned discovery attempted an external operation")
        if event == "open" and not isinstance(arguments[0], int):
            mode, flags = arguments[1:3]
            write = (
                isinstance(mode, str) and any(part in mode for part in "wax+")
            ) or (
                isinstance(flags, int)
                and flags
                & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
            )
            if write and not Path(arguments[0]).resolve().is_relative_to(owned):
                raise AssertionError("owned discovery attempted an unowned file write")

        if event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.chown"}:
            if not isinstance(arguments[0], int) and not Path(
                arguments[0]
            ).resolve().is_relative_to(owned):
                raise AssertionError("owned discovery attempted an unowned mutation")
        if event in {"os.rename", "os.link", "os.symlink"}:
            if any(
                not Path(path).resolve().is_relative_to(owned) for path in arguments[:2]
            ):
                raise AssertionError(
                    "owned discovery attempted an unowned path mutation"
                )

    sys.addaudithook(guard)
    result = asyncio.run(inspect(operation, owned))
    sys.stdout.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
