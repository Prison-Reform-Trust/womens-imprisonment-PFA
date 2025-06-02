#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script downloads the data needed for analysis from the Ministry of Justice
Criminal Justice System statistics quarterly: December 2024.

Published at https://www.gov.uk/government/collections/criminal-justice-statistics-quarterly
"""

import logging
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Dict, List

import requests

import src.data.raw.data_filters as data_filters
import src.utilities as utils

config = utils.read_config()


def download_files(
        url: str,
        path: str,
        file_filter: Callable[[List[Dict]], List[str]]
        ):
    """
    Downloads file from a given API URL if not already downloaded.
    """
    response = requests.get(url, timeout=10)
    data = response.json()
    logging.info("Downloading data from %s", url)

    # Filtering attachments to download
    files = file_filter(data)

    os.makedirs(path, exist_ok=True)  # Ensure the directory exists

    files_downloaded = False  # Track if any files were downloaded
    files_skipped = 0  # Track skipped files

    for file in files:
        filename = os.path.join(path, os.path.basename(file))

        if os.path.exists(filename):
            logging.info("Skipping %s (already downloaded).", os.path.basename(filename))
            files_skipped += 1
            continue  # Skip downloading this file

        # Make a GET request to download the spreadsheet file
        file_response = requests.get(file, timeout=10)

        # Save the spreadsheet content to a local file
        with open(filename, 'wb') as file:
            file.write(file_response.content)

        logging.info("Downloaded file %s to %s", os.path.basename(filename), path)
        files_downloaded = True  # Mark that at least one file was downloaded

    # Log completion message
    if files_downloaded:
        logging.info("Download completes")
    elif files_skipped == len(files):
        # Only log this message once if all files were skipped
        logging.info("All files for %s were already downloaded. No new downloads.", filename)


def main():
    """Main function to download files."""
    utils.setup_logging()
    download_files(
        url=config['data']['downloadPaths'].get('cjs_dec_2024'),
        path=config['data']['rawFilePath'],
        file_filter=data_filters.outcomes_by_offence_data_filter
    )


if __name__ == "__main__":
    # Run the main function
    with ThreadPoolExecutor() as executor:
        executor.submit(main)
    # Ensure the script runs when executed directly
