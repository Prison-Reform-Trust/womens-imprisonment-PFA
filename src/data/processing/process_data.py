#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module completes the full processing stages the Criminal Justice System statistics
quarterly: December 2024 Outcomes by Offence dataset pipeline for this project.

Using the scripts contained within the `src/data/processing` directory.
Interim and fully processed datasets are saved as CSV files in the `intFilePath`
and `clnFilePath` directories.
"""

import logging

import src.utilities as utils
from src.data.processing import (filter_custody_offences,
                                 filter_sentence_length, filter_sentence_type,
                                 group_pfa_sentence_outcome,
                                 make_custody_tables)

utils.setup_logging()

config = utils.read_config()


def process_data():
    """
    Main function to process the Criminal Justice System statistics quarterly: December 2024
    Outcomes by Offence datasets.
    """
    logging.info("Starting data processing pipeline...")

    filter_sentence_type.main()
    group_pfa_sentence_outcome.main()
    filter_sentence_length.main()
    make_custody_tables.main()
    filter_custody_offences.main()

    logging.info("Data processing pipeline completed successfully.")


if __name__ == "__main__":
    process_data()
