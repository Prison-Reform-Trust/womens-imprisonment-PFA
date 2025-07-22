"""
This script allows users to access the Office for National Statistics (ONS) Open Geography Portal
to retrieve a lookup file between Local Authority Districts and Police Force Areas in England and Wales.

Rich Leyshon's blog at https://thedatasavvycorner.com/blogs/06-working-with-ons-open-geo-portal was particularly
helpful in understanding how to use the ONS Open Geography Portal API.
"""

import logging

import pandas as pd
import requests

import src.utilities as utils

config = utils.read_config()
utils.setup_logging()


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


def main(endpoint: str, params: dict, path: str, filename: str) -> None:
    """Main function to set up logging and return the response and DataFrame."""
    _, df = request_to_df(endpoint, params)
    logging.info("Successfully retrieved data from ONS Open Geography Portal.")

    if utils.check_file_exists(path, filename):
        return

    utils.safe_save_data(
        df,
        path,
        filename,
    )
