.PHONY: help

help: ## this Makefile help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

up: ## build and run all the containers in the docker compose configuration (in daemon mode)
	docker-compose up -d

down: ## shuts down all the ontainers
	docker-compose down -v˚

clean: ## shuts down all the containers and removes orphans
	docker-compose down -v --remove-orphans

build: ## builds all the images
	docker-compose build