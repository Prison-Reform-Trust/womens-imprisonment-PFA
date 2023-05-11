#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Using the cleansed dataset from data_cleansing.py this script builds a series of refined datasets ready for analysis
'''

import utilities as utils
import pandas as pd

#Importing cleansed dataset
df = pd.read_csv('data/interim/PFA_2009-21_women_cust_comm_sus.csv')

## 1.SENTENCING OUTCOME FOR EACH PFA BY YEAR

#Grouping dataset
pfa_sentencing_outcomes = df.groupby(['pfa', 'year', 'outcome'], as_index=False)['freq'].sum()

#Outputting to CSV
pfa_sentencing_outcomes.to_csv('data/processed/PFA_2009-21_women_sentencing_outcomes_FINAL.csv', index=False)


## 2.CUSTODIAL SENTENCE LENGTHS FOR EACH PFA BY YEAR
'''THIS PRODUCES THE DATA FOR FIGURE 1 IN THE PFA FACTSHEET'''

#Filtering cleansed dataset
filt = df['outcome'] == 'Immediate custody'
pfa_custody_sentence_lengths = df[filt].copy()

#Defining sentence_len categories
less_6months = ["Up to 1 month", 
                "More than 1 month and up to 2 months",
                "More than 2 months and up to 3 months",
                "More than 3 months and under 6 months"]

six_12_months = ["6 months",
                 "More than 6 months and up to 9 months",
                 "More than 9 months and under 12 months"]

#Mapping sentence_len categories
def sentence_length_groups(sentence_len):
    if sentence_len in less_6months:
        return 'Less than 6 months'
    elif sentence_len in six_12_months:
        return '6 months and under 12 months'
    else:
        return 'Over 12 months'
    
pfa_custody_sentence_lengths['sentence_len'] = pfa_custody_sentence_lengths['sentence_len'].map(sentence_length_groups)

#Grouping dataset
final_df = pfa_custody_sentence_lengths.groupby(['pfa', 'year', 'sentence_len'], as_index=False)['freq'].sum()

#Outputting to CSV
final_df.to_csv('data/interim/PFA_2009-21_women_cust_sentence.csv', index=False)