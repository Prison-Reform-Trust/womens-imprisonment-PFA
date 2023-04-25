# Import sentencing outcomes data (all courts) from Ministry of Justice Criminal Justice Statistics
# Downloaded on 23 March, 2023

import utilities as utils
import pandas as pd
import utilities as utils

## IMPORTING DATASETS ##
# 1. Sentencing data 2017–21 (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1076592/Data-behind-interactive-tools-3.zip)
cols = ['Police Force Area', 'Year', 'Sex', 'Age group', 'Offence group', 'Sentence Outcome', 'Custodial Sentence Length','Sentenced']
df = utils.loadData("data/external/sentencing.csv", cols=cols)

# 2. Court outcomes by police force area 2009–2019 (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/888561/csvs-behind-data-tools-2-2019.zip)
cols_2009 =['Police Force Area', 'Year of Appearance', 'Sex', 'Age Group', 'Offence Group', 'Outcome', 'Custodial Sentence Length','Count'] 
df_2009 = utils.loadData('../womens-pfa-analysis/data/external/court-outcomes-by-PFA-2019.csv', cols=cols_2009)

## RENAMING AND RE-ORDERING COLUMNS

# def cleanData(data):
for data in [df, df_2009]:
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
    utils.orderColumns(data, column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_length', 'freq'])
    utils.remove_num_prefix(data)
