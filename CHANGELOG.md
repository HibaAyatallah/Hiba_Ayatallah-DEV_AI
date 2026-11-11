# Journal des versions

Le numéro de version suit les TP : 0.N.0 à la fin du TP N. Chaque version publiée porte une étiquette Git `v0.N.0`.

## 0.6.0 (TP6) : le paquet

- **Pour celui qui installe** : le dépôt devient un paquet Python standard installable via une roue (`sentiment_app-0.6.0-py3-none-any.whl`). Il fournit la commande CLI `sentiment` (`--version`, `predict`, `serve`, `ui`), capable de fonctionner hors du dépôt avec le modèle configuré via `SENTIMENT_MODELE`.
- **Pour celui qui développe** : `predict.py` est déplacé dans le paquet `sentiment_app/` avec un pont de compatibilité transparent conservé dans `src/predict.py`. L'API `api/model.py` s'affranchit de toute manipulation de `sys.path` au profit d'un import de paquet direct `from sentiment_app.predict import ...`. Le paquet est installable en mode éditable (`pip install -e .`).
- **Pour la CI** : scikit-learn est épinglé (`scikit-learn==1.5.*`) pour assurer la cohérence binaire du modèle sérialisé, et une nouvelle étape construit la roue puis valide son installation et son exécution dans un environnement virtuel étanche.

## 0.5.0 (TP5) : l'interface

- Page Streamlit : un avis, ou un fichier d'avis ; le client HTTP traduit chaque réponse de l'API.

## 0.4.0 (TP4) : tests et qualité

- Contrat d'entrée testé, abstention `INDETERMINE`, jeu d'or, tests d'intégration, contrat typé, ruff, mypy, pre-commit.

## 0.3.0 (TP3) : l'API

- FastAPI : `/health`, `/predict`, contrat Pydantic ; la CI entraîne le modèle avant les tests.

## 0.2.0 (TP2) : le modèle

- TF-IDF et régression logistique ; les métriques sont versionnées, le modèle ne l'est pas.

## 0.1.0 (TP1) : le cadrage

- Environnement Python 3.11, structure du dépôt, trois fiches de cadrage, dépôt GitHub à deux auteurs.
