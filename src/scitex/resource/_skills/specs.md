---
description: Collect full system hardware and software specifications as a dict or YAML string.
---

# stx.resource — System Specifications

## get_specs

Collects system info into a nested dict (or YAML string).

```python
from scitex.resource import get_specs

specs = get_specs()
# {
#   "Collected Time": "2024-11-04 10:30:00",
#   "System Information": {"OS": "Linux", "Node Name": "myhost", ...},
#   "CPU Info": {"Physical cores": 8, "Total cores": 16, ...},
#   "Memory Info": {"Memory": {"Total": "32.0 GiB", ...}, "SWAP": {...}},
#   "GPU Info": {"NVIDIA GPU models": [...], "NVIDIA Driver Version": "..."},
#   "Disk Info": {"Partitions": {...}, "Total read": "...", "Total write": "..."},
#   "Network Info": {"Interfaces": {...}, "Total Sent": "...", "Total Received": "..."},
# }

# Select only some sections
cpu_only = get_specs(cpu=True, gpu=False, disk=False, network=False)

# Print to console
get_specs(verbose=True)

# Get as YAML string
yaml_str = get_specs(yaml=True)
print(yaml_str)

# Save to file (using stx.io)
import scitex as stx
specs = get_specs()
stx.io.save(specs, "specs.yaml")
```

Parameters (all default `True`):
- `system` — OS, node name, kernel release/version
- `cpu` — core counts, frequency range, per-core and total usage; also includes memory info
- `gpu` — NVIDIA GPU models, driver version, CUDA runtime, cuDNN version (via `_supple_nvidia_info`)
- `disk` — partition mount points, sizes, IO counters
- `network` — interface addresses, total bytes sent/received
- `verbose` — print via `pprint`
- `yaml` — return YAML string instead of dict

## Component-level helpers

```python
from scitex.resource import (
    _cpu_info, _memory_info, _disk_info, _network_info,
    _supple_nvidia_info, _supple_os_info, _supple_python_info,
    _system_info,
)

print(_cpu_info())         # dict with core counts, freq, per-core usage
print(_memory_info())      # dict with RAM and SWAP stats in readable units
print(_supple_nvidia_info())  # dict with GPU model, driver, CUDA, cuDNN
print(_supple_python_info())  # dict with python_version, torch_version, pip packages
```

All readable byte values use `scitex.str.readable_bytes` for human-friendly formatting (e.g., `"32.0 GiB"`).
