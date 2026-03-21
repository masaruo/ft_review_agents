.PHONY: build run test clean

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
