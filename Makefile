.PHONY: help build run test clean

.DEFAULT_GOAL := help

IMAGE_NAME = 42-review-agent
TARGET_DIR ?= $(PWD)
FILE_TYPE ?= .py
PROJECT ?=

ENV_FILE := $(wildcard .env)
ENV_FLAG := $(if $(ENV_FILE),--env-file .env,)

# Build the Docker container
build:
	docker build -t $(IMAGE_NAME) .

# Run the reviewer inside the container, mounting the target directory
run:
	docker run --rm -it \
		-v "$(TARGET_DIR):/workspace" \
		$(ENV_FLAG) \
		-e OLLAMA_HOST=$(OLLAMA_HOST) \
		-e OPENAI_API_KEY=$(OPENAI_API_KEY) \
		$(IMAGE_NAME) --path /workspace --type $(FILE_TYPE) --project "$(PROJECT)"

# Run tests locally via uv
test:
	uv run pytest tests/

# Clean local environment
clean:
	rm -rf .venv
	rm -rf uv.lock
	rm -rf __pycache__
	rm -rf .pytest_cache

# Show help menu
help:
	@echo "Usage:"
	@echo "  make build    - Build the Docker image ($(IMAGE_NAME))"
	@echo "  make run      - Run the agent against TARGET_DIR (default: current directory)"
	@echo "                  Options: TARGET_DIR=/path/to/project FILE_TYPE=\".c .h\" PROJECT=\"ft_irc\""
	@echo "  make test     - Run tests locally using uv and pytest"
	@echo "  make clean    - Remove local python caches and virtual environment"
	@echo "  make help     - Show this help message"
