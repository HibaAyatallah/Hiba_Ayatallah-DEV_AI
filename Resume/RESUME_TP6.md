# Compte rendu : Le packaging de l'application et la distribution autonome (TP6)

**Binôme :** Hiba Ayatallah ([@HibaAyatallah](https://github.com/HibaAyatallah)) et Manal Wassila ([@manalwassila](https://github.com/manalwassila))  
**Dépôt :** [https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila](https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila)  
**Date :** 28 octobre 2026  
**Module :** Développement et déploiement d'applications intelligentes — Pr. A. Larhlimi  

---

## 1. Introduction et Objectifs du TP6

Après avoir cadré l'application (TP1), entraîné et évalué le modèle (TP2), exposé une API REST FastAPI (TP3), blindé la robustesse et la qualité statique (TP4), puis développé une interface web interactive Streamlit (TP5), le **TP6 concrétise l'industrialisation logicielle du projet en le transformant en un paquet Python installable et distribuable**.

Les objectifs majeurs de cette étape de packaging sont :
1. **Création d'un paquet Python standardisé (`sentiment-app 0.6.0`) :** Définir les métadonnées, les points d'entrée et les dépendances du projet au standard moderne `pyproject.toml` (PEP 517/518/621).
2. **Fourniture d'une interface en ligne de commande unifiée (`sentiment`) :** Rendre l'application utilisable sans que l'opérateur n'ait à connaître les chemins internes des fichiers, offrant les sous-commandes `--version`, `predict`, `serve` et `ui`.
3. **Assainissement architectural des imports :** Supprimer définitivement les manipulations manuelles de `sys.path` dans `api/model.py` au profit d'imports propres depuis `sentiment_app.predict`.
4. **Découplage strict entre code et modèle via `SENTIMENT_MODELE` :** Exclure le modèle binaire `.joblib` de la distribution logicielle, et permettre son chargement dynamique depuis n'importe quel emplacement du système hôte.
5. **Génération d'une roue binaire universelle (`.whl`) :** Construire une archive pure Python (`sentiment_app-0.6.0-py3-none-any.whl`) contenant uniquement le code exécutable (`api/`, `sentiment_app/`, `ui/`), à l'exclusion stricte des tests, des jeux de données et des artefacts d'entraînement.
6. **Contrôle strict des dépendances (épinglage de scikit-learn) :** Épingler `scikit-learn>=1.5,<1.6` pour prévenir toute rupture de compatibilité binaire lors de la désérialisation du classifieur.
7. **Validation continue intégrale :** Porter la suite de tests à **101 tests passés et 2 xfailed** (103 tests au total), et enrichir le workflow GitHub Actions d'une étape de test en boîte noire étanche hors du dépôt.

---

## 2. Architecture du Paquet et Organisation des Fichiers

Le kit TP6 réorganise l'arborescence pour séparer nettement le paquet distribué, le code source historique, les tests et la configuration de build :

```text
sentiment-app/
├── pyproject.toml                  # Déclaration PEP 621 : build-system, dépendances, scripts CLI, packages
├── sentiment_app/                  # Le paquet Python officiel (versionné 0.6.0)
│   ├── __init__.py                 # Unique source de vérité pour __version__ = "0.6.0"
│   ├── __main__.py                 # Support de l'exécution module : python -m sentiment_app
│   ├── cli.py                      # Définition de la commande console sentiment (argparse)
│   └── predict.py                  # Inférence unitaire découplée, modèle configurable via SENTIMENT_MODELE
├── api/
│   ├── main.py                     # API FastAPI
│   ├── model.py                    # Raccord épuré : import direct depuis sentiment_app.predict
│   └── schemas.py                  # Contrats Pydantic v2
├── ui/                             # Interface Streamlit
│   ├── app.py
│   └── client.py
├── src/
│   ├── predict.py                  # Pont de compatibilité rétroactive (sys.modules[__name__] = _module)
│   ├── make_demo.py / train.py     # Scripts d'entraînement MLOps
│   └── evaluate.py / courbe_seuil.py
├── tests/
│   └── test_packaging.py          # 6 tests de validation du packaging
├── CHANGELOG.md                    # Historique sémantique des versions (0.1.0 à 0.6.0)
└── docs/
    ├── semaine6.md                 # Compte rendu technique argumenté
    └── journal-tp1-tp6.md          # Journal de bord complet (contrôles T0 à T41)
```

### 2.1 Synthèse des responsabilités des nouveaux composants

| Fichier / Dossier | Responsabilité | Ce qu'il garantit |
| :--- | :--- | :--- |
| **`sentiment_app/__init__.py`** | Déclare `__version__ = "0.6.0"`. | Centralise le numéro de version (Single Source of Truth). |
| **`sentiment_app/cli.py`** | Implémente la CLI `sentiment`. | Exécute prédiction, serveur FastAPI ou page Streamlit sans script intermédiaire. |
| **`sentiment_app/predict.py`** | Inférence unitaire & localisation du modèle. | Modèle configurable par la variable d'environnement `SENTIMENT_MODELE`. |
| **`src/predict.py`** | Module de compatibilité rétroactive. | Remplace son propre module dans `sys.modules` pour garder valides `import predict` et `monkeypatch`. |
| **`api/model.py`** | Raccord de l'API REST. | Élimine `sys.path.insert(0, ...)` et importe conventionnellement `sentiment_app.predict`. |
| **`pyproject.toml`** | Configuration de packaging setuptools. | Spécifie `packages = ["sentiment_app", "api", "ui"]` et associe la commande console `sentiment`. |

---

## 3. Déroulement Pas à Pas et Validation des Jalons (T35 à T41)

### Étape A — Installation du kit et contrôle de départ (T35)
- Application du kit via `appliquer_tp6.py`.
- Installation de l'outil standard de construction `build==1.2.2.post1` dans `requirements-dev.txt`.
- Exécution de `pytest -q` : **2 échecs voulus** constatant que `sentiment_app.predict` n'est pas encore créé et que `api/model.py` modifie encore `sys.path` (99 passed, 2 xfailed, 2 failed).

### Étape B — Migration de `predict.py` et configuration du modèle (T36)
- Déplacement de `src/predict.py` vers `sentiment_app/predict.py` via `git mv`, conservant l'historique Git complet depuis la semaine 2.
- Mise en place du module de compatibilité `src/predict.py` issu de `extraits/predict_compatibilite.py`.
- Implémentation de la fonction `chemin_modele()` dans `sentiment_app/predict.py` :
  ```python
  def chemin_modele() -> Path:
      return Path(os.environ.get("SENTIMENT_MODELE") or RACINE / "models" / "sentiment.joblib")
  ```
- Amélioration du message de `charger_modele()` guidant explicitement l'utilisateur en cas d'absence du modèle.
- Exécution de `pytest -q` : **1 seul échec restant** (`test_l_api_ne_bricole_plus_le_chemin_de_python`).
- Validation de l'inférence rétrocompatible : `python src/predict.py "..."` renvoie fidèlement `positive (confiance 78%)`.

### Étape C — Raccordement propre de l'API (T37)
- Nettoyage d'`api/model.py` : suppression de `sys.path.insert`, des imports `sys` et `Path`, et des directives `# noqa: E402`.
- Adoption d'imports directs :
  ```python
  from sentiment_app.predict import charger_modele
  from sentiment_app.predict import predict as _predict
  ```
- Validation :
  - `Select-String -Path api\*.py -Pattern "sys.path"` : aucun résultat.
  - `ruff check .` : `All checks passed!`.
  - `mypy api` : `Success: no issues found in 4 source files`.
  - `pytest -q` : **101 passed, 2 xfailed** (tous les tests passent).

### Étape D — Validation de la commande CLI `sentiment` (T38)
- Installation en mode éditable : `pip install -e .`.
- Vérification de version : `sentiment --version` affiche `sentiment-app 0.6.0`.
- Inférence unitaire franche : `sentiment predict "Livraison rapide..."` renvoie `{"label": "POSITIVE", "score": 0.777, ...}`.
- Inférence sous abstention : `sentiment predict "xqzvb wlkptr grombu"` renvoie `{"label": "INDETERMINE", "score": 0.5162, ...}` car la CLI applique le seuil d'abstention de 0.60 défini dans `api/model.py`.
- Démarrage du serveur : `sentiment serve --port 8000` démarre Uvicorn et `/health` répond `200 OK`.

### Étape E — Construction de la roue et validation étanche hors dépôt (T39 & T40)
- Nettoyage et compilation : `python -m build --wheel` produit l'archive `dist/sentiment_app-0.6.0-py3-none-any.whl`.
- Inspection de l'archive wheel : elle contient exclusivement `api`, `sentiment_app`, `ui` et les métadonnées `dist-info`. Les dossiers `tests/`, `data/`, `models/` et `src/` en sont totalement absents.
- Simulation d'un utilisateur externe dans `$env:TEMP\roue-tp6` :
  - `pip install sentiment_app-0.6.0-py3-none-any.whl` télécharge et installe automatiquement toutes les dépendances requises.
  - Exécution sans variable : l'appel échoue immédiatement avec le code 1 et le message explicatif `modèle introuvable : ...\site-packages\models\sentiment.joblib...`.
  - Exécution avec `$env:SENTIMENT_MODELE` : prédiction validée avec succès `{"label": "POSITIVE", "score": 0.777, ...}` et code de sortie 0.

### Étape F — Traçabilité, versioning et intégration continue (T41)
- Rédaction complète de la note de version dans `CHANGELOG.md`.
- Rédaction des réponses argumentées dans `docs/semaine6.md`.
- Finalisation du journal de bord complet dans `docs/journal-tp1-tp6.md`.
- Pose de l'étiquette Git annotée `v0.6.0`.
- Synchronisation avec le dépôt distant et validation du pipeline CI avec l'étape de roue isolée.

---

## 4. Analyse Technique et Arbitrages Clés

### 4.1 Pourquoi exclure le modèle de la roue ?
Un modèle de Machine Learning est un artefact lourd dont le cycle de vie applicatif diffère de celui du code :
- **Fréquence de mise à jour asynchrone :** Le modèle peut être réentraîné sur de nouveaux volumes de données (ex: quotidiennement ou hebdomadairement) sans qu'il soit nécessaire de modifier une seule ligne de code ni de réémettre une release du paquet.
- **Taille de l'archive et portabilité :** La roue doit rester légère (quelques dizaines de kilo-octets) pour être distribuée rapidement sur n'importe quel serveur ou conteneur.
- **Multi-environnements :** Permet d'injecter des modèles différents selon l'environnement (modèle de démo en staging, modèle entraîné sur corpus massif en production).

### 4.2 L'artifice du fichier de compatibilité `src/predict.py`
Le déplacement d'un module historique présente un risque majeur de régression pour les suites de tests existantes. Le fichier de compatibilité `src/predict.py` résout cette problématique de manière élégante :
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sentiment_app import predict as _module
if __name__ == "__main__":
    raise SystemExit(_module.main())
sys.modules[__name__] = _module
```
L'instruction `sys.modules[__name__] = _module` substitue dans la table des modules chargés l'instance du module de compatibilité par l'instance réelle `sentiment_app.predict`. Ainsi, lorsque des tests unitaires exécutent `monkeypatch.setattr(predict, "MODELE", ...)`, ils modifient directement l'unique objet en mémoire vive partagé par l'API et la CLI.

### 4.3 Pourquoi épingler scikit-learn (`scikit-learn>=1.5,<1.6`) ?
Lors de la sérialisation avec `joblib.dump()`, Python stocke une représentation binaire exacte des instances de classes scikit-learn (`Pipeline`, `TfidfVectorizer`, `LogisticRegression`). Si l'environnement de production installe une version majeure ou mineure différente de celle ayant produit le fichier `.joblib`, la structure des attributs internes peut différer.
Sans épinglage, la désérialisation provoque une rupture fatale :
```text
AttributeError: 'LogisticRegression' object has no attribute 'multi_class'
```
Épingler scikit-learn en version 1.5 dans `pyproject.toml` et dans la CI garantit une compatibilité binaire sans faille entre le pipeline d'entraînement et le moteur d'inférence en production.

---

## 5. Synthèse des Métriques et Couverture

| Indicateur | Valeur mesurée | Seuil attendu / Statut |
| :--- | :--- | :--- |
| **Tests automatisés** | **101 passed, 2 xfailed** (103 au total) | 0 failed / Conforme |
| **Couverture de code API (`api/`)** | **100 %** (82 stmts, 0 miss) | $\ge$ 95 % / Conforme |
| **Linters & Qualité (`ruff`)** | **All checks passed!** | 0 avertissement / Conforme |
| **Vérificateur de types (`mypy`)** | **Success: no issues found** | 4 fichiers validés / Conforme |
| **Format de la roue** | **`sentiment_app-0.6.0-py3-none-any.whl`** | Pure Python, packages `api, sentiment_app, ui` |
| **Étiquette Git** | **`v0.6.0`** | Étiquette annotée conforme |
