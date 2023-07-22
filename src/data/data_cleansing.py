# Import sentencing outcomes data (all courts) from Ministry of Justice Criminal Justice Statistics
# Downloaded on 8 July, 2023

import utilities as utils
import pandas as pd
import glob

## Collecting file paths with glob
path="data/external/obo_sent_pivot_2010_2022/"
all_files = glob.glob(path + "*.csv")

## IMPORTING DATASETS ##

# 1. Sentencing data 2010–22 
# (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1157979/obo_sent_pivot_2010_2015.zip and 
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1157991/obo_sent_pivot_2016_2022.zip)

cols = ['Police Force Area', 'Year', 'Sex', 'Age group', 'Offence group', 'Sentence Outcome', 'Custodial Sentence Length','Sentenced']
all_csvs = [utils.loadData(filename, cols=cols) for filename in all_files]
df = pd.concat(all_csvs, axis=0, ignore_index=True)

## DATA CLEANING PROCESS

# Renaming columns
utils.lcColumns(df)
utils.renameColumns(df, columns={
    'year_of_appearance': 'year',
    'offence_group': 'offence',
    'police_force_area': 'pfa',
    'sentence_outcome': 'outcome',
    'custodial_sentence_length': 'sentence_length',
    'sentenced': 'freq',
    'count': 'freq'}
    )

# Tidying elements using regex function
utils.tidy_elements(df)

# Reordering columns
column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_length', 'freq']
df = df.reindex(columns=column_order)

# Setting categorical columns
convert_dict = {'outcome': "category",
                'sentence_length': "category"
                }
df = df.astype(convert_dict)

# Setting outcomes to lowercase
df['outcome'] = df['outcome'].str.capitalize()

## FILTERING DATASET
filt1 = df['sex'] == 'Female'
filt2 = df['outcome'].isin(['Immediate custody', 'Community sentence','Suspended sentence'])
filt3 = df['age_group'].isin(["Adults", "Young adults"])
filt4 = df['pfa'].isin(["City of London", "Not known"])
filt = filt1 & filt2 & filt3 & ~filt4
women_dataset = df[filt].sort_values(['year', 'pfa']).copy()

## OUTPUTTING INTERIM DATASET FOR FURTHER ANALYSIS
women_dataset.to_csv('data/interim/PFA_2010-22_women_cust_comm_sus.csv', index=False)