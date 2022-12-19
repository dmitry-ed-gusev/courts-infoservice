#!/usr/bin/env bash

###############################################################################
#
#   Build and test for Courts Info Service [web-ui] module.
#
#   Script can be run from outside of virtual (pipenv) environment (from the
#   system shell) and from the pipenv environment as well (pipenv shell).
#
#   Created:  Dmitrii Gusev, 29.11.2022
#   Modified: Dmitrii Gusev, 18.12.2022
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
SITE_NAME="courtsinfo"

clear
printf "Building Courts Info Service Web UI...\n"
sleep 2

# -- clean build and distribution folders
printf "\nClearing temporary directories.\n"
printf "\nDeleting [%s]...\n" ${BUILD_DIR}
rm -r ${BUILD_DIR} || printf "%s doesn't exist!\n" ${BUILD_DIR}
printf "\nDeleting [%s]...\n" ${DIST_DIR}
rm -r ${DIST_DIR} || printf "%s doesn't exist!\n" ${DIST_DIR}

# -- create build folder
printf "\nCreating folder [%s%s]...\n" ${BUILD_DIR} ${SITE_NAME}
mkdir ${BUILD_DIR} || printf "Can't create %s folder!\n" ${BUILD_DIR}
mkdir ${BUILD_DIR}${SITE_NAME} || printf "Can't create %s%s folder!\n" ${BUILD_DIR} ${SITE_NAME}

# -- copy web site modules and files to build dir
cp -a courts "${BUILD_DIR}${SITE_NAME}"
cp -a courtsinfo "${BUILD_DIR}${SITE_NAME}"
cp -a home "${BUILD_DIR}${SITE_NAME}"
cp -a logs "${BUILD_DIR}${SITE_NAME}"
cp -a scripts "${BUILD_DIR}${SITE_NAME}"
cp -a stats "${BUILD_DIR}${SITE_NAME}"
cp manage.py "${BUILD_DIR}${SITE_NAME}"
cp requirements.txt "${BUILD_DIR}${SITE_NAME}"
# -- copy env configuration file for PROD (if exists)
cp .env.prod "${BUILD_DIR}${SITE_NAME}" || printf "File [.env.prod] doesn't exist or can't copy!"

# generating new [requirements.txt] - we need it for hosting
printf "\nGenerating [requirements.txt] file\n"
pipenv requirements > requirements.txt

# -- clean caches and sync + lock pipenv dependencies (update from the file Pipfile.lock)
# printf "\nCleaning pipenv cache and update dependencies.\n"
# pipenv clean ${VERBOSE}
# pipenv update --outdated ${VERBOSE}
# pipenv update ${VERBOSE}

# -- run pytest with pytest-cov (see pytest.ini/setup.cfg - additional parameters)
# printf "\nExecuting tests.\n"
# pipenv run pytest tests/

# -- run black code formatter
# todo: black formats code without any notification, do we need it?
# printf "\n\n"
# pipenv run black src/ --verbose --line-length 110
# pipenv run black tests/ --verbose --line-length 110

# -- run mypy - types checker
# printf "\nExecuting mypy.\n"
# pipenv run mypy src/
# pipenv run mypy tests/

# -- run flake8 for checking code formatting
# printf "\nExecuting flake8.\n"
# pipenv run flake8 --output-file .reports/flake8.report --count --show-source src/
# pipenv run flake8 --output-file .reports/flake8.report --count --show-source tests/

printf "\nBuild finished.\n\n"
