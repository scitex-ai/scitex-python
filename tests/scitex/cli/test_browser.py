"""The real optional browser command refuses before browser/session work."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click

_CHILD = r"""
import importlib.util,json,os,sys
from pathlib import Path
site,source,home=sys.argv[1:]
sys.path.insert(0,site)
os.environ['HOME']=home
assert importlib.util.find_spec('playwright') is None

def guard(event,args):
    if event in {'subprocess.Popen','socket.connect','socket.bind','os.mkdir','os.remove','os.rename'}:
        raise AssertionError('browser command attempted runtime work before dependency refusal')
    if event=='open':
        mode,flags=args[1:3]
        if (isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)):
            raise AssertionError('browser command attempted session/state writes')
sys.addaudithook(guard)
from click.testing import CliRunner
spec=importlib.util.spec_from_file_location('owned_browser_command',source)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result=CliRunner().invoke(module.browser,['open','--stealth'])
print(json.dumps({'exit_code':result.exit_code,'output':result.output,
                  'session_exists':module.BROWSER_STATE_FILE.exists(),
                  'browser_provider_imported':'scitex.browser.core' in sys.modules}))
"""


def test_missing_playwright_refuses_before_any_browser_or_session_work(tmp_path):
    # Arrange: a real Click copy is the only third-party package on the child path.
    site = tmp_path / "site"
    site.mkdir()
    shutil.copytree(Path(click.__file__).parent, site / "click")
    home = tmp_path / "home"
    home.mkdir()
    source = Path(__file__).resolve().parents[3] / "src/scitex/cli/browser.py"
    environment = {
        key: os.environ[key] for key in ("PATH", "LANG") if key in os.environ
    }
    # Act
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-B",
            "-c",
            _CHILD,
            str(site),
            str(source),
            str(home),
        ],
        env=environment,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    observed = json.loads(result.stdout)
    # Assert
    assert (
        result.returncode,
        observed["exit_code"],
        "scitex[browser]" in observed["output"],
        observed["session_exists"],
        observed["browser_provider_imported"],
    ) == (0, 1, True, False, False)
