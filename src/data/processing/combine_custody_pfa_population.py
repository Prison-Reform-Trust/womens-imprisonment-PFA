#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the ONS population by Police Force Area (PFA) data and
combines it with the Criminal Justice System (CJS) statistics custody data to
enable calculation of the imprisonment rate by PFA.
"""

import logging
from typing import Tuple

import pandas as pd

import src.utilities as utils

config = utils.read_config()
utils.setup_logging()

OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['match_la_to_pfa']


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the PFA population data and CJS custody data."""
    custody_data_template = config['data']['datasetFilenames']['make_custody_tables_template']
    custody_data_filename = custody_data_template.format(category='all')

    population_data_filename = utils.fetch_latest_file(
        pattern="*LA_PFA_population*.csv",  # NOTE: Would be better to draw this from config
        path=config['data']['intFilePath']
    )

    custody_data = utils.load_data('processed', custody_data_filename)
    population_data = utils.load_data('interim', population_data_filename)
    return custody_data, population_data


def process_custody_data(custody_data: pd.DataFrame) -> pd.DataFrame:
    """Process the CJS custody data to ensure it is in the correct format."""
    logging.info("Processing CJS custody data...")
    custody_data = (
        custody_data
        .drop(custody_data.columns[-1], axis=1)
        .melt(id_vars='pfa', var_name='year', value_name='custody_count')
        .assign(year=lambda df: df['year'].astype(int))
        .sort_values(by=['pfa', 'year'])
    )

    return custody_data


def process_population_data(population_data: pd.DataFrame, custody_data: pd.DataFrame) -> pd.DataFrame:
    """Process the population data to ensure it is in the correct format."""
    min_year, _ = utils.get_year_range(custody_data)
    logging.info("Processing population data...")
    population_data = (
        population_data
        .loc[lambda df: df['year'] >= min_year]  # Filter years to match population data
        # .drop(columns=['ladcode', 'pfa'])
        # .rename(columns={'pfa': 'pfa'})
        # .melt(id_vars='pfa', var_name='year', value_name='population')
        # .assign(year=lambda df: df['year'].astype(int))
        # .sort_values(by=['pfa', 'year'])
    )

    return population_data


def filter_and_clean_data(df_pop: pd.DataFrame) -> pd.DataFrame:
    """Filter the DataFrame to remove rows with missing PFA and City of London,
    and standardize Devon & Cornwall name using method chaining."""
    logging.info("Filtering and cleaning population data...")
    return (
        df_pop
        .dropna(subset=['pfa'])
        .loc[lambda df: df['pfa'] != 'London, City of']
        .assign(pfa=lambda df: df['pfa'].replace({'Devon & Cornwall': 'Devon and Cornwall'}))
    )


def load_and_process_data() -> Tuple[pd.DataFrame, int, int]:
    """Load, process, and return the population DataFrame with PFA mapping."""
    la_pfa, df_pop = load_data()
    df_pop = (
        match_la_to_pfa(la_pfa, df_pop)
        .pipe(filter_and_clean_data)
    )
    min_year, max_year = utils.get_year_range(df_pop)

    logging.info("Data successfully processed for Local Authority to PFA matching.")
    return df_pop, min_year, max_year


def main():
    """Main function to load, process, and save the data."""

    df, min_year, max_year = load_and_process_data()
    filename = utils.get_output_filename(year=(min_year, max_year), template=OUTPUT_FILENAME_TEMPLATE)

    utils.safe_save_data(
        df,
        path=config['data']['intFilePath'],
        filename=filename
    )


if __name__ == "__main__":
    main()
