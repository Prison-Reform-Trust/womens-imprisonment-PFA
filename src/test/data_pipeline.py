#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script is part of the testing process for the implementation of a new config system
to allow for analyses for different years. This script is specifically designed to test the
functionality of the new config system in downloading and saving the raw datasets required.
'''

import src.utilities as utils
from src.configuration import load_config
from src.data.processing import filter_years
from src.data.processing import make_custody_tables as custody
from src.data.processing import process_data
from src.data.raw import download_data


def test_download_data(config: dict):
    """Test the download_data function with the new config system."""

    # Download and save the raw datasets based on the loaded configuration
    download_data.main(config=config)


def debug_custody_tables():
    """Debug the make_custody_tables function with the new config system."""

    # Debugging IndexError in line 140 of make_custody_tables.py

    # NOTE: This calls the same transformation steps as the target script make_custody_tables,
    # but only for "all"; change that argument to "6 months" or "12 months" to inspect another category.
    # The processed input file must already exist. If you instead call custody.main(config),
    # it will run this stage for all categories and save the CSVs.

    config = load_config(2025)

    df = utils.load_data(
        config=config,
        status="processed",
        filename=config["data"]["filenames"]["filter_sentence_length"],
    )

    df_sentence = (
        df.copy()
        .pipe(custody.get_sentence_length, "all")
        .pipe(filter_years.get_year)
        .pipe(custody.perform_crosstab)
        .pipe(custody.calculate_percentage_change)
    )

    return df_sentence


def test_process_data(config: dict):
    """Test the process_data function with the new config system."""

    # Process the raw datasets based on the loaded configuration
    process_data.main(config=config)


def main():
    """Main function to test the data pipeline using the new config system."""
    # Load the configuration for the year 2025
    config = load_config(2025)

    # Download and save the raw datasets based on the loaded configuration
    download_data.main(config=config)
    process_data.main(config=config)
