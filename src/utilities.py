"""
This script provides useful functions to all other scripts
"""

import glob
import logging
import os
import re
from typing import List, Optional

import pandas as pd
import plotly.graph_objs as go
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

# TODO: #20 Refactor the save and safe_save functions to be more concise and reduce repetition
def save_data(df: pd.DataFrame, path: str, filename: str, index: bool) -> bool:
    """Save the processed DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to save.
    path : str
        The directory path where the file will be saved.
    filename : str
        The name of the file to save the DataFrame to.
    index : bool
        Whether to keep the current index as a column on save
    Returns
    -------
    bool
        True if the data was saved successfully, False otherwise.
    """
    logging.info('Saving...')
    ensure_directory(path)
    save_path = os.path.join(path, filename)
    df.to_csv(save_path, index=index)
    logging.info('Data successfully saved to %s', save_path)
    return True


def safe_save_data(df: pd.DataFrame, path: str, filename: str, index: bool = False) -> bool:
    """
    Save a DataFrame and log an error if saving fails.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to save.
    path : str
        The directory path to save the file.
    filename : str
        The filename to use when saving the file.
    index : bool
        Whether to keep the current index as a column on save
    Returns
    -------
    bool
        True if saving was successful, False otherwise.
    """
    success = save_data(df, path, filename, index)
    if not success:
        logging.error("Failed to save data to %s/%s", path, filename)
    return success


def save_chart(fig: go.Figure, path: str, filename: str) -> bool:
    """
    Save a chart figure to a file.

    Parameters
    ----------
    fig : go.Figure
        The figure to save.
    path : str
        The directory path where the file will be saved.
    filename : str
        The name of the file to save the figure to.

    Returns
    -------
    bool
        True if the figure was saved successfully, False otherwise.
    """
    logging.info('Saving chart...')
    ensure_directory(path)
    fig_path = os.path.join(path, filename)
    fig.write_image(fig_path)
    logging.info('Figure saved to %s', fig_path)
    return True


def safe_save_chart(fig: go.Figure, path: str, filename: str) -> bool:
    """
    Save a chart and log an error if saving fails.

    Parameters
    ----------
    fig : go.Figure
        The figure to save.
    path : str
        The directory path where the file will be saved.
    filename : str
        The name of the file to save the figure to.

    Returns
    -------
    bool
        True if saving was successful, False otherwise.
    """
    success = save_chart(fig, path, filename)
    if not success:
        logging.error("Failed to save chart to %s/%s", path, filename)
    return success


def get_year_range(df: pd.DataFrame, column: str = 'year') -> tuple:
    """
    Retrieves the minimum and maximum years from a specified column in a DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the year data.
        column (str, optional): The name of the column to extract years from. Defaults to 'year'.

    Returns:
        tuple: A tuple containing the start and end years (min_year, max_year).
    """
    min_year = int(df[column].min())
    max_year = int(df[column].max())
    return min_year, max_year


def get_latest_year_from_files(path: str, template: str) -> int:
    """
    Find the latest year from files matching the template pattern.
    Example template: 'PFA_custodial_sentences_by_offence_{year}_FINAL.csv'
    """
    # Build a glob pattern by replacing {year} with *
    pattern = template.replace("{year}", "*")
    files = glob.glob(os.path.join(path, pattern))
    years = []
    for f in files:
        # Extract year using regex
        match = re.search(r'(\d{4})', os.path.basename(f))
        if match:
            years.append(int(match.group(1)))
    if not years:
        raise FileNotFoundError("No files matching pattern found.")
    return max(years)
