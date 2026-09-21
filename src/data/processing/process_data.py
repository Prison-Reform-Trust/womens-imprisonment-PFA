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


def process_data(config: dict) -> None:
    """Run the processing pipeline for the selected analysis configuration."""

    logging.info(
        "Starting processing for analysis %s",
        config["analysis"]["id"],
    )

    filter_sentence_type.main(config)
    group_pfa_sentence_outcome.main(config)
    filter_sentence_length.main(config)
    make_custody_tables.main(config)
    filter_custody_offences.main(config)

    logging.info("Data processing pipeline completed successfully.")
