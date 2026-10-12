# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is part of the data visualisation pipeline for the Criminal Justice System
statistics quarterly: December 2024 Outcomes by Offence dataset.

This script generates all publication ready visualisations in this project.
"""

from src.visualisation import custody_sentence_lengths, sentence_types


def main(config: dict) -> None:
    """
    Main function to produce all visualisations for the fact sheets.
    """
    custody_sentence_lengths.main(config=config)
    sentence_types.main(config=config)
