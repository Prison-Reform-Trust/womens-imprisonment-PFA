#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 09:57:41 2022

@author: alex
"""

import pandas as pd

#Importing dataset and filtering columns
usecols =['Police Force Area', 'Year', 'Sex', 'Age group', 'Offence group', 'Sentence Outcome', 'Custodial Sentence Length','Sentenced']
df = pd.read_csv('data/external/sentencing.csv', usecols=usecols, encoding = 'latin1', low_memory=False)

#Importing dataset going back to 2009 and filtering columns
usecols_2009 =['Police Force Area', 'Year of Appearance', 'Sex', 'Age Group', 'Offence Group', 'Outcome', 'Custodial Sentence Length','Count'] 
df_2009 = pd.read_csv('data/external/court-outcomes-by-PFA-2019.csv', usecols=usecols_2009, encoding = 'latin1', low_memory=False)

#Dropping duplicate data from 2009 dataset that also appears in df
filt = df_2009['Year of Appearance'] < 2017
df_2009 = df_2009[filt]

#Renaming and re-ordering columns
df.columns = ['year', 'offence', 'sex', 'age_group', 'pfa', 'outcome', 'sentence_len', 'freq']
df_2009.columns = ['pfa', 'year', 'sex', 'age_group', 'offence', 'outcome', 'sentence_len', 'freq']

df_column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_len', 'freq']
df = df[df_column_order]
df_2009 = df_2009[df_column_order]

#Removing sentence length prefixes
df['sentence_len'] = df['sentence_len'].str.replace("^\S*: \S* - ","", regex=True)
df_2009['sentence_len'] = df_2009['sentence_len'].str.replace("\d\d: ","", regex=True)

#Concatenating the two dataframes
df_combined = pd.concat([df_2009, df])

#Regexing unnecessary code prefixes
df_combined['outcome'] = df_combined['outcome'].str.replace("\d\d: ","", regex=True)
df_combined['sex'] = df_combined['sex'].str.replace("\d\d: ","", regex=True)
df_combined['age_group'] = df_combined['age_group'].str.replace("\d\d: ","", regex=True)
df_combined['offence'] = df_combined['offence'].str.replace("\d\d: ","", regex=True)

#Stansardising outcomes of interest
df_combined['outcome'] = df_combined['outcome'].str.replace("(Total Immediate custody)","Immediate custody", regex=True)
df_combined['outcome'] = df_combined['outcome'].str.replace("(Total Community sentence)","Community sentence", regex=True)

#Standardising sentence lengths
df_combined['sentence_len'] = df_combined['sentence_len'].str.replace("(Over)","More than", regex=True)
df_combined['sentence_len'] = df_combined['sentence_len'].str.replace("( and including)","", regex=True)
df_combined['sentence_len'] = df_combined['sentence_len'].str.replace("(to less than)","and under", regex=True)
df_combined['sentence_len'] = df_combined['sentence_len'].str.replace("Life$","Life sentence", regex=True)
df_combined['sentence_len'] = df_combined['sentence_len'].str.capitalize()

#Applying filters
filt1 = df_combined['sex'] == 'Female'
filt2 = df_combined['outcome'].isin(['Immediate custody', 'Community sentence','Suspended sentence'])
filt3 = df_combined['age_group'].isin(["Adults", "Young adults"])
filt4 = df_combined['pfa'].isin(["Special/miscellaneous and unknown police forces", "City of London"])
filt = filt1 & filt2 & filt3 & ~filt4
women_custody = df_combined[filt]

#Outputting data for continued analysis
women_custody.to_csv('data/interim/PFA_2009-21_women_cust_comm_sus.csv', index=False)