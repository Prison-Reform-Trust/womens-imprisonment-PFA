#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script is part of the testing process for the implementation of a new config system
to allow for analyses for different years. This script is specifically designed to test the
functionality of the new config system in downloading and saving the raw datasets required.
'''

from src.configuration import load_config
from src.data.processing import filter_sentence_type as sentence_type
from src.data.processing import process_data
from src.data.raw import download_data


def test_download_data(config: dict):
    """Test the download_data function with the new config system."""

    # Download and save the raw datasets based on the loaded configuration
    download_data.main(config=config)


def debug_filter_sentence_type():
    """
    Used to debug the filter_sentence_type module which was failing to perform regex
    replacements on a number of str columns in the DataFrame.
    """

    # Load the configuration for the year 2025
    config = load_config(2025)

    # Filter the DataFrame to include only records with relevant sentence types
    df_filtered = sentence_type.load_and_process_data(config=config)

    return df_filtered


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


if __name__ == "__main__":
    test_process_data(load_config(2025))
