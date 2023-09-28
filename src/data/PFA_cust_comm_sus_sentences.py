#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 14:46:17 2022

@author: alex
"""

import pandas as pd

#Importing cleaned dataset
df = pd.read_csv('../../data/interim/PFA_2009-21_women_cust_comm_sus.csv')

#Grouping dataset
df2 = df.groupby(['pfa', 'year', 'outcome'], as_index=False)['freq'].sum()

#Outputting to CSV
df2.to_csv('../../data/processed/PFA_2009-21_women_cust_comm_sus_FINAL.csv', index=False)