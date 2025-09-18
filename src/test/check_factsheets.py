#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
This script is part of the testing process checking the final factsheets. It performs
a review of a random sample of Police Force Areas (PFAs) to ensure accuracy in the factsheet
creation process.
'''

import math
import random

import pandas as pd

import src.utilities as utils
from src.data.processing.combine_custody_pfa_population import load_data

utils.setup_logging()

config = utils.read_config()


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
    return data.loc[filt, cols]


def load_less_than_six_months_data() -> pd.DataFrame:
    """Load the six months and under custodial sentences data.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the six months and under custodial sentences data.
    """
    custody_data_template = config['data']['datasetFilenames']['make_custody_tables_template']
    custody_data_filename = custody_data_template.format(category='6_months')

    under_six_months_custody = utils.load_data('processed', custody_data_filename)
    return under_six_months_custody


def create_under_six_months_table(sample_pfas: list[str]) -> pd.DataFrame:
    """Create a table showing the number of custodial sentences of under six months
    and the proportion of all custodial sentences that this represents for the sampled PFAs.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the number of custodial sentences of under six months
        by PFA for a recommended sample size of PFAs.
    """
    under_six_months_data = load_less_than_six_months_data()
    


def main():
    all_custody_data, _ = load_data()
    sample_pfas = create_pfa_sample(all_custody_data)
    create_total_custodial_sentences_table(all_custody_data, sample_pfas)
    under_six_months_data = load_less_than_six_months_data()
    create_under_six_months_table(under_six_months_data, sample_pfas)


if __name__ == "__main__":
    main()
