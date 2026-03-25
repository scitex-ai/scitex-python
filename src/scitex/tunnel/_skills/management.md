---
name: tunnel-management
description: Create reverse SSH tunnels with setup(), remove them with remove(), and inspect their status with status(). Uses autossh for persistent connections through NAT.
---

# Tunnel Management

## setup

Create a persistent reverse SSH tunnel via autossh.

```python
setup(port: int, bastion_server: str, secret_key_path: str) -> dict
```

| Parameter | Description |
|-----------|-------------|
| `port` | Local port to expose through the tunnel |
| `bastion_server` | `user@host` of the bastion server |
| `secret_key_path` | Path to the SSH private key |

Returns a dict with `success`, `stdout`, and `stderr` keys.

```python
import scitex as stx

result = stx.tunnel.setup(
    port=8888,
    bastion_server="researcher@bastion.example.org",
    secret_key_path="~/.ssh/id_ed25519",
)
print(result["success"])  # True
```

---

## remove

Tear down a previously-created tunnel.

```python
remove(port: int) -> dict
```

```python
import scitex as stx

stx.tunnel.remove(8888)
```

---

## status

Check the current state of tunnels.

```python
status(port: int | None = None) -> dict
```

Pass `port=None` to check all tunnels.

```python
import scitex as stx

info = stx.tunnel.status()
print(info)  # {'success': True, 'stdout': '...', 'stderr': ''}

# Check a specific port
info = stx.tunnel.status(port=8888)
```

---

## AVAILABLE

Module-level flag indicating whether `scitex-tunnel` is installed.

```python
import scitex as stx

if stx.tunnel.AVAILABLE:
    stx.tunnel.setup(8888, "bastion@example.com", "~/.ssh/id_rsa")
else:
    print("Install: pip install scitex-tunnel")
```
