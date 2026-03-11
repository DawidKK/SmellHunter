SHELL := /bin/bash

UV ?= uv
APP ?= smell-hunter
TARGET ?= ./frontend
MOCK_LOG ?= examples/mock_git_log.txt
DISTANCE ?= 0.85
MAX_FILES ?= 50
MIN_COCHANGE ?= 1
EXTRA_ARGS ?=

.PHONY: help install test test-verbose run run-mock run-mock-tight

help:
	@echo "SmellHunter commands"
	@echo ""
	@echo "make install        - Install/sync project dependencies"
	@echo "make test           - Run test suite"
	@echo "make test-verbose   - Run tests with verbose output"
	@echo "make run            - Analyze real git history (TARGET=./frontend)"
	@echo "make run-mock       - Analyze mocked history (MOCK_LOG=examples/mock_git_log.txt)"
	@echo "make run-mock-tight - Mocked run with stricter clustering (DISTANCE=0.4)"
	@echo ""
	@echo "Overridable vars: TARGET, MOCK_LOG, DISTANCE, MAX_FILES, MIN_COCHANGE, EXTRA_ARGS"
	@echo "Example: make run-mock TARGET=./src DISTANCE=0.7"

install:
	$(UV) sync

test:
	$(UV) run pytest

test-verbose:
	$(UV) run pytest -v

run:
	$(UV) run $(APP) analyze $(TARGET) \
		--distance-threshold $(DISTANCE) \
		--max-files-per-commit $(MAX_FILES) \
		--min-cochange $(MIN_COCHANGE) \
		$(EXTRA_ARGS)

run-mock:
	$(UV) run $(APP) analyze $(TARGET) \
		--mock-log-file $(MOCK_LOG) \
		--distance-threshold $(DISTANCE) \
		--max-files-per-commit $(MAX_FILES) \
		--min-cochange $(MIN_COCHANGE) \
		$(EXTRA_ARGS)

run-mock-tight:
	$(MAKE) run-mock DISTANCE=0.4
