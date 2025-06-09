#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the Criminal Justice System statistics quarterly: December 2024
Outcomes by Offence datasets.

Using the interim dataset produced by the `filter_sentence_type` module, it groups the
data by Police Force Area (PFA), year, and sentence outcome, summing the frequency of
sentences. This processed DataFrame is then saved to a CSV file in the `clnFilePath` directory.

This script is part of the data processing pipeline, and results in a cleaned dataset showing:
    * The number of women in each Police Force Area who received a:
        - Community sentence
        - Suspended sentence
        - Sentence of immediate custody
    [Used to produce Figure 1 and further processing].
"""

import logging

import pandas as pd

import src.utilities as utils

utils.setup_logging()

config = utils.read_config()

INPUT_FILENAME = config['data']['datasetFilenames']['filter_sentence_type']
OUTPUT_FILENAME = config['data']['datasetFilenames']['group_pfa_sentence_outcome']


def group_by_pfa_sentence_outcome(df: pd.DataFrame) -> pd.DataFrame:
    """
    Group the DataFrame by Police Force Area (PFA), year, and sentence outcome,
    summing the frequency of sentences.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the interim dataset.

    Returns
    -------
    pd.DataFrame
        A DataFrame grouped by PFA, year, and sentence outcome with summed frequencies.
    """
    logging.info("Grouping data by PFA, year, and sentence outcome...")
    grouped_df = df.groupby(['pfa', 'year', 'outcome'], as_index=False, observed=True)['freq'].sum()
    return grouped_df


def main():
    """
    Main function to process the PFA sentence outcome data.
    """
    (
        utils.load_data(status='interim', filename=INPUT_FILENAME)
        .pipe(group_by_pfa_sentence_outcome)
        .pipe(
            utils.safe_save_data,
            path=config['data']['clnFilePath'],
            filename=OUTPUT_FILENAME
            )
    )


if __name__ == "__main__":
    main()
