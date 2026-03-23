.PHONY: help build run test clean all

.DEFAULT_GOAL := help

all: help

# Build the Docker container using docker compose
build:
	docker compose --build

FILE_TYPE ?= .cpp .hpp
FOLDERS ?= 

# Run the reviewer inside the container using docker compose run
run:
	docker compose run --rm review_agent --type $(FILE_TYPE) $(if $(FOLDERS),--folders $(FOLDERS),)

# Run tests locally via uv
test:
	uv run pytest tests/

# Clean local environment
clean:
	rm -rf .venv
	rm -rf uv.lock
	rm -rf __pycache__
	rm -rf .pytest_cache
	docker compose down -v

# Show help menu
help:
	@echo "Usage:"
	@echo "  make build    - Build the Docker image using docker-compose"
	@echo "  make run      - Run the agent using docker-compose (reads from ./target/)"
	@echo "                  Options: FILE_TYPE=\".cpp .hpp\" FOLDERS=\"srcs includes\""
	@echo "  make test     - Run tests locally using uv and pytest"
	@echo "  make clean    - Remove local python caches, virtual env, and containers"
	@echo "  make help     - Show this help message"
