#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Cleaned and filtered sentencing data 2010–22
# (from `data_cleansing.py`)
# this script builds a series of refined datasets ready for further analysis and final output

import pandas as pd
import utilities as utils
import numpy as np
import operator

config = utils.read_config()

##FUNCTIONS

def categoryColumns(df) -> pd.DataFrame:
    """Convert columns to category data type if they meet ratio

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        Processed DataFrame with object columns which meet criteria replaced with categories
    """
    cols = df.select_dtypes(include='object').columns
    for col in cols:
        ratio = len(df[col].value_counts()) / len(df)
        if ratio < 0.05:
            df[col] = df[col].astype('category')
    return df

def loadData(status='interim', filename='PFA_2010-22_women_cust_comm_sus.csv') -> pd.DataFrame:
    """Load CSV file into Pandas DataFrame and convert object columns to categories when they meet criteria in `categoryColumns()`

    Parameters
    ----------
    status : {'raw', 'interim', 'processed'}, default is 'interim'
        Status of the data processing.
        * If 'raw' file is located in "rawFilePath" within config file
        * If 'interim', file is located in "intFilePath"
        * If 'processed', file is located in "clnFilePath"
    filename : str, default is 'PFA_2010-22_women_cust_comm_sus.csv'
        Name of CSV file to be loaded.

    Returns
    -------
    DataFrame
        CSV data is returned as Pandas DataFrame with any eligible object columns converted into category columns to limit memory requirements
    """
    paths = {
        "raw": 'rawFilePath',
        "interim": 'intFilePath',
        "processed": 'clnFilePath'
    }

    dfPath=f"{config['data'][paths[status]]}{filename}"
    df = pd.read_csv(dfPath)
    print('Data loaded')
    return categoryColumns(df)

def saveData(df, status, filename, index=True):
    """Save data during or at the end of a data processing pipeline

    Parameters
    ----------
    df : DataFrame
        
    status : {'interim', 'processed'}
        Status of the data processing. 
        * If 'interim', file is saved to "intFilePath"
        * If 'processed', file is saved to "clnFilePath"

    filename : str
        filename parameter for csv export

    index : bool
        include index of DataFrame in csv output, by default True

    Returns
    -------
    DataFrame
        Render DataFrame as comma-separated file.
    """
    
    paths = {
            "interim": 'intFilePath',
            "processed": 'clnFilePath'
        }
    
    df.to_csv(f"{config['data'][paths[status]]}{filename}.csv", index=index)
    print(f"{filename} saved")
    return df

def groupAndSum(df, columns, sum_column=['freq']) -> pd.DataFrame:
    """Perform groupby and sum on a DataFrame

    Parameters
    ----------
    df : DataFrame
        _description_
    columns : label or list
        column names of DataFrame to perform `groupby()` operation
    sum_column : label, optional
        column name of DataFrame to perform `sum()` operation, by default "['freq']"

    Returns
    -------
    DataFrame
        Reshaped DataFrame grouped by `columns` parameter and the sum of the values over `sum_column`.
    """
    return df.groupby(columns, as_index=False)[sum_column].sum()

def sentencesByPFA(df, filename="sentencesByPFA") -> pd.DataFrame:
    """Data processing pipeline to produce sentencing outcomes by Police Force Area across
    the entire available date range.

    Parameters
    ----------
    df : DataFrame

    filename : str, optional
        filename parameter for final csv export, by default "sentencesByPFA"

    Returns
    -------
    DataFrame
        Returns the original DataFrame, but saves a fully processed CSV file containing sentencing outcomes by Police Force Area across 
        the entire available date range.
    """
    my_df = df.copy()

    (my_df
    .pipe(groupAndSum, columns=['pfa', 'year', 'outcome'])
    .pipe(saveData, status='processed', filename=filename, index=False)
    )
    
    #Return original DataFrame to allow for continued processing through the pipeline.
    return df

def filterSentence(df, sentence_type=None, column='outcome') -> pd.DataFrame:
    """DataFrame filter allowing selection of subset of data by sentence type

    Parameters
    ----------
    df : DataFrame

    sentence_type : single label or list-like, optional
        select from the available sentence types within the DataFrame
        {'Community sentence', 'Immediate custody', 'Suspended sentence'}, by default 'Immediate custody'

    column : str, optional
        column name of DataFrame with sentence outcome values, by default 'outcome'

    Returns
    -------
    DataFrame
        A filtered DataFrame displaying the chosen sentence type
    """
    if sentence_type is None:
        sentence_type = 'Immediate custody'

    mask = None
    if type(sentence_type) == str:
        mask = df[column] == sentence_type
    elif type(sentence_type) == list:
        mask = df[column].isin(sentence_type)
    
    filtered_df = df.loc[mask].copy()
    return filtered_df

def filterYear(df, year=None, op="eq", column='year') -> pd.DataFrame: 
    """DataFrame filter allowing selection of subset of data by year using comparison operators from operator library
    Evaluate a comparison operation `=`, `!=`, `>=`, `>`, `<=`, or `<`.

    Parameters
    ----------
    df : DataFrame
        
    year : int,
        target year, will use the most recent year available in DataFrame if no parameter is provided, default None
    op : {eq, ne, gt, ge, lt, le}, optional
        comparison operator, by default "eq"
        lt is equivalent to a < b, 
        le is equivalent to a <= b, 
        eq is equivalent to a == b, 
        ne is equivalent to a != b, 
        gt is equivalent to a > b and 
        ge is equivalent to a >= b.
    column : str, optional
        column name of DataFrame with year values, by default 'year'

    Returns
    -------
    DataFrame
        A filtered DataFrame displaying the records for a chosen year or period
    """

    methods = {
            "eq": operator.eq,
            "ne": operator.ne,
            "lt": operator.lt,
            "gt": operator.gt,
            "le": operator.le,
            "ge": operator.ge,
        }
    if year is None:
        mask = methods[op](df[column], df['year'].max())
    else:
        mask = methods[op](df[column], year)
    
    filtered_df = df[mask]
    return filtered_df

def offenceProportions(df) -> pd.DataFrame:
    """Calculate proportions of each offence type for each Police Force Area

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        A cross-tabulated DataFrame with float values normalised to each Police Force Area
    """
    return pd.crosstab(index=df['pfa'], 
                columns=df['offence'], 
                values=df['freq'], 
                aggfunc=sum, 
                normalize='index',
                ).round(3)

def custodialSentencesByOffence(df, filename=None):
    """Data processing pipeline to produce interim dataset of offence types which received a custodial sentence, by Police Force Area

    Parameters
    ----------
    df : DataFrame

    filename : str, optional
        filename parameter for final csv export, by default f"custodial_sentences_by_offence_{df['year'].max()}"

    Returns
    -------
    pd.DataFrame
        Produces and saves CSV of a processed DataFrame containing offence types which received a custodial sentence, by Police Force Area, for the latest available year
    """
    if filename is None:
        filename = f"custodial_sentences_by_offence_{df['year'].max()}"
    
    my_df = df.copy()
    
    (my_df
    .pipe(filterYear, 2022)
    .pipe(filterSentence)
    .pipe(groupAndSum, columns=['pfa', 'offence'])
    .pipe(offenceProportions)
    .pipe(saveData, status='processed', filename=filename)
    )
    
    #Returns original DataFrame to allow for continued processing through the pipeline.
    return df

def consolidateSentenceLengths(df) -> pd.DataFrame:
    """Bin sentence lengths into three new distinct categories:
        * Less than 6 months;
        * 6 months to less than 12 months
        * 12 months or more

        12 months or more is the default value if it is not found in dict_map.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    DataFrame
        A processed DataFrame with three distinct custodial sentence length categories based on values in `dict-map`
    """
    dict_map = {"Up to and including 1 month": 'Less than 6 months',
                    "More than 1 month and up to and including 2 months": 'Less than 6 months',
                    "More than 2 months and up to and including 3 months": 'Less than 6 months',
                    "More than 3 months and up to 6 months": 'Less than 6 months',
                    "6 months": '6 months to less than 12 months',
                    "More than 6 months and up to and including 9 months": '6 months to less than 12 months',
                    "More than 9 months and up to 12 months": '6 months to less than 12 months'
                    }
        
    
    df['sentence_length'] = df['sentence_length'].map(lambda x: dict_map.get(x, "12 months or more"))

    return df

def custodialSentenceLengths(df, filename=None) -> pd.DataFrame:
    """Data processing pipeline to produce interim dataset of grouped custodial sentence lengths, by Police Force Area

    Parameters
    ----------
    df : _type_
        _description_
    filename : _type_, optional
        _description_, by default f"women_cust_sentence_length_PFA_{df['year'].min()}-{df['year'].max()}"

    Returns
    -------
    pd.DataFrame
        Produces and saves CSV of a processed DataFrame containing grouped custodial sentence lengths, by Police Force Area
    """
    if filename is None:
        filename = f"women_cust_sentence_length_PFA_{df['year'].min()}-{df['year'].max()}"

    my_df = df.copy()
    
    df_processed =(
        my_df
        .pipe(filterSentence)
        .pipe(consolidateSentenceLengths)
        .pipe(groupAndSum, columns=['pfa', 'year', 'sentence_length'])
        .pipe(saveData, status="interim", filename=filename, index=False) #Query whether the status of this is interim given that it is used in production of figure 1
    )
    #Returning processed version of DataFrame in order to allow for further filtering by year and sentence length
    return df_processed

def filterSentenceLength(df, sentence_length, column='sentence_length') -> pd.DataFrame:
    """DataFrame filter allowing selection of subset of data by custodial sentence length

    Parameters
    ----------
    df : DataFrame

    sentence_length : str or list-like
        {"Less than 6 months", "6 months to less than 12 months", "12 months or more"}

    column : str, optional
        column name of DataFrame with custodial sentence length values, by default 'sentence_length'

    Returns
    -------
    DataFrame
        A filtered DataFrame displaying the chosen custodial sentence length
    """
    mask = None
    if type(sentence_length) == str:
        mask = df[column] == sentence_length
    elif type(sentence_length) == list:
        mask = df[column].isin(sentence_length)
    
    filtered_df = df.loc[mask]
    return filtered_df

def aggregateSentences(df) -> pd.DataFrame:
    """Calculate total number of custodial sentences of a given length in each year, by Police Force Area

    Parameters
    ----------
    df : DataFrame
        Ensure that the DataFrame being passed to this function contains the correct sentence length(s)

    Returns
    -------
    DataFrame
        A cross-tabulated DataFrame of the total number of custodial sentences in each year, by Police Force Area
    """
    
    agg_df = pd.crosstab(index=df['pfa'], 
                columns=df['year'], 
                values=df['freq'], 
                aggfunc=sum, 
                )
    return agg_df

def percentageChange(df, periods=8) -> pd.DataFrame:
    """Function to calculate percentage change between the first and last year in the DataFrame.

    Parameters
    ----------
    df : DataFrame
        
    periods : int, optional
        The total time period in years, by default 8

    Returns
    -------
    DataFrame
        DataFrame is returned with additional column showing the percentage change as a float
    """
    df.fillna(0.0).astype(int)
    df[f'per_change_{df.columns[0]}'] = df.pct_change(axis='columns', periods=periods).dropna(axis='columns')
    return df

def custodialSentenceTableProcessing(df, filename):
    """Processing chain to output number of custodial sentences by Police Force Area and percentage change

    Parameters
    ----------
    df : DataFrame
        
    filename : str
        filename parameter for csv export
    """
    (df
    .pipe(aggregateSentences)
    .pipe(percentageChange)
    .pipe(saveData, status='processed', filename=f'{filename}_TEST')
    )

def custodialSentenceTableOutput(df):
    """Output final tables in csv format by:
    * Total number of women sentenced to custody and percentage change by Police Force Area; and of those
        * Sentenced to less than six months; and
        * Sentenced to less than 12 months.

    Parameters
    ----------
    df : DataFrame

    Returns
    -------
    str
        Returns message if processing has been successful
    """

    df_custodialSentences_PFA = df.pipe(filterYear, 2014, op="ge")
    

    sentence_length_dict = {'cust_sentences_total': "", 'cust_sentences_lt_12m': ["Less than 6 months", "6 months to less than 12 months"], 'cust_sentences_lt_6m':"Less than 6 months"}

    for k, v in sentence_length_dict.items():
        if v != "":
            (df_custodialSentences_PFA
            .pipe(filterSentenceLength, sentence_length=v)
            .pipe(custodialSentenceTableProcessing, filename=f'{k}')
            )

        else:
            (df_custodialSentences_PFA
            .pipe(custodialSentenceTableProcessing, filename=f'{k}')
            )
    
    print("Processing complete")

def main():
        df=loadData()

        (df
        .pipe(sentencesByPFA) ## 1.SENTENCING OUTCOME FOR EACH PFA BY YEAR
        .pipe(custodialSentencesByOffence) ## 2. CUSTODIAL SENTENCES FOR EACH PFA BY OFFENCE TYPE
        .pipe(custodialSentenceLengths) ## 3.CUSTODIAL SENTENCE LENGTHS FOR EACH PFA BY YEAR (FIG 1, FACTSHEET)
        .pipe(custodialSentenceTableOutput) ## 4. CUSTODIAL SENTENCES FOR EACH PFA BY YEAR WITH % CHANGE
        )

if __name__ == '__main__':
    main()