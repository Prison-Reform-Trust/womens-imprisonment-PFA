#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script provides filter functions to locate specific data files to download
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
