#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import Any, cast

from omegaconf import OmegaConf

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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

    merged_config = OmegaConf.merge(
        OmegaConf.load(defaults_path),
        OmegaConf.load(analysis_path),
    )

    resolved_config = OmegaConf.to_container(
        merged_config,
        resolve=True,
    )

    if not isinstance(resolved_config, dict):
        raise ValueError("Expected the merged configuration to be a mapping")

    config = cast(dict[str, Any], resolved_config)

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
