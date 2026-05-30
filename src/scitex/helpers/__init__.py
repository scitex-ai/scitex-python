"""Internal helpers for scitex (env loading, install guidance, optional deps)."""

from scitex_config import (
    load_scitex_env,
)  # env-loading lives in scitex-config (>=0.3.6)

from ._install_guide import (
    require_module,
    show_install_guide,
)
from ._optional_deps import (
    PACKAGE_TO_EXTRA,
    check_optional_deps,
)

__all__ = [
    "load_scitex_env",
    "require_module",
    "show_install_guide",
    "PACKAGE_TO_EXTRA",
    "check_optional_deps",
]
