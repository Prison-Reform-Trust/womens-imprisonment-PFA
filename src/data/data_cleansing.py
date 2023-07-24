# Sentencing data 2010–22 
# (from: https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1157979/obo_sent_pivot_2010_2015.zip and 
# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1157991/obo_sent_pivot_2016_2022.zip)

# Downloaded on 8 July, 2023

import pandas as pd
import glob
from time import sleep

## FUNCTIONS

def loadData():
    path="data/external/obo_sent_pivot_2010_2022/"
    cols = ['Police Force Area', 'Year', 'Sex', 'Age group', 'Offence group', 'Sentence Outcome', 'Custodial Sentence Length','Sentenced']
    all_files = glob.glob(path + "*.csv")
    all_csvs = [pd.read_csv(filename, usecols=cols, encoding= 'unicode_escape', low_memory=False) for filename in all_files]
    return pd.concat(all_csvs, axis=0, ignore_index=True)

def filterDataFrame(x_df):      #Filtering DataFrame
    filt1 = x_df['Sex'] == '01: Female'
    filt2 = x_df['Sentence Outcome'].isin(['06: Total Immediate Custody', '04: Total Community sentence','05: Suspended Sentence'])
    filt3 = x_df['Age group'].isin(['02: Young adults', '03: Adults'])
    filt4 = x_df['Police Force Area'].isin(['City of London', 'Not known'])
    filt = filt1 & filt2 & filt3 & ~filt4
    return x_df[filt].sort_values(['Year', 'Police Force Area'])

def lcColumns(x_df):        #Converting columns to lowercase and replacing spaces with underscores
    x_df.columns = x_df.columns.str.lower().str.replace(' ', '_')
    return x_df

def renameColumns(x_df):    #Renaming columns
    mapping={
    'offence_group': 'offence',
    'police_force_area': 'pfa',
    'sentence_outcome': 'outcome',
    'custodial_sentence_length': 'sentence_length',
    'sentenced': 'freq'
    }
    
    x_df = x_df.rename(columns=mapping)
    return x_df

def removePrefix(x_df):     #Removing numbered prefixes from all elements in DataFrame
    cols = x_df.select_dtypes(include='object').columns
    for col in cols:
        x_df[col] = x_df[col].str.replace('^\d+:', '', regex=True).str.lstrip()
    return x_df
    
def removeTotal(x_df, col):     #Removing "Total" prefix
    x_df[col] = x_df[col].str.replace("Total ", "").str.capitalize()
    return x_df

def standardiseSentences(x_df, col):    #Replacing wording of some sentence lengths
    mapping = {r"^\S* - ": "",
        "(Over)": "More than",
        "(to less than)": "and under",
        "Life$": "Life sentence",
        }
    x_df[col].replace(regex=mapping, inplace=True)
    return x_df

def categoryColumns(x_df):      #Converting object columns to category
    cols = x_df.select_dtypes(include='object').columns
    for col in cols:
        ratio = len(x_df[col].value_counts()) / len(x_df)
        if ratio < 0.05:
            x_df[col] = x_df[col].astype('category')
    return x_df

def orderColumns(x_df):     #Setting column order of dataframe
    column_order = ['year', 'pfa', 'sex', 'age_group', 'offence', 'outcome', 'sentence_length', 'freq']

    x_df = x_df.reindex(columns=column_order)
    return x_df

def cleanData(x_df):        #Data cleaning pipeline
    my_df = x_df.copy()
    print('Cleaning data...')

    df_cleaned=(
        my_df
        .pipe(filterDataFrame)
        .pipe(lcColumns)
        .pipe(renameColumns)
        .pipe(removePrefix)
        .pipe(removeTotal, 'outcome')
        .pipe(standardiseSentences, 'sentence_length')
        .pipe(categoryColumns)
        .pipe(orderColumns)   
    )
    sleep(5)
    print('Data successfully cleaned')
    return df_cleaned

def main():
    print('Loading data...')
    df=loadData()
    print('Data loaded')
    df_cleaned=cleanData(df)
    print('Saving...')
    df_cleaned.to_csv('data/interim/PFA_2010-22_women_cust_comm_sus.csv', index=False)
    print('Complete')

if __name__ == "__main__":
    main()