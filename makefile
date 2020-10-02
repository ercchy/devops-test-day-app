.PHONY: help

help: ## this Makefile help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

up: ## run all the containers in the docker compose configuration (in daemon mode)
	docker-compose up -d

down: ## shuts down all the containers
	docker-compose down -v

clean: ## shuts down all the containers, removes orphans cleans the persistance and PID
	docker-compose down -v --remove-orphans
	rm -rf persistance/postgres
	rm -rf persistance/redis
	rm -rf tmp/pids/*.pid

build: ## builds all the images
	docker-compose build

CMD_CLEAN := "make clean"
CMD_RUN_SCRIPT := ""
stop_climate_change: ## reinstalls environment and fixes the temperature (20 deg - 1)
	python stop_climate_change.py
