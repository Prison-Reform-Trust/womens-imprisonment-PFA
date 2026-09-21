#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from src.configuration import load_config
from src.data.processing import process_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year",
        required=True,
        choices=["2025", "2026"],
        help="Analysis configuration to run",
    )
    args = parser.parse_args()

    config = load_config(args.year)

    print(f"Running analysis: {config['analysis']['id']}")
    print(f"Data release: {config['analysis']['data_release']}")

    # Pass config to the pipeline:
    # run_downloads(config)
    process_data.main(config)
    # run_visualisations(config)


if __name__ == "__main__":
    main()
