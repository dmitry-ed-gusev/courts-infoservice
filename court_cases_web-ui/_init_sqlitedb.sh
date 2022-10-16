#!/usr/bin/env bash
###############################################################################
#
#   Shell script for initializing local sqlite3 db with data from CSV files.
#
#   Warning: script can be used (run) from shell or from the virtual
#            environment (for ex., pipenv shell).
#
#   Created:  Dmitrii Gusev, 16.10.2022
#   Modified:
#
###############################################################################

# -- safe bash scripting
set -euf -o pipefail

# -- general setup
export LANG='en_US.UTF-8'

# -- sqlite db file and init script
SQLITE_DB_FILE='db.sqlite3'
SQLITE_SQL_INIT='sql/init_db.sql'
SQLITE_SQL_TMP_FILE='_tmp_.sql'

# -- table [courts] name and CSV data
SQLITE_TABLE_COURTS='dm_court_cases'
SQLITE_CSV_DATA_COURTS='csv/dm_court_cases.csv'

# -- table [statistics] name and CSV data
SQLITE_TABLE_STAT='dm_v_court_stats'
SQLITE_CSV_DATA_STAT='csv/dm_v_court_stats.csv'

clear
printf "Initializing local sqlite3 DB [%s]\n\n" ${SQLITE_DB_FILE}

# -- remove old sqlite3 db file
rm ${SQLITE_DB_FILE}
printf "\n ** remove sqlite3 DB file [%s] - done **\n" ${SQLITE_DB_FILE}

# -- create sqlite3 DB and execute SQL script for the DB structure initialization
# todo: we can use option I or II - ?
cat ${SQLITE_SQL_INIT} | sqlite3 ${SQLITE_DB_FILE}  # option I
# sqlite3 ${SQLITE_DB_FILE} ".read ${SQLITE_CSV_DATA_COURTS}"  # option II
printf "\n ** initializing db with script [%s] - done **\n" ${SQLITE_SQL_INIT}

# -- loading data from CSV into DB - [statistics] table
printf "\n ** loading data to table [%s] ** \n" ${SQLITE_TABLE_STAT}
tail -n +2 ${SQLITE_CSV_DATA_STAT} > ${SQLITE_SQL_TMP_FILE}  # rewrite file without first line (header)
printf "    *** tmp file [%s] created ***\n" ${SQLITE_SQL_TMP_FILE}
sqlite3 -csv ${SQLITE_DB_FILE} ".import ${SQLITE_SQL_TMP_FILE} ${SQLITE_TABLE_STAT}"  # load CSV file to DB
rm ${SQLITE_SQL_TMP_FILE}  # remove temporary file
printf " ** loading data from [%s] to table [%s] - done **\n" ${SQLITE_CSV_DATA_STAT} ${SQLITE_TABLE_STAT}

# -- loading data from CSV into DB - [courts] table
printf "\n ** loading data to table [%s] ** \n" ${SQLITE_TABLE_COURTS}
tail -n +2 ${SQLITE_CSV_DATA_COURTS} > ${SQLITE_SQL_TMP_FILE}  # rewrite file without first line (header)
printf "    *** tmp file [%s] created ***\n" ${SQLITE_SQL_TMP_FILE}
sqlite3 -csv ${SQLITE_DB_FILE} ".import ${SQLITE_SQL_TMP_FILE} ${SQLITE_TABLE_COURTS}"  # load CSV file to DB
rm ${SQLITE_SQL_TMP_FILE}  # remove temporary file
printf " ** loading data from [%s] to table [%s] - done **\n" \
    ${SQLITE_CSV_DATA_COURTS} ${SQLITE_TABLE_COURTS}

printf "\n\nLocal sqlite3 DB [%s] initialized.\n\n\n" ${SQLITE_DB_FILE}

# .import --csv --skip 1 --schema temp C:/work/somedata.csv tab1