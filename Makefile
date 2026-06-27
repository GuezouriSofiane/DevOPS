# Variables
COMPOSE=docker compose

.PHONY: help start stop restart status logs clean check

help: ## Afficher l'aide et la liste des commandes
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

start: ## Lancer l'environnement en arrière-plan (build si nécessaire)
	$(COMPOSE) up -d --build

stop: ## Arrêter les conteneurs
	$(COMPOSE) down

restart: ## Redémarrer tous les services
	$(COMPOSE) down
	$(COMPOSE) up -d --build

status: ## Afficher l'état des conteneurs
	$(COMPOSE) ps

logs: ## Afficher les logs en temps réel
	$(COMPOSE) logs -f

check: ## Exécuter le script de supervision
	@chmod +x scripts/check.sh
	./scripts/check.sh

clean: ## Arrêter l'environnement et supprimer les volumes (remise à zéro de la DB)
	$(COMPOSE) down -v