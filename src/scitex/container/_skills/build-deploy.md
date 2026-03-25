---
name: container-build-deploy
description: Build Apptainer container images with build(), snapshot Python environments with freeze(), and deploy containers to target directories with deploy().
---

# Build and Deploy

## build

Build an Apptainer `.sif` image from a definition file.

```python
build(def_file: str, output: str | None = None, sandbox: bool = False) -> dict
```

```python
import scitex as stx

result = stx.container.build(
    "environment.def",
    output="env_v1.sif",
)
print(result["success"])
```

---

## freeze

Snapshot the current Python environment into a container-compatible requirements format.

```python
freeze(output_path: str | None = None) -> dict
```

```python
import scitex as stx

stx.container.freeze("requirements_frozen.txt")
```

---

## deploy

Deploy a built container to a versioned target directory.

```python
deploy(sif_path: str, target_dir: str | None = None, version: str | None = None) -> dict
```

```python
import scitex as stx

stx.container.deploy(
    "env_v1.sif",
    target_dir="/scratch/containers/myproject",
    version="v1.0",
)
```
