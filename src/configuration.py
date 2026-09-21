#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_yaml(path: Path) -> dict[str, Any]:
    """Read a YAML file and return its contents as a dictionary."""
    with path.open(encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}

    if not isinstance(config, dict):
        raise ValueError(f"Expected a mapping in {path}")

    return config


def deep_merge(
    base: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Recursively merge overrides into base without mutating either input."""

    result = deepcopy(base)

    for key, value in overrides.items():
        if (
            isinstance(result.get(key), dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)

    return result


def load_config(year: str | int) -> dict[str, Any]:
    """Load shared defaults and the configuration for one analysis release."""

    year = str(year)

    defaults_path = PROJECT_ROOT / "config" / "defaults.yaml"
    analysis_path = PROJECT_ROOT / "config" / "analyses" / f"{year}.yaml"

    if not defaults_path.exists():
        raise FileNotFoundError(f"Missing defaults file: {defaults_path}")

    if not analysis_path.exists():
        raise FileNotFoundError(
            f"No configuration exists for analysis {year}: {analysis_path}"
        )

    config = deep_merge(
        read_yaml(defaults_path),
        read_yaml(analysis_path),
    )

    analysis = config.get("analysis", {})
    if analysis.get("id") != year:
        raise ValueError(
            f"Analysis configuration ID {analysis.get('id')!r} "
            f"does not match requested year {year!r}"
        )

    config["_metadata"] = {
        "defaults_path": str(defaults_path.relative_to(PROJECT_ROOT)),
        "analysis_path": str(analysis_path.relative_to(PROJECT_ROOT)),
    }

    return config
