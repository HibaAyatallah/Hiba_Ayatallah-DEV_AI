# Semaine 6 : le paquet, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi le modèle n'est-il pas dans la roue ? Comment le paquet le trouve-t-il ?

Le modèle entraîné (`models/sentiment.joblib`) n'est pas inclus dans la roue `.whl` car il s'agit d'un artefact binaire volumineux dont le cycle de vie est indépendant du code source. Un modèle peut être réentraîné sur de nouvelles données, versionné ou remplacé sans nécessiter la recompilation et la republication du paquet Python.

Le paquet trouve le modèle via la fonction `chemin_modele()` dans `sentiment_app/predict.py`. Par défaut, s'il est exécuté dans le contexte du dépôt de développement, il résout le chemin relatif `RACINE / "models" / "sentiment.joblib"`. Lorsqu'il est installé comme roue autonome hors du dépôt, il utilise la variable d'environnement `SENTIMENT_MODELE`. Si cette variable n'est pas configurée, le paquet lève une exception explicite `FileNotFoundError` indiquant le chemin manquant et les solutions possibles (`python src/train.py` ou définition de la variable), renvoyant un code d'erreur 1.

## 2. Qu'est-ce qui a changé dans api/model.py quand predict() est entré dans le paquet, et pourquoi est-ce mieux ?

Dans `api/model.py`, nous avons supprimé le bricolage du chemin d'exécution Python (`RACINE = Path(__file__).resolve().parents[1]` et `sys.path.insert(0, str(RACINE / "src"))`), ainsi que les directives d'inhibition du linter `# noqa: E402` et les imports `sys` et `Path`. Nous importons désormais proprement les dépendances de prédiction sous forme de paquet standard :
```python
from sentiment_app.predict import charger_modele
from sentiment_app.predict import predict as _predict
```

C'est nettement supérieur car cela respecte les conventions de modularité et de distribution Python. L'API ne dépend plus de la structure physique relative des dossiers sur le système de fichiers hôte, ce qui élimine les effets de bord sur `sys.path` et assure un comportement identique en environnement de développement local ou lors d'un déploiement conteneurisé.

## 3. La roue installée hors du dépôt : qu'a-t-il fallu lui fournir, et pourquoi scikit-learn est-il épinglé dans pyproject.toml ?

Lors de l'installation de la roue dans un environnement vierge (`$env:TEMP\roue-tp6`), `pip` a automatiquement téléchargé et installé toutes les dépendances de production déclarées dans les métadonnées (`fastapi`, `uvicorn`, `pydantic`, `scikit-learn`, `joblib`). La seule dépendance externe qu'il a fallu fournir manuellement au paquet pour inférer est le chemin absolu vers le modèle sérialisé via `$env:SENTIMENT_MODELE = "..."`.

scikit-learn est strictement épinglé (`scikit-learn>=1.5,<1.6` dans `pyproject.toml` et `scikit-learn==1.5.*` dans la CI) car la sérialisation avec `joblib` dépend intimement des structures internes des classes de scikit-learn. Sans cet épinglage, la CI ou l'environnement d'entraînement pouvait utiliser une version différente (comme scikit-learn 1.9.1) alors que la roue installait scikit-learn 1.5.2, provoquant une rupture de compatibilité binaire à la relecture :
`AttributeError: 'LogisticRegression' object has no attribute 'multi_class'`. Épingler la version 1.5 garantit l'alignement strict entre la phase d'entraînement et la phase d'inférence en production.
