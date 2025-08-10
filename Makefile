.PHONY: help build run test clean docker-build docker-run docker-stop install dev

help: ## Affiche cette aide
	@echo "Commandes disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installe les dépendances Python
	uv sync

dev: ## Lance l'application en mode développement
	uv run python main.py

test: ## Lance les tests
	uv run pytest tests/ -v

clean: ## Nettoie les fichiers temporaires
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

docker-build: ## Construit l'image Docker
	docker build -t ldvh-companion .

docker-run: ## Lance l'application avec Docker
	docker run -d --name ldvh-companion -p 8000:8000 ldvh-companion

docker-stop: ## Arrête l'application Docker
	docker stop ldvh-companion
	docker rm ldvh-companion

docker-compose-up: ## Lance l'application avec docker-compose
	docker-compose up -d

docker-compose-down: ## Arrête l'application docker-compose
	docker-compose down

docker-compose-logs: ## Affiche les logs docker-compose
	docker-compose logs -f

build: docker-build ## Alias pour docker-build

run: docker-compose-up ## Alias pour docker-compose-up

stop: docker-compose-down ## Alias pour docker-compose-down
