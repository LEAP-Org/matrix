#!/bin/bash

# shellcheck disable=SC1091
source .env

trap 'handler $? $LINENO' ERR

function handler() {
    if [ "$1" != "0" ]; then
        printf "%b" "${FAIL} ✗ ${NC} ${0##*/} failed on line $2 with status code $1\n"
        exit "$1"
    fi
}

printf "%b" "${OKB}Linting extensions: ${OKG}$LINT_EXT${OKB} in ${OKG}$SRC_PATH${OKB} and ${OKG}$LD_PATH${NC}\n"
cpplint --recursive "$SRC_PATH" "$LD_PATH"
printf "%b" "${OKG} ✓ ${NC} complete\n"