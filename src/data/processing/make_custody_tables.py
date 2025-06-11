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
    "all": {
        "filter": None,
        "slug": "all"
    },
    "6 months": {
        "filter": ["Less than 6 months"],
        "slug": "6_months"
    },
    "12 months": {
        "filter": ["Less than 6 months", "6 months to less than 12 months"],
        "slug": "12_months"
    }
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
    filt = df['sentence_len'].isin(VALID_CATEGORIES[category]['filter'])
    return df[filt].groupby(['pfa', 'year'], as_index=False, observed=True)['freq'].sum()


def perform_crosstab(df: pd.DataFrame) -> pd.DataFrame:
    """This function takes the DataFrame from the `get_sentence_length` function and
    cross tabulates it for readability."""

    df_crosstab = pd.crosstab(index=df['pfa'], columns=df['year'],
                              values=df['freq'], aggfunc='sum')

    return df_crosstab


def calculate_percentage_change(df: pd.DataFrame) -> pd.DataFrame:
    """This function calculates the percentage change between the first and last year
    in the dataframe and adds a new column.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame for processing

    Returns
    -------
    pd.DataFrame
        DataFrame with additional column showing percentage change since first year.
    """
    periods = len(df.columns) - 1
    col_name = f"per_change_{df.columns[0]}"
    
    percentage_change = df.pct_change(axis='columns', periods=periods).dropna(axis='columns')
    df[col_name] = percentage_change
    
    return df


def get_output_filename(category: str, template: str) -> str:
    """
    Generate the output filename based on the selected category.

    Parameters
    ----------
    category : str
        One of the valid sentence length categories.
    template : str
        A filename template, e.g., 'PFA_custodial_sentences_{category}_FINAL.csv'

    Returns
    -------
    str
        The formatted output filename.

    Raises
    ------
    ValueError
        If the category is invalid.
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(
            f"Invalid category: {category!r}. Must be one of: {list(VALID_CATEGORIES)}"
        )

    slug = VALID_CATEGORIES[category]["slug"]
    return template.format(category=slug)


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
    for category in VALID_CATEGORIES:
        df_sentence = (
            df
            .copy()
            .pipe(get_sentence_length, category)
            .pipe(filter_years.get_year)
            .pipe(perform_crosstab)
            .pipe(calculate_percentage_change)
            )

        filename = get_output_filename(category, OUTPUT_FILENAME_TEMPLATE)

        utils.safe_save_data(
            df=df_sentence,
            path=config['data']['clnFilePath'],
            filename=filename,
            index=True
        )

    return None


def main():
    """
    Load the dataset and process it to output the final dataframes
    """
    (
        utils.load_data(status='processed', filename=INPUT_FILENAME)
        .pipe(make_sentence_length_tables)
    )

    return None


if __name__ == "__main__":
    main()
