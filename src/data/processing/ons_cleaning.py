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
import glob
import logging
import os
from typing import Tuple

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['ons_cleaning']


def find_latest_ons_population_file(pattern: str = "*ONS*_v*.csv", path: str = config['data']['rawFilePath']) -> str:
    """
    Find the latest ONS population file in the given directory matching the pattern.
    Returns the filename (not the full path).
    """
    files = glob.glob(os.path.join(path, pattern))
    if not files:
        raise FileNotFoundError(f"No ONS population files found in {path}.")
    # Sort by modification time, newest last
    files.sort(key=os.path.getmtime)
    return os.path.basename(files[-1])


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
    input_filename = find_latest_ons_population_file()
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
    df.columns = [
        'freq',
        'year',
        'ladcode',
        'laname',
        'sex',
        'age',
    ]
    column_order = ['ladcode', 'laname', 'year', 'sex', 'age', 'freq']

    return df[column_order]


def remove_regional_and_national_aggregates(
        df: pd.DataFrame,
        name_col: str = 'laname',
        code_col: str = 'ladcode') -> pd.DataFrame:
    """
    Drop rows containing aggregated regional or national data,
    which are not relevant for local area analysis.
    """
    logging.info("Finding aggregated national and regional data codes...")
    logging.info("Current number of rows: %d", len(df))

    drop_codes = list(df[df[name_col].str.isupper()][code_col].unique())
    logging.info("Aggregated codes found: %s", drop_codes)

    logging.info("Dropping unwanted rows...")
    df = df[~df[code_col].isin(drop_codes)]

    logging.info("Rows dropped. Remaining rows: %d", len(df))
    return df


def filter_adult_women(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to include only adult women (age >= 18, sex == "Female").
    Handles "90+" by treating it as 90 for filtering.
    """
    logging.info("Filtering for adult women...")

    # Replacing "90+" with 90 to allow for filtering
    df['age'] = df['age'].cat.rename_categories({"90+": 90})
    df['age'] = pd.to_numeric(df['age'], errors='coerce')
    df = df[(df['age'] >= 18) & (df['sex'] == "Female")]

    return df


def combine_ages(df: pd.DataFrame) -> pd.DataFrame:
    """Combine age groups for aggregation."""
    logging.info("Combining age groups for aggregation...")

    # Ensure columns exist before grouping
    required_columns = ['ladcode', 'laname', 'year', 'freq']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise KeyError(f"Missing columns in DataFrame: {missing_cols}")
    return df.groupby(['ladcode', 'laname', 'year'], as_index=False, observed=True).agg({'freq': 'sum'})


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply filters to the DataFrame to include only relevant records.

    Parameters
    ----------
    df : DataFrame
        The DataFrame to be filtered.

    Returns
    -------
    DataFrame
        The filtered DataFrame.
    """
    logging.info("Processing data...")
    df = (
        rename_and_reorder_columns(df)
        .pipe(remove_regional_and_national_aggregates)
        .pipe(filter_adult_women)
        .pipe(combine_ages)
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
