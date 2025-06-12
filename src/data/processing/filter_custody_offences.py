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
    df_grouped = df.groupby(['pfa', 'year', 'offence'], as_index=False, observed=True)['freq'].sum()
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


def load_and_process_data() -> tuple[pd.DataFrame, int]:
    """
    Load the interim dataset and process it to filter custodial sentences,
    latest year and group by PFA.

    Returns
    -------
    tuple[pd.DataFrame, int]
        The processed DataFrame and the latest year used in filtering.
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
    )

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
        filename=filename,
        index=True
    )


if __name__ == "__main__":
    main()
