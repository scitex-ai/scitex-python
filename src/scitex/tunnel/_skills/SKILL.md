---
name: stx.tunnel
description: SSH reverse tunnel management for NAT traversal via autossh.
---

# stx.tunnel

The `stx.tunnel` module manages SSH reverse tunnels for NAT traversal, enabling remote access to machines behind firewalls. It delegates to the `scitex-tunnel` package (autossh-based).

## Python API

```python
import scitex as stx

# Check if tunnel package is available
if stx.tunnel.AVAILABLE:
    # Set up a reverse tunnel
    stx.tunnel.setup(
        port=8080,
        bastion_server="bastion.example.com",
        secret_key_path="~/.ssh/id_rsa"
    )

    # Check tunnel status
    status = stx.tunnel.status()
    status = stx.tunnel.status(port=8080)  # specific port

    # Remove a tunnel
    stx.tunnel.remove(port=8080)

    # Get package version
    version = stx.tunnel.get_version()
```

## Key Features

- `setup(port, bastion_server, secret_key_path)` — establish autossh reverse tunnel
- `remove(port)` — terminate and remove a tunnel
- `status(port=None)` — check tunnel status (all or specific port)
- `get_version()` — get scitex-tunnel package version
- `AVAILABLE` flag — gracefully handles missing `scitex-tunnel` package
- Based on autossh for persistent tunnel management
