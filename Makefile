# Raccourcis du projet (TP1 à TP5). Linux, macOS et Git Bash ; sous Windows, lancez les
# commandes directement ou utilisez PowerShell.

.PHONY: help setup check test test-cadrage test-env test-git test-api test-cov verif clean exemple-ml exemple-ui api ui lint mypy

help:
	@echo "Cibles disponibles :"
	@echo "  make setup        installe le venv et les dependances, puis diagnostique"
	@echo "  make check        lance le diagnostic lisible"
	@echo "  make test         lance la suite complete de tests (97 tests)"
	@echo "  make test-cadrage lance les 12 tests des fiches (TP1)"
	@echo "  make test-env     lance les 23 tests d'environnement (TP1)"
	@echo "  make test-git     lance les 3 tests d'historique Git (TP1)"
	@echo "  make test-api     lance les tests de l'API FastAPI"
	@echo "  make test-cov     mesure la couverture de tests de l'API"
	@echo "  make lint         verifie le code avec ruff"
	@echo "  make mypy         verifie les types statiques avec mypy"
	@echo "  make api          demarre le serveur API FastAPI (port 8000)"
	@echo "  make ui           demarre l'interface Streamlit (port 8501)"
	@echo "  make verif URL=<url>  rejoue le test de l'enseignant sur un clone frais"
	@echo "  make clean        supprime les caches (garde le venv)"

setup:
	bash scripts/setup.sh

check:
	.venv/bin/python scripts/check_setup.py

test:
	.venv/bin/python -m pytest -q

test-cadrage:
	.venv/bin/python -m pytest tests/test_cadrage.py -q

test-env:
	.venv/bin/python -m pytest tests/test_environment.py -q

test-git:
	.venv/bin/python -m pytest tests/test_git_history.py -q

test-api:
	.venv/bin/python -m pytest tests/test_api.py tests/test_schemas.py tests/test_integration.py -q

test-cov:
	.venv/bin/python -m pytest --cov=api --cov-fail-under=95

lint:
	.venv/bin/ruff check .

mypy:
	.venv/bin/mypy api ui

api:
	.venv/bin/uvicorn api.main:app --reload --port 8000

ui:
	.venv/bin/streamlit run ui/app.py

verif:
	@test -n "$(URL)" || (echo "Usage : make verif URL=https://github.com/<org>/sentiment-app.git"; exit 2)
	bash scripts/verif_clone.sh $(URL)

clean:
	rm -rf .pytest_cache
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
