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

printf "%b" "${OKB}Compiling ${OKG}$SRC_PATH${OKB} into ${OKG}$BUILD_PATH${NC}\n"
arduino-cli compile -v --warnings "all" \
	--libraries "$PWD"/"$LD_PATH" \
	--fqbn "$FBQN" "$SRC_PATH" \
	--output-dir "$BUILD_PATH"
printf "%b" "${OKG} ✓ ${NC} complete\n"
