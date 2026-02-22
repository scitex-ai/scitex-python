#!/usr/bin/env python3
# Timestamp: "2026-02-23"
# File: /home/ywatanabe/proj/scitex-code/src/scitex/module/_manifest.py

from __future__ import annotations

"""Module manifest dataclass describing metadata for a SciTeX module."""

from dataclasses import dataclass, field

VALID_CATEGORIES = (
    "writing",
    "visualization",
    "data",
    "analysis",
    "reference",
    "utility",
    "other",
)


@dataclass
class ModuleManifest:
    """Metadata for a SciTeX workspace module.

    Attributes
    ----------
        name: Auto-generated slug from the decorated function name.
        label: Human-readable display name shown in the UI.
        icon: FontAwesome class (e.g. "fa-brain").
        category: One of the VALID_CATEGORIES.
        description: Short description of what the module does.
        version: Semantic version string.
        dependencies: Extra pip packages required by this module.
        min_scitex_version: Minimum scitex version required (empty = any).
    """

    name: str = ""
    label: str = ""
    icon: str = "fa-puzzle-piece"
    category: str = "other"
    description: str = ""
    version: str = "0.1.0"
    dependencies: list = field(default_factory=list)
    min_scitex_version: str = ""

    def __post_init__(self):
        if self.category not in VALID_CATEGORIES:
            raise ValueError(
                f"Invalid category '{self.category}'. "
                f"Must be one of: {', '.join(VALID_CATEGORIES)}"
            )

    def to_dict(self) -> dict:
        """Serialize manifest to a plain dictionary."""
        return {
            "name": self.name,
            "label": self.label,
            "icon": self.icon,
            "category": self.category,
            "description": self.description,
            "version": self.version,
            "dependencies": list(self.dependencies),
            "min_scitex_version": self.min_scitex_version,
        }

    @classmethod
    def from_dict(cls, data: dict) -> ModuleManifest:
        """Construct a ModuleManifest from a dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# EOF
