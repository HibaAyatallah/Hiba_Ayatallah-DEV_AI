# Compte rendu global des TP1 à TP5
## Du cadrage métier au microservice FastAPI et à l'interface Streamlit

**Binôme :** Hiba Ayatallah ([@HibaAyatallah](https://github.com/HibaAyatallah)) et Manal Wassila ([@manalwassila](https://github.com/manalwassila))  
**Dépôt :** [https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila](https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila)  
**Date :** 14 octobre 2026  
**Module :** Développement et déploiement d'applications intelligentes — Pr. A. Larhlimi  

---

## 1. Le besoin et son cadrage

### 1.1 Le problème métier
Une équipe de relation client reçoit chaque jour un flux massif de milliers d'avis de consommateurs (retours produits, incidents logistiques, demandes de support). Dans l'organisation initiale en file d'attente FIFO (*First In, First Out*), les réclamations urgentes et les avis négatifs sévères attendent plusieurs jours avant d'être pris en charge. Cette latence aggrave l'insatisfaction client, favorise l'attrition (*churn*) et porte atteinte à l'image de marque de l'entreprise.

L'objectif de l'application est d'inverser ce paradigme : filtrer et classer automatiquement les avis dès leur réception pour propulser les avis négatifs en tête de file de traitement, tout en isolant les cas ambigus pour qu'ils soient revus par un conseiller humain.

### 1.2 Justification de l'approche technique pour le Cas 3 (Avis négatifs)
L'évaluation multicritère formalisée au cours du TP1 a conduit au choix exclusif du **Machine Learning supervisé classique** (traitement du langage naturel statistique) pour répondre à ce besoin, face aux alternatives (règles métier, RAG ou modèles génératifs purs) :

- **(a) Données étiquetées disponibles sans surcoût :** Les plateformes d'e-commerce collectent nativement une note numérique (de 1 à 5 étoiles) en regard du commentaire textuel. La conversion de ces notes en étiquettes binaires (1-2 étoiles = négatif, 4-5 étoiles = positif) fournit instantanément des dizaines de milliers d'exemples annotés pour l'apprentissage supervisé, sans mobiliser d'équipe d'annotation dédiée.
- **(c) Coût d'inférence et volumétrie élevée :** Pour absorber des milliers d'appels quotidiens, un appel à une API de modèle génératif commercial (LLM) représenterait une dépense mensuelle disproportionnée et introduirait une latence de plusieurs secondes par requête. À l'inverse, un modèle classique TF-IDF couplé à une régression logistique s'exécute en quelques millisecondes sur CPU standard pour un coût marginal strictement nul.
- **(d) Conséquence modérée d'une erreur d'aiguillage :** L'algorithme ne valide pas une transaction financière ni un diagnostic médical ; il réordonne une file de tâches. Un faux positif (avis positif priorisé par erreur) ne lèse aucun client ; un faux négatif (avis négatif traité dans l'ordre ordinaire) ne dégrade pas le service par rapport à la situation historique. L'erreur est donc peu grave et rend le recours au Machine Learning particulièrement adapté, d'autant plus qu'un seuil de confiance isole les avis incertains.
- **(b) Explicabilité suffisante et auditabilité :** Les poids vectoriels et les coefficients de la régression logistique permettent d'extraire les termes les plus prédictifs pour chaque classe, garantissant une compréhension claire des décisions algorithmiques pour les superviseurs métier.

---

## 2. L'architecture du dépôt et principes MLOps

### 2.1 Organisation modulaire du dépôt
Le dépôt `sentiment-app` structure rigoureusement les responsabilités pour garantir la testabilité, la reproductibilité et l'isolation des composants :

```text
sentiment-app/
├── README.md, TP1-ENONCE.md, TP2-ENONCE.md, TP3-ENONCE.md, TP4-ENONCE.md, TP5-ENONCE.md
├── requirements.txt, requirements.lock, .gitignore, pytest.ini, Makefile, .pre-commit-config.yaml
├── .github/workflows/ci.yml       # Intégration continue (GitHub Actions avec pytest, ruff, mypy)
├── docs/                          # Spécifications de cadrage et synthèses TP1 à TP5
│   ├── cadrage/                   # cas1-pharmacie.md, cas2-reglement.md, cas3-avis-negatifs.md
│   ├── semaine2.md                # Analyse qualitative des erreurs du modèle (TP2)
│   ├── semaine3.md                # Choix et argumentation du seuil d'incertitude (TP3)
│   ├── semaine4.md                # Tests aux limites, robustesse et courbe de seuil (TP4)
│   ├── semaine5.md                # Architecture client-serveur et recette Streamlit (TP5)
│   ├── journal-tp1-tp5.md         # Journal complet des jalons T0 à T34
│   └── compte-rendu.md            # Rapport d'ingénierie global
├── Resume/                        # Rapports et livrables de synthèse
│   ├── RESUME_TP1.pdf             # Synthèse TP1
│   ├── RESUME_TP2.md             # Synthèse TP2
│   ├── RESUME_TP4.md             # Synthèse TP4
│   ├── RESUME_TP5.md             # Synthèse TP5
│   └── RESUME_GLOBAL.md           # Le présent compte rendu global (TP1 à TP5)
├── src/                           # Pipeline ML d'entraînement et d'inférence (TP2/TP4)
│   ├── make_demo.py               # Générateur du jeu synthétique de démo
│   ├── train.py                   # Entraînement scikit-learn (démo et Allociné)
│   ├── evaluate.py                # Rapport de classification et matrice de confusion
│   ├── predict.py                 # Logique pure d'inférence unitaire
│   └── courbe_seuil.py            # Analyse du compromis couverture / précision
├── api/                           # Microservice REST FastAPI (TP3-TP5)
│   ├── main.py                    # Endpoints /health, /predict, /predict/batch, gestion d'erreurs
│   ├── schemas.py                 # Schémas de validation Pydantic v2 (PredictRequest, etc.)
│   └── model.py                   # Chargement fail-fast du modèle et inférence
├── ui/                            # Interface utilisateur Streamlit découplée (TP5)
│   ├── app.py                     # Composants visuels, onglets unitaire / lot / santé, graphiques
│   └── client.py                  # Client HTTP typé communiquant avec l'API FastAPI
├── tests/                         # Suite complète de 97 tests automatisés (95 validés, 2 xfailed)
│   ├── test_environment.py       # 23 tests de structure et d'environnement (TP1)
│   ├── test_cadrage.py           # 12 tests de conformité des fiches métier (TP1)
│   ├── test_git_history.py       # 3 tests d'historique et de contribution binôme (TP1)
│   ├── test_model.py             # 4 tests sur le modèle et metrics.json (TP2)
│   ├── test_api.py               # 7 tests des endpoints FastAPI et codes HTTP (TP3)
│   ├── test_schemas.py           # 5 tests de validation Pydantic et sérialisation (TP3)
│   ├── test_limites.py           # 10 tests aux limites et propriétés Hypothesis (TP4)
│   ├── test_integration.py       # 13 tests d'intégration bout-en-bout et pannes API (TP4)
│   ├── test_jeu_or.py            # 14 tests de robustesse et cas difficiles sur jeu d'or (TP4)
│   └── test_ui_client.py         # 6 tests du client HTTP et logique d'affichage UI (TP5)
├── models/                        # Artefacts de modélisation
│   ├── .gitkeep                   # Préservation du répertoire dans Git
│   ├── metrics.json               # Métriques validées et versionnées
│   └── sentiment.joblib           # Fichier binaire du modèle (local, ignoré par Git)
└── data/                          # Données d'expérimentation et de recette
    ├── demo_reviews.csv          # Données d'entraînement démo (290 avis régénérables)
    ├── avis_exemple.csv          # Lot de recette pour l'interface Streamlit (242 avis)
    └── jeu_or.csv                # Jeu d'or de test annoté (20 avis étalons)
```

### 2.2 Stratégie MLOps : Versionnage sélectif et reproductibilité
Un logiciel traditionnel ne versionne que du code source. Une application intelligente manipule trois natures d'artefacts distinctes :

| Artefact | Présent dans Git ? | Justification |
| :--- | :---: | :--- |
| **Le code source** (`src/`, `api/`, `ui/`, `tests/`) | **Oui** | C'est le cœur reproductible du travail d'ingénierie. |
| **L'environnement** (`.venv/`) | **Non** | Reconstructible instantanément via `pip install -r requirements.txt`. Son inclusion alourdirait le dépôt de plusieurs centaines de Mo. |
| **Les données** (`demo_reviews.csv`, `avis_exemple.csv`, `jeu_or.csv`) | **Sélectif** | `demo_reviews.csv` est régénérable via `src/make_demo.py` ; `avis_exemple.csv` et `jeu_or.csv` sont versionnés comme étalons de recette et de non-régression. |
| **Le modèle sérialisé** (`sentiment.joblib`) | **Non** | Fichier binaire lourd, inadapté aux diffs Git, et régénérable fidèlement via `python src/train.py --allocine` grâce à la fixation de la graine aléatoire (`random_state=42`). |
| **La mesure de performance** (`metrics.json`) | **OUI** | Fichier texte léger contenant les scores officiels validés. Elle ne peut être recalculée sans ré-entraîner. |

### 2.3 Pourquoi `models/metrics.json` est dans Git et pas `models/sentiment.joblib` ?
Cette règle répond directement aux exigences de l'intégration continue (CI) :
- **Transporter la preuve de conformité sans le poids du binaire :** Sur les serveurs GitHub Actions, la machine virtuelle d'intégration exécute les tests sur un environnement éphémère. Les tests `test_metriques_completes` et `test_f1_au_dessus_du_seuil` valident la qualité du travail en lisant `metrics.json`. Si le modèle `sentiment.joblib` est absent, les tests de prédiction directe sont simplement ignorés (`pytest.skip`).
- **Traçabilité des performances dans l'historique :** Chaque ré-entraînement enregistre formellement ses métriques (date, volume de données, F1 macro, exactitude, rappel négatif). Un commit permet ainsi d'auditer l'amélioration ou la régression du modèle sans polluer l'historique Git avec des binaires incompatibles.

---

## 3. Le modèle de sentiment

### 3.1 Pipeline scikit-learn et étanchéité des données
Le modèle est conçu sous forme d'un `Pipeline` scikit-learn garantissant que la même chaîne de traitement s'applique rigoureusement à l'apprentissage et en inférence :
1. **`TfidfVectorizer` :**
   - Combinaison d'unigrammes et de bigrammes (`ngram_range=(1, 2)`) pour capturer des associations lexicales locales (ex. « pas bon », « très rapide »).
   - Filtrage des termes rares avec `min_df=2`.
   - Normalisation logarithmique des fréquences (`sublinear_tf=True`).
2. **`LogisticRegression` :**
   - Pondération inverse des classes (`class_weight="balanced"`) pour compenser tout déséquilibre.
   - Algorithme d'optimisation robuste avec `max_iter=1000` et `random_state=42`.

> **Point méthodologique fondamental :** Le découpage `train_test_split` (80 % train, 20 % test, stratifié sur les classes) intervient **strictement avant toute vectorisation**. Si le vectoriseur apprenait sur l'intégralité du corpus, le vocabulaire du jeu de test « fuiterait » dans l'entraînement (*data leakage*), faussant la validité des scores.

### 3.2 Résultats chiffrés réels : Démonstration vs Allociné

| Métrique / Paramètre | Jeu de Démonstration (`demo`) | Vrai Jeu Public (`allocine`) |
| :--- | :---: | :---: |
| **Source des données** | `data/demo_reviews.csv` | Validation Allociné (Parquet) |
| **Volume total d'avis** | 290 avis | 20 000 avis |
| **Nombre d'avis d'entraînement** | 232 avis | 16 000 avis |
| **Nombre d'avis de test** | 58 avis | 4 000 avis |
| **Taille du vocabulaire appris** | 349 termes | **149 529 termes** |
| **Exactitude globale (*Accuracy*)** | 87.93 % | **92.05 %** |
| **Score $F_1$ macro** | **0.8793** | **0.9205** (seuil exigé : 0.85) |
| **Rappel sur la classe négative** | **86.21 %** (25 / 29) | **91.13 %** |
| **Précision sur la classe négative** | 89.29 % (25 / 28) | 93.19 % |

Sur le jeu réel Allociné, l'explosion du vocabulaire (multiplié par près de 470) permet au modèle d'atteindre un score $F_1$ macro de **0.9205**, surpassant très nettement le seuil d'exigence fixé à 0.85.

### 3.3 Analyse de la matrice de confusion (Jeu de démo)
Sur les 58 avis du jeu de test de démonstration, la matrice de confusion mesurée est la suivante :

```text
                  Prédiction : negative    Prédiction : positive
Vérité : negative                   25                        4
Vérité : positive                    3                       26
```

- **Ligne 1 (Vérité = négatif, 29 avis) :**
  - **25 vrais négatifs (TN) :** 86.21 % des avis mécontents sont correctement détectés pour être remontés en tête de file.
  - **4 faux positifs (FP) :** Quatre avis négatifs sont classés positifs. C'est l'erreur la plus coûteuse pour le métier, car ces clients mécontents subiront le délai de traitement ordinaire.
- **Ligne 2 (Vérité = positif, 29 avis) :**
  - **3 faux négatifs (FN) :** Trois avis favorables sont étiquetés négatifs. Ils sont placés à tort dans la file prioritaire mais seront rapidement traités par un agent sans conséquence néfaste.
  - **26 vrais positifs (TP) :** 89.66 % des clients satisfaits sont correctement identifiés.

---

## 4. L'analyse des erreurs

### 4.1 Diagnostic et inventaire des erreurs
Sur les 58 avis de démo, le modèle commet exactement **7 erreurs**. L'examen systématique démontre que **100 % des erreurs surviennent sur des avis mitigés** comportant une première proposition d'un sentiment, un connecteur d'opposition, puis une conclusion du sentiment inverse.

Exemples réels extraits directement de nos données d'évaluation (`python src/evaluate.py`) :
1. *« Notice incompréhensible et pièces manquantes les premiers jours, puis rapidement service impeccable. »*  
   $\rightarrow$ Vérité = positive, Prédit = negative.
2. *« Excellent rapport qualité prix au début, mais finalement produit cassé à l'arrivée. »*  
   $\rightarrow$ Vérité = negative, Prédit = positive (cas critique).
3. *« Excellent rapport qualité prix sur le papier, puis rapidement taille trop petite et retour payant. »*  
   $\rightarrow$ Vérité = negative, Prédit = positive.

### 4.2 Le mécanisme générateur : l'absence d'ordre du sac de mots
L'extraction TF-IDF repose sur le paradigme du « sac de mots » (*bag-of-words*) :
- Le modèle additionne les poids des mots indépendamment de leur position dans la phrase.
- Dans l'exemple 3, les termes élogieux (*impeccable*, *livraison en avance*, *service*) pèsent plus lourd numériquement que le seul terme *cassé*.
- Le modèle est structurellement incapable de comprendre que la proposition introduite par *« sauf que ensuite »* annule la proposition précédente. Pour un modèle sans ordre, l'expression *« bon puis mauvais »* et l'expression *« mauvais puis bon »* produisent rigoureusement le même vecteur de caractéristiques.

### 4.3 Pistes de remédiation technique
Pour corriger ces erreurs sans complexité inutile :
1. **Surpondération positionnelle :** Attribuer un poids croissant aux n-grammes situés vers la fin du texte, là où réside la conclusion.
2. **Segmentation par marqueurs discursifs :** Scinder le texte au niveau des conjonctions d'opposition (*mais*, *cependant*, *sauf que*) et orienter la prédiction sur la clause finale.
3. **Modèles de langue séquentiels (Transformers) :** L'emploi d'un modèle pré-entraîné comme **CamemBERT**, dont les couches d'auto-attention bidirectionnelle et les encodages positionnels capturent la syntaxe et la négation à longue portée.

---

## 5. L'architecture découplée FastAPI & Streamlit et la politique d'abstention

### 5.1 Séparation stricte Microservice REST et Client Frontend
L'architecture logicielle finale (TP3 à TP5) adopte un patron découplé client-serveur hautement modulaire :
- **Backend FastAPI (`api/`) :**
  - **`api/main.py` :** Points d'entrée REST `/health`, `/predict` (inférence unitaire) et `/predict/batch` (inférence vectorisée par lot). Gestion sémantique et normalisée des codes HTTP (200 OK, 422 Unprocessable Entity en cas de format invalide, 503 Service Unavailable si le modèle est absent ou corrompu). Chargement *fail-fast* du modèle via le gestionnaire de cycle de vie `lifespan`.
  - **`api/schemas.py` :** Validation déclarative stricte avec Pydantic v2 (`PredictRequest`, `PredictResponse`, `BatchPredictRequest`, `BatchPredictResponse`, `HealthResponse`).
  - **`api/model.py` :** Encapsulation de la logique de prédiction, calcul des probabilités et vectorisation.
- **Frontend Streamlit (`ui/`) :**
  - **`ui/client.py` :** Client HTTP typé isolant l'ensemble des appels réseau (`requests`). Gestion robuste des pannes d'infrastructure (timeout, indisponibilité de l'API avec message d'alerte explicite). Typage strict validé sous `mypy`.
  - **`ui/app.py` :** Interface utilisateur réactive, totalement agnostique des détails de modélisation scikit-learn, consommant exclusivement les données fournies par l'API.

### 5.2 Les fonctionnalités développées
1. **Onglet « Un avis » :** Zone de saisie dynamique affichant la jauge de confiance et le code couleur adapté (vert pour positif, rouge pour négatif prioritaire, orange pour arbitrage agent en cas d'abstention).
2. **Onglet « Un fichier CSV » :** Traitement par lot permettant de glisser-déposer un export d'avis, de visualiser les 3 métriques produit immédiates, d'explorer le tableau trié des avis urgents et de télécharger le CSV annoté (validé sur les 242 avis de `data/avis_exemple.csv` : 94 positifs, 14 négatifs, 134 indéterminés).
3. **Onglet « Santé de l'API » :** Diagnostic opérationnel en temps réel vérifiant la disponibilité de l'API `/health`, la présence du modèle en mémoire et la version applicative.

#### Illustrations de l'interface Streamlit en conditions réelles
| Détection d'un avis favorable (Confiance élevée) | Détection d'un avis négatif (Traitement prioritaire) |
| :---: | :---: |
| ![Interface Streamlit - Avis Positif](screenshots/demo_avis_positif.png) | ![Interface Streamlit - Avis Négatif](screenshots/demo_avis_negatif.png) |
*Figure 1 : Interface utilisateur en action démontrant la jauge de probabilité, le diagnostic immédiat et l'orientation des retours clients.*

### 5.3 Analyse chiffrée et justification du seuil d'incertitude
La politique d'abstention régit la bascule entre l'automatisation totale et l'intervention humaine. Lorsqu'un avis présente une probabilité maximale inférieure au seuil de confiance, le système s'abstient et retourne l'étiquette `INDETERMINE`.

| Seuil d'incertitude | Avis « à vérifier » (sur 290 démo) | Avis « à vérifier » (sur 30 sample) | Risque opérationnel |
| :---: | :---: | :---: | :--- |
| **0.50** | ~ 40 avis (14 %) | 1 avis (3 %) | Risque élevé : le modèle tranche seul des avis mitigés et commet des faux négatifs critiques. |
| **0.60 (Retenu)** | **117 avis (40.3 %)** | **7 avis (23.3 %)** | **Compromis idéal :** isole les avis ambigus tout en automatisant en toute sécurité 75 à 85 % des flux nets. |
| **0.75** | > 190 avis (> 65 %) | 18 avis (60 %) | Surcharge humaine : la file de vérification déborde, l'automatisation perd sa valeur ajoutée. |

**Justification métier :**  
Le seuil de **0.60** constitue le point d'équilibre optimal pour l'équipe relation client (validé par l'analyse de courbe de seuil dans `src/courbe_seuil.py`). Sur des avis ordinaires, il automatise la majorité du flux sans risque ; sur des avis difficiles et mitigés, il renvoie les cas ambigus vers un conseiller, neutralisant l'impact des erreurs inhérentes au modèle TF-IDF.

---

## 6. Ce qui a échoué (Difficultés réelles et résolutions)

La réalisation des cinq séances a été jalonnée de plusieurs incidents concrets résolus avec méthode :

1. **Incompatibilité de l'interpréteur système sous Windows (TP1) :**
   - *Incident :* L'appel initial `python -m pytest` a échoué avec l'erreur `C:\Python313\python.exe: No module named pytest`.
   - *Cause :* Le terminal utilisait le Python global de la machine (3.13) au lieu de l'environnement virtuel du projet.
   - *Solution :* Exécution ciblée via le chemin explicite `.\.venv\Scripts\python.exe` et activation de la politique de scripts PowerShell via `Set-ExecutionPolicy RemoteSigned`.
2. **Échec attendu du contrôle C1 au TP2 :**
   - *Incident :* Lors de l'installation du kit TP2, `pytest` a affiché `2 failed, 38 passed, 2 skipped`.
   - *Cause :* Les tests de `test_model.py` cherchaient `models/metrics.json` avant que l'entraînement n'ait eu lieu.
   - *Solution :* Lancement immédiat de `python src/train.py`, produisant les métriques et faisant repasser la suite au vert.
3. **Rejet de push Git par divergence distante (TP2) :**
   - *Incident :* Erreur `! [rejected] main -> main (fetch first)` lors du push du commit Semaine 2.
   - *Cause :* La collaboratrice du binôme avait ajouté un fichier de compte rendu PDF directement sur l'interface GitHub, créant un commit distant non présent en local.
   - *Solution :* Rapatriement par `git fetch origin` suivi d'un `git rebase origin/main` propre pour rejouer notre commit au sommet de la branche sans polluer l'historique avec un merge commit.
4. **Robustesse aux données aberrantes et tests de propriétés (TP4) :**
   - *Incident :* Lors des tests Hypothesis générant des chaînes aléatoires et des caractères d'échappement, certaines longueurs extrêmes provoquaient des comportements inattendus.
   - *Solution :* Encadrement strict par validation Pydantic (longueur maximale, nettoyage des entrées) et tests d'intégration simulant les coupures réseau et codes HTTP 500/503.
5. **Typage strict Mypy sur le comptage des étiquettes (TP5) :**
   - *Incident :* L'analyseur de type `mypy ui` levait une erreur d'incompatibilité de type `Argument 1 to "sorted" has incompatible type "dict_items[str | None, int]"`.
   - *Cause :* Les requêtes en échec réseau retournaient un label `None`, polluant le dictionnaire `Counter` avec des clés optionnelles non ordonnables.
   - *Solution :* Typage explicite `compte: Counter[str]` et filtrage strict des labels non nuls ou substitution par une étiquette explicite `"REFUS OU ERREUR"`.

---

## 7. Ce que nous ferions pour un passage à l'échelle industrielle

Avec le recul de l'ensemble des cinq séances et dans un contexte d'ingénierie logicielle d'entreprise :
1. **Conteneurisation et orchestration (Docker & Kubernetes) :** Packager l'API FastAPI et le frontend Streamlit dans des images Docker multi-stage légères basées sur `python:3.11-slim`, avec déploiement managé et autoscaling horizontal (HPA) selon la charge des requêtes.
2. **Modèles de langue séquentiels (Transformers / CamemBERT) :** Dépasser les limites structurelles de TF-IDF sur les avis mitigés et les négations inversées en fine-tunant un modèle CamemBERT ou RoBERTa-français, exécuté sur GPU ou via une inférence optimisée avec ONNX Runtime.
3. **Versionnage des données et du modèle (DVC & MLflow) :** Lier formellement chaque commit Git à un hash immuable des jeux de données d'entraînement stockés sur un bucket S3/GCS, avec registre centralisé des artefacts et suivi des métriques d'expérimentation.
4. **Surveillance continue de la dérive lexicale (*Data & Concept Drift*) :** En production, le vocabulaire des consommateurs évolue continuellement. L'intégration d'un moniteur de dérive (ex. Evidently AI / Prometheus) analyserait en continu la distribution des scores de confiance pour déclencher des alertes et des ré-entraînements automatisés.

---

## 8. Répartition du travail au sein du binôme

Le travail a été réalisé en binôme équilibré et complémentaire tout au long des cinq séances de travaux pratiques :

| Membre | Rôle | Contributions détaillées sur l'ensemble des 5 TP |
| :--- | :---: | :--- |
| **Hiba Ayatallah** | **Membre A** | - **TP1 :** Création et administration du dépôt GitHub distant, cadrage méthodologique multicritère des cas d'usage, rédaction des fiches de décision conformes.<br>- **TP2 :** Cadrage métier, validation des métriques de classification et des seuils F1 macro, analyse de la matrice de confusion.<br>- **TP3 :** Validation des endpoints `/health` et `/predict`, tests manuels Swagger et vérification du démarrage *fail-fast*.<br>- **TP4 :** Rédaction et annotation des avis du jeu d'or (`data/jeu_or.csv`), identification des cas difficiles et erreurs connues (`test_jeu_or.py`), conception des tests d'intégration et pannes 500 (`test_integration.py`), intégration des linters `ruff`, typage `mypy` et configuration `pre-commit`.<br>- **TP5 :** Recette des codes d'erreur et de l'indisponibilité API (T32), validation de l'ingestion de lot et export CSV (T33), rédaction des réponses argumentées dans `docs/semaine5.md`, mise à jour du journal T0-T34 et rédaction des synthèses. |
| **Manal Wassila** | **Membre B** | - **TP1 :** Configuration de l'environnement virtuel local Python 3.11, diagnostic de build et CI GitHub Actions.<br>- **TP2 :** Pipeline scikit-learn, entraînement du modèle sur le corpus Allociné et démo, analyse qualitative des erreurs d'inférence.<br>- **TP3 :** Architecture de l'API FastAPI, implémentation des schémas Pydantic (`schemas.py`), endpoints et tests d'API (`test_api.py`).<br>- **TP4 :** Implémentation des tests aux limites et des propriétés Hypothesis (`test_limites.py`), analyse de la courbe de seuil (`courbe_seuil.py`), gestion de l'abstention à 0.60, rédaction de `docs/semaine4.md` et `Resume/RESUME_TP4.md`.<br>- **TP5 :** Implémentation du client HTTP typé (`ui/client.py`), interface Streamlit découplée (`ui/app.py`), tests unitaires client UI (`test_ui_client.py`), validation des contrôles T29 à T31 sur l'interface utilisateur. |

---

## Outils d'aide à la rédaction

Conformément à la politique d'intégrité académique, nous déclarons avoir utilisé l'assistant d'IA Antigravity pour nous aider à structurer la mise en forme Markdown, à concevoir les tableaux comparatifs et à vérifier la cohérence des chiffres réels issus de notre fichier `models/metrics.json` ; l'ensemble du travail technique, des commandes, de l'analyse des résultats et des choix d'ingénierie a été réalisé, vérifié et validé par nos soins.
