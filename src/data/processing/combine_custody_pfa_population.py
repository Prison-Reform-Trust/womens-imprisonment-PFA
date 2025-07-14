#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script processes the ONS population by Police Force Area (PFA) data and
combines it with the Criminal Justice System (CJS) statistics custody data to
enable calculation of the imprisonment rate by PFA.

The script includes 2024 population projections using validated statistical methods
(Linear Trend, CAGR, Moving Average) with backtesting to select the best approach.
"""

import logging
from typing import Tuple

import numpy as np
import pandas as pd

import src.data.processing.common_ons_processing as common
import src.utilities as utils

config = utils.read_config()
utils.setup_logging()

OUTPUT_FILENAME_TEMPLATE = config['data']['datasetFilenames']['combine_custody_pfa_population']
FINAL_TABLE_FILENAME_TEMPLATE = config['data']['datasetFilenames']['custody_rate_pfa']


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load the PFA population data and CJS custody data."""
    custody_data_template = config['data']['datasetFilenames']['make_custody_tables_template']
    custody_data_filename = custody_data_template.format(category='all')

    population_data_filename = utils.fetch_latest_file(
        pattern="*LA_PFA_population*.csv",  # NOTE: Would be better to draw this from config
        path=config['data']['intFilePath']
    )

    custody_data = utils.load_data('processed', custody_data_filename)
    population_data = utils.load_data('interim', population_data_filename)
    return custody_data, population_data


def process_custody_data(custody_data: pd.DataFrame) -> pd.DataFrame:
    """Process the CJS custody data to ensure it is in the correct format."""
    logging.info("Processing CJS custody data...")
    custody_data = (
        custody_data
        .drop(custody_data.columns[-1], axis=1)
        .melt(id_vars='pfa', var_name='year', value_name='custody_count')
        .assign(year=lambda df: df['year'].astype(int))
        .sort_values(by=['pfa', 'year'])
        .reset_index(drop=True)
    )

    return custody_data


def process_population_data(population_data: pd.DataFrame, custody_data: pd.DataFrame) -> pd.DataFrame:
    """Process the population data to ensure it is in the correct format."""
    min_year, _ = utils.get_year_range(custody_data)
    logging.info("Processing population data...")

    # Standardise PFA names to match custody data
    population_data['pfa'] = population_data['pfa'].cat.rename_categories({
        'Dyfed-Powys': 'Dyfed Powys',
        'Metropolitan Police': 'London'
    })

    population_data = (
        population_data
        .loc[lambda df: df['year'] >= min_year]  # Filter years to match custody data
        .pipe(common.group_and_sum, group_cols=['pfa', 'year'], sum_col='freq')
    )

    return population_data


def project_linear_trend(
        df: pd.DataFrame,
        pfa_col: str = 'pfa',
        year_col: str = 'year',
        pop_col: str = 'freq',
        projection_year: int = 2024,
        trend_years: int = 5,
) -> pd.DataFrame:

    """Project population using linear trend extrapolation."""

    projections = []

    for pfa in df[pfa_col].unique():
        pfa_data = df[df[pfa_col] == pfa].copy()

        # Get recent years for trend fitting
        max_year = pfa_data[year_col].max()
        min_trend_year = max_year - trend_years + 1
        trend_data = pfa_data[pfa_data[year_col] >= min_trend_year]

        if len(trend_data) >= 3:  # Need at least 3 points for trend
            # Aggregate by year for this PFA
            yearly_totals = trend_data.groupby(year_col)[pop_col].sum().reset_index()

            # Fit linear trend
            years = yearly_totals[year_col].values
            pop = yearly_totals[pop_col].values

            # Linear regression
            coeffs = np.polyfit(years, pop, 1)
            slope, intercept = coeffs

            # Project to target year
            projected_pop = slope * projection_year + intercept

            projections.append({
                pfa_col: pfa,
                year_col: projection_year,
                pop_col: max(int(round(projected_pop)), 0),
                'method': 'linear_trend',
                'trend_slope': slope
            })

    return pd.DataFrame(projections)


def project_cagr(
        df: pd.DataFrame,
        pfa_col: str = 'pfa',
        year_col: str = 'year',
        pop_col: str = 'freq',
        projection_year: int = 2024,
        base_years: int = 5
) -> pd.DataFrame:

    """Project population using Compound Annual Growth Rate."""

    projections = []

    for pfa in df[pfa_col].unique():
        pfa_data = df[df[pfa_col] == pfa].copy()

        # Get base period data
        max_year = pfa_data[year_col].max()
        start_year = max_year - base_years + 1

        yearly_totals = pfa_data.groupby(year_col)[pop_col].sum()

        if start_year in yearly_totals.index and max_year in yearly_totals.index:
            start_pop = yearly_totals[start_year]
            end_pop = yearly_totals[max_year]

            # Calculate CAGR
            years_diff = max_year - start_year
            if years_diff > 0 and start_pop > 0:
                cagr = (end_pop / start_pop) ** (1/years_diff) - 1

                # Project forward
                years_to_project = projection_year - max_year
                projected_pop = end_pop * (1 + cagr) ** years_to_project

                projections.append({
                    pfa_col: pfa,
                    year_col: projection_year,
                    pop_col: max(int(round(projected_pop)), 0),
                    'method': 'cagr',
                    'growth_rate': cagr
                })

    return pd.DataFrame(projections)


def project_moving_average(
        df: pd.DataFrame,
        pfa_col: str = 'pfa',
        year_col: str = 'year',
        pop_col: str = 'freq', projection_year: int = 2024,
        window: int = 3
) -> pd.DataFrame:

    """Project population using moving average of year-over-year changes."""

    projections = []

    for pfa in df[pfa_col].unique():
        pfa_data = df[df[pfa_col] == pfa].copy()
        yearly_totals = pfa_data.groupby(year_col)[pop_col].sum().sort_index()

        if len(yearly_totals) >= window + 1:
            # Calculate year-over-year changes
            changes = yearly_totals.diff().dropna()

            # Take moving average of recent changes
            avg_change = changes.tail(window).mean()

            # Project forward
            latest_pop = yearly_totals.iloc[-1]
            years_to_project = projection_year - yearly_totals.index[-1]
            projected_pop = latest_pop + (avg_change * years_to_project)

            projections.append({
                pfa_col: pfa,
                year_col: projection_year,
                pop_col: max(int(round(projected_pop)), 0),
                'method': 'moving_average',
                'avg_annual_change': avg_change.round(2)
            })

    return pd.DataFrame(projections)


def validate_projection_method(df: pd.DataFrame, method_func, actual_year: int = 2023,
                               **kwargs) -> pd.DataFrame:
    """Validate projection method by predicting a known year and comparing to actual."""
    # Use data up to year before actual_year for prediction
    train_data = df[df['year'] < actual_year].copy()

    # Get actual values for comparison
    actual_data = df[df['year'] == actual_year].groupby('pfa', observed=True)['freq'].sum()

    # Generate projections
    projections = method_func(train_data, projection_year=actual_year, **kwargs)

    # Compare projections to actual
    comparison = projections.merge(actual_data.reset_index(), on='pfa', suffixes=('_pred', '_actual'))
    comparison['abs_error'] = abs(comparison['freq_pred'] - comparison['freq_actual'])
    comparison['pct_error'] = comparison['abs_error'] / comparison['freq_actual'] * 100

    return comparison


def select_best_projection_method(population_data: pd.DataFrame) -> Tuple[str, pd.DataFrame]:
    """Test projection methods and select the best performing one."""
    logging.info("Testing projection methods with backtesting validation...")

    # Generate projections for the maximum custody year
    max_custody_year = population_data['year'].max() + 1  # Assuming projection is for the next year
    linear_proj = project_linear_trend(population_data, projection_year=max_custody_year)
    cagr_proj = project_cagr(population_data, projection_year=max_custody_year)
    ma_proj = project_moving_average(population_data, projection_year=max_custody_year)

    # Validate each method by predicting the last available year in population data
    last_year = population_data['year'].max()
    linear_validation = validate_projection_method(population_data, project_linear_trend, actual_year=last_year)
    cagr_validation = validate_projection_method(population_data, project_cagr, actual_year=last_year)
    ma_validation = validate_projection_method(population_data, project_moving_average, actual_year=last_year)

    # Calculate mean absolute percentage error for each method
    methods = {
        'Linear Trend': linear_validation['pct_error'].mean(),
        'CAGR': cagr_validation['pct_error'].mean(),
        'Moving Average': ma_validation['pct_error'].mean()
    }

    # Select best method
    best_method = min(methods, key=lambda method: methods[method])
    best_mape = methods[best_method]

    logging.info("Validation Results (Mean Absolute Percentage Error):")
    for method, mape in methods.items():
        logging.info("%s: %.5f%%", method, mape)

    logging.info("Best performing method: %s (MAPE: %.5f%%)", best_method, best_mape)

    # Get projections using best method
    if best_method == 'Linear Trend':
        final_projections = linear_proj.copy()
    elif best_method == 'CAGR':
        final_projections = cagr_proj.copy()
    else:
        final_projections = ma_proj.copy()

    return best_method, final_projections


def create_extended_population_data(population_data: pd.DataFrame, projections: pd.DataFrame) -> pd.DataFrame:
    """Combine historical population data with projections."""
    # Prepare projection data in the same format as historical data
    projection_year = projections['year'].max()
    logging.info("Adding projections for %s to population data...", projection_year)

    # Combine datasets
    extended_data = pd.concat([population_data, projections], ignore_index=True)
    extended_data = extended_data.sort_values(by=['pfa', 'year']).reset_index(drop=True)

    logging.info("Extended population data: %s to %s", extended_data['year'].min(), extended_data['year'].max())

    return extended_data


def merge_custody_and_population(custody_data: pd.DataFrame,
                                 extended_population_data: pd.DataFrame) -> pd.DataFrame:
    """Merge custody and population data for rate calculations."""
    logging.info("Merging custody and population data...")

    merged_df = extended_population_data.merge(
        custody_data,
        on=['pfa', 'year'],
        how='left',
        suffixes=('', '_custody')
    )

    # Check for any missing custody data
    missing_custody = merged_df['custody_count'].isna().sum()
    if missing_custody > 0:
        logging.warning("Found %s rows with missing custody data", missing_custody)
        missing_pfas = merged_df[merged_df['custody_count'].isna()]['pfa'].unique()
        logging.warning("PFAs with missing data: %s", ', '.join(missing_pfas))

    # Calculate imprisonment rate (per 100,000 women)
    merged_df['imprisonment_rate'] = ((merged_df['custody_count'] / merged_df['freq']) * 100000).round(1)

    logging.info("Final merged dataset: %s rows", len(merged_df))
    logging.info("Data covers: %s to %s", merged_df['year'].min(), merged_df['year'].max())

    return merged_df


def load_and_process_data() -> Tuple[pd.DataFrame, int, int]:
    """Load, process, and return the merged custody and population data with projections."""
    # Load data
    custody_df, population_df = load_data()

    # Process datasets
    custody_data = process_custody_data(custody_df)
    population_data = process_population_data(population_df, custody_data)

    # Create population projections if needed
    max_pop_year = population_data['year'].max()
    max_custody_year = custody_data['year'].max()

    if max_custody_year > max_pop_year:
        logging.info("Custody data extends to %s, population data to %s", max_custody_year, max_pop_year)
        logging.info("Generating population projections for %s...", max_custody_year)

        _, projections = select_best_projection_method(population_data)
        extended_population_data = create_extended_population_data(population_data, projections)
    else:
        extended_population_data = population_data

    # Merge custody and population data
    merged_df = merge_custody_and_population(custody_data, extended_population_data)

    min_year, max_year = utils.get_year_range(merged_df)

    logging.info("Data successfully processed and merged with projections.")
    return merged_df, min_year, max_year


def create_publication_ready_table(df: pd.DataFrame) -> pd.DataFrame:
    """Create a publication-ready table from the merged data."""
    logging.info("Creating final publication-ready table...")

    # Get the most recent year for sorting
    latest_year = df['year'].max()

    publication_table = (df
                         .pivot_table(index='pfa', columns='year', values='imprisonment_rate')
                         .sort_values(by=latest_year, ascending=True)
                         )
    return publication_table


def main():
    """Main function to load, process, and save the data."""
    df, min_year, max_year = load_and_process_data()
    filename = utils.get_output_filename(
        year=(min_year, max_year),
        template=OUTPUT_FILENAME_TEMPLATE
    )

    utils.safe_save_data(
        df,
        path=config['data']['clnFilePath'],
        filename=filename
    )

    publication_table = create_publication_ready_table(df)
    publication_filename = utils.get_output_filename(
        year=(min_year, max_year),
        template=FINAL_TABLE_FILENAME_TEMPLATE
    )
    utils.safe_save_data(
        publication_table,
        path=config['data']['clnFilePath'],
        filename=publication_filename,
        index=True  # Keep PFA as index for publication table
    )


if __name__ == "__main__":
    main()
