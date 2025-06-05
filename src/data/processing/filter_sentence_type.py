#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the Criminal Justice System statistics quarterly: December 2024
datasets for analysis. It filters the data to include only relevant records. This includes
sentence types such as 'Immediate custody', 'Community sentence', and 'Suspended sentence',
and excludes certain police force areas like 'Special/miscellaneous and unknown police forces'
and 'City of London', it also excludes children.

Published at https://www.gov.uk/government/collections/criminal-justice-statistics-quarterly
"""
import logging

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

OUTCOMES_BY_OFFENCE = config['data']['datasetFilenames']['outcomes_by_offence']
OUTCOMES_BY_OFFENCE_EARLIER = config['data']['datasetFilenames']['outcomes_by_offence_earlier']


def load_outcomes_data() -> pd.DataFrame:
    """
    Load the outcomes by offence data from the raw data directory.
    """
    columns = [
        'Police Force Area',
        'Year',
        'Sex',
        'Age Group',
        'Offence Group',
        'Sentence Outcome',
        'Custodial Sentence Length',
        'Sentenced'
    ]
    dataframes = []

    logging.info("Loading outcomes by offence data...")
    for filename in [OUTCOMES_BY_OFFENCE, OUTCOMES_BY_OFFENCE_EARLIER]:
        try:
            df = utils.load_data(
                status='raw',
                filename=filename,
                usecols=columns
            )
        except FileNotFoundError:
            logging.warning("File %s not found; skipping.", filename)
        else:
            dataframes.append(df)

    return pd.concat(dataframes, ignore_index=True)


def join_dataframes(dataframes: list) -> pd.DataFrame:
    """
    Join multiple DataFrames into a single DataFrame.

    Parameters
    ----------
    dataframes : list
        List of DataFrames to be joined.

    Returns
    -------
    DataFrame
        A single DataFrame containing all the data from the input DataFrames.
    """
    if not dataframes:
        return pd.DataFrame()

    return pd.concat(dataframes, ignore_index=True)


def main():
    """
    Main function to process the sentencing data.
    It loads the data, applies filters, and returns a cleaned DataFrame.
    """

