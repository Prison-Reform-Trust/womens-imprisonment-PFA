#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script is part of the testing process for the implementation of a new config system 
to allow for analyses for different years. This script is specifically designed to test the 
functionality of the new config system in downloading and saving the raw datasets required.
'''

from src.configuration import load_config
from src.data.raw import download_data


def main():
    """Main function to test the downloading of raw datasets using the new config system."""
    # Load the configuration for the year 2025
    config = load_config(2025)

    # Download and save the raw datasets based on the loaded configuration
    download_data.main(config=config)


if __name__ == "__main__":
    main()
