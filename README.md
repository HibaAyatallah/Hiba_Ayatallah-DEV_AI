# sentiment-app : projet de Hiba Ayatallah

<div align="center">

| **Hiba Ayatallah** |
| :---: |
| <img src="docs/captures/hiba_ayatallah.jpg" width="200" alt="Hiba Ayatallah"> |
| [@HibaAyatallah](https://github.com/HibaAyatallah) |

</div>

Application fil rouge du module *Développement et déploiement d'applications intelligentes* (Pr. A. Larhlimi).  
Ce dépôt retrace la chaîne d'ingénierie complète d'une application de traitement automatique du langage naturel (NLP) pour la relation client, du cadrage métier jusqu'à la qualification logicielle industrielle et l'exposition d'une API de production :

- **Semaine 1 (TP1) — Cadrage & Environnement :** Cadrage métier multicritère, environnement virtuel Python 3.11 reproductible, structure canonique du dépôt, fiches de décision et pipeline d'Intégration Continue (38 tests).
- **Semaine 2 (TP2) — Modèle de sentiment & MLOps :** Pipeline scikit-learn (TF-IDF + Régression logistique), entraînement synthétique (`demo_reviews.csv`) et massif (`allocine`), analyse qualitative des erreurs, versionnage sélectif (`models/metrics.json` versionné, modèle binaire ignoré par Git) (42 tests).
- **Semaine 3 (TP3) — API REST FastAPI :** Exposition du modèle derrière un microservice HTTP asynchrone (`/health`, `/predict`), validation Pydantic v2, chargement unique en mémoire au démarrage (`lifespan`) et architecture *fail-fast* (48 tests).
- **Semaine 4 (TP4) — Tests approfondis & Garde-fous :** Tests aux limites paramétrés et tests de propriétés (`hypothesis`), arbitrage du seuil d'abstention à 0.60 avec verdict `INDETERMINE`, constitution d'un jeu d'or de 20 avis annotés, tests d'intégration réels et masquage des erreurs 500, couverture à 100 %, typage strict `mypy`, linters `ruff` et crochets `pre-commit` (83 tests passés, 2 xfailed).
- **Semaine 5 (TP5) — Interface utilisateur Streamlit & Découplage :** Application web interactive pour les conseillers relation client, découplage architectural total (la page ne connaît que l'API via `ui/client.py`), traitement unitaire et par lot avec export CSV (`data/avis_exemple.csv`), affichage bienveillant de l'abstention (« Je ne sais pas... ») et tests UI automatisés sans serveur avec `AppTest` (95 tests passés, 2 xfailed).
- **Semaine 6 (TP6) — Packaging & Distribution industrielle :** Transformation du dépôt en un paquet Python installable standard (`sentiment-app 0.6.0`), création de la commande CLI `sentiment` (`--version`, `predict`, `serve`, `ui`), découplage définitif de l'API sans manipulation de `sys.path`, modèle configurable via `SENTIMENT_MODELE`, construction d'une roue `.whl` autonome et tests complets (101 tests passés, 2 xfailed).

---

## Démarrage rapide

### 1. Activer l'environnement virtuel
```bash
# Windows PowerShell :
.\.venv\Scripts\Activate.ps1

# Linux / macOS / Git Bash :
source .venv/bin/activate
```

*(Si nécessaire, installer les dépendances applicatives et de développement :)*
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Entraîner le modèle de démonstration
```bash
python src/train.py
```
*Le modèle est généré dans `models/sentiment.joblib` (F1 macro = 0.879) et les métriques dans `models/metrics.json`.*

### 3. Lancer l'API FastAPI
```bash
uvicorn api.main:app --reload
```
Le terminal confirme : `Modèle chargé avec succès : tfidf-logreg (TP2, models/sentiment.joblib)`.  
La documentation interactive Swagger est immédiatement consultable dans votre navigateur sur **[http://localhost:8000/docs](http://localhost:8000/docs)**.

### 4. Lancer l'interface Streamlit (TP5)
Dans un second terminal (environnement activé, avec l'API toujours en cours d'exécution sur le port 8000) :
```bash
streamlit run ui/app.py
```
L'interface s'ouvre sur **[http://localhost:8501](http://localhost:8501)** et affiche en légende : `API prête : tfidf-logreg (TP2, models/sentiment.joblib)`.

### 5. Utiliser la commande CLI `sentiment` et la roue (TP6)
Une fois le paquet installé en mode éditable (`pip install -e .`) :
```bash
# Vérifier la version unique du paquet
sentiment --version

# Classifier un avis en ligne de commande (applique le seuil d'abstention)
sentiment predict "Livraison rapide, produit conforme, très satisfait"
sentiment predict "xqzvb wlkptr grombu"

# Démarrer le serveur API
sentiment serve --port 8000

# Construire la roue standard (.whl)
python -m build --wheel
```

---

## Validation et Qualification logicielle (TP1 à TP6)

Toutes les vérifications de qualité et de robustesse se lancent en une seule commande depuis la racine du dépôt :

```bash
# 1. Exécuter l'intégralité de la suite de tests automatisés (101 passés, 2 xfailed)
pytest -q

# 2. Mesurer la couverture de code sur l'API (seuil minimal exigé : 95 % ; obtenu : 100 %)
pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95

# 3. Contrôler le typage statique du contrat d'interface
mypy api

# 4. Vérifier la conformité stylistique et l'absence d'erreurs avec le linter ruff
ruff check .

# 5. Tester le crochet de pré-commit
pre-commit run --all-files
```

---

## Les Endpoints de l'API (Semaines 3 & 4)

L'API REST expose trois routes principales documentées via OpenAPI :

| Méthode & Route | Description & Contrat | Codes de statut HTTP |
| :--- | :--- | :---: |
| **`GET /`** | Accueil et pointage vers la documentation. | `200 OK` |
| **`GET /health`** | Sonde de santé opérationnelle (*liveness probe*). Valide que le modèle `tfidf-logreg` est instancié en mémoire. | `200 OK`<br>`503 Service Unavailable` |
| **`POST /predict`** | Classification d'un texte (`1` à `2000` caractères). Renvoie `label` (`POSITIVE`, `NEGATIVE`, `INDETERMINE`), `score` et aperçu textuel. | `200 OK`<br>`422 Unprocessable Entity`<br>`500 Internal Error` |

### Exemples d'appels en ligne de commande (`httpx`) :

```bash
# Vérifier la santé du service (T15)
python -c "import httpx; print(httpx.get('http://127.0.0.1:8000/health').json())"

# Prédire un avis positif (T16)
python -c "import httpx; r = httpx.post('http://127.0.0.1:8000/predict', json={'text': 'Livraison rapide, produit conforme, très satisfait'}); print(r.status_code, r.json())"

# Prédire un avis négatif (T17)
python -c "import httpx; r = httpx.post('http://127.0.0.1:8000/predict', json={'text': 'Produit cassé et service injoignable, à fuir'}); print(r.status_code, r.json())"

# Observer l'abstention sur un texte hors vocabulaire (T24)
python -c "import httpx; r = httpx.post('http://127.0.0.1:8000/predict', json={'text': 'xqzvb wlkptr grombu'}); print(r.status_code, r.json())"
# Réponse : 200 {'label': 'INDETERMINE', 'score': 0.5162, ...}
```

---

## Synthèse des Garde-fous et de l'Interface (TP4 & TP5)

1. **Validation stricte aux limites (`tests/test_limites.py`) :**
   - Contrôle paramétré sur 8 cas frontières (vide, blancs seuls, 1 car., 2000 car., 2001 car., champ manquant, type non-chaîne, corps non-JSON).
   - Tests de propriétés probabilistes avec **Hypothesis** (150 tirages valides et 100 tirages de blancs purs).
   - Validation via `@field_validator("text")` dans `api/schemas.py` éliminant le bug du caractère Unicode `\x85` (Next Line).
2. **Abstention probabiliste (`api/model.py`) :**
   - Seuil de confiance fixé à `SEUIL_ABSTENTION = 0.60` sur la base de la courbe empirique (`src/courbe_seuil.py`).
   - Réduction de 71.4 % des erreurs du modèle au prix de seulement 27.6 % d'avis délégués à une revue humaine.
3. **Le Jeu d'or (`data/jeu_or.csv` & `tests/test_jeu_or.py`) :**
   - 20 avis de test conçus manuellement (dont 6 cas complexes : négation, ironie, avis mitigé, critique cinéma).
   - 2 erreurs structurelles documentées et protégées par `xfail(strict=True)`.
4. **Résilience et Sécurité de l'API (`tests/test_integration.py`) :**
   - Interception de toute panne imprévue du modèle pour répondre un HTTP 500 générique sans fuite de message technique (`from None`).
   - Refus strict de démarrage si le modèle binaire est absent ou si ses classes ne correspondent pas au contrat.
   - Couverture de test complète : **100 % sur `api/`**.
5. **Interface Streamlit découplée (`ui/` & `tests/test_*.py`) :**
   - Respect de la 3ème règle d'architecture : la page n'importe jamais `predict()` ni `.joblib` et passe par `ui/client.py`.
   - Traitement par lot avec restitution visuelle et export CSV (`data/avis_exemple.csv`).
   - 12 tests automatisés sans navigateur (7 pour `test_client.py` et 5 pour `test_interface.py` via `AppTest`).

---

## Documentation et Livrables

| Document | Contenu & Objectif |
| :--- | :--- |
| **`Resume/RESUME_TP5.md`** | **Compte rendu complet du TP5 (Interface Streamlit, architecture client-serveur, cycle de vie, AppTest et traitement par lot)** |
| **`Resume/RESUME_TP4.md`** | Compte rendu complet du TP4 (Tests aux limites, Hypothesis, Seuil d'abstention, Jeu d'or, Couverture 100 % et Linters) |
| `Resume/RESUME_TP2.md` | Synthèse détaillée du TP2 (Modélisation, pipeline scikit-learn et analyse qualitative des erreurs) |
| `Resume/RESUME_GLOBAL.md` | Synthèse globale des étapes initiales du projet |
| `docs/semaine5.md` | Réponses argumentées de la semaine 5 (Découplage architectural, gestion de l'abstention, résilience de l'API et mesures sur avis_exemple.csv) |
| `docs/semaine4.md` | Réponses argumentées et mesures d'exécution de la semaine 4 (Couverture, courbe de seuil, bilan du jeu d'or et audit statique) |
| `docs/semaine3.md` | Analyse de la conception d'API (Fail-Fast au démarrage et défense en profondeur Pydantic vs modèle) |
| `docs/semaine2.md` | Analyse qualitative des erreurs du sac de mots sur les avis mitigés |
| `docs/journal-tp1-tp5.md` | Journal de projet avec les résultats réels des contrôles T0 à T34 |
| `docs/cadrage/` | Fiches de cadrage métier formalisées lors du TP1 (pharmacie, règlement, avis négatifs) |

---

## Structure du Dépôt

```text
sentiment-app/
├── README.md, TP1-ENONCE.md, TP2-ENONCE.md, TP3-ENONCE.md, TP4-ENONCE.md, TP5-ENONCE.md
├── MARCHE-A-SUIVRE-TP*.md          # Guides d'exécution pas à pas de chaque TP
├── requirements.txt, requirements-dev.txt, requirements.lock, .gitignore, pytest.ini, pyproject.toml
├── .pre-commit-config.yaml         # Crochets de pré-commit automatisés (ruff, mypy)
├── .github/workflows/ci.yml        # Pipeline d'Intégration Continue (train, ruff, mypy, pytest >=95%)
├── api/                            # Microservice REST FastAPI (TP3 & TP4)
│   ├── __init__.py
│   ├── main.py                     # Application ASGI, routes, lifespan et gestion 500/503
│   ├── schemas.py                  # Contrats Pydantic v2 (PredictRequest, PredictResponse, Label)
│   └── model.py                    # Raccord modèle, seuil d'abstention (0.60) et contrôle des classes
├── ui/                             # Interface graphique Streamlit (TP5)
│   ├── __init__.py                 # Paquet Python ui
│   ├── client.py                   # Client HTTP vers l'API (/health, /predict, traitement de lot)
├── sentiment_app/                  # Le paquet Python installable (TP6)
│   ├── __init__.py                 # Version unique du paquet (0.6.0)
│   ├── __main__.py                 # Point d'entrée exécutable (python -m sentiment_app)
│   ├── cli.py                      # Commande CLI « sentiment » (version, predict, serve, ui)
│   └── predict.py                  # Inférence unitaire découplée et modèle configurable
├── src/                            # Pipeline ML et scripts de mesure (TP2, TP4 & TP6)
│   ├── make_demo.py                # Générateur du jeu de démo (290 avis)
│   ├── train.py                    # Entraînement scikit-learn (démo et Allociné)
│   ├── evaluate.py                 # Matrice de confusion et rapport de classification
│   ├── predict.py                  # Module de compatibilité rétroactive (TP6)
│   ├── courbe_seuil.py             # Calculateur empirique de la courbe de compromis abstention/erreur
│   └── bilan_jeu_or.py             # Évaluateur opérationnel du jeu d'or
├── tests/                          # 101 tests automatisés (+ 2 xfailed)
│   ├── test_environment.py        # 23 tests de conformité de l'environnement (TP1)
│   ├── test_cadrage.py            # 12 tests des fiches de cadrage (TP1)
│   ├── test_git_history.py        # 3 tests de l'historique et des contributions (TP1)
│   ├── test_model.py              # 4 tests sur le modèle et metrics.json (TP2)
│   ├── test_api.py                # 6 tests de bon fonctionnement de l'API (TP3)
│   ├── test_limites.py            # 10 tests aux limites et propriétés Hypothesis (TP4)
│   ├── test_integration.py        # 6 tests d'intégration, résilience 500 et démarrage réel (TP4)
│   ├── test_jeu_or.py             # 21 tests de validation du jeu d'or (TP4)
│   ├── test_client.py             # 7 tests du client HTTP de l'API (TP5)
│   ├── test_interface.py          # 5 tests de l'interface Streamlit avec AppTest (TP5)
│   └── test_packaging.py          # 6 tests de packaging, roue et commande CLI (TP6)
├── models/
│   ├── .gitkeep
│   ├── metrics.json                # Métriques validées et versionnées dans Git
│   └── sentiment.joblib            # Binaire sérialisé (local, exclu de Git)
├── data/
│   ├── sample_reviews.csv          # Échantillon de test
│   ├── demo_reviews.csv           # Données synthétiques (régénérables par make_demo.py)
│   ├── jeu_or.csv                 # Jeu d'or de 20 avis annotés de référence (versionné)
│   └── avis_exemple.csv           # 242 avis de démonstration pour l'interface (versionné)
├── docs/
│   ├── semaine2.md à semaine6.md   # Bilans hebdomadaires et réponses argumentées
│   ├── journal-tp1-tp6.md          # Journal de bord complet pour chaque contrôle T0 à T41
│   ├── captures/                   # Dossier de captures d'écran des jalons T0 à T41
│   └── cadrage/                    # Fiches de cadrage des cas d'usage
├── CHANGELOG.md                    # Journal des versions de 0.1.0 à 0.6.0 (TP6)
└── Resume/
    ├── RESUME_TP5.md               # Compte rendu spécifique complet du TP5
    ├── RESUME_TP4.md               # Compte rendu spécifique complet du TP4
    ├── RESUME_TP2.md               # Compte rendu du TP2
    └── RESUME_GLOBAL.md            # Synthèse globale initiale
```

---

## Auteur et Répartition des Travaux

| Auteur | Identifiant GitHub | Contributions principales (TP1 à TP6) |
| :--- | :--- | :--- |
| **Hiba Ayatallah** | [@HibaAyatallah](https://github.com/HibaAyatallah) | - **TP1 :** Création du dépôt GitHub, cadrage multicritère des cas d'usage, structuration initiale de la documentation.<br>- **TP2 :** Cadrage métier, validation des métriques de classification et des seuils F1 macro.<br>- **TP3 :** Validation des endpoints `/health` et `/predict`, tests manuels Swagger et vérification du démarrage *fail-fast*.<br>- **TP4 :** Rédaction et annotation des avis du jeu d'or (`data/jeu_or.csv`), identification des cas difficiles et erreurs connues (`test_jeu_or.py`), conception des tests d'intégration et pannes 500 (`test_integration.py`), intégration des linters `ruff`, typage `mypy` et configuration `pre-commit`.<br>- **TP5 :** Recette des codes d'erreur et de l'indisponibilité (T32), validation de l'ingestion de lot et export CSV (T33), rédaction des réponses argumentées dans `docs/semaine5.md`, mise à jour du journal T0-T34 et rédaction de `Resume/RESUME_TP5.md`.<br>- **TP6 :** Installation du kit TP6, migration de `predict.py` dans le paquet `sentiment_app/`, suppression définitive de `sys.path` dans `api/model.py`, validation des contrôles T35 à T37, rédaction du compte rendu `docs/semaine6.md` et finalisation du journal T0-T41. |

