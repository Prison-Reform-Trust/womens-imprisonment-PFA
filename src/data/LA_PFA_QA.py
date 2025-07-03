#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is a quick and dirty placeholder script to incorporate my previous work on combining local authorities and
police force areas for QA purposes.

Raw data is sourced from the Office for National Statistics (ONS) and includes population estimates
for England and Wales, as well as a lookup table for local authority districts to police force areas
as of December 2022.
Data sources:
https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland/mid2021/populationestimatesmid2021unformatteddata.zip
https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/populationandmigration/populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland/mid2021/dataforreconciliation.zip
https://geoportal.statistics.gov.uk/datasets/4206337e432b45f686e29ac31d731765_0/

"""

import logging
from typing import Tuple

import pandas as pd

import src.utilities as utils

config = utils.read_config()
utils.setup_logging()


# 1. Combining population estimates for England and Wales from 2021 census and MYE reconciliation data

def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load the population estimates and reconciliation data."""
    df_population = utils.load_data('raw', 'MYEB1_detailed_population_estimates_series_UK_(2021_geog21).csv')
    df_reconciliation = utils.load_data('raw', 'MYEB2_detailed_components_of_change_for reconciliation_EW_(2021_geog21).csv',
                                        usecols=range(26))
    return df_population, df_reconciliation


df = pd.read_csv('data/raw/MYEB1_detailed_population_estimates_series_UK_(2021_geog21).csv')
filt = df['country'].str.contains("(?:^E|^W)", regex=True)
df_eng_wales = df[filt].reset_index(drop=True)

df_recon = pd.read_csv('data/raw/MYEB2_detailed_components_of_change_for reconciliation_EW_(2021_geog21).csv',
                       usecols=range(26))

df_merged = df_recon.merge(df_eng_wales, how='inner', on=['ladcode21', 'sex', 'age'], suffixes=(None, '_census'))
df_merged.drop(columns=['population_2021', 'ladname21_census', 'country_census'], inplace=True)
df_merged.rename(columns={'population_2021_census': 'population_2021'}, inplace=True)

filt1 = df_merged['age'] >= 18
filt2 = df_merged['sex'] == 2
filt = filt1 & filt2
df3 = df_merged[filt]

df4 = df3.melt(id_vars=["ladcode21", "ladname21", "country", "sex", "age"], var_name="year", value_name="population")
df4['year'] = df4['year'].str.replace("population_", "", regex=True)

df5 = df4.groupby(['ladcode21', 'ladname21', 'year'], as_index=False, sort=False).agg({'population': 'sum'})
df5['year'] = df5['year'].astype('int')
df5.to_csv('data/interim/LA_population_female_2001_2021_NOT_REBASED.csv', index=False)


# 2. Matching local authorities to police force areas for QA querying

df = pd.read_csv('data/interim/LA_population_female_2001_2021_NOT_REBASED.csv')
ons_pfa = pd.read_csv('data/raw/Local_Authority_District_to_Community_Safety_Partnerships_to_Police_Force_Areas_(December_2022)_Lookup_in_England_and_Wales.csv', usecols=['LAD22CD','LAD22NM', 'PFA22NM'])

lad_to_pfa_dict = ons_pfa.set_index('LAD22CD')['PFA22NM'].to_dict()

for key in lad_to_pfa_dict:
    df.loc[df['ladcode21'].str.contains(key), 'pfa'] = lad_to_pfa_dict[key]

df2 = df.query('ladname21 != "City of London"').copy()
df2.replace(to_replace='Devon & Cornwall', value="Devon and Cornwall", inplace=True)
df2.reset_index(drop=True)
df2.to_csv('data/interim/LA_population_female_2001_2021_PFAs_NOT_REBASED.csv', index=False)

