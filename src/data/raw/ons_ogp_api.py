#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script allows users to access the Office for National Statistics (ONS) Open Geography Portal
to retrieve a lookup file between Local Authority Districts and Police Force Areas in England and Wales.

Heavily lifted from Rich Leyshon's helpful blog at https://thedatasavvycorner.com/blogs/06-working-with-ons-open-geo-portal
"""

import logging

import pandas as pd
import requests

import src.utilities as utils

config = utils.read_config()
utils.setup_logging()

ENDPOINT = config['data']['downloadPaths']['ons_la_pfa_2024']
PARAMS = config['ons_ogp_params']
PATH = config['data']['intFilePath']
FILENAME = config['data']['datasetFilenames']['ons_la_pfa']


def request_to_df(url: str, query_params: dict) -> tuple[requests.Response, pd.DataFrame]:
    """Send a get request to ArcGIS API & store the response as a DataFrame.

    Parameters
    ----------
    url : str
        The url endpoint.
    query_params : dict
        A dictionary of query parameter : value pairs.

    Returns
    -------
    requests.response
        The response from ArcGIS API server.
    pd.DataFrame
        A DataFrame of the requested data in the records specified by
        the response metadata.

    Raises
    ------
    requests.exceptions.RequestException
        The response was not ok.
    """
    query_params["f"] = "geoJSON"
    response = requests.get(url, params=query_params, timeout=10)
    if response.ok:
        content = response.json()
        records = [feature['properties'] for feature in content['features']]
        return (
            response,
            pd.DataFrame(records))
    else:
        raise requests.RequestException(
            f"HTTP Code: {response.status_code}, Status: {response.reason}"
        )


def main():
    """Main function to set up logging and return the response and DataFrame."""
    _, df = request_to_df(ENDPOINT, PARAMS)
    logging.info("Successfully retrieved data from ONS Open Geography Portal.")

    utils.safe_save_data(
        df,
        PATH,
        FILENAME,
    )


if __name__ == "__main__":
    main()
