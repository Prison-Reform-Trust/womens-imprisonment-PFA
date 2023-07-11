#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Using the cleansed dataset from data_cleansing.py this script builds a series of refined datasets ready for further analysis as well as final output
'''

import utilities as utils
import pandas as pd

#Importing cleansed dataset
df = pd.read_csv('data/interim/PFA_2010-22_women_cust_comm_sus.csv')


## 1.SENTENCING OUTCOME FOR EACH PFA BY YEAR

#Grouping dataset and saving out
(
    df
    .groupby(['pfa', 'year', 'outcome'], as_index=False)['freq'].sum()
    .to_csv('data/processed/PFA_2010-22_women_sentencing_outcomes_FINAL.csv', index=False)
)


## 2. CUSTODIAL SENTENCES FOR EACH PFA BY OFFENCE TYPE

#Filtering cleansed dataset and grouping by PFA and offence group 
sentence_type = 'Immediate custody'
year = 2022

pfa_custody = (
    df
    .query("outcome == @sentence_type & year == @year")
    .groupby(['pfa', 'offence'], as_index=False)['freq'].sum()
)

#Using crosstab with normalize argument to calculate offence group proportions by PFA
pfa_custody_offences = pd.crosstab(index=pfa_custody['pfa'], columns=pfa_custody['offence'], values=pfa_custody['freq'], aggfunc=sum, normalize='index').round(3)

#Outputting to CSV
pfa_custody_offences.to_csv('data/processed/PFA_2022_offences.csv')


## 3.CUSTODIAL SENTENCE LENGTHS FOR EACH PFA BY YEAR
'''THIS PRODUCES THE DATA FOR FIGURE 1 IN THE PFA FACTSHEET'''

#Defining sentence_length categories—THESE HAVE BEEN UPDATED
less_6months = ["Up to and including 1 month", 
                "More than 1 month and up to and including 2 months",
                "More than 2 months and up to and including 3 months",
                "More than 3 months and up to 6 months"]

six_12_months = ["6 months",
                "More than 6 months and up to and including 9 months",
                "More than 9 months and up to 12 months"]

#Mapping sentence_len categories
def sentence_length_groups(sentence_len):
    if sentence_len in less_6months:
        return 'Less than 6 months'
    elif sentence_len in six_12_months:
        return '6 months and under 12 months'
    else:
        return 'Over 12 months'

#Filtering for custodial sentences and applying the map

pfa_custody_sentence_lengths = df.query('outcome == @sentence_type').copy()
pfa_custody_sentence_lengths['sentence_length'] = pfa_custody_sentence_lengths['sentence_length'].map(sentence_length_groups)

#Grouping dataset
pfa_custody_sentence_lengths = pfa_custody_sentence_lengths.groupby(['pfa', 'year', 'sentence_length'], as_index=False)['freq'].sum()

#Outputting to CSV
pfa_custody_sentence_lengths.to_csv('data/interim/PFA_2010-22_women_cust_sentence_length.csv', index=False)


## 4. CUSTODIAL SENTENCES FOR EACH PFA BY YEAR

'''THIS PRODUCES THREE DATASETS: 
    * TOTAL NUMBER OF WOMEN SENTENCED TO CUSTODY BY PFA; AND OF THOSE 
        * SENTENCED TO LESS THAN SIX MONTHS; AND
        * SENTENCED TO LESS THAN 12 MONTHS'''

#FILTERING DATA

#By year
filt = pfa_custody_sentence_lengths['year'] >= 2014
pfa_df_2014 = pfa_custody_sentence_lengths[filt].copy()

#By sentences of less than six months
filt = pfa_df_2014['sentence_length'] == "Less than 6 months"
lt_6m = pfa_df_2014[filt].copy()

#By sentences of less than 12 months
filt = pfa_df_2014['sentence_length'] != "Over 12 months"
lt_12m = pfa_df_2014[filt].copy()

#Defining new function for aggregating data and adding a percentage change column
def aggregate_sentences(df):
    new_df = pd.crosstab(index=df['pfa'], columns=df['year'],
                        values=df['freq'], aggfunc='sum')
    
    new_df = new_df.fillna(0.0).astype(int)
    new_df['per_change_2014'] = new_df.pct_change(axis='columns', periods=8).dropna(axis='columns')
    return new_df

#Using dictionary comprehension to run both DataFrames through the function
'''This returns a new dictionary df_dict with _table added to the keys. Values can be accessed using df_dict['key'] and DataFrame functionality is retained
See https://stackoverflow.com/questions/51845732/apply-a-function-to-multiple-dataframes-return-multiple-dfs-as-output'''

sentence_length_dict = {'cust_sentences_total':pfa_df_2014, 'cust_sentences_lt_6m':lt_6m, 'cust_sentences_lt_12m': lt_12m}
df_dict = {i+'_table': aggregate_sentences(sentence_length) for i, sentence_length in sentence_length_dict.items()}

#Outputting to CSV
#These are the final versions ready for formatting and publication
for i, df in df_dict.items():
    df.to_csv(f'data/processed/{i}.csv')