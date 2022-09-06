#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 25 15:34:13 2022

@author: alex
"""

import pandas as pd

#Importing cleaned dataset
df = pd.read_csv('../../data/interim/PFA_2009-21_women_cust_comm_sus.csv')

#Filtering data for custodial sentences from 2014
filt = df['outcome'] == 'Immediate custody'
filt2 = df['year'] >= 2014
df2 = df[filt & filt2]

#Aggregating by PFA for each year
pfa_years = pd.crosstab(index=df2['pfa'], columns=df2['year'],
                     values=df2['freq'], aggfunc='sum')

#Converting floats to int and filling na values
pfa_years = pfa_years.fillna(0.0).astype(int)

#Calculating percentage change between 2014 and 2021 data
per_change = pfa_years.pct_change(axis='columns', periods=7).dropna(axis='columns').copy()

#Adding this calculated data to a joined dataframe
df3 = pfa_years.join(per_change.iloc[:,-1], rsuffix='_per_change')
df3.rename(columns={'2021_per_change':'per_change_2014'}, inplace = True)

#Outputting final data to new csv
df3.to_csv('../../data/processed/female_custodial_sentences_PFA.csv')