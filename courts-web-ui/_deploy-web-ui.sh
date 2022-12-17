#!/usr/bin/env bash

###############################################################################
#
#   Deploy script for the Courts Info Service [web-ui] module. Performs
#   deploy to the hosting [REG.RU].
#
#   This script cotains also some useful ssh/scp commands (commented) - read
#   the file contents itself.
#
#   Script can be run from outside of virtual (pipenv) environment (from the
#   system shell) and from the pipenv environment as well (pipenv shell).
#
#   Created:  Dmitrii Gusev, 11.12.2022
#   Modified:
#
###############################################################################

# -- safe bash scripting - fail-fast pattern (google for more info)
set -euf -o pipefail

# -- set up encoding/language
export LANG="en_US.UTF-8"

# -- build directories
BUILD_DIR='build/'
DIST_DIR='dist/'

# -- remote paths
# - current tmp site path (on the itech-lab.ru)
SITE_PATH="/var/www/u1747464/data/www/courts.itech-lab.ru/"
# - main path for site (courtsinfo.ru)
# SITE_PATH="/var/www/u1747464/data/www/courtsinfo.ru"

clear
printf "Deployment the Courts Info Service Web UI to the remote host...\n"
sleep 2

# - copy file [passenger_wsgi.py] from hosting to the local dir
# scp u1747464@31.31.196.3:~/www/courts.itech-lab.ru/passenger_wsgi.py .

# - execute [ls] command on the remote host
# ssh u1747464@31.31.196.3 "ls -al ~/www/courts.itech-lab.ru"
