#!/bin/bash

source .env

trap 'handler $? $LINENO' ERR

function handler() {
    if [ "$1" != "0" ]; then
        printf "%b" "${FAIL} ✗ ${NC} ${0##*/} failed on line $2 with status code $1\n"
        exit "$1"
    fi
}

printf "%b" "${OKB}Cleaning build artefacts: ${OKG}$BUILD_PATH${NC}\n";
rm -rfv "$BUILD_PATH"
printf "%b" "${OKG} ✓ ${NC} complete\n"