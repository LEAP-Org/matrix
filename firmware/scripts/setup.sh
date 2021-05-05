#!/bin/bash

# shellcheck disable=SC1091
source .env

trap 'handler $? $LINENO' ERR

function handler() {
    if [ "$1" != "0" ]; then
        printf "%b" "${FAIL} ✗ ${NC} ${0##*/} init failed on line $2 with status code $1\n"
        exit "$1"
    fi
}

# configure arduino-cli
arduino-cli config init
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli core upgrade
# install cpp linter
python3 -m pip install cpplint
printf "%b" "${OKG} ✓ ${NC} complete\n"