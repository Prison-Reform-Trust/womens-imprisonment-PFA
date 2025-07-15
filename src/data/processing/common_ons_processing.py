"""Common ONS data processing functions for handling population data."""

import logging

import pandas as pd

from src.utilities import setup_logging

setup_logging()


def filter_england_wales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the DataFrame to only include data for England and Wales.
    """
    logging.info("Filtering for England and Wales...")
    filt = df['country'].str.contains("(?:^E|^W)", regex=True)
    df_eng_wales = df[filt]
    return df_eng_wales


def remove_regional_and_national_aggregates(df, name_col='laname', code_col='ladcode'):
    """
    Drop rows containing aggregated regional or national data,
    which are not relevant for local area analysis.
    """
    logging.info("Finding aggregated national and regional data codes...")
    drop_codes = list(df[df[name_col].str.isupper()][code_col].unique())
    df = df[~df[code_col].isin(drop_codes)]
    logging.info("Aggregated national and regional data codes removed...")
    return df


def filter_adult_women(df: pd.DataFrame, sex_value: str | int, sex_col: str = 'sex', age_col: str = 'age', min_age: int = 18):
    """
    Filter the DataFrame to include only adult women (age >= min_age, sex == sex_value).
    Handles "90+" by treating it as 90 for filtering if dtype is category.
    """
    logging.info("Filtering for adult women...")
    if df[age_col].dtype.name == 'category':
        df[age_col] = df[age_col].cat.rename_categories({"90+": 90})
    df[age_col] = pd.to_numeric(df[age_col], errors='coerce')
    df = df[(df[age_col] >= min_age) & (df[sex_col] == sex_value)]
    return df


def group_and_sum(df, group_cols=None, sum_col='freq'):
    """
    Aggregate the DataFrame by summing the specified column
    across the specified group columns.
    """
    if group_cols is None:
        group_cols = ['ladcode', 'laname', 'year']
    logging.info("Aggregating by: %s", ', '.join(group_cols))
    return df.groupby(group_cols, as_index=False, observed=True).agg({sum_col: 'sum'})
