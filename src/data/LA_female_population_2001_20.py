#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 18:09:15 2022

@author: alex
"""

import pandas as pd

#Importing dataset
df = pd.read_csv('../../data/external/MYEB1_detailed_population_estimates_series_UK_(2020_geog21).csv')

#Filtering data to only include England and Wales
filt = df['country'].str.contains("(?:^E|^W)", regex=True)
df_eng_wales= df[filt]

#Filtering further to only include adult women
filt1 = df_eng_wales['age'] >= 18
filt2 = df_eng_wales['sex'] == 2
filt = filt1 & filt2
df3 = df_eng_wales[filt]

#Melting data from wide to long
df4 = df3.melt(id_vars=["ladcode21", "laname21", "country", "sex", "age"], var_name="year", value_name="population")

#Removing population from year value
df4['year'] = df4['year'].str.replace("population_","", regex=True)

#Grouping all ages into one value
df5 = df4.groupby(['ladcode21', 'laname21', 'year'], as_index=False, sort=False).agg({'population':'sum'})

#Converting year values to int to enable filtering
df5['year']= df5['year'].astype('int')

#Outputting to CSV
df5.to_csv('../../data/interim/LA_population_female_2001_2020-cleansed.csv', index=False)