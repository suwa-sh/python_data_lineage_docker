.PHONY: build run stop clean help

# Docker image name
IMAGE_NAME := ghcr.io/suwa-sh/python_data_lineage_docker

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker image
	docker build -t $(IMAGE_NAME) .

run: ## Run Docker container with HTTP server
	docker run -d --name $(IMAGE_NAME)-server -p 8080:8000 -v $$(pwd):/app $(IMAGE_NAME) serve

stop: ## Stop and remove Docker container
	docker stop $(IMAGE_NAME)-server || true
	docker rm $(IMAGE_NAME)-server || true

clean: stop ## Clean up Docker image and container
	docker rmi $(IMAGE_NAME) || true

shell: ## Run interactive shell in Docker container
	docker run -it --rm -v $$(pwd):/app $(IMAGE_NAME) /bin/bash

dlineage: ## Run dlineage.py in Docker (usage: make dlineage ARGS="/f sample.sql /t oracle /graph")
	docker run --rm -v $$(pwd):/app $(IMAGE_NAME) $(ARGS)

analyze_delete: ## Run analyze_delete.py in Docker (usage: make analyze_delete ARGS="input.sql --output output/")
	docker run --rm -v $$(pwd):/app $(IMAGE_NAME) analyze_delete $(ARGS)

bulk_dlineage: ## Run bulk_dlineage.py in Docker (usage: make bulk_dlineage ARGS="/path/to/dirs /t oracle")
	docker run --rm -v $$(pwd):/app $(IMAGE_NAME) bulk_dlineage $(ARGS)

split: ## Run split.py in Docker (usage: make split ARGS="input.sql output/")
	docker run --rm -v $$(pwd):/app $(IMAGE_NAME) split $(ARGS)