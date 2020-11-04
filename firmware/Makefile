OKGREEN=\033[92m
# WARNING=\033[93m
# FAIL=\033[91m
OKBLUE=\033[94m
UNDERLINE=\033[4m
NC=\033[0m

SRC_DIR=src
BUILD_DIR=src/build/
CORE=arduino:avr:uno
# scrape serial port from /dev
TTY=$$(ls /dev/tty.usbserial*)


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
all: compile flash

.PHONY: setup
setup:
	@arduino-cli config init;
	@arduino-cli core update-index;
	@arduino-cli core install arduino:avr;
	@arduino-cli core upgrade
	@arduino-cli core list;
	@arduino-cli board listall;

.PHONY: compile
compile:
	@printf "${OKBLUE}Compiling .ino into ${BUILD_DIR}${NC}\n"
	@arduino-cli compile --fqbn ${CORE} ${SRC_DIR}
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: flash
flash:
	@printf "${OKBLUE}Flashing ${BUILD_DIR}${CORE} to ${TTY}${NC}\n"
	@arduino-cli upload -v -p ${TTY} --fqbn ${CORE} ${SRC_DIR}
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: clean
clean:
	@printf "${OKBLUE}Cleaning build artefacts: ${BUILD_DIR}${NC}\n"
	@rm -rfv ${BUILD_DIR}
	@printf "${OKGREEN} ✓ ${NC} Complete\n"

.PHONY: monitor
monitor: ## ctrl-a + d to exit!
	@screen ${TTY}
	# screen -r [pid.]tty.host