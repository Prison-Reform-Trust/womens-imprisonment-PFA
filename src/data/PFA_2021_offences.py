#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 16:36:27 2022

@author: alex
"""

import pandas as pd

#Importing dataset
df = pd.read_csv('../../data/interim/PFA_2009-21_women_cust_comm_sus.csv')

#Filtering data for custodial sentences and 2021
filt = df['outcome'] == 'Immediate custody'
filt2 = df['year'] == 2021
df2 = df[filt & filt2]

#Grouping by PFA and offence group 
df3 = df2.groupby(['pfa', 'offence'], as_index=False)['freq'].sum()

#Using crosstab with normalize argument to calculate offence group proportions by PFA
df4 = pd.crosstab(index=df3['pfa'], columns=df3['offence'], values=df3['freq'], aggfunc=sum, normalize='index').round(3)

#Outputting to CSV
df4.to_csv('../../data/processed/PFA_2021_offences.csv')