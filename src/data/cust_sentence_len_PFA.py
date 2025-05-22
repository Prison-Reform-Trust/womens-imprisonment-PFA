#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 13:52:45 2022

@author: alex
"""

import pandas as pd

#Importing cleaned dataset
df = pd.read_csv('../../data/interim/PFA_2009-21_women_cust_comm_sus.csv')

#Filtering data for custodial sentences
filt = df['outcome'] == 'Immediate custody'
df2 = df[filt]

#Setting categories
less_6months = ["Up to 1 month", 
                "More than 1 month and up to 2 months",
                "More than 2 months and up to 3 months",
                "More than 3 months and under 6 months"]

six_12_months = ["6 months",
                "More than 6 months and up to 9 months",
                "More than 9 months and under 12 months",
                "12 months"]

#Applying categories
filt = df2['sentence_len'].isin(less_6months)
df2.loc[filt, 'sentence_len'] = "Less than 6 months"

filt= df2['sentence_len'].isin(six_12_months)
df2.loc[filt, 'sentence_len'] = "6–12 months"

filt1 = df2['sentence_len'] != "Less than 6 months"
filt2 = df2['sentence_len'] != "6–12 months"
filt = filt1 & filt2
df2.loc[filt, 'sentence_len'] = "Over 12 months"

#Grouping by PFA for future analysis
df3 = df2.groupby(['pfa', 'year', 'sentence_len'], as_index=False)['freq'].sum()

#Outputting to CSV
df3.to_csv('../../data/interim/PFA_2009-21_women_cust_sentence_len.csv', index=False)