#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes an earlier ONS Mid-2001 to mid-2020 detailed time series
edition of the ONS population data for QA purposes.

Available at:
https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland

"""

import logging

import pandas as pd

import src.data.processing.common_ons_processing as common_processing
import src.utilities as utils


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the DataFrame to:
    - Rename columns
    - Filter for England and Wales
    - Filter for adult women
    - Melt the DataFrame to long format
    - Clean the year column
    - Combine age groups for aggregation
    """
    # Define column patterns for standardisation
    column_patterns = {
        r"ladcode.*": "ladcode",
        r"laname|ladname": "laname"
    }

    df = (
        df
        .pipe(utils.standardise_columns, column_patterns)
        .pipe(common_processing.filter_england_wales)
        .pipe(common_processing.filter_adult_women, sex_value=2)
        .pipe(common_processing.melt_data)
        .pipe(common_processing.clean_year_column)
        .pipe(common_processing.group_and_sum)
    )

    return df


def load_and_process_data(config: dict) -> tuple[pd.DataFrame, int, int]:
    """
    Load the ONS population data, rename and reorder columns, and apply filters.
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and filenames.

    Returns
    -------
    tuple[pd.DataFrame, int, int]
        A tuple containing the processed DataFrame, minimum year, and maximum year.
    """
    logging.info("Loading comparator ONS population data...")

    df = utils.load_data(
        status='raw',
        filename="MYEB1_detailed_population_estimates_series_UK_(2020_geog21).csv",
        config=config
    )

    if df.empty:
        logging.error("No data loaded from ONS population file.")

    df = process_data(df)
    min_year, max_year = utils.get_year_range(df)

    logging.info("Data successfully processed for ONS comparator population estimates")
    return df, min_year, max_year


def main(config: dict) -> None:
    """
    Main function to process the sentencing data.
    It loads the data, applies filters, and returns a cleaned DataFrame.
    Parameters
    ----------
    config : dict
        Configuration dictionary containing paths and filenames.
    """

    df, min_year, max_year = load_and_process_data(config=config)

    output_filename_template = config['data']['qaFilenames']['ons_comparator']
    filename = utils.get_output_filename(year=(min_year, max_year), template=output_filename_template)

    if not isinstance(df, pd.DataFrame):
        logging.error("Data processing failed, no DataFrame returned.")
        return

    utils.safe_save_data(
        df=df,
        path=config['paths']['interim'],
        filename=filename
    )
