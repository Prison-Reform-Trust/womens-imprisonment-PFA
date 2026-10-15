#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from src.configuration import load_config
from src.data.processing import process_data
from src.data.raw import download_data
from src.visualisation import make_visualisations


def main() -> None:
    """This is the entry point for the entire pipeline. It will
    allow you to run the analysis for a given year, using the defined
    values within the accompanying config file."""
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

    # Pass config to the pipeline:
    download_data.main(config=config)
    process_data.main(config=config)
    make_visualisations.main(config=config)


if __name__ == "__main__":
    main()
