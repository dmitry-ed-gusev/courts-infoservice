#!/usr/bin/env bash

###############################################################################
#
#   Deploy script for the Courts Info Service [web-ui] module. Performs
#   deploy to the hosting [REG.RU]. Uses scp to copy files.
#
#   Script can be run from outside of virtual (pipenv) environment (from the
#   system shell) and from the pipenv environment as well (pipenv shell).
#
#   WARNINGS!
#       - as script uses scp - content of the target files is overwritten
#
#   Created:  Dmitrii Gusev, 11.12.2022
#   Modified: Dmitrii Gusev, 18.12.2022
#
###############################################################################

# -- safe bash scripting - fail-fast pattern (google for more info)
set -euf -o pipefail

# -- set up encoding/language
export LANG="en_US.UTF-8"

# -- build directories
# todo: should we use DIST dir instead of BUILD dir?
BUILD_DIR='build'
# DIST_DIR='dist'

# -- remote connection settings
HOSTING_IP="31.31.196.3"
HOSTING_USER="u1747464"

# -- remote paths (on the hosting REG.RU)
HOME_DIR="/var/www/u1747464/data"
WWW_DIR="${HOME_DIR}/www"
# - this is the site ROOT directory
# SITE_DIR="${WWW_DIR}/courts.itech-lab.ru"
SITE_DIR="${WWW_DIR}/courtsinfo.ru"

# -- remote names (some names on the hosting)
SITE_NAME="courtsinfo"
REBOOT_FILE=".restart-app"
# VENV_NAME=".venv-courts"
VENV_NAME=".venv-courtsinfo"

# -- remote environment
# HOSTING_PYTHON_PATH="/opt/python/python-3.10.1/bin/python"

# -- call build script before deployment
source ./_build-web-ui.sh

clear
printf "Deployment the Courts Info Service Web UI to the remote host...\n"
sleep 2

# -- copy file [passenger_wsgi.py] from hosting to the local dir
printf "\nGet file [passenger_wsgi.py] from the hosting (back up).\n\n"
scp ${HOSTING_USER}@${HOSTING_IP}:${SITE_DIR}/passenger_wsgi.py ./.resources/

# -- copy the site to hosting dir
printf "\nDeploying Web UI to hosting (copy files).\n\n"
scp -r ${BUILD_DIR}/${SITE_NAME} ${HOSTING_USER}@${HOSTING_IP}:${SITE_DIR}

# -- run installation of the requirements on the remote host in virtual environment
printf "\nExecuting pip upgrade and dependencies installation on the remote host.\n\n"
ssh ${HOSTING_USER}@${HOSTING_IP} \
    "source ${HOME_DIR}/${VENV_NAME}/bin/activate; \
     pip install --upgrade pip; \
     pip install -r ${SITE_DIR}/${SITE_NAME}/requirements.txt"

# -- execute [collectstatic] command on the remote host
printf "\nExecuting [collectstatic] command.\n\n"
ssh ${HOSTING_USER}@${HOSTING_IP} \
    "source ${HOME_DIR}/${VENV_NAME}/bin/activate; \
     cd ${SITE_DIR}; \
     python ${SITE_DIR}/${SITE_NAME}/manage.py collectstatic --noinput;"

# -- create special marker-file for the reboot of the site
printf "\nCreate file [.restart-app] in order to request site reboot.\n"
ssh ${HOSTING_USER}@${HOSTING_IP} "touch ${SITE_DIR}/${REBOOT_FILE}"

# -- execute [ls] command on the remote host (just simple check)
# ssh u1747464@31.31.196.3 "ls -al ~/www/courts.itech-lab.ru"

printf "\nDeployment finished.\n\n"
