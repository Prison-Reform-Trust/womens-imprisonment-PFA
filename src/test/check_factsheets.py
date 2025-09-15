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


def calculate_sample_size(N, z=1.96, p=0.5, e=0.2):
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


def select_random_pfas(data, sample_size):
    """
    Select a random sample of Police Force Areas (PFAs) from the dataset.

    Parameters:
    data (pd.DataFrame): DataFrame containing the custody data with a 'pfa' column
    sample_size (int): Number of PFAs to sample

    Returns:
    list: List of randomly selected PFAs
    """
    pfa_sample = random.sample(list(data['pfa'].unique()), sample_size)
    return pfa_sample


def filter_pfas(data, pfa_sample):
    """
    Filter the DataFrame to include only the selected PFAs.

    Parameters:
    data (pd.DataFrame): DataFrame containing the custody data
    pfa_sample (list): List of PFAs to include

    Returns:
    pd.DataFrame: Filtered DataFrame with only the selected PFAs
    """
    filt = data['pfa'].isin(pfa_sample)
    cols = list(data.columns[:2]) + list(data.columns[-3:])
    return data.loc[filt, cols]

'''
Working through the factsheet data tables to check a random sample of PFAs.
Currently using all custodial sentences data. Produce tables showing:
- Number of sentences of six months and under for latest year and % of total.
- Proportion of custodial sentences for theft offences for latest year.
- Number of community sentences for 2014, latest year and % change.

* Check Sheet5 which shows cautions — don't think these are taken from my analysis.
'''




def main():
    custody_data, _ = load_data()
    N = len(custody_data['pfa'].unique())
    sample_size = calculate_sample_size(N)
    random_pfas = select_random_pfas(custody_data, sample_size)
    print(f"Recommended sample size: {sample_size}")
    print("Randomly selected PFAs for review:")
    print(random_pfas)


if __name__ == "__main__":
    main()
