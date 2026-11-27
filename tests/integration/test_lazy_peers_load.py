#!/usr/bin/env python3
# File: ./tests/integration/test_lazy_peers_load.py
"""Every peer that `import scitex` registers lazily must execute cleanly.

`import scitex` puts each installed peer in ``sys.modules`` behind an
``importlib.util.LazyLoader``. Anything that walks ``sys.modules`` and touches
an attribute (``inspect.getmodule``, which torch calls while it initialises)
executes those peers. A peer release whose import body does not survive that
(scitex-db < 0.1.9 deleting its own attributes in ``__init__``, scitex-ml 0.1.0
importing torch eagerly) then breaks ``import scitex; import torch``. The
min-versions CI leg runs this against every member floor.
"""

import json
import subprocess
import sys

_PROBE = """
import json, sys
import scitex  # registers the lazy peers
from scitex.re_export import EXTERNAL_REEXPORTS
failed = {}
for short, target in sorted(EXTERNAL_REEXPORTS.items()):
    module = sys.modules.get(target)
    if module is None:
        continue  # peer not installed
    try:
        getattr(module, "__file__")
    except Exception as exc:
        failed[target] = f"{type(exc).__name__}: {str(exc)[:200]}"
print(json.dumps(failed))
"""


def test_every_registered_lazy_peer_executes_without_error():
    # Arrange
    cmd = [sys.executable, "-c", _PROBE]
    # Act
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600, check=True)
    failed = json.loads(proc.stdout.strip().splitlines()[-1])
    # Assert
    assert failed == {}


# EOF
