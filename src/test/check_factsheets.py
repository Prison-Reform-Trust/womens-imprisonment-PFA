#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script is part of the testing process checking the final factsheets. It performs
a review of a random sample of Police Force Areas (PFAs) to ensure accuracy in the factsheet
creation process.
'''

import logging
import math
import random
from typing import Optional

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

OUTPUT_FILENAME_TEMPLATE = config['data']['factsheetTests']['custodial_sentences']


def load_data(
        data_type: str,
        sentence_length: Optional[str] = None,
        year: Optional[str] = None
        ) -> pd.DataFrame:
    """Load the custody data by sentence length or offence.
    Parameters
    ----------
    data_type : str
        The type of data to load: 'sentence_length', 'offence' or 'sentence_type'.
    sentence_length : str, optional
        The sentence length category to load (e.g., 'all', '6_months'). Required if data_type is 'sentence_length'.
    year : str, optional
        The year of offence data to load (e.g., '2024'). Only used if data_type is 'offence'.
        Defaults to the latest year available if no argument is provided.
    Returns
    -------
    pd.DataFrame
        The loaded DataFrame."""

    if data_type == 'sentence_length':
        if sentence_length is None:
            raise ValueError("sentence_length must be provided when data_type is 'sentence_length'")
        if sentence_length not in ['all', '6_months', '12_months']:
            raise ValueError("sentence_length must be either 'all', '6_months' or '12_months'")
        logging.info("Loading sentence length data...")
        data_template = config['data']['datasetFilenames']['make_custody_tables_template']
        data_filename = data_template.format(category=sentence_length)

    elif data_type == 'offence':
        logging.info("Loading offences data...")
        year = '*' if year is None else year
        # NOTE: Use this in other implementations where fetch_latest_file is currently used
        data_template = config['data']['datasetFilenames']['filter_custody_offences']
        data_pattern = data_template.format(year=year)
        data_filename = utils.fetch_latest_file(
            pattern=data_pattern,
            path=config['data']['clnFilePath']
        )
    elif data_type == 'sentence_type':
        logging.info("Loading sentence type data...")
        data_filename = config['data']['datasetFilenames']['group_pfa_sentence_outcome']
    else:
        raise ValueError("data_type must be either 'sentence_length', 'offence' or 'sentence_type'")

    data = utils.load_data('processed', data_filename)
    return data


def save_data(df: pd.DataFrame, category: str) -> None:
    """Save the DataFrame to a CSV file in the tests directory.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to save.
    category : str
        The category for the filename e.g. 'all' or '6_months'.

    Returns
    -------
    None
    """
    filename = OUTPUT_FILENAME_TEMPLATE.format(category=category)

    utils.safe_save_data(
        df=df,
        path=config['data']['testsFilePath'],
        filename=filename,
    )
    return None


def calculate_sample_size(N, z=1.96, p=0.5, e=0.2) -> int:
    """
    Calculate the recommended sample size for a given population size (N)
    using the formula for sample size calculation.

    Parameters:
    N (int): Population size
    z (float): Z-score for the desired confidence level (default is 1.96 for 95% confidence)
    p (float): Estimated proportion of the population (default is 0.5 for maximum variability)
    e (float): Margin of error (default is 0.2 for 20% margin of error)

    Returns:
    int: Recommended sample size
    """
    n = (N * z**2 * p * (1-p)) / ((N-1)*e**2 + z**2*p*(1-p))
    return math.ceil(n)


'''
Working through the factsheet data tables to check a random sample of PFAs.
Currently using all custodial sentences data. Produce tables showing:
- Number of sentences of six months and under for latest year and % of total.
- Proportion of custodial sentences for theft offences for latest year.
- Number of community sentences for 2014, latest year and % change.

* Check Sheet5 which shows cautions — don't think these are taken from my analysis.
'''


def create_pfa_sample(data: pd.DataFrame) -> list[str]:
    """Select a random sample of Police Force Areas (PFAs) from the dataset.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the custody data with a 'pfa' column.

    Returns
    -------
    list[str]
        A list of randomly selected PFAs.
    """
    N = len(data['pfa'].unique())
    sample_size = calculate_sample_size(N)
    sample_pfas = random.sample(list(data['pfa'].unique()), sample_size)
    return sample_pfas


def create_total_custodial_sentences_table(data: pd.DataFrame, sample_pfas: list[str]) -> pd.DataFrame:
    """Create a table showing the total number of custodial sentences in each PFA.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing the custody data
    sample_pfas : list[str]
        List of PFAs to include in the table

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the total number of custodial sentences by PFA for the selected sample PFAs.
    """
    filt = data['pfa'].isin(sample_pfas)
    cols = list(data.columns[:2]) + list(data.columns[-3:])
    df = data.loc[filt, cols]
    save_data(df, category='all')

    return df


def create_under_six_months_table(sample_pfas: list[str], all_custody_data: pd.DataFrame) -> pd.DataFrame:
    """Create a table showing the number of custodial sentences of under six months in the latest year.
    and the proportion of all custodial sentences that this represents for the sampled PFAs.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the number of custodial sentences of under six months
        by PFA for a recommended sample size of PFAs.
    """
    data = load_data(data_type='sentence_length', sentence_length='6_months')
    filt = data['pfa'].isin(sample_pfas)
    cols = data.columns[[0, -2]]
    df = data.loc[filt, cols]

    all_custody_data = all_custody_data[['pfa', all_custody_data.columns[-2]]]  # pfa and latest year
    df = df.merge(all_custody_data, on='pfa', how='left', suffixes=('_under_6_months', '_all_sentences'))
    df['proportion_under_6_months'] = df.iloc[:, 1] / df.iloc[:, 2]
    save_data(df, category='6_months')
    return df


def create_theft_offences_table(sample_pfas: list[str], all_custody_data: pd.DataFrame) -> pd.DataFrame:
    """Create a table showing the proportion of custodial sentences for theft offences in the latest year.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the proportion of custodial sentences for theft offences by PFA.
    """
    data = load_data(data_type='offence')
    filt = data['pfa'].isin(sample_pfas) & (data['offence'] == 'Theft offences')
    cols = ['pfa', 'offence', 'freq']
    df = data.loc[filt, cols]

    all_custody_data = all_custody_data[['pfa', all_custody_data.columns[-2]]]  # pfa and latest year
    df = df.merge(all_custody_data, on='pfa', how='left')

    # Use explicit column names for division
    theft_freq_col = 'freq'
    total_sentences_col = all_custody_data.columns[-1]
    df['proportion_theft_offences'] = df[theft_freq_col] / df[total_sentences_col]
    drop_cols = [theft_freq_col, total_sentences_col]  # dropping columns used in calculation
    df.drop(columns=drop_cols, inplace=True)

    save_data(df, category='theft_offences')
    return df


def build_sample_pfa_list() -> list[str]:
    """FOR TESTING PURPOSES: Build a list of sample PFAs from the full custody data."""
    all_custody_data = load_data(data_type='sentence_length', sentence_length='all')
    sample_pfas = create_pfa_sample(all_custody_data)
    return sample_pfas


def main():
    """Main function to produce the factsheet data review process.

    Returns
    -------
    None
    """

    all_custody_data = load_data(data_type='sentence_length', sentence_length='all')
    sample_pfas = create_pfa_sample(all_custody_data)

    df_all = create_total_custodial_sentences_table(all_custody_data, sample_pfas)
    create_under_six_months_table(sample_pfas, df_all)
    create_theft_offences_table(sample_pfas, all_custody_data)
    return None


if __name__ == "__main__":
    main()
