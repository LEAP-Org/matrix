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

printf "%b" "${OKB}Flashing ${OKG}$BUILD_PATH${OKB} to ${OKG}$TTY${NC}\n"
arduino-cli upload -v -p "$TTY" --fqbn "$FBQN" "$SRC_PATH" --input-dir "$BUILD_PATH"
printf "%b" "${OKG} ✓ ${NC} complete\n"