#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script provides filter functions to locate specific data files to download
from API responses, including GOV.UK and the Office for National Statistics (ONS).
"""


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
