#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes an earlier ONS Mid-2001 to mid-2020 detailed time series
edition of the ONS population data for QA purposes.

Available at: https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland

"""

import logging
import re

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['ons_comparator']


def load_population_data(filename: str = "MYEB1_detailed_population_estimates_series_UK_(2020_geog21).csv") -> pd.DataFrame:
    """
    Load the ONS population data from the raw data directory.
    """

    logging.info("Loading ONS population data...")
    try:
        df = utils.load_data(
            status='raw',
            filename=filename
        )
    except FileNotFoundError:
        logging.warning("File %s not found.", filename)

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns: if a column contains 'ladcode' or 'laname', strip any extra characters after.
    """
    logging.info("Renaming columns with regex...")

    def clean_col(col):
        if re.match(r"ladcode", col):
            return "ladcode"
        elif re.match(r"laname", col):
            return "laname"
        return col

    df = df.rename(columns=clean_col)
    return df


def filter_england_wales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to only include data for England and Wales.
    """
    filt = df['country'].str.contains("(?:^E|^W)", regex=True)
    df_eng_wales = df[filt]
    return df_eng_wales


def filter_adult_women(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to include only adult women (age >= 18, sex == 2).
    Sex 2 corresponds to female in the dataset.
    """
    logging.info("Filtering for adult women...")

    df = df[(df['age'] >= 18) & (df['sex'] == 2)]

    return df


def melt_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melt the DataFrame from wide to long format.
    The 'population_' prefix in the year column is removed.
    """
    logging.info("Melting DataFrame from wide to long format...")

    return df.melt(id_vars=["ladcode", "laname", "country", "sex", "age"], var_name="year", value_name="freq")


def clean_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the 'year' column by removing the 'population_' prefix.
    """
    logging.info("Cleaning year column...")
    df['year'] = df['year'].str.replace("population_", "", regex=True)
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
    Process the DataFrame to:
    - Rename columns
    - Filter for England and Wales
    - Filter for adult women
    - Melt the DataFrame to long format
    - Clean the year column
    - Combine age groups for aggregation
    """
    df = (
        df
        .pipe(rename_columns)
        .pipe(filter_england_wales)
        .pipe(filter_adult_women)
        .pipe(melt_data)
        .pipe(clean_year_column)
        .pipe(combine_ages)
    )

    return df


def load_and_process_data():
    """
    Load the ONS population data, rename and reorder columns, and apply filters.

    Returns
    -------
    DataFrame
        The processed DataFrame ready for further QA work with latest edition.
    """
    df = load_population_data()
    if df.empty:
        logging.error("No data loaded from ONS population file.")
        return pd.DataFrame()

    df = process_data(df)
    min_year, max_year = utils.get_year_range(df)

    logging.info("Data successfully processed for ONS comparator population estimates")
    return df, min_year, max_year


def main():
    """
    Main function to process the sentencing data.
    It loads the data, applies filters, and returns a cleaned DataFrame.
    """

    df, min_year, max_year = load_and_process_data()
    filename = utils.get_output_filename(year=(min_year, max_year), template=OUTPUT_FILENAME_TEMPLATE)

    utils.safe_save_data(
        df=df,
        path=config['data']['intFilePath'],
        filename=filename
    )


if __name__ == "__main__":
    main()
