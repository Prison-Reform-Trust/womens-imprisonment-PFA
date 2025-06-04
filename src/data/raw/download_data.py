#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script downloads the data needed for analysis from the Ministry of Justice
Criminal Justice System statistics quarterly: December 2024.

Published at https://www.gov.uk/government/collections/criminal-justice-statistics-quarterly
"""

import logging
import os
import zipfile
from io import BytesIO
from typing import Callable, Dict, List, Optional

import requests

import src.data.raw.data_filters as data_filters
import src.data.raw.ons_api as ons_api
import src.utilities as utils

config = utils.read_config()


def fetch_json(url: str, timeout: int = 10) -> Dict:
    """Fetch and return JSON data from a given URL."""
    logging.info("Fetching JSON data from %s", url)
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def ensure_directory(path: str) -> None:
    """Ensure the download directory exists."""
    os.makedirs(path, exist_ok=True)


def download_file(url: str, path: str) -> None:
    """Download a file from a URL to a given path."""
    response = requests.get(url, timeout=10)
    with open(path, 'wb') as f:
        f.write(response.content)
    logging.info("Downloaded file %s to %s", os.path.basename(path), path)


def download_files(
    url: str,
    path: str,
    file_filter: Callable[[Dict], List[str]],
    filename_fn: Optional[Callable[[str, Dict], str]] = None,
    zip_filter: Optional[Callable[[str], bool]] = None
) -> None:
    """
    Downloads files from a given API URL using a file filter function.
    Skips files that already exist locally.
    Automatically detects and extracts ZIP files if necessary.
    """
    data = fetch_json(url)
    file_urls = file_filter(data)

    ensure_directory(path)

    if not file_urls:
        logging.warning("No files matched the filter criteria.")
        return

    files_downloaded = False
    files_skipped = 0

    for file_url in file_urls:
        filename = filename_fn(file_url, data) if filename_fn else os.path.basename(file_url)
        full_path = os.path.join(path, filename)

        if os.path.exists(full_path):
            logging.info("Skipping %s (already downloaded).", filename)
            files_skipped += 1
            continue

        response = requests.get(file_url, timeout=100)
        response.raise_for_status()

        content = BytesIO(response.content)

        if zipfile.is_zipfile(content):
            logging.info("Detected ZIP file: %s", file_url)
            with zipfile.ZipFile(content) as zf:
                to_extract = [f for f in zf.namelist() if zip_filter is None or zip_filter(f)]
                for f in to_extract:
                    extracted_path = os.path.join(path, f)
                    if os.path.exists(extracted_path):
                        logging.info("Skipping %s (already extracted).", f)
                        files_skipped += 1
                        continue

                    zf.extract(f, path)
                    logging.info("Extracted: %s", f)
                    files_downloaded = True

    if files_downloaded:
        logging.info("Downloads complete.")
    elif files_skipped == len(file_urls):
        logging.info("All files were already downloaded. No new downloads.")


def ons_filename_fn(file_url: str, metadata: Dict) -> str:
    """
    Custom filename function for ONS datasets to address unclear default values."""
    edition = metadata.get("edition", "unknown-edition")
    base = os.path.basename(file_url)
    return f"{edition}_v{base}"


def get_outcomes_by_offence_data():
    """
    Function to download outcomes by offence data.
    """
    logging.info("Starting download of outcomes by offence data.")
    download_files(
        url=config['data']['downloadPaths'].get('cjs_dec_2024'),
        path=config['data']['rawFilePath'],
        file_filter=data_filters.outcomes_by_offence_data_filter,
        zip_filter=data_filters.zip_filter_csv_outcomes,
    )
    logging.info("Outcomes by offence data download completed.")


def get_population_data():
    """
    Function to download population data.
    """
    logging.info("Starting download of population data.")
    download_files(
        url=ons_api.get_population_url(),
        path=config['data']['rawFilePath'],
        file_filter=data_filters.population_data_filter,
        filename_fn=ons_filename_fn
    )
    logging.info("Population data download completed.")


def raw_data_pipeline():
    """
    Function to run the raw data pipeline.
    """
    logging.info("Starting raw data pipeline.")
    get_outcomes_by_offence_data()
    get_population_data()

    # Add more data download functions here as needed
    logging.info("Raw data pipeline completed.")


def main():
    """Main function to download files."""
    utils.setup_logging()
    raw_data_pipeline()


if __name__ == "__main__":
    main()
