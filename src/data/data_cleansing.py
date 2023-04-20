# Import sentencing outcomes data (all courts) from Ministry of Justice Criminal Justice Statistics
# Downloaded on 23 March, 2023

import load
import pandas as pd

## IMPORTING DATASETS ##
# 1. Sentencing data 2017–21 (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1076592/Data-behind-interactive-tools-3.zip)
cols = ['Police Force Area', 'Year', 'Sex', 'Age group', 'Offence group', 'Sentence Outcome', 'Custodial Sentence Length','Sentenced']
df = load.loadData("../../../data/external/sentencing.csv", cols=cols)

# 2. Court outcomes by police force area 2009–2019 (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/888561/csvs-behind-data-tools-2-2019.zip)
cols_2009 =['Police Force Area', 'Year of Appearance', 'Sex', 'Age Group', 'Offence Group', 'Outcome', 'Custodial Sentence Length','Count'] 
df_2009 = load.loadData('../../../womens-pfa-analysis/data/external/court-outcomes-by-PFA-2019.csv', cols=cols_2009)

## DATA CLEANSING FUNCTIONS ##

def lcColumns(data):
    '''
    Converting all `data` columns to lowercase

    Parameters
    ----------
    data: Pandas dataframe
    '''
    data.columns = data.columns.str.lower()

def renameColumns(data, columns):
    '''
    Rename columns within a Pandas dataframe to standardised dictionary values
    
    Parameters
    ----------
    data: Pandas dataframe

    columns: dict of original and replacement column names
    '''
    data.rename(
        columns = columns,
        inplace = True
    )

def orderColumns(data, column_order):
    '''
    Set column order for dataframe

    Parameters
    ----------
    data

    column_order: list, ordered in ascending order to be displayed
    '''
    data = data[column_order]

#Renaming and re-ordering columns

for data in [df, df_2009]:
    lcColumns(data)
    renameColumns(data, columns={
        'year of appearance': 'year',
        'offence group': 'offence',
        'age group': 'age_group',
        'police force area': 'pfa',
        'sentence outcome': 'outcome',
        'custodial sentence length': 'sentence_len',
        'sentenced': 'freq',
        'count': 'freq'}
        )
    orderColumns(data, column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_len', 'freq'])




# def cleanData(data):

# #Importing dataset and filtering columns
# usecols =['Police Force Area', 'Year', 'Sex', 'Age group', 'Offence group', 'Sentence Outcome', 'Custodial Sentence Length','Sentenced']
# df = pd.read_csv('../../data/external/sentencing.csv', usecols=usecols, encoding = 'latin1', low_memory=False)