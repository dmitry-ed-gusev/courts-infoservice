#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    Common utilities module for Courts Info Service.

    Created:  Gusev Dmitrii, 13.11.2022
    Modified:
"""

import logging
import os

import pymysql

log = logging.getLogger(__name__)


def file_2_str(filename: str) -> str:
    """Read content from the provided file as string/text."""
    log.debug(f"file_2_str(): reading content from file: [{filename}].")

    if not filename:  # fail-fast behaviour (empty path)
        raise ValueError("Specified empty file path!")
    if not os.path.exists(
        os.path.dirname(filename)
    ):  # fail-fast behaviour (non-existent path)
        raise ValueError(f"Specified path [{filename}] doesn't exist!")

    with open(filename, mode="r") as infile:
        return infile.read()


def get_mysql_conn():
    """Utility method: returning new mysql connection."""

    return pymysql.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        passwd=os.environ["MYSQL_PASS"],
        database=os.environ["MYSQL_DB"],
    )


def form_message_from_db_response(row) -> str:
    """dm.court, dm.check_date, dm.section_name, dm.order_num, dm.case_num,
    dm.hearing_time, dm.hearing_place, dm.case_info, dm.stage, dm.judge, dm.hearing_result,
    dm.decision_link, dm.case_link, dm.row_hash, dm.court_alias"""
    message = (
        "Суд: "
        + str(row[0])
        + "\nДата заседания: "
        + row[1].isoformat()
        + "\nНомер дела: "
        + str(row[4])
    )
    if row[2] and len(row[2]) > 0:
        message = message + "\nКатегория: " + str(row[2])
    if row[5] and len(row[5]) > 0:
        message = message + "\nВремя слушания: " + str(row[5])
    if row[6] and len(row[6]) > 0:
        message = message + "\nМесто проведения: " + str(row[6])
    if row[7] and len(row[7]) > 0:
        message = message + "\nИнформация по делу: " + str(row[7])
    if row[8] and len(row[8]) > 0:
        message = message + "\nСтадия дела: " + str(row[8])
    if row[9] and len(row[9]) > 0:
        message = message + "\nСудья: " + str(row[9])
    if row[10] and len(row[10]) > 0:
        message = message + "\nРезультат слушания: " + str(row[10])
    if row[11] and len(row[11]) > 0:
        message = message + "\nСудебный акт: " + str(row[11])
    if row[12] and len(row[12]) > 0:
        message = message + "\nСсылка на дело: " + str(row[12])
    return message
