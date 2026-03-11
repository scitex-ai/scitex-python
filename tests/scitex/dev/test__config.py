#!/usr/bin/env python3
# Timestamp: 2026-03-12
# File: tests/scitex/dev/test__config.py

"""Tests for scitex._dev._config module.

Covers:
- DevConfig dataclass defaults
- config_to_dict() serialization
- load_config() with non-existent path returns defaults
- _parse_host_config() dict parsing
- _parse_github_remote() / _parse_pypi_account()
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from scitex._dev._config import (
    DevConfig,
    GitHubRemote,
    HostConfig,
    PackageConfig,
    PyPIAccount,
    _parse_github_remote,
    _parse_host_config,
    _parse_package_config,
    _parse_pypi_account,
    config_to_dict,
    get_enabled_hosts,
    get_enabled_remotes,
    load_config,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_config() -> DevConfig:
    """Build a minimal DevConfig with one of each sub-object."""
    return DevConfig(
        packages=[
            PackageConfig(
                name="scitex",
                local_path="~/proj/scitex-python",
                pypi_name="scitex",
                github_repo="ywatanabe1989/scitex-python",
            )
        ],
        hosts=[HostConfig(name="myhost", hostname="192.168.1.1", user="dev")],
        github_remotes=[GitHubRemote(name="ywatanabe1989", org="ywatanabe1989")],
        pypi_accounts=[PyPIAccount(name="ywatanabe1989")],
        branches=["main", "develop"],
    )


# ---------------------------------------------------------------------------
# Tests for DevConfig defaults
# ---------------------------------------------------------------------------


class TestDevConfigDefaults:
    """Tests for DevConfig dataclass field defaults."""

    def test_empty_devconfig_has_empty_lists(self):
        """DevConfig() with no args has empty packages, hosts, etc."""
        config = DevConfig()
        assert config.packages == []
        assert config.hosts == []
        assert config.github_remotes == []
        assert config.pypi_accounts == []

    def test_branches_default_includes_main_and_develop(self):
        """Default branches list contains 'main' and 'develop'."""
        config = DevConfig()
        assert "main" in config.branches
        assert "develop" in config.branches

    def test_host_config_defaults(self):
        """HostConfig has sensible defaults for optional fields."""
        host = HostConfig(name="h", hostname="host.local", user="u")
        assert host.role == "dev"
        assert host.enabled is True
        assert host.port == 22
        assert host.python_bin == "python3"
        assert host.pip_bin == "pip"
        assert host.remote_base == "~/proj"
        assert host.packages == []

    def test_github_remote_enabled_by_default(self):
        """GitHubRemote.enabled is True by default."""
        remote = GitHubRemote(name="r", org="myorg")
        assert remote.enabled is True

    def test_pypi_account_enabled_by_default(self):
        """PyPIAccount.enabled is True by default."""
        acct = PyPIAccount(name="user")
        assert acct.enabled is True


# ---------------------------------------------------------------------------
# Tests for config_to_dict
# ---------------------------------------------------------------------------


class TestConfigToDict:
    """Tests for config_to_dict() serialization."""

    def test_returns_dict(self):
        """config_to_dict returns a plain dict."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert isinstance(result, dict)

    def test_top_level_keys_present(self):
        """Result has packages, hosts, github_remotes, branches keys."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert "packages" in result
        assert "hosts" in result
        assert "github_remotes" in result
        assert "branches" in result

    def test_packages_serialized_correctly(self):
        """Each package entry has name, local_path, pypi_name, github_repo."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert len(result["packages"]) == 1
        pkg = result["packages"][0]
        assert pkg["name"] == "scitex"
        assert pkg["local_path"] == "~/proj/scitex-python"
        assert pkg["pypi_name"] == "scitex"
        assert pkg["github_repo"] == "ywatanabe1989/scitex-python"

    def test_hosts_serialized_correctly(self):
        """Each host entry has name, hostname, user, role, enabled."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert len(result["hosts"]) == 1
        host = result["hosts"][0]
        assert host["name"] == "myhost"
        assert host["hostname"] == "192.168.1.1"
        assert host["user"] == "dev"
        assert "role" in host
        assert "enabled" in host

    def test_github_remotes_serialized_correctly(self):
        """Each GitHub remote entry has name, org, enabled."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert len(result["github_remotes"]) == 1
        remote = result["github_remotes"][0]
        assert remote["name"] == "ywatanabe1989"
        assert remote["org"] == "ywatanabe1989"
        assert "enabled" in remote

    def test_branches_serialized(self):
        """branches is serialized as a list."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert result["branches"] == ["main", "develop"]

    def test_config_path_included_when_provided(self):
        """config_path key is included when the argument is given."""
        config = _minimal_config()
        path = Path("/home/user/.scitex/dev_config.yaml")
        result = config_to_dict(config, config_path=path)
        assert "config_path" in result
        assert result["config_path"] == str(path)

    def test_config_path_absent_when_not_provided(self):
        """config_path key is absent when argument is None."""
        config = _minimal_config()
        result = config_to_dict(config)
        assert "config_path" not in result

    def test_empty_config_produces_empty_lists(self):
        """DevConfig() with no fields serializes to empty lists."""
        config = DevConfig()
        result = config_to_dict(config)
        assert result["packages"] == []
        assert result["hosts"] == []
        assert result["github_remotes"] == []


# ---------------------------------------------------------------------------
# Tests for load_config with non-existent path
# ---------------------------------------------------------------------------


class TestLoadConfig:
    """Tests for load_config() behavior."""

    def test_nonexistent_path_returns_devconfig(self):
        """load_config() with a non-existent path returns a DevConfig instance."""
        result = load_config(config_path="/nonexistent/path/dev_config.yaml")
        assert isinstance(result, DevConfig)

    def test_nonexistent_path_has_default_branches(self):
        """load_config() with missing file still sets default branches."""
        result = load_config(config_path="/nonexistent/path/dev_config.yaml")
        assert "main" in result.branches
        assert "develop" in result.branches

    def test_nonexistent_path_falls_back_to_ecosystem_packages(self):
        """load_config() with missing file populates packages from ECOSYSTEM."""
        result = load_config(config_path="/nonexistent/path/dev_config.yaml")
        assert len(result.packages) > 0
        pkg_names = [p.name for p in result.packages]
        assert "scitex" in pkg_names

    def test_nonexistent_path_has_default_github_remote(self):
        """load_config() with missing file creates default GitHub remote."""
        result = load_config(config_path="/nonexistent/path/dev_config.yaml")
        assert len(result.github_remotes) >= 1
        assert result.github_remotes[0].name == "ywatanabe1989"

    def test_nonexistent_path_has_default_pypi_account(self):
        """load_config() with missing file creates default PyPI account."""
        result = load_config(config_path="/nonexistent/path/dev_config.yaml")
        assert len(result.pypi_accounts) >= 1

    def test_valid_yaml_file_parsed(self):
        """load_config() reads a real YAML file when it exists."""
        yaml_content = """\
hosts:
  - name: testhost
    hostname: 10.0.0.1
    user: admin
    role: staging
    enabled: true
branches:
  - main
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name

        try:
            result = load_config(config_path=tmp_path)
            assert isinstance(result, DevConfig)
            assert len(result.hosts) == 1
            assert result.hosts[0].name == "testhost"
            assert result.hosts[0].hostname == "10.0.0.1"
            assert result.hosts[0].role == "staging"
        finally:
            os.unlink(tmp_path)

    def test_env_var_overrides_host_enablement(self):
        """SCITEX_DEV_HOSTS env var enables only named hosts."""
        yaml_content = """\
hosts:
  - name: alpha
    hostname: a.local
    user: u
  - name: beta
    hostname: b.local
    user: u
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            tmp_path = f.name

        try:
            with patch.dict(os.environ, {"SCITEX_DEV_HOSTS": "alpha"}):
                result = load_config(config_path=tmp_path)
            host_map = {h.name: h for h in result.hosts}
            assert host_map["alpha"].enabled is True
            assert host_map["beta"].enabled is False
        finally:
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Tests for _parse_host_config
# ---------------------------------------------------------------------------


class TestParseHostConfig:
    """Tests for _parse_host_config() dict-to-HostConfig conversion."""

    def test_parses_required_fields(self):
        """name, hostname, user are read from dict."""
        data = {"name": "myhost", "hostname": "192.168.0.1", "user": "alice"}
        host = _parse_host_config(data)
        assert host.name == "myhost"
        assert host.hostname == "192.168.0.1"
        assert host.user == "alice"

    def test_defaults_applied_for_missing_optional_fields(self):
        """Missing optional fields fall back to defaults."""
        data = {"name": "h", "hostname": "h.local", "user": "u"}
        host = _parse_host_config(data)
        assert host.role == "dev"
        assert host.enabled is True
        assert host.port == 22
        assert host.python_bin == "python3"
        assert host.pip_bin == "pip"
        assert host.remote_base == "~/proj"
        assert host.packages == []

    def test_ssh_key_parsed(self):
        """ssh_key field is read when present."""
        data = {
            "name": "h",
            "hostname": "h.local",
            "user": "u",
            "ssh_key": "~/.ssh/id_ed25519",
        }
        host = _parse_host_config(data)
        assert host.ssh_key == "~/.ssh/id_ed25519"

    def test_ssh_key_none_when_absent(self):
        """ssh_key is None when not in the dict."""
        data = {"name": "h", "hostname": "h.local", "user": "u"}
        host = _parse_host_config(data)
        assert host.ssh_key is None

    def test_port_parsed(self):
        """Non-default port is read correctly."""
        data = {"name": "h", "hostname": "h.local", "user": "u", "port": 2222}
        host = _parse_host_config(data)
        assert host.port == 2222

    def test_packages_as_list(self):
        """packages list is passed through directly."""
        data = {
            "name": "h",
            "hostname": "h.local",
            "user": "u",
            "packages": ["scitex", "figrecipe"],
        }
        host = _parse_host_config(data)
        assert host.packages == ["scitex", "figrecipe"]

    def test_packages_as_comma_string(self):
        """packages as CSV string is split into a list."""
        data = {
            "name": "h",
            "hostname": "h.local",
            "user": "u",
            "packages": "scitex, figrecipe",
        }
        host = _parse_host_config(data)
        assert "scitex" in host.packages
        assert "figrecipe" in host.packages

    def test_enabled_false_parsed(self):
        """enabled=false is read correctly."""
        data = {
            "name": "h",
            "hostname": "h.local",
            "user": "u",
            "enabled": False,
        }
        host = _parse_host_config(data)
        assert host.enabled is False

    def test_empty_dict_uses_all_defaults(self):
        """Empty dict produces a HostConfig with all defaults."""
        host = _parse_host_config({})
        assert host.name == "unknown"
        assert host.hostname == "localhost"
        assert host.port == 22


# ---------------------------------------------------------------------------
# Tests for _parse_github_remote and _parse_pypi_account
# ---------------------------------------------------------------------------


class TestParseGitHubRemote:
    """Tests for _parse_github_remote()."""

    def test_name_and_org_parsed(self):
        data = {"name": "ywatanabe1989", "org": "ywatanabe1989"}
        remote = _parse_github_remote(data)
        assert remote.name == "ywatanabe1989"
        assert remote.org == "ywatanabe1989"

    def test_enabled_true_by_default(self):
        remote = _parse_github_remote({"name": "r", "org": "myorg"})
        assert remote.enabled is True

    def test_enabled_false_parsed(self):
        remote = _parse_github_remote({"name": "r", "org": "myorg", "enabled": False})
        assert remote.enabled is False

    def test_empty_dict_defaults(self):
        remote = _parse_github_remote({})
        assert remote.name == "unknown"
        assert remote.org == ""
        assert remote.enabled is True


class TestParsePyPIAccount:
    """Tests for _parse_pypi_account()."""

    def test_name_parsed(self):
        acct = _parse_pypi_account({"name": "ywatanabe1989"})
        assert acct.name == "ywatanabe1989"

    def test_enabled_true_by_default(self):
        acct = _parse_pypi_account({"name": "u"})
        assert acct.enabled is True

    def test_enabled_false_parsed(self):
        acct = _parse_pypi_account({"name": "u", "enabled": False})
        assert acct.enabled is False


# ---------------------------------------------------------------------------
# Tests for _parse_package_config
# ---------------------------------------------------------------------------


class TestParsePackageConfig:
    """Tests for _parse_package_config()."""

    def test_required_fields_parsed(self):
        data = {
            "name": "scitex",
            "local_path": "~/proj/scitex-python",
            "pypi_name": "scitex",
        }
        pkg = _parse_package_config(data)
        assert pkg.name == "scitex"
        assert pkg.local_path == "~/proj/scitex-python"
        assert pkg.pypi_name == "scitex"

    def test_pypi_name_falls_back_to_name(self):
        """pypi_name defaults to name when absent."""
        data = {"name": "mypkg", "local_path": "/tmp/mypkg"}
        pkg = _parse_package_config(data)
        assert pkg.pypi_name == "mypkg"

    def test_github_repo_and_import_name_optional(self):
        """github_repo and import_name are None when absent."""
        data = {"name": "mypkg", "local_path": "/tmp/mypkg", "pypi_name": "mypkg"}
        pkg = _parse_package_config(data)
        assert pkg.github_repo is None
        assert pkg.import_name is None

    def test_github_repo_parsed(self):
        data = {
            "name": "scitex",
            "local_path": "~/proj/scitex-python",
            "pypi_name": "scitex",
            "github_repo": "ywatanabe1989/scitex-python",
            "import_name": "scitex",
        }
        pkg = _parse_package_config(data)
        assert pkg.github_repo == "ywatanabe1989/scitex-python"
        assert pkg.import_name == "scitex"


# ---------------------------------------------------------------------------
# Tests for get_enabled_hosts / get_enabled_remotes
# ---------------------------------------------------------------------------


class TestGetEnabledHelpers:
    """Tests for get_enabled_hosts and get_enabled_remotes."""

    def test_get_enabled_hosts_returns_only_enabled(self):
        """get_enabled_hosts filters out disabled hosts."""
        config = DevConfig(
            hosts=[
                HostConfig(name="on", hostname="a.local", user="u", enabled=True),
                HostConfig(name="off", hostname="b.local", user="u", enabled=False),
            ]
        )
        result = get_enabled_hosts(config)
        names = [h.name for h in result]
        assert "on" in names
        assert "off" not in names

    def test_get_enabled_remotes_returns_only_enabled(self):
        """get_enabled_remotes filters out disabled remotes."""
        config = DevConfig(
            github_remotes=[
                GitHubRemote(name="active", org="org1", enabled=True),
                GitHubRemote(name="inactive", org="org2", enabled=False),
            ]
        )
        result = get_enabled_remotes(config)
        names = [r.name for r in result]
        assert "active" in names
        assert "inactive" not in names

    def test_get_enabled_hosts_empty_when_all_disabled(self):
        """Returns empty list when all hosts are disabled."""
        config = DevConfig(
            hosts=[HostConfig(name="h", hostname="h.local", user="u", enabled=False)]
        )
        assert get_enabled_hosts(config) == []


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
