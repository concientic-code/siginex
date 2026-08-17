ARTIFACT ?= siginex-autodiagnostico-500.html

.PHONY: kb evals migrate up down demo

kb:            ## Genera kb.json y kb-version.json desde el artefacto
	python3 siginex_kb_export.py $(ARTIFACT)

evals:         ## Corre la batería de evals (compuerta 8/8)
	python3 siginex_evals.py $(ARTIFACT)

demo:          ## Ejecuta el orquestador de referencia
	python3 siginex_orchestrator.py $(ARTIFACT)

migrate:       ## Aplica el DDL a la base de datos ($$DATABASE_URL)
	psql "$(DATABASE_URL)" -f siginex-schema.sql

up: kb         ## Levanta base de datos + API con Docker Compose
	docker compose up -d --build

down:          ## Detiene los servicios
	docker compose down
