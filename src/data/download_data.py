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

import requests

import src.utilities as utils

config = utils.read_config()


def download_files(url=config['data']['downloadPaths'].get('cjs_dec_2024'), path=config['data']['rawFilePath']):
    """Downloads file from a given API URL if not already downloaded."""
    response = requests.get(url, timeout=10)
    data = response.json()

    """
    NOTE: This section could be abstracted into a separate function
    to handle the extraction of URLs from the JSON response.
    """
    attachments = data['details']['attachments']

    # Filtering attachments to download
    files = [
        attachment['url'] for attachment in attachments
        if attachment.get('content_type') == 'application/zip'
        and "outcomes by offence" in attachment.get('title', '').lower()
    ]

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
    download_files()


if __name__ == "__main__":
    # Run the main function
    with ThreadPoolExecutor() as executor:
        executor.submit(main)
    # Ensure the script runs when executed directly
