#!/usr/bin/env bash
###############################################################################
#
#   Development environment setup script. Script can be used to re-create
#   development environment from 'scratch'.
#
#   Warning: script must be used (run) from shell, not from the virtual
#            environment (pipenv shell).
#
#   Created:  Dmitrii Gusev, 04.10.2022
#   Modified: Dmitrii Gusev, 17.12.2022
#
###############################################################################

# -- safe bash scripting
set -euf -o pipefail

# -- project modules directories
SCRAPER_DIR='courts-scraper'
BOT_DIR='courts-tele-bot'
WEBUI_DIR='courts-web-ui'

# -- verbose output mode
VERBOSE="--verbose"
# -- set up encoding/language
export LANG='en_US.UTF-8'
# -- build and distribution directories
BUILD_DIR='build/'
DIST_DIR='dist/'
# -- local ipykernel name
# IPYKERNEL_NAME='courts-infoservice-ipkernel'

setup_virtual_env() {
    # -- upgrade pip
    printf "\nUpgrading pip.\n"
    pip --no-cache-dir install --upgrade pip

    # -- upgrading pipenv (just for the case)
    printf "\nUpgrading pipenv.\n"
    pip --no-cache-dir install --upgrade pipenv

    # -- remove existing virtual environment, clear caches
    printf "\nDeleting virtual environment and clearing caches.\n"
    pipenv --rm ${VERBOSE} || printf "No virtual environment found for the project!\n"
    pipenv --clear ${VERBOSE}

    # -- clean build and distribution folders
    printf "\nClearing temporary directories.\n"
    printf "\nDeleting [%s]...\n" ${BUILD_DIR}
    rm -r ${BUILD_DIR} || printf "%s doesn't exist!\n" ${BUILD_DIR}
    printf "\nDeleting [%s]...\n" ${BUILD_DIR}
    rm -r ${DIST_DIR} || printf "%s doesn't exist!\n" ${DIST_DIR}

    # -- removing Pipfile.lock (re-generate it)
    printf "\nRemoving Pipfile.lock\n"
    rm Pipfile.lock || printf "Pipfile.lock doesn't exist!\n"

    # -- install all dependencies, incl. development
    printf "\nInstalling dependencies, updating all + outdated.\n"
    pipenv install --dev ${VERBOSE}

    # todo: do we need the local jupyter kernel for modules?
    # -- install local ipykernel
    # printf "\nInstalling local ipykernel + check\n"
    # pipenv run ipython kernel install --user --name=${IPYKERNEL_NAME}
    # -- list installed ipykernels
    # jupyter kernelspec list
    # sleep 5

    # - check for vulnerabilities and show dependencies graph
    printf "\nChecking virtual environment for vulnerabilities.\n"
    pipenv check || printf "There are some issues, check logs...\n"
    pipenv graph

    # - outdated packages report
    printf "\n\nOutdated packages list (pip list):\n"
    pipenv run pip list --outdated
}

# -- main script part
clear
printf "Development Virtual Environment setup is starting...\n"
printf "We are here: [%s]\n" "$(pwd)"
sleep 2

# todo: implement list of dirs/modules and iterating/processing over it

# -- go to the Telegram Bot directory
clear
cd ${BOT_DIR}
printf "\nProcessing Telegram Bot\n"
printf "We are here: [%s]\n" "$(pwd)"
sleep 2
setup_virtual_env
cd ..

# -- go to the Scraper/Parser directory
clear
cd ${SCRAPER_DIR}
printf "\nProcessing Scraper\n"
printf "We are here: [%s]\n" "$(pwd)"
sleep 2
setup_virtual_env
cd ..

# -- go to the Scraper/Parser directory
clear
cd ${WEBUI_DIR}
printf "\nProcessing Web UI\n"
printf "We are here: [%s]\n" "$(pwd)"
sleep 2
setup_virtual_env
# additional for Web UI - generate [requirements.txt] - for hosting
printf "\nGenerating [requirements.txt] file\n"
pipenv requirements > requirements.txt
cd ..

# -- we returned to the root project directory
printf "\nReturned to the project root: [%s]\n\n" "$(pwd)"
