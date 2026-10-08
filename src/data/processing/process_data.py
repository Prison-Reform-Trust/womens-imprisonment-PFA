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
from src.data.processing import (combine_custody_pfa_population,
                                 filter_custody_offences,
                                 filter_sentence_length, filter_sentence_type,
                                 group_pfa_sentence_outcome,
                                 la_to_pfa_matching, make_custody_tables,
                                 ons_cleaning)


def process_data(config: dict) -> None:
    """Run the processing pipeline for the selected analysis configuration."""

    logging.info(
        "Starting processing for %s analysis",
        config["analysis"]["id"],
    )

    filter_sentence_type.main(config=config)
    group_pfa_sentence_outcome.main(config=config)
    filter_sentence_length.main(config=config)
    make_custody_tables.main(config=config)
    filter_custody_offences.main(config=config)
    ons_cleaning.main(config=config)
    la_to_pfa_matching.main(config=config)
    combine_custody_pfa_population.main(config=config)

    logging.info("Data processing pipeline completed successfully.")


def main(config: dict) -> None:
    """Run the processing pipeline"""
    utils.setup_logging()
    process_data(config=config)
