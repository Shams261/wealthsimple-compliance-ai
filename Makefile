.PHONY: test eval run docker docker-run lint clean install help deploy

# ──────────────────────────────────────────────────────────────
# Wealthsimple Compliance AI — Makefile
# ──────────────────────────────────────────────────────────────

PYTHON   ?= python
PIP      ?= pip
PYTEST   ?= pytest
PORT     ?= 8000
IMG_NAME ?= compliance-ai

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install Python dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install pytest httpx

test: ## Run pytest test suite (91 tests)
	$(PYTEST) tests/ -v --tb=short

eval: ## Run the 70-case eval harness
	$(PYTHON) -m eval.run_eval

run: ## Start the development server
	$(PYTHON) backend/server.py

docker: ## Build the Docker image
	docker build -t $(IMG_NAME) .

docker-run: docker ## Build and run in Docker
	docker run --rm -p $(PORT):8000 \
		--env-file .env \
		$(IMG_NAME)

lint: ## Run basic Python linting (syntax check)
	$(PYTHON) -m py_compile backend/analyzer.py
	$(PYTHON) -m py_compile backend/server.py
	$(PYTHON) -m py_compile backend/storage.py
	$(PYTHON) -m py_compile backend/models.py
	@echo "✓ All files compile cleanly"

clean: ## Remove caches and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f eval_results.json
	rm -f data/compliance.db
	rm -f data/llm_cache.json
	@echo "✓ Cleaned"

deploy: ## Deploy to Railway (push to GitHub first)
	@echo "\033[36m── Deployment Guide ──\033[0m"
	@echo "1. Push code to GitHub:  git push origin main"
	@echo "2. Go to https://railway.app → New Project → Deploy from GitHub"
	@echo "3. Railway auto-detects Dockerfile and sets PORT"
	@echo "4. Add env vars in Railway dashboard: OPENROUTER_API_KEY, ALLOWED_ORIGINS"
	@echo "5. Set ALLOWED_ORIGINS to your Railway URL"
	@echo ""
	@echo "Or deploy with Railway CLI:"
	@echo "  brew install railway && railway login && railway up"
