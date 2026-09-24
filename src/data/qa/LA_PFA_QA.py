#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a quick and dirty placeholder script to incorporate my previous work on combining local authorities and
police force areas for QA purposes.

Raw data is sourced from the Office for National Statistics (ONS) and includes population estimates
for England and Wales, as well as a lookup table for local authority districts to police force areas
as of December 2022.
Data sources:
https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland/mid2021/populationestimatesmid2021unformatteddata.zip
https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland/mid2021/dataforreconciliation.zip
https://geoportal.statistics.gov.uk/datasets/4206337e432b45f686e29ac31d731765_0/

"""

import logging
from typing import Tuple

import pandas as pd

import src.data.processing.common_ons_processing as common_processing
import src.data.processing.la_to_pfa_matching as la_to_pfa_matching
import src.utilities as utils


# 1. Combining population estimates for England and Wales from 2021 census and MYE reconciliation data
def load_population_data(config: dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the population estimates and reconciliation data.
    Parameters:
        config (dict): Configuration dictionary containing file paths and other settings.
    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: DataFrames for population estimates and reconciliation data
    """
    df_population = utils.load_data(
        status='raw',
        filename='MYEB1_detailed_population_estimates_series_UK_(2021_geog21).csv',
        config=config
    )

    df_reconciliation = utils.load_data(
        status='raw',
        filename='MYEB2_detailed_components_of_change_for reconciliation_EW_(2021_geog21).csv',
        usecols=range(25),  # Not including 'population_2021' column
        config=config
    )

    return df_population, df_reconciliation


def load_la_to_pfa_lookup(filename: str, config: dict) -> pd.DataFrame:
    """Load the Local Authority to PFA lookup file."""
    la_to_pfa_lookup_filename = filename
    return utils.load_data(
        status='raw',
        filename=la_to_pfa_lookup_filename,
        config=config
    )


def prepare_population_data(df: pd.DataFrame) -> pd.DataFrame:
    """Preprocess DataFrame to:
    - Rename columns
    - Filter for England and Wales
    - Filter for adult women
    """
    logging.info("Preprocessing population data...")
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
    )
    return df


def combine_population_data(df_population: pd.DataFrame, df_reconciliation: pd.DataFrame) -> pd.DataFrame:
    """Combine the population estimates with the reconciliation data."""
    logging.info("Combining 2021 census population figures with reconciliation data...")
    df_population, df_reconciliation = map(prepare_population_data, [df_population, df_reconciliation])

    df_merged = df_reconciliation.merge(
        df_population[['ladcode', 'sex', 'age', 'population_2021']],
        how='inner',
        on=['ladcode', 'sex', 'age']
    )
    return df_merged


def process_population_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the DataFrame to:
    - Melt the DataFrame to long format
    - Clean the year column
    - Combine age groups for aggregation
    """
    df = (
        df
        .pipe(common_processing.melt_data)
        .pipe(common_processing.clean_year_column)
        .pipe(common_processing.group_and_sum)
        .assign(year=lambda df: df['year'].astype(int))
    )
    return df


def map_la_to_pfa(df_pop: pd.DataFrame, la_pfa_lookup: pd.DataFrame) -> pd.DataFrame:
    """Map Local Authority Districts to Police Force Areas in the population dataset."""
    df = (
        la_to_pfa_matching.assign_pfa(la_pfa_lookup, df_pop)
        .pipe(la_to_pfa_matching.filter_and_clean_data)
    )
    return df


def load_and_process_data(config: dict) -> pd.DataFrame:
    """Load, process, and return the combined population DataFrame with PFAs.
    Parameters:
        config (dict): Configuration dictionary containing file paths and other settings.
    Returns:
        pd.DataFrame: Processed DataFrame with population data and PFA mapping.
    """
    df_population, df_reconciliation = load_population_data(config=config)
    la_pfa_lookup = load_la_to_pfa_lookup(
        filename=config['data']['Filenames']['la_to_pfa_lookup'],
        config=config
    )

    df = (
        combine_population_data(df_population, df_reconciliation)
        .pipe(process_population_data)
        .pipe(map_la_to_pfa, la_pfa_lookup)
        )
    return df


def main(config: dict):
    """Main function to load, process, and save the population data with PFA mapping.
    Parameters:
        config (dict): Configuration dictionary containing file paths and other settings.
    """
    df = load_and_process_data(config=config)
    min_year, max_year = utils.get_year_range(df)
    filename = utils.get_output_filename(
        year=(min_year, max_year),
        template=config['data']['qaFilenames']['la_pfa']
        )

    utils.safe_save_data(
        df=df,
        path=config['paths']['interim'],
        filename=filename
    )
