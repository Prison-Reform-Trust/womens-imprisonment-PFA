#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the Criminal Justice System statistics quarterly: December 2024
Outcomes by Offence datasets.

This script is part of the data processing pipeline, and results the following dataset:
    * The number of women in each Police Force Area who received an immediate custodial sentence of:
        - Less than six months
        - Six to less than 12 months
        - 12 months or more
    [Used to produce Figure 2 and further processing].
"""

import logging

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

INPUT_FILENAME = config['data']['datasetFilenames']['filter_sentence_type']
OUTPUT_FILENAME = config['data']['datasetFilenames']['filter_sentence_length']


def filter_custodial_sentences(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to include only records with an immediate custodial sentence.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the interim dataset.
    Returns
    -------
    pd.DataFrame
        A DataFrame containing only records with an immediate custodial sentence.
    """
    logging.info("Filtering data for custodial sentences...")
    # Ensure the 'outcome' column exists in the DataFrame
    if 'outcome' not in df.columns:
        raise ValueError("The DataFrame must contain an 'outcome' column.")
    filt = df['outcome'] == 'Immediate Custody'
    return df[filt]


def group_sentence_lengths(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group the DataFrame by simplified sentence length categories.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the filtered custodial sentences.

    Returns
    -------
    pd.DataFrame
        A DataFrame with grouped sentence lengths.
    """
    logging.info("Grouping sentence lengths...")

    # Define the raw categories to group
    less_6months = [
        "Up to and including 1 month",
        "More than 1 month and up to and including 2 months",
        "More than 2 months and up to and including 3 months",
        "More than 3 months and up to 6 months"
    ]

    six_12_months = [
        "6 months",
        "More than 6 months and up to and including 9 months",
        "More than 9 months and up to 12 months",
    ]

    # Convert to string for flexible assignment
    df['sentence_len'] = df['sentence_len'].astype(str)

    # Apply grouping logic
    df.loc[df['sentence_len'].isin(less_6months), 'sentence_len'] = "Less than 6 months"
    df.loc[df['sentence_len'].isin(six_12_months), 'sentence_len'] = "6 months to less than 12 months"
    df.loc[~df['sentence_len'].isin(["Less than 6 months", "6 months to less than 12 months"]), 'sentence_len'] = "12 months or more"

    # Convert back to ordered categorical
    sentence_order = ["Less than 6 months", "6 months to less than 12 months", "12 months or more"]
    df['sentence_len'] = pd.Categorical(df['sentence_len'], categories=sentence_order, ordered=True)

    logging.info("Sentence lengths grouped and recategorised.")

    return df


def group_by_pfa_and_sentence_length(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group the DataFrame by Police Force Area (PFA), year, and sentence length,
    summing the frequency of sentences.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the grouped sentence lengths.
    Returns
    -------
    pd.DataFrame
        A DataFrame grouped by PFA, year, and sentence length with summed frequencies.
    """
    logging.info("Grouping data by PFA, year, and sentence length...")
    # Group by PFA, year, and sentence length
    df_grouped = df.groupby(['pfa', 'year', 'sentence_len'], as_index=False, observed=True)['freq'].sum()
    return df_grouped


def get_sentence_length(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Filter the DataFrame to include only records with a specified sentence length.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the interim dataset.
    
    category : str 
        Sentence length category. Must be one of ["all", "6 months", "12 months"]
    Returns
    -------
    pd.DataFrame
        A DataFrame containing only records with the sentence length specified
        by category.
    """

    pass


def load_and_process_data() -> pd.DataFrame:
    """
    Load the interim dataset and process it to filter custodial sentences
    and group by sentence length.

    Returns
    -------
    pd.DataFrame
        The processed DataFrame with grouped sentence lengths.
    """
    df = (
        utils.load_data(status='interim', filename=INPUT_FILENAME)
        .pipe(filter_custodial_sentences)
        .pipe(group_sentence_lengths)
        .pipe(group_by_pfa_and_sentence_length)
    )
    return df


def main():
    """
    Main function to process the PFA sentence outcome data.
    """
    (
        load_and_process_data()
        .pipe(utils.safe_save_data,
              path=config['data']['clnFilePath'],
              filename=OUTPUT_FILENAME
              )
    )


if __name__ == "__main__":
    main()
