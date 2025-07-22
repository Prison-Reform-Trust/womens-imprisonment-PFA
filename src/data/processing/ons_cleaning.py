#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the ONS mid-year population estimates into a cleaned DataFrame
for further analysis.

This script is part of the data processing pipeline, and results in a cleaned interim
DataFrame by:
    - Loading the latest ONS population data from the raw data directory.
    - Renaming and reordering columns to a standard format.
    - Removing regional and national aggregated figures that are not relevant
    for local area analysis.
    - Filtering the data to include only adult women.
    - Combines age groups to calculate the total number of adult women in each
    local authority area by year.
    - Saves the processed DataFrame to a CSV file in the `intFilePath` directory.

"""
import logging
from typing import Tuple

import pandas as pd

import src.data.processing.common_ons_processing as common_processing
import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['ons_cleaning']


def load_population_data() -> pd.DataFrame:
    """
    Load the ONS population data from the raw data directory.
    """
    columns = [
        'administrative-geography',
        'Geography',
        'calendar-years',
        'Sex',
        'Age',
        'v4_0',
    ]

    logging.info("Loading ONS population data...")
    input_filename = utils.fetch_latest_file(
        pattern="*ONS*_v*.csv",
        path=config['data']['rawFilePath']
    )
    try:
        df = utils.load_data(
            status='raw',
            filename=input_filename,
            usecols=columns
        )
    except FileNotFoundError:
        logging.warning("File %s not found. Have you run download_data.py first?", input_filename)

    return df


def rename_and_reorder_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename and reorder columns in the DataFrame to a standard format.

    Parameters
    ----------
    df : DataFrame
        The DataFrame with original column names.

    Returns
    -------
    DataFrame
        The DataFrame with renamed columns.
    """
    logging.info("Renaming columns...")
    df.columns = [
        'freq',
        'year',
        'ladcode',
        'laname',
        'sex',
        'age',
    ]
    logging.info("Reordering columns...")
    column_order = ['ladcode', 'laname', 'year', 'sex', 'age', 'freq']

    return df[column_order]


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply filters to the DataFrame to include only relevant records.
    """
    logging.info("Processing data...")
    df = (
        rename_and_reorder_columns(df)
        .pipe(common_processing.remove_regional_and_national_aggregates)
        .pipe(common_processing.filter_adult_women, sex_value='Female')
        .pipe(common_processing.group_and_sum)
    )
    return df


def load_and_process_data() -> Tuple[pd.DataFrame, int, int]:
    """
    Load the ONS population data, rename and reorder columns, and apply filters.

    Returns
    -------
    Tuple[DataFrame, int, int]
        The processed DataFrame, minimum year, and maximum year.
    """
    df = load_population_data()
    if df.empty:
        logging.error("No data loaded from ONS population file.")
        return pd.DataFrame(), 0, 0

    df = process_data(df)
    min_year, max_year = utils.get_year_range(df)

    logging.info("Data successfully processed for ONS population estimates")
    return df, min_year, max_year


def main():
    """
    Main function to process the sentencing data.
    It loads the data, applies filters, and returns a cleaned DataFrame.
    """

    df, min_year, max_year = load_and_process_data()
    filename = utils.get_output_filename(year=(min_year, max_year), template=OUTPUT_FILENAME_TEMPLATE)

    utils.safe_save_data(
        df,
        path=config['data']['intFilePath'],
        filename=filename
    )


if __name__ == "__main__":
    main()
