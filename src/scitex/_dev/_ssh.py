#!/usr/bin/env python3
# Timestamp: 2026-02-02
# File: scitex/_dev/_ssh.py

"""SSH-based remote version checking for scitex ecosystem."""

from __future__ import annotations

import subprocess
from typing import Any

from ._config import DevConfig, HostConfig, get_enabled_hosts, load_config


def get_remote_version(host: HostConfig, package: str) -> dict[str, Any]:
    """Get version of a package on a remote host via SSH.

    Parameters
    ----------
    host : HostConfig
        Host configuration.
    package : str
        Package name (PyPI name).

    Returns
    -------
    dict
        Version info with keys: installed, status, error (if any).
    """
    # Build SSH command
    ssh_args = ["ssh"]

    if host.ssh_key:
        ssh_args.extend(["-i", host.ssh_key])

    if host.port != 22:
        ssh_args.extend(["-p", str(host.port)])

    # Add connection options for non-interactive use
    ssh_args.extend(
        [
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "ConnectTimeout=5",
        ]
    )

    ssh_target = f"{host.user}@{host.hostname}"
    ssh_args.append(ssh_target)

    # Python command to get version
    python_cmd = f"""python3 -c "
try:
    from importlib.metadata import version
    print(version('{package}'))
except Exception as e:
    print('ERROR:' + str(e))
"
"""
    ssh_args.append(python_cmd)

    try:
        result = subprocess.run(
            ssh_args,
            capture_output=True,
            text=True,
            timeout=15,
        )

        # SSH stdout may contain shell warnings before the actual output.
        # Take the last non-empty line as the python output.
        output = result.stdout.strip()
        lines = [l.strip() for l in output.splitlines() if l.strip()]
        output = lines[-1] if lines else ""

        if result.returncode != 0:
            error = result.stderr.strip() or "SSH connection failed"
            return {
                "installed": None,
                "status": "error",
                "error": error,
            }

        if output.startswith("ERROR:"):
            return {
                "installed": None,
                "status": "not_installed",
                "error": output[6:],
            }

        return {
            "installed": output,
            "status": "ok",
        }

    except subprocess.TimeoutExpired:
        return {
            "installed": None,
            "status": "timeout",
            "error": "SSH connection timed out",
        }
    except Exception as e:
        return {
            "installed": None,
            "status": "error",
            "error": str(e),
        }


def get_remote_versions(
    host: HostConfig,
    packages: list[str],
) -> dict[str, dict[str, Any]]:
    """Get versions of multiple packages on a remote host.

    Parameters
    ----------
    host : HostConfig
        Host configuration.
    packages : list[str]
        List of package names.

    Returns
    -------
    dict
        Package name -> version info mapping.
    """
    # Build SSH command that checks all packages at once
    ssh_args = ["ssh"]

    if host.ssh_key:
        ssh_args.extend(["-i", host.ssh_key])

    if host.port != 22:
        ssh_args.extend(["-p", str(host.port)])

    ssh_args.extend(
        [
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "ConnectTimeout=5",
        ]
    )

    ssh_target = f"{host.user}@{host.hostname}"
    ssh_args.append(ssh_target)

    # Build Python command to check all packages (installed + toml + git)
    # Use base64 encoding to avoid shell escaping issues
    import base64

    packages_list = repr(packages)
    python_script = f"""
import json
import subprocess
from importlib.metadata import version
from pathlib import Path
import re

def get_pkg_dir(pkg):
    pkg_dir_names = [pkg, pkg.replace("-", "_"), pkg.replace("_", "-")]
    if pkg == "scitex":
        pkg_dir_names.extend(["scitex-python", "scitex-code"])
    for dir_name in pkg_dir_names:
        pkg_dir = Path.home() / "proj" / dir_name
        if pkg_dir.exists():
            return pkg_dir
    return None

def get_toml_version(pkg_dir):
    if not pkg_dir:
        return None
    toml_path = pkg_dir / "pyproject.toml"
    if toml_path.exists():
        try:
            content = toml_path.read_text()
            match = re.search(r'^version\\s*=\\s*["\\'](.*?)["\\']\\s*$', content, re.MULTILINE)
            if match:
                return match.group(1)
        except Exception:
            pass
    return None

def get_git_info(pkg_dir):
    if not pkg_dir:
        return None, None
    try:
        tag = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, cwd=str(pkg_dir), timeout=5
        ).stdout.strip() or None
    except Exception:
        tag = None
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, cwd=str(pkg_dir), timeout=5
        ).stdout.strip() or None
    except Exception:
        branch = None
    return tag, branch

results = {{}}
for pkg in {packages_list}:
    result = {{"installed": None, "toml": None, "git_tag": None, "git_branch": None, "status": "not_installed"}}
    try:
        result["installed"] = version(pkg)
        result["status"] = "ok"
    except Exception as e:
        result["error"] = str(e)
    pkg_dir = get_pkg_dir(pkg)
    result["toml"] = get_toml_version(pkg_dir)
    result["git_tag"], result["git_branch"] = get_git_info(pkg_dir)
    results[pkg] = result
print(json.dumps(results))
"""
    encoded = base64.b64encode(python_script.encode()).decode()
    python_cmd = (
        f"python3 -c \"import base64;exec(base64.b64decode('{encoded}').decode())\""
    )
    ssh_args.append(python_cmd)

    try:
        result = subprocess.run(
            ssh_args,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            error = result.stderr.strip() or "SSH connection failed"
            return {
                pkg: {"installed": None, "status": "error", "error": error}
                for pkg in packages
            }

        import json
        from typing import cast

        try:
            # SSH stdout may contain shell warnings before the JSON.
            # Extract the last line that looks like JSON (starts with '{').
            stdout = result.stdout.strip()
            for line in reversed(stdout.splitlines()):
                line = line.strip()
                if line.startswith("{"):
                    stdout = line
                    break
            return cast(dict[str, dict[str, Any]], json.loads(stdout))
        except json.JSONDecodeError:
            return {
                pkg: {
                    "installed": None,
                    "status": "error",
                    "error": f"Invalid response: {result.stdout[:100]}",
                }
                for pkg in packages
            }

    except subprocess.TimeoutExpired:
        return {
            pkg: {"installed": None, "status": "timeout", "error": "SSH timed out"}
            for pkg in packages
        }
    except Exception as e:
        return {
            pkg: {"installed": None, "status": "error", "error": str(e)}
            for pkg in packages
        }


def check_all_hosts(
    packages: list[str] | None = None,
    hosts: list[str] | None = None,
    config: DevConfig | None = None,
) -> dict[str, dict[str, dict[str, Any]]]:
    """Check versions on all enabled hosts.

    Parameters
    ----------
    packages : list[str] | None
        List of package names. If None, uses ecosystem packages.
    hosts : list[str] | None
        List of host names to check. If None, checks all enabled hosts.
    config : DevConfig | None
        Configuration to use. If None, loads default config.

    Returns
    -------
    dict
        Mapping: host_name -> package_name -> version_info
    """
    if config is None:
        config = load_config()

    if packages is None:
        from ._ecosystem import get_all_packages

        packages = get_all_packages()

    # Get pypi names for packages
    from ._ecosystem import ECOSYSTEM

    pypi_names = []
    name_map = {}  # pypi_name -> package_name
    for pkg in packages:
        if pkg in ECOSYSTEM:
            pypi_name = ECOSYSTEM[pkg].get("pypi_name", pkg)
        else:
            pypi_name = pkg
        pypi_names.append(pypi_name)
        name_map[pypi_name] = pkg

    # Get enabled hosts
    enabled_hosts = get_enabled_hosts(config)
    if hosts:
        enabled_hosts = [h for h in enabled_hosts if h.name in hosts]

    results: dict[str, dict[str, dict[str, Any]]] = {}

    for host in enabled_hosts:
        host_versions = get_remote_versions(host, pypi_names)
        # Map back to package names
        results[host.name] = {
            name_map.get(pypi, pypi): info for pypi, info in host_versions.items()
        }
        # Add host metadata
        results[host.name]["_host"] = {
            "hostname": host.hostname,
            "role": host.role,
            "user": host.user,
        }

    return results


def test_host_connection(host: HostConfig) -> dict[str, Any]:
    """Test SSH connection to a host.

    Parameters
    ----------
    host : HostConfig
        Host to test.

    Returns
    -------
    dict
        Connection status with keys: connected, error, python_version.
    """
    ssh_args = ["ssh"]

    if host.ssh_key:
        ssh_args.extend(["-i", host.ssh_key])

    if host.port != 22:
        ssh_args.extend(["-p", str(host.port)])

    ssh_args.extend(
        [
            "-o",
            "BatchMode=yes",
            "-o",
            "StrictHostKeyChecking=accept-new",
            "-o",
            "ConnectTimeout=5",
        ]
    )

    ssh_target = f"{host.user}@{host.hostname}"
    ssh_args.append(ssh_target)
    ssh_args.append("python3 --version")

    try:
        result = subprocess.run(
            ssh_args,
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            return {
                "connected": True,
                "python_version": result.stdout.strip(),
            }
        return {
            "connected": False,
            "error": result.stderr.strip() or "Connection failed",
        }

    except subprocess.TimeoutExpired:
        return {"connected": False, "error": "Connection timed out"}
    except Exception as e:
        return {"connected": False, "error": str(e)}


# EOF
