#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the ONS Local Authority to to PFA lookup file and matches
the Local Authority Districts (LAD) to Police Force Areas (PFA) in England and Wales
against the latest ONS mid-year population estimates for further analysis.

This script is part of the data processing pipeline, and results in a cleaned interim
DataFrame by:
    - Loading the processed ONS population data from the interim data directory.
    - Loading the Local Authority to PFA lookup file from the raw data directory.
    - Creates a dictionary to map Local Authority Districts (LAD) to Police Force Areas (PFA).
    - Merging the population data with the PFA lookup file to assign each Local Authority
      to its corresponding Police Force Area.
    - Filtering the merged DataFrame to remove any rows where the PFA is not in the lookup file,
      as well as City of London which is not relevant for this analysis.
    - Renaming Devon & Cornwall to Devon and Cornwall for consistency between datasets.
    - Saves the processed DataFrame to a CSV file in the `intFilePath` directory.
"""

import logging
from typing import Tuple

import pandas as pd

import src.utilities as utils


def load_data(config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the Local Authority to PFA lookup file and population data.
    Parameters:
        config (dict): Configuration dictionary containing file paths and names.
    Returns:
        tuple[pd.DataFrame, pd.DataFrame]: A tuple containing the Local Authority to PFA lookup DataFrame
        and the population DataFrame.
    """
    la_to_pfa_lookup = config['data']['filenames']['la_to_pfa_lookup']
    ons_la_data = utils.fetch_latest_file(
        pattern="*LA_population_women*.csv",  # NOTE: Would be better to draw this from config
        path=config['paths']['interim']
    )

    la_pfa = utils.load_data(
        status='raw',
        filename=la_to_pfa_lookup,
        config=config
    )

    df_pop = utils.load_data(
        status='interim',
        filename=ons_la_data,
        config=config
    )

    return la_pfa, df_pop


def assign_pfa(la_pfa: pd.DataFrame, df_pop: pd.DataFrame) -> pd.DataFrame:
    """Map Local Authority Districts to Police Force Areas in the population dataset
    using the lookup file and add a new PFA column."""

    # Check if the lookup file columns need to be standardised
    if 'ladcode' not in la_pfa.columns or 'pfa_name' not in la_pfa.columns:
        # Define column patterns for standardisation of lookup file
        column_patterns = {
            r"LAD.*CD": "ladcode",
            r"PFA.*NM": "pfa_name"
        }

        # Create lookup dictionary with standardisation
        logging.info("Matching Local Authority Districts to Police Force Areas...")
        la_pfa_dict = utils.create_lookup_dict(
            df=la_pfa,
            key_col_pattern="ladcode",
            value_col_pattern="pfa_name",
            column_patterns=column_patterns
        )
    else:
        # Columns already standardised, create dictionary directly
        logging.info("Matching Local Authority Districts to Police Force Areas...")
        la_pfa_dict = la_pfa.set_index('ladcode')['pfa_name'].to_dict()

    df_pop['pfa'] = df_pop['ladcode'].map(la_pfa_dict)
    return df_pop


def filter_and_clean_data(df_pop: pd.DataFrame) -> pd.DataFrame:
    """Filter the DataFrame to remove rows with missing PFA and City of London,
    and standardise Devon & Cornwall name using method chaining."""
    logging.info("Filtering and cleaning population data...")
    return (
        df_pop
        .dropna(subset=['pfa'])  # NOTE: These PFA values probably should be removed earlier in the pipeline.
        # They are E10 (Counties) and E11 codes (Metropolitan Counties) at a higher geographic level.
        .loc[lambda df: df['pfa'] != 'London, City of']
        .assign(pfa=lambda df: df['pfa'].replace({'Devon & Cornwall': 'Devon and Cornwall'}))
    )


def load_and_process_data(config: dict) -> Tuple[pd.DataFrame, int, int]:
    """Load, process, and return the population DataFrame with PFA mapping.
    Parameters:
        config (dict): Configuration dictionary containing file paths and names.
    Returns:
        Tuple[pd.DataFrame, int, int]: A tuple containing the processed population DataFrame
        with PFA mapping, the minimum year, and the maximum year in the dataset.
    """
    la_pfa, df_pop = load_data(config=config)

    df_pop = (
        assign_pfa(la_pfa, df_pop)
        .pipe(filter_and_clean_data)
    )
    min_year, max_year = utils.get_year_range(df_pop)

    logging.info("Data successfully processed for Local Authority to PFA matching.")
    return df_pop, min_year, max_year


def main(config: dict) -> None:
    """Main function to load, process, and save the data.
    Parameters:
        config (dict): Configuration dictionary containing file paths and names.
    """

    df, min_year, max_year = load_and_process_data(config=config)
    output_filename_template = config['data']['filenames']['la_to_pfa_matching']
    filename = utils.get_output_filename(year=(min_year, max_year), template=output_filename_template)

    utils.safe_save_data(
        df,
        path=config['paths']['interim'],
        filename=filename
    )
