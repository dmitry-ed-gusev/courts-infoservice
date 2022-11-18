#!/usr/bin/env bash

###############################################################################
#
#   Build [courts-telegram-bot] distributive (installable).
#   Distributive is put into folder [dist].
#
#   Created:  Dmitrii Gusev, 13.11.2022
#   Modified:
#
###############################################################################

# -- safe bash scripting - fail-fast pattern (google for more info)
set -euf -o pipefail

# -- set up encoding/language
export LANG="en_US.UTF-8"

# building docker image for telegram bot
docker build --no-cache -t courtsbot:latest .
