#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 18:43:30 2022

@author: alex
"""

import pandas as pd

#Importing LA and PFA datasets
df = pd.read_csv('../../data/interim/LA_population_female_2001_2020-cleansed.csv')
ons_pfa = pd.read_csv('../../data/external/LAD21_CSP21_PFA21_EW_LU.csv', usecols=['LAD21CD','LAD21NM', 'PFA21NM'])

#Creating a dictionary of values matching LA code to PFA name
dict = ons_pfa.set_index('LAD21CD')['PFA21NM'].to_dict()

#Running dataframe through a for loop to assign PFAs to all of the LAs
for key in dict:
    df.loc[df['ladcode21'].str.contains(key), 'pfa'] = dict[key]

##Amending data to match CJS PFA data
#Dropping City of London entries
df2 = df.query('laname21 != "City of London"').copy()
#Replacing '&' for Devon and Cornwall
df2.replace(to_replace='Devon & Cornwall', value="Devon and Cornwall", inplace=True)

#Outputting to CSV    
df2.to_csv('../../data/interim/LA_population_female_2001_2021_PFAs_cleansed.csv', index=False)    