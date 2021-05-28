# Makefile for Arduino Interfacing
# ================================
# Makefile for linting, compiling, flashing larger scale ardunio projects and
# interfacing with the arduino serial monitor
# 
# Modified: 2021-04
# Copyright © 2021 Christian Sargusingh

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
all: lint compile flash monitor

.PHONY: setup
setup: ## configure arduino-cli and install cpplinter
	@./scripts/setup.sh

.PHONY: lint
lint: ## lint with cpplint (Google standards)
	@./scripts/lint.sh

.PHONY: compile
compile: ## compile source code and save artefactsto the build directory
	@./scripts/compile.sh

.PHONY: flash
flash: ## flash arduino build artefacts to board
	@./scripts/flash.sh

.PHONY: clean
clean: ## wipe build artefacts
	@./scripts/clean.sh

.PHONY: monitor
monitor: ## Stream plaintext from arduino serial monitor
	@./scripts/monitor.sh