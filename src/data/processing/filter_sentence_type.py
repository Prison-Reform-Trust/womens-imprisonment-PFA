#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the Criminal Justice System statistics quarterly: December 2024
Outcomes by Offence datasets. It filters the data to include only relevant records which are
set in config['outcomes_by_offence_filter']. This includes sentence types such as
'Immediate custody', 'Community sentence', and 'Suspended sentence',
and excludes 'Not known' police force areas, it also excludes children.

It renames and reorders columns, applies regex replacements to clean up the data,
and saves the processed DataFrame to a CSV file in the `intFilePath` directory.

This script is part of the data processing pipeline, and results in a cleaned interim
DataFrame ready for further processing to produce the following dataset:
    * The number of women in each Police Force Area who received an immediate custodial sentence of:
        - Less than six months
        - Six to less than 12 months
        - 12 months or more
    [Used to produce Figure 2 and further processing].
"""

import logging
import os
import re

import pandas as pd
from pandas.api.types import CategoricalDtype

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
        'year',
        'sex',
        'age_group',
        'pfa',
        'offence',
        'outcome',
        'sentence_len',
        'freq'
    ]
    column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_len', 'freq']

    return df[column_order]


def apply_multiple_regex_replacements(
    df: pd.DataFrame,
    replacements: dict
) -> pd.DataFrame:
    """
    Apply multiple regex replacements per column in a DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to process.
    replacements : dict
        Dictionary where keys are column names and values are lists of (pattern, replacement) tuples.

    Returns
    -------
    pd.DataFrame
        The updated DataFrame with all regex replacements applied.
    """
    for col, changes in replacements.items():
        if col not in df.columns:
            continue

        if isinstance(df[col].dtype, CategoricalDtype):
            categories = df[col].cat.categories
            for pattern, repl in changes:
                categories = [re.sub(pattern, repl, cat) for cat in categories]
            df[col] = df[col].cat.rename_categories(categories)

        elif pd.api.types.is_object_dtype(df[col]):
            for pattern, repl in changes:
                df[col] = df[col].str.replace(pattern, repl, regex=True)

        else:
            logging.warning("Column %s is not object or category dtype. Skipping.", col)

    return df


def filter_dataframe(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """
    Filter the DataFrame based on include and exclude criteria.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to filter.
    filters : dict
        Dictionary containing 'include' and 'exclude' keys with filtering criteria.

    Returns
    -------
    pd.DataFrame
        The filtered DataFrame.
    """
    logging.info("Applying filters...")

    include = filters.get('include', {})
    exclude = filters.get('exclude', {})
    sort_by = filters.get('sort_by', [])

    for col, allowed_values in include.items():
        logging.info("Include filter on column '%s' with values: %s", col, allowed_values)
        df = df[df[col].isin(allowed_values)]

    for col, disallowed_values in exclude.items():
        logging.info("Exclude filter on column '%s' with values: %s", col, disallowed_values)
        df = df[~df[col].isin(disallowed_values)]

    if sort_by:
        df = df.sort_values(sort_by)
    logging.info("Data filtered.")

    return df


def process_data(df: pd.DataFrame, config_file: dict) -> pd.DataFrame:
    """
    Apply filters to the DataFrame to include only relevant records.

    Parameters
    ----------
    df : DataFrame
        The DataFrame to be filtered.
    config_file : dict
        Configuration dictionary containing filter criteria.

    Returns
    -------
    DataFrame
        The filtered DataFrame.
    """
    logging.info("Processing data...")

    # Defining regex replacements for specific columns
    regex_replacements = {
        'sex': [(r"\d\d: ", "")],
        'age_group': [(r"\d\d: ", "")],
        'offence': [(r"\d\d: ", "")],
        'outcome': [(r"\d\d: ", "")],
        'sentence_len': [
            (r"\d\d: ", ""),
            (r"Custody - ", ""),
            (r"Over", "More than"),
            (r"Life$", "Life sentence"),
        ]
    }
    # Filtering configuration
    filters = config_file.get('outcomes_by_offence_filter', {})

    df = (
        rename_and_reorder_columns(df)
        .pipe(
            apply_multiple_regex_replacements,
            replacements=regex_replacements
        )
        .pipe(
            filter_dataframe,
            filters=filters
        )
    )

    return df


def load_and_process_data() -> pd.DataFrame:
    """
    Load and filter the outcomes by offence data.

    Returns
    -------
    DataFrame
        The filtered DataFrame with relevant records.
    """
    df = (
        load_outcomes_data()
        .pipe(process_data, config_file=config)
    )
    logging.info("Data loaded and processed successfully.")
    return df


def main():
    """
    Main function to process the sentencing data.
    It loads the data, applies filters, and returns a cleaned DataFrame.
    """

    df = load_and_process_data()
    success = (
        utils.save_data(
            df,
            path=config["data"]["intFilePath"],
            filename=config['data']['datasetFilenames']['filter_sentence_type'])
        )
    if not success:
        logging.error('Data processing failed')


if __name__ == "__main__":
    main()
