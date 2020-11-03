
SRC_DIR=src
BUILD_DIR=src/build
CORE=arduino:avr:uno

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
	@arduino-cli core list;
	@arduino-cli board listall;

.PHONY: compile
compile:
	@arduino-cli compile --fqbn ${CORE} ${SRC_DIR}

.PHONY: flash
flash:
	@arduino-cli upload -v -p /dev/tty.usbserial-A6024AOD --fqbn ${CORE} ${SRC_DIR}

.PHONY: clean
clean:
	@rm -rfv ${BUILD_DIR}