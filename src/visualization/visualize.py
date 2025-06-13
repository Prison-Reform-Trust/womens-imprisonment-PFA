# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is part of the data visualisation pipeline for the Criminal Justice System
statistics quarterly: December 2024 Outcomes by Offence dataset.

It is intended to be run as a standalone script to generate all publication ready visualisations
in this project.
"""

from src.visualization import custody_sentence_lengths


def main():
    """
    Main function to run all visualisations.
    """
    custody_sentence_lengths.main()


if __name__ == "__main__":
    main()
