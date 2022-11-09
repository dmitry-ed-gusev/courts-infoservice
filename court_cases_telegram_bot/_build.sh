#!/usr/bin/env bash

###############################################################################
#
#   Build and test for [courts-telegram-bot] project.
#
#   Script can be run from outside of virtual (pipenv) environment (from the
#   system shell) and from the pipenv environment as well (pipenv shell).
#
#   Created:  Dmitrii Gusev, 05.11.2022
#   Modified: Dmitrii Gusev, 10.11.2022
#
###############################################################################

# -- safe bash scripting - fail-fast pattern (google for more info)
set -euf -o pipefail

# -- verbose output mode
VERBOSE="--verbose"
# -- set up encoding/language
export LANG="en_US.UTF-8"
# -- build directories
BUILD_DIR='build/'
DIST_DIR='dist/'

clear
printf "Building Courts Infoservice Telegram Bot...\n"
sleep 2

# -- clean build and distribution folders
printf "\nClearing temporary directories.\n"
printf "\nDeleting [%s]...\n" ${BUILD_DIR}
rm -r ${BUILD_DIR} || printf "%s doesn't exist!\n" ${BUILD_DIR}
printf "\nDeleting [%s]...\n" ${BUILD_DIR}
rm -r ${DIST_DIR} || printf "%s doesn't exist!\n" ${DIST_DIR}

# -- clean caches and sync + lock pipenv dependencies (update from the file Pipfile.lock)
printf "\nCleaning pipenv cache and update dependencies.\n"
pipenv clean ${VERBOSE}
# todo: we can use key --outdated - ?
pipenv update ${VERBOSE}

# -- run pytest with pytest-cov (see pytest.ini/setup.cfg - additional parameters)
# printf "\nExecuting tests.\n"
# pipenv run pytest tests/

# -- run mypy - types checker
# printf "\nExecuting mypy.\n"
# pipenv run mypy src/
# pipenv run mypy tests/

# -- run black code formatter
# todo: black formats code without any notification, do we need it?
# printf "\n\n"
# pipenv run black src/ --verbose --line-length 110
# pipenv run black tests/ --verbose --line-length 110

# -- run flake8 for checking code formatting
# printf "\nExecuting flake8.\n"
# pipenv run flake8 --output-file .reports/flake8.report --count --show-source src/
# pipenv run flake8 --output-file .reports/flake8.report --count --show-source tests/

# -- build two distributions: binary (whl) and source (tar.gz)
printf "\nBuilding distribution for Telegram Bot.\n"
pipenv run python -m build

printf "\nBuild finished.\n"
