#!/usr/bin/env bash
###############################################################################
#
#   General python environment setup/reset script. Script can be used to 
#   re-create python general environment from 'scratch'.
#   Script installs basic libraries:
#       - pipenv
#       - jupyter
#       - pytest
#   Warning: script must be used (run) from shell, not from the virtual
#            environment (pipenv shell).
#
#   Created:  Dmitrii Gusev, 04.10.2022
#   Modified:
#
###############################################################################

# -- safe bash scripting
set -euf -o pipefail

# -- general setup - some variables
export LANG='en_US.UTF-8'
TMP_FILE="req.txt"

clear
printf "Python Development Environment setup is starting...\n\n"

# -- upgrading pip (just for the case)
pip --no-cache-dir install --upgrade pip
printf "\n\n ** upgrading pip - done **\n"

# -- freeze current global dependencies
pip freeze > ${TMP_FILE}
printf "\n\n ** freezing the current dependencies to the [%s] file - done **\n\n" ${TMP_FILE}

# -- remove all dependencies
pip uninstall -r ${TMP_FILE} -y
printf "\n\n ** uninstalling the current dependencies - done **\n"

# -- list the current empty environment
printf "\n\n--- The Current Empty Environment (no dependencies) ---\n\n"
pip list
sleep 5

# -- remove temporary file
rm ${TMP_FILE}
printf "\n\n ** removing tmp file %s - done **\n\n" ${TMP_FILE}

# -- install necessary dependencies
pip --no-cache-dir install pipenv pytest jupyter
printf "\n\n ** installing core dependencies - done **\n"

printf "\n\nPython Development Environment setup is done.\n\n\n"
