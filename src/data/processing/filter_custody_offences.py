#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the Criminal Justice System statistics quarterly: December 2024
Outcomes by Offence datasets.

This script is part of the data processing pipeline, and results the following dataset:
    * The number of women in each Police Force Area who received an immediate custodial sentence
    in the latest available year, by offence
    [Used to produce Figure 3].
"""

import logging

import pandas as pd

import src.utilities as utils
from src.data.processing import filter_sentence_length, filter_years

utils.setup_logging()

config = utils.read_config()

INPUT_FILENAME = config['data']['datasetFilenames']['filter_sentence_type']
OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['filter_custody_offences']

HIGHLIGHTED_OFFENCE_GROUPS = ['Theft offences', 'Drug offences', 'Violence against the person']
ASSAULT_EMERGENCY_WORKER = "Assault of an emergency worker"


def load_data() -> pd.DataFrame:
    """
    Load the interim dataset and filter it to include only records with an immediate custodial sentence.
    Returns
    -------
    pd.DataFrame
        The filtered DataFrame containing only immediate custodial sentences.
    """
    logging.info("Loading interim data for custody offences...")
    df = utils.load_data(status='interim', filename=INPUT_FILENAME)
    return filter_sentence_length.filter_custodial_sentences(df)


def group_by_pfa_and_offence(df: pd.DataFrame, specific_offence: bool = True) -> pd.DataFrame:
    """
    Group the DataFrame by Police Force Area (PFA), year, offence, and optionally specific offence,
    summing the frequency of sentences.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame for processing.
    specific_offence : bool, optional
        If True, includes 'specific_offence' in the grouping. Defaults to True.

    Returns
    -------
    pd.DataFrame
        A DataFrame grouped by PFA, year, offence, and optionally specific offence, with summed frequencies.
    """
    columns = ['pfa', 'year', 'offence']
    if specific_offence:
        columns.append('specific_offence')

    logging.info("Grouping data by %s and summing frequencies...", ', '.join(columns))
    df_grouped = df.groupby(columns, observed=True)['freq'].sum().reset_index()

    return df_grouped


def extract_assault_of_emergency_worker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Store the 'Assault of an emergency worker' offence in a separate DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to modify.

    Returns
    -------
    pd.DataFrame
        The modified DataFrame with the 'Assault of an emergency worker' offence added.
    """
    logging.info("Extracting 'Assault of an emergency worker' offence...")
    mask_filter = df['specific_offence'] == ASSAULT_EMERGENCY_WORKER
    # Create a new DataFrame with the specific offence
    emergency_worker_df = df.loc[mask_filter].copy()
    emergency_worker_df['offence'] = ASSAULT_EMERGENCY_WORKER
    return emergency_worker_df


def add_assault_of_emergency_worker(df: pd.DataFrame, emergency_worker_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add the 'Assault of an emergency worker' offence to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to modify.
    emergency_worker_df : pd.DataFrame
        The DataFrame containing the 'Assault of an emergency worker' offence.

    Returns
    -------
    pd.DataFrame
        The modified DataFrame with the 'Assault of an emergency worker' offence added.
    """
    logging.info("Adding 'Assault of an emergency worker' offence to the main DataFrame...")
    # Append the assault of an emergency worker DataFrame to the main DataFrame
    return pd.concat([df, emergency_worker_df], ignore_index=True).sort_values(by=['offence', 'freq'], ascending=True).reset_index(drop=True)


def filter_offences(df: pd.DataFrame) -> pd.Series:
    """
    Creates a boolean mask to filter processing on DataFrame rows that
    are in the specified offence groups.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing offence data.

    Returns
    -------
    pd.Series
        A boolean mask indicating whether each row's offence is in the specified groups.
    """
    logging.info("Creating filter for highlighted offence groups...")
    return df['offence'].isin(HIGHLIGHTED_OFFENCE_GROUPS)


def set_parent_column(df: pd.DataFrame, filter_mask: pd.Series) -> pd.DataFrame:
    """
    Set the parent column in the DataFrame based on the filter mask.

    Note: This function modifies the input DataFrame in place.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to modify.
    filter_mask : pd.Series
        A boolean Series indicating which rows are highlighted.

    Returns
    -------
    pd.DataFrame
        The modified DataFrame with the parent column set.
    """
    logging.info("Setting parent column for offence groups...")
    # Set parent for highlighted offences and others
    df.loc[filter_mask, 'parent'] = "All offences"
    df.loc[~filter_mask, 'parent'] = "All other offences"
    # Use the first highlighted offence group that matches as parent for 'Assault of an emergency worker'
    df.loc[df['offence'] == ASSAULT_EMERGENCY_WORKER, 'parent'] = "Violence against the person"
    return df


def set_plot_order(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assigns a plotting order to offences in the DataFrame based on predefined categories.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing an 'offence' column.

    Returns:
        pd.DataFrame: DataFrame with an added 'plot_order' column, where each offence is mapped to an integer
                      representing its plotting order. Offences not in the predefined list are assigned 0.
    """
    logging.info("Setting plot order for offences...")
    plot_dict = {
        'All other offences': 0,
        'Theft offences': 1,
        'Violence against the person': 2,
        ASSAULT_EMERGENCY_WORKER: 2,
        'Drug offences': 3,
    }
    df['plot_order'] = df["offence"].map(plot_dict).fillna(0)
    return df


def process_data(df: pd.DataFrame):
    """
    This function processes a DataFrame containing custody offences data by
    applying a series of transformations and filters. It includes steps to
    filter data by the most recent year, group data by Police Force Area (PFA)
    and offence, extract specific offences (e.g., assault of an emergency worker),
    and prepare the data for visualisation.

    Args:
        df (pd.DataFrame): Input DataFrame containing custody offences data.
            Must include at least the following columns:
            - 'year': The year of the offence.
            - 'specific_offence': The specific offence type.

    Returns:
        pd.DataFrame: Processed DataFrame with the following transformations:
            - Filtered to include only data from the most recent year.
            - Grouped by PFA and offence type.
            - Highlights assault of an emergency worker offences.
            - Orders for plotting purposes.
            - Includes a parent column for go.Sunburst plot control.
    """
    logging.info("Starting data processing...")

    max_year = df["year"].max()

    df = (
        df
        .pipe(filter_years.get_year, year_from=max_year)
        .pipe(group_by_pfa_and_offence)
    )

    emergency_workers_df = extract_assault_of_emergency_worker(df)

    df = (
        df
        .pipe(group_by_pfa_and_offence, specific_offence=False)
        .pipe(add_assault_of_emergency_worker, emergency_workers_df)
        .pipe(set_plot_order)
        .drop(columns=['specific_offence'])
    )

    filter_mask = filter_offences(df)
    df = df.pipe(set_parent_column, filter_mask=filter_mask)

    logging.info("Data processing complete.")
    return df


def load_and_process_data() -> tuple[pd.DataFrame, int]:
    """
    Load the interim dataset and process it to filter custodial sentences,
    select the latest year, group by PFA and offence, calculate proportions,
    and return a melted DataFrame ready for plotting.

    Returns
    -------
    tuple[pd.DataFrame, int]
        The processed and melted DataFrame ready for plotting, and the latest year used in filtering.
    """
    df = (
        load_data()
        .pipe(process_data)
    )
    max_year = df["year"].max()

    logging.info("Data successfully processed for PFA offences charts")
    return df, max_year


def get_output_filename(year: str | int, template: str) -> str:
    """This function adds the year parameter to the template filename"""
    return template.format(year=year)


def main():
    """Main function to load, process, and save the filtered custody offences data."""
    df, max_year = load_and_process_data()
    filename = get_output_filename(year=max_year, template=OUTPUT_FILENAME_TEMPLATE)

    utils.safe_save_data(
        df,
        path=config['data']['clnFilePath'],
        filename=filename
    )


if __name__ == "__main__":
    main()
