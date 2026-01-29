.PHONY: all build clean install test help

# Variables
PYTHON := python3
CARGO := cargo
MAKE_C := make

# Colors for output
GREEN := \033[0;32m
BLUE := \033[0;34m
YELLOW := \033[0;33m
NC := \033[0m # No Color

all: build

help:
	@echo "$(BLUE)SysGuard Build System$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@echo "  $(YELLOW)build$(NC)      - Build all native components (Rust + C + web server)"
	@echo "  $(YELLOW)clean$(NC)      - Clean all build artifacts"
	@echo "  $(YELLOW)install$(NC)    - Install Python dependencies"
	@echo "  $(YELLOW)test$(NC)       - Run tests (if available)"
	@echo "  $(YELLOW)run$(NC)        - Run the CLI (status command)"
	@echo "  $(YELLOW)run-web$(NC)    - Start the native web server"
	@echo "  $(YELLOW)dev$(NC)        - Install dev dependencies"
	@echo "  $(YELLOW)format$(NC)     - Format Python code with black"
	@echo "  $(YELLOW)lint$(NC)       - Lint Python code"
	@echo ""

build:
	@echo "$(GREEN)[1/3] Building Rust monitoring backend...$(NC)"
	cd monitor/native/rust && $(CARGO) build --release
	@echo "$(GREEN)[2/3] Building C process monitor...$(NC)"
	cd monitor/native/c && $(MAKE_C)
	@echo "$(GREEN)[3/3] Building native web server...$(NC)"
	cd api/native && $(MAKE_C)
	@echo "$(GREEN)✓ Build complete!$(NC)"

clean:
	@echo "$(YELLOW)Cleaning build artifacts...$(NC)"
	cd monitor/native/rust && $(CARGO) clean || true
	cd monitor/native/c && $(MAKE_C) clean || true
	cd api/native && $(MAKE_C) clean || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -f storage/*.db 2>/dev/null || true
	@echo "$(GREEN)✓ Clean complete!$(NC)"

install:
	@echo "$(GREEN)Installing Python dependencies...$(NC)"
	$(PYTHON) -m pip install -r requirements/requirements.txt
	@echo "$(GREEN)✓ Dependencies installed!$(NC)"

dev:
	@echo "$(GREEN)Installing development dependencies...$(NC)"
	$(PYTHON) -m pip install -r requirements/requirements-dev.txt 2>/dev/null || \
		$(PYTHON) -m pip install pytest black mypy pylint
	@echo "$(GREEN)✓ Dev dependencies installed!$(NC)"

test:
	@echo "$(BLUE)Running tests...$(NC)"
	@if [ -d "tests" ]; then \
		$(PYTHON) -m pytest tests/ -v; \
	else \
		echo "$(YELLOW)No tests directory found$(NC)"; \
	fi

run:
	@echo "$(BLUE)Running SysGuard status...$(NC)"
	$(PYTHON) run.py status

run-web:
	@echo "$(BLUE)Starting native web server...$(NC)"
	@if [ -f "api/native/webserver" ]; then \
		$(PYTHON) api/server.py; \
	else \
		echo "$(YELLOW)Web server not built. Run 'make build' first.$(NC)"; \
	fi

format:
	@echo "$(BLUE)Formatting Python code...$(NC)"
	black . --exclude '/(\.git|\.venv|venv|build|dist)/'

lint:
	@echo "$(BLUE)Linting Python code...$(NC)"
	pylint **/*.py --disable=all --enable=E,F || true
	mypy . --ignore-missing-imports || true

.DEFAULT_GOAL := help
