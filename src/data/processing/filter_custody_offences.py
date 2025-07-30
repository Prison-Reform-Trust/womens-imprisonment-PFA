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


def group_by_pfa_and_offence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group the DataFrame by Police Force Area (PFA), year, and offence,
    summing the frequency of sentences.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame for processing.
    Returns
    -------
    pd.DataFrame
        A DataFrame grouped by PFA, year, and offence with summed frequencies.
    """
    logging.info("Grouping data by PFA, year, and offence...")
    df_grouped = df.groupby(['pfa', 'year', 'offence'], observed=True)['freq'].sum().reset_index()
    return df_grouped


def calculate_offence_proportions(df: pd.DataFrame) -> pd.DataFrame:
    """The function uses crosstab with the normalize argument to
    calculate offence group proportions by PFA

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame for processing.

    Returns
    -------
    pd.DataFrame
        The processed DataFrame.
    """
    return pd.crosstab(
        index=df['pfa'],
        columns=df['offence'],
        values=df['freq'],
        aggfunc="sum",
        normalize='index').round(3)


def melt_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melt the DataFrame from wide to long format.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to melt.

    Returns
    -------
    pd.DataFrame
        The melted DataFrame.
    """
    logging.info("Melting DataFrame to long format...")
    return pd.melt(
        df,
        id_vars=['pfa'],
        value_vars=list(df.columns[1:]),
        var_name='offence',
        value_name='proportion')


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
    # TODO: #24 Replace hardcoded new line breaks with a more robust solution
    highlighted_offence_groups = ['Theft offences', 'Drug offences', 'Violence against the person']
    return df['offence'].isin(highlighted_offence_groups)


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
    df.loc[filter_mask, 'parent'] = "All offences"
    df.loc[~filter_mask, 'parent'] = "All other offences"
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
        'Drug offences': 2,
        'Violence against the person': 3
    }
    df['plot_order'] = df["offence"].map(plot_dict).fillna(0)
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
        utils.load_data(status='interim', filename=INPUT_FILENAME)
        .pipe(filter_sentence_length.filter_custodial_sentences)
    )
    max_year = df["year"].max()

    df = (
        df
        .pipe(filter_years.get_year, year_from=max_year)
        .pipe(group_by_pfa_and_offence)
        .pipe(calculate_offence_proportions)
        .reset_index()
        .pipe(melt_dataframe)
    )

    filter_mask = filter_offences(df)
    df = (
        set_parent_column(df, filter_mask)
        .pipe(set_plot_order)
        )
    logging.info("Data successfully processed for PFA offences charts")
    return df, max_year


def get_output_filename(year: str, template: str) -> str:
    """This function adds the year parameter to the template filename"""
    return template.format(year=year)


def main():
    df, max_year = load_and_process_data()
    filename = get_output_filename(year=max_year, template=OUTPUT_FILENAME_TEMPLATE)

    utils.safe_save_data(
        df,
        path=config['data']['clnFilePath'],
        filename=filename
    )


if __name__ == "__main__":
    main()
