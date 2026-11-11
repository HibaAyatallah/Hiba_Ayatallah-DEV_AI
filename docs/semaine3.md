# Semaine 3 : l'API, notes du binôme

> Deux questions, quelques phrases chacune. Répondez avec ce que vous avez observé, pas avec le cours.

## 1. Pourquoi l'API refuse-t-elle de démarrer sans `models/sentiment.joblib`, plutôt que de démarrer et de répondre 503 ?

Dans le cycle de vie de FastAPI (`@asynccontextmanager lifespan`), `load_model()` tente de charger le fichier `models/sentiment.joblib` dès l'initialisation du processus (`app.state.classifier = load_model()`). Si le modèle binaire est absent, `charger_modele()` dans `src/predict.py` lève immédiatement une exception `FileNotFoundError: models/sentiment.joblib absent : lancez python src/train.py`, provoquant un `Application startup failed` et l'arrêt immédiat du serveur.

Ce comportement d'échec franc (*fail-fast*) est préférable à un démarrage suivi d'erreurs 503 pour trois raisons observées :
1. **Intégrité de l'orchestration et du déploiement :** Si l'API démarrait et ouvrait son port réseau sans modèle, un orchestrateur (Docker, Kubernetes ou reverse proxy) pourrait considérer le conteneur actif et lui router du trafic utilisateur qui échouerait systématiquement. L'échec au démarrage avertit immédiatement l'infrastructure que le service n'est pas opérationnel.
2. **Diagnostic immédiat pour le développeur et la CI :** En CI/CD ou en local, un plantage net au démarrage met en évidence l'oubli de l'étape d'entraînement (`python src/train.py`), plutôt que de laisser croire à une anomalie réseau ou transitoire.
3. **Inutilité d'un service sans cœur métier :** L'unique raison d'être de cette API est de classifier des avis. Sans modèle chargé en mémoire, le service ne peut rendre aucun service métier et ne doit donc pas consommer de ressources.

## 2. Un texte vide est refusé deux fois : par Pydantic, puis par `predict()`. Est-ce redondant ?

Non, ce double contrôle n'est pas une redondance inutile, mais l'illustration du principe de **défense en profondeur** et de **séparation des responsabilités** entre la couche d'exposition et la couche métier :

1. **Le rôle de Pydantic (`api/schemas.py`) — Contrôle de frontière HTTP :**
   Pydantic valide le contrat d'interface dès la réception de la charge utile HTTP (`min_length=1`). Il protège l'application en amont en rejetant les requêtes vides (`""`), manquantes (`{}`) ou mal typées (`{"text": 42}`) avec un statut HTTP 422 standardisé, sans consommer de temps CPU dans la logique de prédiction.
2. **Le rôle de `predict()` (`src/predict.py`) — Robustesse de la logique métier pure :**
   La fonction `predict(texte)` est un composant métier autonome conçu au TP2. Elle ne dépend pas de FastAPI et peut être appelée directement dans un script en ligne de commande, un traitement par lot ou un pipeline de données. Elle ne doit jamais faire l'hypothèse qu'un filtre web a validé ses arguments en amont ; elle doit donc valider ses propres préconditions (`if not isinstance(texte, str) or not texte.strip(): raise ValueError("texte vide")`).
3. **Observation concrète sur les espaces blancs (Contrôle T22) :**
   Au TP3, une chaîne composée uniquement d'espaces (`"   "`) satisfait `min_length=1` pour Pydantic, mais est interceptée par le `.strip()` de `src/predict.py`. C'est l'exception `ValueError("texte vide")` du modèle qui est rattrapée par le bloc `except ValueError` de l'API pour renvoyer le 422. Les deux niveaux sont donc parfaitement complémentaires.
