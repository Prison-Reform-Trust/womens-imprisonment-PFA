#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script provides filter functions to locate specific data files to download
from API responses, including GOV.UK and the Office for National Statistics (ONS).
"""

from src.utilities import read_config

config = read_config()


def outcomes_by_offence_data_filter(data):
    """
    Filter to locate the outcomes by offence data from the Ministry of Justice
    Criminal Justice System statistics quarterly: December 2024.

    Published at https://www.gov.uk/government/collections/criminal-justice-statistics-quarterly

    """
    attachments = data['details']['attachments']

    return [
        attachment['url'] for attachment in attachments
        if attachment.get('content_type') == 'application/zip'
        and "outcomes by offence" in attachment.get('title', '').lower()
    ]


def zip_filter_csv_outcomes(name: str) -> bool:
    """
    Filter to locate CSV files that contain outcomes data in ZIP files.
    This is used to filter files in ZIP archives that are relevant to the
    Criminal Justice System statistics outcomes data.
    """
    return name.endswith(".csv") and "outcomes" in name.lower()


def population_data_filter(data):
    """
    Filter to locate population by age and gender for each local authority
    in England and Wales data from the Office for National Statistics (ONS).

    Published at https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/
    populationestimates/datasets/populationestimatesforukenglandandwalesscotlandandnorthernireland
    """
    downloads = data['downloads']
    return [
        downloads['csv']['href']] if 'csv' in downloads and 'href' in downloads['csv'] else []


def ons_la_pfa_filter(version: str):
    """
    Filter to locate the lookup file between Local Authority Districts and
    Police Force Areas in England and Wales from the Office for National Statistics (ONS).

    Published at https://geoportal.statistics.gov.uk/datasets/ons::local-authority-districts-to-police-force-areas-in-england-and-wales-lookup-2022/about
    """
    keys = {
        'latest': ('ons_la_pfa', 'ons_pfa_params', 'ons_la_pfa'),
        'earlier': ('ons_la_pfa_earlier_qa', 'ons_pfa_earlier_params', 'ons_la_pfa_earlier_qa')
    }
    if version not in keys:
        raise ValueError(f"Invalid version '{version}'. Expected one of {list(keys.keys())}.")
    download_key, params_key, filename_key = keys[version]
    return {
            'endpoint': config['data']['downloadPaths'][download_key],
            'params': config[params_key],
            'path': config['data']['rawFilePath'],
            'filename': config['data']['datasetFilenames'][filename_key]
        }
