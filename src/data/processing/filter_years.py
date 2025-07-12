"""
This script provides functions to filter dataframes by years.
"""

import logging

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()


def get_year(df: pd.DataFrame, year_from: int = 2014, year_to: int = None, column: str = "year") -> pd.DataFrame:
    """_summary_

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be filtered by year
    year_from : int
        The starting year to filter the data from (inclusive)
    year_to : int (optional)
        The end year to filter the data to (inclusive). Default will
        return all years after `year_from` if not specified.
    column : str (optional) "year" (default)
        The column name of the dataframe with the year value

    Returns
    -------
    pd.DataFrame
        A filtered dataframe including records with year_from to year_to
    """
    if column not in df.columns:
        raise ValueError("The DataFrame must contain a valid year column.")

    if year_to is None:
        logging.info("Filtering data from %s onwards", year_from)
        filt = df[column] >= year_from
        return df[filt]

    logging.info("Filtering data from %s to %s", year_from, year_to)
    filt_start = df[column] >= year_from
    filt_end = df[column] < year_to
    filt = filt_start & filt_end

    return df[filt]
