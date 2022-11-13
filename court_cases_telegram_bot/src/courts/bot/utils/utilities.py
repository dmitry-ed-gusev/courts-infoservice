#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Common utilities module for Courts Info Service.

    Created:  Gusev Dmitrii, 13.11.2022
    Modified:
"""

import os
import logging

log = logging.getLogger(__name__)


def file_2_str(filename: str) -> str:
    """Read content from the provided file as string/text."""
    log.debug(f'file_2_str(): reading content from file: [{filename}].')

    if not filename:  # fail-fast behaviour (empty path)
        raise ValueError("Specified empty file path!")
    if not os.path.exists(os.path.dirname(filename)):  # fail-fast behaviour (non-existent path)
        raise ValueError(f"Specified path [{filename}] doesn't exist!")

    with open(filename, mode='r') as infile:
        return infile.read()
