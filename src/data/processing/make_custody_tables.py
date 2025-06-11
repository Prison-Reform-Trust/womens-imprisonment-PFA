#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script outputs final versions of three datasets showing the number of women sentenced
to immediate custody in England and Wales by Police Force Area, timeseries and percentage change,
for:
    * All custodial sentences
    * Custodial sentences of less than six months
    * Custodial sentences of less than 12 months
"""

import logging

import pandas as pd

import src.utilities as utils
from src.data.processing import filter_years

utils.setup_logging()

config = utils.read_config()

INPUT_FILENAME = config['data']['datasetFilenames']['filter_sentence_length']
VALID_CATEGORIES = {
    "all": None,
    "6 months": ["Less than 6 months"],
    "12 months": ["Less than 6 months", "6 months to less than 12 months"]
}
OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['make_custody_tables_template']


def get_sentence_length(df: pd.DataFrame, category: str) -> pd.DataFrame:
    """
    Filter the DataFrame to include only records with a specified sentence length.
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category '{category}'. Must be one of {list(VALID_CATEGORIES.keys())}."
            )

    if 'sentence_len' not in df.columns:
        raise ValueError("The DataFrame must contain a 'sentence_len' column.")

    if category == "all":
        logging.info("Filtering for the total number of custodial sentences")
        return df.groupby(['pfa', 'year'], as_index=False, observed=True)['freq'].sum()

    logging.info("Filtering for custodial sentences of less than %s", category)
    filt = df['sentence_len'].isin(VALID_CATEGORIES[category])
    return df[filt].groupby(['pfa', 'year'], as_index=False, observed=True)['freq'].sum()


def perform_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """This function takes the dataframe from the `get_sentence_length function and
    cross tabulates it for readability."""

    return pd.crosstab(index=df['pfa'], columns=df['year'],
                       values=df['freq'], aggfunc='sum')


def get_output_filename(category: str, template: str) -> str:
    category_slug_map = {
        "all": "all",
        "6 months": "six_months",
        "12 months": "12_months"
    }

    if category not in category_slug_map:
        valid_categories = ', '.join(repr(key) for key in category_slug_map.keys())
        raise ValueError(f"Invalid category: {category!r}. Must be one of: {valid_categories}")

    return template.format(category=category_slug_map[category])


def make_sentence_length_tables(df: pd.DataFrame):
    """This function takes the interim dataframe and performs filtering and
    processing steps to produce the final tables for ["all custodial sentences",
    "custodial sentences of less than 6 months", "custodial sentences of less than 12 months"]
    and save them as individual csv files in the `clnFilePath`.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the interim dataset.
    """
    for sentence in VALID_CATEGORIES:
        df_sentence = (
            df
            .pipe(get_sentence_length, sentence)
            .pipe(filter_years.get_year)
            .pipe(perform_crosstab)
            .pipe(utils.safe_save_data,
                  path=config['data']['clnFilePath'],
                  filename="PLACEHOLDER"
                  )
            )
        return df_sentence


def load_and_process_data():
    """
    Load the dataset and process it to output the final dataframes
    """
    df = (
        utils.load_data(status='processed', filename=INPUT_FILENAME)
    )

    return df
