# Makefile for Arduino Interfacing
# ================================
# Make file for linting, compiling, flashing and interfacing with the arduino serial monitor
# 
# Modified: 2020-11
# Copyright 2020 Christian Sargusingh

OKGREEN=\033[92m
# WARNING=\033[93m
# FAIL=\033[91m
OKBLUE=\033[94m
UNDERLINE=\033[4m
NC=\033[0m

# User Env flags
INCLUDE_DIR=include 	# include files
SRC_DIR=src 			# src files 
BUILD_DIR=src/build/	# build directory
CORE=arduino:avr:uno	# build core (ref arduino-cli)
LINT_EXT=ino,h,cpp
# scrape serial port from /dev
# TODO: scrape using `arduino-cli board list` (requires FBQN resolvers)
TTY := $$(ls /dev/tty.usbserial*)
kill_serial := $$(kill -9 $$(lsof ${TTY} | awk 'NR>1 {print $$2}'))

.PHONY: help	
help:
	@echo Usage:
	@echo "  make [target]"
	@echo
	@echo Targets:
	@awk -F ':|##' \
		'/^[^\t].+?:.*?##/ {\
			printf "  %-30s %s\n", $$1, $$NF \
		 }' $(MAKEFILE_LIST)

.PHONY: all
all: lint compile flash

.PHONY: setup
setup: ## configure arduino-cli and install cpplinter
	@arduino-cli config init;
	@arduino-cli core update-index;
	@arduino-cli core install arduino:avr;
	@arduino-cli core upgrade;
	@arduino-cli core list;
	@arduino-cli board listall;
	@python3 -m pip install cpplint

.PHONY: lint
lint: ## lint with cpplint for Google cpp guidelines and code styling
	@printf "${OKBLUE}Linting filesystems ... \n\tExtensions:\t${OKGREEN}${LINT_EXT} \n${OKBLUE}\
		Source dir:\t${OKGREEN}${SRC_DIR}\n\t${OKBLUE}Include dir:\t${OKGREEN}${INCLUDE_DIR}${NC}\n"
	@cpplint --recursive --extensions=${LINT_EXT} ${SRC_DIR} ${INCLUDE_DIR}
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: compile
compile: ## build arduino artefacts
	@printf "${OKBLUE}Compiling .ino into ${BUILD_DIR}${NC}\n"
	@arduino-cli compile --fqbn ${CORE} ${SRC_DIR}
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: flash
flash: ## flash arduino build artefacts to board
	@printf "${OKBLUE}Flashing ${BUILD_DIR}${CORE} to ${TTY}${NC}\n"
	@if [[ -n "$$(lsof ${TTY})" ]]; then \
		printf "${OKBLUE}Closing serial montior @ ${TTY}${NC}\n" \
		$(call kill_serial); fi;
	@arduino-cli upload -v -p ${TTY} --fqbn ${CORE} ${SRC_DIR};
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: clean
clean: ## clear build artefacts and close serial monitor
	@printf "${OKBLUE}Cleaning build artefacts: ${BUILD_DIR}${NC}\n";
	@rm -rfv ${BUILD_DIR};
	@if [[ -n "$$(lsof ${TTY})" ]]; then \
		printf "${OKBLUE}Closing serial montior @ ${TTY}${NC}\n" \
		$(call kill_serial); fi;
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: monitor
monitor: ## Open serial port using tty. Ctrl-a + d to exit screen
	@screen ${TTY}
	# to reconnnect to serial monitor: screen -r [pid.]tty.host