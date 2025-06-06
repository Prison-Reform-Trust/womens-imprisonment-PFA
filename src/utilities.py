"""
This script provides useful functions to all other scripts
"""

import logging
import os
from typing import List, Optional

import pandas as pd
import yaml


def setup_logging():
    """Set up logging configuration"""
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )


def read_config():
    """Read in config file"""
    config = {k: v for d in yaml.load(
        open('config.yaml', encoding='utf-8'),
        Loader=yaml.SafeLoader) for k, v in d.items()}
    return config


def load_data(status: str, filename: str, usecols: Optional[List[str]] = None) -> pd.DataFrame:
    """Load CSV file into Pandas DataFrame and convert object columns
    to categories when they meet criteria in `set_columns_to_category()`

    Parameters
    ----------
    status : {'raw', 'interim', 'processed'}
        Status of the data processing.
        * If 'raw' file is located in "rawFilePath" within config file
        * If 'interim', file is located in "intFilePath"
        * If 'processed', file is located in "clnFilePath"
    filename : str
        Name of CSV file to be loaded.
    usecols : list of str, optional
        Subset of columns to read from the CSV file.

    Returns
    -------
    DataFrame
        CSV data is returned as Pandas DataFrame with any eligible object columns
        converted into category columns to limit memory requirements.

    Raises
    ------
    FileNotFoundError
        If the specified file does not exist.
    """
    paths = {
        "raw": 'rawFilePath',
        "interim": 'intFilePath',
        "processed": 'clnFilePath'
    }
    config = read_config()
    df_path = os.path.join(config['data'][paths[status]], filename)

    setup_logging()

    try:
        df = pd.read_csv(df_path, encoding='latin1', low_memory=False, usecols=usecols)
        logging.info("Loaded data from %s", df_path)
        return set_columns_to_category(df)
    except FileNotFoundError:
        logging.error("File not found: %s", df_path)
        raise  # Still raise it so the calling code can choose how to handle


def set_columns_to_category(df):
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


def ensure_directory(path: str) -> None:
    """Ensure the download directory exists."""
    os.makedirs(path, exist_ok=True)
