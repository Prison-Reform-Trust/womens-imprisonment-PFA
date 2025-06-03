#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script allows users to access the Office for National Statistics (ONS) API 
to retrieve metadata about available datasets and download by name, version, and other attributes.

Heavily lifted from David Corney's repo at https://github.com/dcorney/ons_api_demo/tree/main
"""

import logging

import pandas as pd
import requests

import src.utilities as utils


def get_list_of_datasets(
        url="https://api.beta.ons.gov.uk/v1/",
        limit=100,
        offset=0

        ):
    """This function retrieves metadata for available datasets from the Office for National Statistics (ONS) API.

    Returns
    -------
    list of dicts
        Metadata objects for each available dataset.
    """
    datasets = []

    while len(datasets) < limit:
        r = requests.get(url + "datasets", params={"offset": offset}, timeout=10)
        results = r.json()
        datasets.extend(results.get("items"))
        num_retrieved = results.get("count")
        offset += num_retrieved
        if num_retrieved == 0:
            break
    logging.info("Found %d datasets", len(datasets))
    return datasets


def get_dataset_by_name(datasets, target_name):
    """Get a dataset by matching on its title (or part of the title).
    Returns the first dataset object whose name contains the given target_name string.

    Parameters
    ----------
    datasets : List
        List of dataset objects
    target_name : str
        name (or partial name) of target dataset

    Returns
    -------
    dict
        Dataset object (or None, if no match is found)
    """
    for ds in datasets:
        if target_name.lower() in ds.get("title").lower():
            logging.info("Found dataset %s", ds.get('title'))
            return ds
    logging.info("No dataset found containing %s", target_name)
    return None


def get_edition(dataset, prefered_edition="time-series"):
    """Get one edition of a dataset. If no preferred edition is
    specified, return the most recent one.

    Parameters
    ----------
    dataset : dict
        dataset metadata
    prefered_edition : str, optional
        name of edition, by default "time-series"

    Returns
    -------
    str
        URL of edition
    """
    editions_url = dataset.get("links").get("editions").get("href")
    r = requests.get(editions_url, timeout=10)
    results = r.json()
    for row in results.get("items"):
        if row.get("edition") == prefered_edition:
            edition = row.get("links").get("latest_version").get("href")
            logging.info("Found dataset edition: %s", row.get("edition"))
            return edition

    # Default to latest version, if requested version is not found.
    latest_version = dataset.get("links").get("latest_version").get("href")
    logging.info("Found latest edition: %s", latest_version)
    return latest_version


def get_population_url():
    """Get the API URL for the mid-year population estimates dataset from ONS.

    Returns
    -------
    str
        URL of the population dataset.
    """
    datasets = get_list_of_datasets()
    population_dataset = get_dataset_by_name(datasets, "Population estimates")
    if not population_dataset:
        raise ValueError("Population dataset not found.")

    edition_url = get_edition(population_dataset)
    return edition_url


def main():
    """Main function to set up logging and return the population dataset URL."""
    utils.setup_logging()
    return get_population_url()


if __name__ == "__main__":
    main()
