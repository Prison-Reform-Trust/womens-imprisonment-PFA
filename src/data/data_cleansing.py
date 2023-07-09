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

# 2. Court outcomes by police force area 2009–2019 (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/888561/csvs-behind-data-tools-2-2019.zip)
cols_2009 =['Police Force Area', 'Year of Appearance', 'Sex', 'Age Group', 'Offence Group', 'Outcome', 'Custodial Sentence Length','Count'] 
df_2009 = utils.loadData('../womens-pfa-analysis/data/external/court-outcomes-by-PFA-2019.csv', cols=cols_2009)

#Filtering `df_2009` for 2009 data
filt = df_2009['Year of Appearance'] == 2009
df_2009 = df_2009[filt].copy()

# Defining datasets to iterate through in following section
df_list = utils.dataframeList(locals()) #Using locals() function to retrieve local symbol table. Note this outputs a complex list, and is no longer a DataFrame.

## DATA CLEANING PROCESS

# Renaming columns
for data in df_list:
    utils.lcColumns(data)
    utils.renameColumns(data, columns={
        'year_of_appearance': 'year',
        'offence_group': 'offence',
        'police_force_area': 'pfa',
        'sentence_outcome': 'outcome',
        'custodial_sentence_length': 'sentence_length',
        'sentenced': 'freq',
        'count': 'freq'}
        )

# Joining and tidying elements into one DataFrame
df_combined = pd.concat(df_list)
utils.tidy_elements(df_combined)

# Reordering columns
column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_length', 'freq']
df_combined = df_combined.reindex(columns=column_order)

# Setting categorical columns
convert_dict = {'outcome': "category",
                'sentence_length': "category"
                }
df_combined = df_combined.astype(convert_dict)

# Setting outcomes to capitalize case
df_combined['outcome'] = df_combined['outcome'].str.capitalize()

## FILTERING DATASET
filt1 = df_combined['sex'] == 'Female'
filt2 = df_combined['outcome'].isin(['Immediate custody', 'Community sentence','Suspended sentence'])
filt3 = df_combined['age_group'].isin(["Adults", "Young adults"])
filt4 = df_combined['pfa'].isin(["Special/miscellaneous and unknown police forces", "City of London", "Not known"])
filt = filt1 & filt2 & filt3 & ~filt4
women_dataset = df_combined[filt].sort_values(['year', 'pfa']).copy()

## OUTPUTTING INTERIM DATASET FOR FURTHER ANALYSIS
women_dataset.to_csv('data/interim/PFA_2009-22_women_cust_comm_sus.csv', index=False)