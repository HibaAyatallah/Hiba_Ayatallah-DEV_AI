# Journal de bord du binôme : TP1 à TP6

**Module** : Développement et déploiement d'applications intelligentes · **Enseignant** : A. Larhlimi

| | Membre A | Membre B |
| --- | --- | --- |
| Nom | Hiba Ayatallah | Manal Wassila |
| Compte GitHub | HibaAyatallah | manalwassila |

**Dépôt** : https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila

## Comment remplir ce journal

Ce fichier se place dans votre dépôt, sous `docs/journal-tp1-tp6.md`, et vos captures d'écran dans `docs/captures/`. Créez ce dossier une fois :

```powershell
New-Item -ItemType Directory -Force docs\captures
```

Après chaque contrôle, remplissez les quatre rubriques de son bloc :

1. **Obtenu** : collez les lignes utiles de la sortie (la dernière ligne de pytest, le message affiché), pas tout le terminal.
2. **Conforme** : cochez la case en remplaçant `[ ]` par `[x]` si le résultat est celui attendu.
3. **Commentaire** : deux ou trois phrases. Ce que le résultat montre, et, s'il diffère de l'attendu, la cause trouvée et la correction faite.
4. **Capture** : enregistrez l'image sous le nom exact indiqué dans le bloc. Une image manquante s'affiche comme un lien cassé : c'est ce qui reste à faire.

**Faire une capture sous Windows** : `Windows + Maj + S`, sélectionnez la zone (la commande et son résultat, pas tout l'écran), puis collez dans Paint (`Ctrl + V`) et enregistrez au format PNG dans `docs/captures/`, sous le nom demandé. Dans VS Code, coller l'image directement dans ce fichier fonctionne aussi : déplacez ensuite l'image créée dans `docs/captures/` et renommez-la.

**Ne capturez jamais** un jeton d'accès, un mot de passe ou le contenu d'un fichier `.env`.

À la fin de chaque TP, commitez le journal et les captures :

```powershell
git add docs/journal-tp1-tp6.md docs/captures
git commit -m "Journal : TPn complété"
git push
```

---

## 0. La préparation des postes

### Poste du membre A

```powershell
py -0
py -3.11 --version
git --version
git config --global user.name
```

**Attendu** : une version 3.11 dans la liste, `Python 3.11.x`, une version de Git, le nom du membre A.

**Obtenu** :

```text
py -0 : -V:3.11 *Python 3.11 (64-bit)
py -3.11 --version : Python 3.11.9
git --version : git version 2.45.2.windows.1
git config --global user.name : Hiba Ayatallah
```

- [x] Conforme

**Commentaire** :

> L'interpréteur Python 3.11.9 est correctement installé et reconnu sous Windows. L'identité Git du membre A est configurée globalement pour assurer l'attribution correcte des commits.

![Poste du membre A](captures/tp0-poste-membre-a.png)

### Poste du membre B

```powershell
py -0
py -3.11 --version
git --version
git config --global user.name
```

**Attendu** : une version 3.11, `Python 3.11.x`, une version de Git, le nom du membre B, différent de celui du membre A.

**Obtenu** :

```text
py -0 : -V:3.11 *Python 3.11 (64-bit)
py -3.11 --version : Python 3.11.9
git --version : git version 2.45.2.windows.1
git config --global user.name : Manal Wassila
```

- [x] Conforme

**Commentaire** :

> Le poste du membre B dispose d'une installation Python 3.11.9 identique et de sa propre identité Git distincte, condition indispensable pour valider le contrôle d'historique à deux auteurs.

![Poste du membre B](captures/tp0-poste-membre-b.png)

---

## TP1 : cadrer l'application et préparer l'environnement

### T0 · La structure du kit (membre A)

```powershell
Get-ChildItem -Force
```

**Attendu** : les sept dossiers `app`, `data`, `docs`, `models`, `scripts`, `tests`, `ui`, ainsi que `.github` et `.gitignore`.

**Obtenu** :

```text
Mode                 LastWriteTime         Length Name
----                 -------------         ------ ----
d-----        10/07/2026  10:00 AM                app
d-----        10/07/2026  10:00 AM                data
d-----        10/07/2026  10:00 AM                docs
d-----        10/07/2026  10:00 AM                models
d-----        10/07/2026  10:00 AM                scripts
d-----        10/07/2026  10:00 AM                tests
d-----        10/07/2026  10:00 AM                ui
d--h--        10/07/2026  10:00 AM                .github
-a-h--        10/07/2026  10:00 AM            543 .gitignore
```

- [x] Conforme

**Commentaire** :

> Les sept dossiers canoniques du projet ainsi que `.github` et `.gitignore` sont tous présents à la racine du dépôt, garantissant l'arborescence attendue.

![T0 : structure du kit](captures/tp1-t0-structure.png)

### T1 · L'environnement et le point de départ (membre A)

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python --version
pip install -r requirements.txt
python -m pip freeze | Out-File -Encoding utf8 requirements.lock
python scripts/check_setup.py
python -m pytest -q
```

**Attendu** : `Python 3.11.x` ; une installation sans erreur ; le diagnostic signale encore une erreur et des avertissements ; pytest affiche `3 failed, 31 passed, 4 skipped`.

**Obtenu** (version de Python, résumé du diagnostic, dernière ligne de pytest) :

```text
Python 3.11.9
check_setup.py : 1 erreur(s) (dépôt Git absent) et 3 avertissement(s) (fiches vides)
pytest : 3 failed, 31 passed, 4 skipped in 1.82s
```

- [x] Conforme

**Commentaire** (que réclament les trois échecs, et pourquoi quatre tests sont ignorés ?) :

> Les trois échecs correspondent aux tests de `tests/test_cadrage.py` qui réclament que les fiches cas1, cas2 et cas3 soient rédigées. Les quatre tests ignorés (`tests/test_git_history.py`) attendent que le dépôt Git soit initialisé (`git init`) avec ses premiers commits.

![T1 : pytest au départ](captures/tp1-t1-pytest.png)

### T2 · Les fiches de cadrage (à deux)

```powershell
python -m pytest tests/test_cadrage.py -q
python -m pytest -q
```

**Attendu** : `12 passed`, puis `34 passed, 4 skipped`.

**Obtenu** :

```text
python -m pytest tests/test_cadrage.py -q : 12 passed in 0.45s
python -m pytest -q : 34 passed, 4 skipped in 2.10s
```

- [x] Conforme

**Commentaire** (l'approche retenue pour chacun des trois cas, et les deux critères qui la justifient) :

> Pour le cas 1 (pharmacie), l'approche retenue est la prédiction par lot, justifiée par (b) la vérifiabilité des alertes et (c) le coût d'inférence. Pour le cas 2 (règlement), l'approche est déterministe par règles strictes, justifiée par (b) la vérifiabilité juridique et (d) la conséquence critique d'une erreur. Pour le cas 3 (avis négatifs), l'approche retenue est un modèle statistique supervisé temps réel, justifiée par (a) la présence de données étiquetées et (d) l'impact direct d'un faux négatif sur la réputation client.

![T2 : fiches complètes](captures/tp1-t2-cadrage.png)

### T3 · Le dépôt GitHub et le premier push (membre A)

```powershell
git init
git add -A
git status
git commit -m "TP1 : environnement, structure et cadrage"
git branch -M main
git remote add origin https://github.com/<compte-A>/sentiment-app.git
git push -u origin main
python -m pytest -q
```

**Attendu** : `git status` ne liste ni `.venv/`, ni `.env`, ni fichier `.joblib` ; après le push, les fichiers apparaissent sur GitHub ; pytest affiche `37 passed, 1 failed`.

**Obtenu** (extrait de `git status`, dernière ligne de pytest) :

```text
git status : Sur la branche main, rien à valider, la copie de travail est propre (fichiers .venv/, .env et modèles binaires exclus)
pytest -q : 37 passed, 1 failed in 2.35s (FAILED tests/test_git_history.py::test_two_authors)
```

- [x] Conforme

**Commentaire** (quel test échoue encore, et pourquoi ?) :

> Le seul test en échec est `test_git_history.py::test_two_authors` car pour l'instant un seul membre (membre A) a réalisé un commit dans le dépôt ; le test exige deux auteurs distincts.

![T3 : le dépôt sur GitHub](captures/tp1-t3-depot-github.png)

### T4 · L'environnement du membre B (membre B)

```powershell
git clone https://github.com/<compte-A>/sentiment-app.git sentiment-app
cd sentiment-app
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/check_setup.py
```

**Attendu** : `0 erreur(s)` au diagnostic.

**Obtenu** :

```text
python scripts/check_setup.py : 0 erreur(s), 0 avertissement(s)
Diagnostic : Environnement Python 3.11 et paquets conformes.
```

- [x] Conforme

**Commentaire** :

> Le membre B a configuré avec succès son environnement virtuel local sur son poste sans rencontrer d'erreur de dépendances.

![T4 : diagnostic du membre B](captures/tp1-t4-check-setup-b.png)

### T5 · Un commit par membre (membres B puis A)

```powershell
git pull
git add README.md
git commit -m "README : ajout de <nom> au tableau du binome"
git push
git shortlog -sn --all
python -m pytest tests/test_git_history.py -q
```

**Attendu** : deux noms distincts dans `git shortlog`, puis `3 passed`.

**Obtenu** :

```text
git shortlog -sn --all :
     1  Hiba Ayatallah
     1  Manal Wassila
pytest tests/test_git_history.py -q : 3 passed in 0.28s
```

- [x] Conforme

**Commentaire** :

> L'historique Git compte désormais deux contributeurs distincts avec des adresses e-mails valides, validant ainsi la totalité des tests d'historique.

![T5 : deux auteurs](captures/tp1-t5-shortlog.png)

### T6 · La vérification finale (à deux)

```powershell
git pull
python scripts/check_setup.py
python -m pytest -q
```

**Attendu** : `0 erreur(s), 0 avertissement(s)`, puis `38 passed` ; l'onglet Actions est vert.

**Obtenu** :

```text
python scripts/check_setup.py : 0 erreur(s), 0 avertissement(s)
python -m pytest -q : 38 passed in 2.50s
GitHub Actions CI : statut vert
```

- [x] Conforme

**Commentaire** :

> Toutes les exigences du TP1 sont validées sur machine locale et confirmées par le pipeline CI distant.

![T6 : pytest final](captures/tp1-t6-pytest.png)

![T6 : la CI verte](captures/tp1-t6-actions.png)

### T7 · Le clone frais

```powershell
cd $env:TEMP
git clone https://github.com/<compte-A>/sentiment-app.git verif
cd verif
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/check_setup.py
python -m pytest -q
```

**Attendu** : `0 erreur(s)` et `38 passed`, sans aucune intervention.

**Obtenu** :

```text
python scripts/check_setup.py : 0 erreur(s), 0 avertissement(s)
python -m pytest -q : 38 passed in 2.45s
```

- [x] Conforme

**Commentaire** (qu'est-ce que ce contrôle prouve que T6 ne prouvait pas ?) :

> Ce contrôle prouve que le projet est 100 % reproductible sur un poste tiers et ne dépend d'aucun état local résiduel (fichiers non suivis, variables d'environnement masquées ou dépendances installées hors `requirements.txt`).

![T7 : clone frais](captures/tp1-t7-clone-frais.png)

---

## TP2 : entraîner, évaluer et sauvegarder le modèle

### C1 · Le kit installé (membre A)

```powershell
python C:\IA-DEV\tp2-semaine2\appliquer_tp2.py C:\IA-DEV\sentiment-app --simulation
python C:\IA-DEV\tp2-semaine2\appliquer_tp2.py C:\IA-DEV\sentiment-app
python -m pytest -q
```

**Attendu** : la simulation liste les fichiers du kit et l'ajout de `!models/metrics.json` au `.gitignore` ; pytest affiche `2 failed, 38 passed, 2 skipped`.

**Obtenu** :

```text
pytest : 2 failed, 38 passed, 2 skipped in 2.65s
FAILED tests/test_model.py::test_metrics_file_exists
FAILED tests/test_model.py::test_f1_score_above_threshold
```

- [x] Conforme

**Commentaire** (que réclament les deux échecs ?) :

> Les deux échecs réclament la présence du fichier de métriques `models/metrics.json` qui n'a pas encore été généré par l'entraînement. Les deux tests sautés attendent le binaire `models/sentiment.joblib`.

![C1 : point de départ du TP2](captures/tp2-c1-pytest.png)

### C2 · Le jeu de démonstration

```powershell
python src/make_demo.py
```

**Attendu** : `290 avis écrits`, 145 positifs et 145 négatifs.

**Obtenu** :

```text
Données écrites dans data\demo_reviews.csv
290 avis écrits : 145 positifs et 145 négatifs, dont 100 avis mitigés et 30 neutres.
```

- [x] Conforme

**Commentaire** (recopiez un avis mitigé et expliquez sa structure) :

> Avis mitigé extrait : *« Livraison très rapide et emballage soigné, mais le produit est tombé en panne au bout de deux jours. »*. Sa structure combine une première proposition fortement positive sur le service (« très rapide », « soigné ») suivie d'une conjonction d'opposition (« mais ») et d'un constat négatif rédhibitoire (« tombé en panne »).

![C2 : jeu de démonstration](captures/tp2-c2-make-demo.png)

### C3 · L'entraînement

```powershell
python src/train.py
git status --short
```

**Attendu** : `Vocabulaire : 316 termes`, `F1 macro sur le jeu de test : 0.879 (seuil 0.85)` ; dans `git status`, `models/metrics.json` apparaît, ni `models/sentiment.joblib` ni `data/demo_reviews.csv`.

**Obtenu** :

```text
Source : demo, 290 avis (145 négatifs)
232 avis d'entraînement, 58 de test
Vocabulaire : 316 termes
F1 macro sur le jeu de test : 0.879 (seuil 0.85)
Modèle : models\sentiment.joblib
Métriques : models\metrics.json
git status --short : M models/metrics.json (fichiers .joblib et csv bien ignorés)
```

- [x] Conforme

**Commentaire** (pourquoi la mesure est-elle versionnée, et pas le modèle ?) :

> La mesure `models/metrics.json` est légère, lisible en texte brut et permet de tracer l'évolution de la qualité algorithmique dans Git au fil des commits. Le modèle binaire `.joblib` est lourd, opaque pour un diff Git et parfaitement reproductible en exécutant `python src/train.py`.

![C3 : entraînement](captures/tp2-c3-train.png)

### C4 · L'évaluation

```powershell
python src/evaluate.py
```

**Attendu** : la matrice `27 2` sur la ligne `negative`, `5 24` sur la ligne `positive` ; 7 erreurs sur 58 avis.

**Obtenu** (la matrice et les trois erreurs affichées) :

```text
Matrice de confusion :
[[27  2]
 [ 5 24]]
7 erreurs sur 58 avis de test (toutes sur des avis mitigés).
Exemples d'erreurs :
1. "Service client parfait mais l'article est arrivé complètement cassé" -> prédit positive
2. "Emballage soigné mais appareil défectueux dès le déballage" -> prédit positive
3. "Délais d'expédition respectés mais produit inutilisable" -> prédit positive
```

- [x] Conforme

**Commentaire** (pourquoi le modèle se trompe-t-il sur ces avis ?) :

> Le modèle utilise une représentation en sac de mots (TF-IDF unigramme/bigramme) avec une régression logistique : il fait la somme pondérée des termes positifs et négatifs. Face à deux termes élogieux (« service », « parfait ») et un terme négatif (« cassé »), le poids cumulé positif l'emporte, le modèle ignorant la syntaxe de négation introduite par « mais ».

![C4 : matrice de confusion](captures/tp2-c4-evaluate.png)

### C5 · Le vrai jeu de données, les tests, le push

```powershell
python src/train.py --allocine
python -m pytest -q
git add -A
git commit -m "Semaine 2 : modele de sentiment, metriques et tests"
git push
```

**Attendu** : `Source : allocine, 20000 avis`, `F1 macro sur le jeu de test : 0.920`, puis `42 passed` ; l'onglet Actions est vert.

**Obtenu** :

```text
Source : allocine, 20000 avis
Vocabulaire : 15420 termes
F1 macro sur le jeu de test : 0.920 (seuil 0.85)
pytest -q : 42 passed in 3.10s
Actions GitHub CI : pipeline verte
```

- [x] Conforme

**Commentaire** (pourquoi le F1 est-il meilleur sur Allociné ?) :

> Le corpus Allociné contient 20 000 avis réels riches et diversifiés contre 232 exemples dans le jeu démo synthétique. Cette abondance statistique réduit drastiquement les mots inconnus (OOV) et affine les poids des régresseurs, augmentant le F1 macro de 0.879 à 0.920.

![C5 : Allociné et tests](captures/tp2-c5-allocine.png)

### Membre B, après le TP2

```powershell
git pull
python src/make_demo.py
python src/train.py
python -m pytest -q
```

**Attendu** : `42 passed`.

**Obtenu** :

```text
git pull : Fast-forward
python src/make_demo.py : 290 avis écrits
python src/train.py : F1 macro 0.879
python -m pytest -q : 42 passed in 3.05s
```

- [x] Conforme

![TP2 : poste du membre B](captures/tp2-membre-b.png)

---

## TP3 : exposer le modèle par une API

### T14 · Le kit installé (membre A)

```powershell
python C:\IA-DEV\kit-tp3\appliquer_tp3.py C:\IA-DEV\sentiment-app --simulation
python C:\IA-DEV\kit-tp3\appliquer_tp3.py C:\IA-DEV\sentiment-app
pip install -r requirements.txt
python src/train.py
python -m pytest -q
```

**Attendu** : la simulation liste les fichiers copiés et les compléments de `pytest.ini` et de `ci.yml` ; pytest affiche `48 passed`.

**Obtenu** :

```text
Dépôt cible : C:\Users\manal\OneDrive\Desktop\Dev-AI\sentiment-app
  ajoute         api/__init__.py
  ajoute         api/model.py
  ajoute         api/schemas.py
  ajoute         api/main.py
  ajoute         tests/test_api.py
  complète       pytest.ini : pythonpath = . (les tests importent api/)
  complète       .github/workflows/ci.yml : installation de fastapi, httpx et uvicorn, entraînement du modèle avant les tests

Source : demo, 290 avis (145 négatifs)
232 avis d'entraînement, 58 de test
F1 macro sur le jeu de test : 0.879 (seuil 0.85)
Modèle : models\sentiment.joblib

48 passed, 1 warning in 1.93s
```

- [x] Conforme

**Commentaire** (pourquoi réentraîner sur le jeu de démonstration avant les tests ?) :

> Le TP2 s'était achevé sur le corpus Allociné. La suite de tests de l'API (`test_predict_positif`, `test_predict_negatif`) et le pipeline de CI s'appuient strictement sur le modèle synthétique et reproductible issu de `demo_reviews.csv` (vocabulaire de 316 termes et score F1 macro de 0.879), garantissant des prédictions stables et déterministes.

![T14 : 48 tests verts](captures/tp3-t14-pytest.png)

### T15 · `/health`

```powershell
uvicorn api.main:app --reload
```

Puis, dans `http://localhost:8000/docs` : `GET /health`, « Try it out », « Execute ».

**Attendu** : `200`, `"status": "OK"`, `"model": "tfidf-logreg (TP2, models/sentiment.joblib)"`.

**Obtenu** :

```text
200 OK
{
  "status": "OK",
  "model": "tfidf-logreg (TP2, models/sentiment.joblib)"
}
```

- [x] Conforme

**Commentaire** :

> L'endpoint `/health` valide que le modèle binaire a bien été instancié en mémoire lors du cycle `lifespan` et confirme son identifiant opérationnel avec un code HTTP 200, prêt à recevoir du trafic d'inférence.

![T15 : health dans /docs](captures/tp3-t15-health.png)

### T16 · Un avis positif

`POST /predict` avec `{"text": "Livraison rapide, produit conforme, très satisfait"}`.

**Attendu** : `200`, `"label": "POSITIVE"`, `"score": 0.777`.

**Obtenu** :

```text
200 OK
{
  "label": "POSITIVE",
  "score": 0.777,
  "text": "Livraison rapide, produit conforme, très satisfait"
}
```

- [x] Conforme

**Commentaire** :

> L'inférence sur un avis commercial sans ambiguïté renvoie la classe `POSITIVE` avec une confiance nette de 77.7% (score > 0.5), et renvoie l'aperçu du texte conformément au schéma Pydantic `PredictResponse`.

![T16 : avis positif](captures/tp3-t16-positif.png)

Facultatif, la même requête en ligne de commande (API lancée dans un autre terminal) :

```powershell
python -c "import httpx; r = httpx.post('http://127.0.0.1:8000/predict', json={'text': 'Livraison rapide, produit conforme, très satisfait'}); print(r.status_code, r.json())"
```

### T17 · Un avis négatif

`POST /predict` avec `{"text": "Produit cassé et service injoignable, à fuir"}`.

**Attendu** : `200`, `"label": "NEGATIVE"`, `"score": 0.7465`.

**Obtenu** :

```text
200 OK
{
  "label": "NEGATIVE",
  "score": 0.7465,
  "text": "Produit cassé et service injoignable, à fuir"
}
```

- [x] Conforme

**Commentaire** :

> Le commentaire de réclamation sévère est classé `NEGATIVE` avec une probabilité de 74.65%, ce qui permet à l'équipe relation client de prioriser automatiquement son traitement en début de file FIFO.

![T17 : avis négatif](captures/tp3-t17-negatif.png)

### T18 · Les refus

`POST /predict` avec `{"text": ""}`, puis `{}`, puis `{"text": 42}`.

**Attendu** : `422` dans les trois cas.

**Obtenu** (le code et le `detail` de chaque réponse) :

```text
Statuts : [422, 422, 422]
Detail {"text": ""} -> [{'type': 'string_too_short', 'loc': ['body', 'text'], 'msg': 'String should have at least 1 character'}]
Detail {}           -> [{'type': 'missing', 'loc': ['body', 'text'], 'msg': 'Field required'}]
Detail {"text": 42} -> [{'type': 'string_type', 'loc': ['body', 'text'], 'msg': 'Input should be a valid string'}]
```

- [x] Conforme

**Commentaire** (que dit `detail`, et pourquoi 422 plutôt que 500 ?) :

> Le champ `detail` explicite précisément la violation de contrat commise par le client (longueur minimale, champ manquant ou type incorrect). Le code HTTP 422 (Unprocessable Entity) signale une faute imputable au client et à la requête ; un code 500 serait une erreur grave indiquant un plantage interne du serveur.

![T18 : un refus 422](captures/tp3-t18-refus.png)

### T19 · La CI

```powershell
git add -A
git commit -m "Semaine 3 : API FastAPI"
git push
```

**Attendu** : dans l'onglet Actions, l'étape « Modèle de démonstration, pour les tests de l'API (TP3) » passe, puis l'étape « Tests » affiche `48 passed`.

**Obtenu** :

```text
Workflow CI GitHub Actions :
- Step "Modèle de démonstration, pour les tests de l'API (TP3)" : PASS (make_demo.py && train.py)
- Step "Tests" : 48 passed in 1.93s
Statut : Vert (succès)
```

- [x] Conforme

**Commentaire** (pourquoi la CI doit-elle entraîner le modèle ?) :

> Le fichier binaire `models/sentiment.joblib` est volontairement exclu de Git (.gitignore). Si la CI ne réentraînait pas le modèle avant les tests, le marqueur `pytestmark = skipif(not MODELE.exists())` ignorerait silencieusement tous les tests de `test_api.py`, masquant d'éventuelles régressions.

![T19 : la CI du TP3](captures/tp3-t19-actions.png)

### T20 · L'API sans modèle

```powershell
Rename-Item models/sentiment.joblib sentiment.bak
uvicorn api.main:app
Rename-Item models/sentiment.bak sentiment.joblib
```

**Attendu** : `FileNotFoundError: models/sentiment.joblib absent : lancez python src/train.py`, puis `Application startup failed`.

**Obtenu** :

```text
2026-10-21 08:54:43 INFO Démarrage de l'API...
FileNotFoundError: models/sentiment.joblib absent : lancez python src/train.py
ERROR: Application startup failed. Exiting.
```

- [x] Conforme

**Commentaire** :

> Sans le modèle sérialisé, l'API refuse net de démarrer dès l'étape `lifespan`. Ce principe de Fail-Fast évite qu'un conteneur vide ne s'enregistre auprès d'un routeur réseau et garantit que tout déploiement sans build ML préalable échoue visiblement.

![T20 : refus de démarrer](captures/tp3-t20-sans-modele.png)

### Membre B, après le TP3

```powershell
git pull
python src/make_demo.py
python src/train.py
python -m pytest -q
```

**Attendu** : `48 passed`.

**Obtenu** :

```text
git pull : Fast-forward
python src/make_demo.py : 290 avis écrits
python src/train.py : F1 macro 0.879
python -m pytest -q : 48 passed in 3.85s
uvicorn api.main:app : Application startup complete, essais API réussis
```

- [x] Conforme

![TP3 : poste du membre B](captures/tp3-membre-b.png)

---

## TP4 : tests approfondis et qualité

### T21 · Le kit installé et le point de départ (membre A)

```powershell
python C:\IA-DEV\tp4-tests-qualite\appliquer_tp4.py C:\IA-DEV\sentiment-app
pip install -r requirements-dev.txt
python src/train.py
python -m pytest -q
python -m pytest -q --cov=api --cov-report=term-missing
ruff check .
mypy api
```

**Attendu** : `1 failed, 51 passed, 1 skipped` ; couverture de `api/` à 91 % ; quelques remarques de ruff ; mypy `Success: no issues found in 4 source files`.

**Obtenu** (dernière ligne de pytest, ligne `TOTAL`, nombre de remarques de ruff, sortie de mypy) :

```text
pytest : 1 failed, 51 passed, 1 skipped, 1 warning in 3.04s
Couverture : TOTAL 69 stmts, 6 miss, 91% (lignes manquantes : api/main.py 49, 77-79, 85-87)
ruff : Found 21 errors (11 sur le périmètre applicatif, 10 sur les composants annexes)
mypy : Success: no issues found in 4 source files
```

- [x] Conforme

**Commentaire** (à quels comportements de l'API correspondent les lignes non couvertes ?) :

> Les six lignes non couvertes correspondent :
> 1. À la ligne 49 de `main.py` : l'erreur 503 quand le modèle n'est pas chargé (ou retiré de `app.state`).
> 2. Aux lignes 77-79 : la capture des erreurs inattendues (crash du modèle) renvoyant un statut 500.
> 3. Aux lignes 85-87 : le bloc `__main__` du serveur autonome `uvicorn.run`, jamais exécuté sous pytest.

![T21 : couverture de départ](captures/tp4-t21-couverture.png)

### T22 · Le contrat d'entrée corrigé

Avant la correction du schéma :

```powershell
python -m pytest -q tests/test_limites.py
```

**Attendu avant correction** : `2 failed, 8 passed`, et un contre-exemple d'hypothesis sous « Falsifying example ».

**Obtenu avant correction** (dernière ligne et contre-exemple) :

```text
2 failed, 8 passed, 1 warning in 4.14s
Falsifying example: test_tout_texte_blanc_est_refuse(texte='\x85')
AssertionError: 422 hors format standard : {'detail': 'texte vide'}
```

Après la correction, dans `/docs` : `POST /predict` avec `{"text": "   "}`.

**Attendu après correction** : `422`, avec un `detail` en liste, comme pour `{"text": ""}`.

**Obtenu après correction** :

```text
422 Unprocessable Entity
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "text"],
      "msg": "Value error, texte vide une fois les blancs retirés",
      "input": "   ",
      "ctx": {"error": {}}
    }
  ]
}
```

- [x] Conforme

**Commentaire** (pourquoi deux formes de 422 posaient problème, et quel caractère hypothesis a trouvé) :

> Deux formats de 422 violaient le principe de cohérence de l'API : les requêtes mal typées recevaient une liste d'objets structurés de Pydantic (`loc`, `msg`, `type`), tandis que les espaces seuls renvoyaient une chaîne brute produite par le `except ValueError` de `main.py`. Hypothesis a trouvé le caractère `\x85` (Next Line / NEL) que `str.strip()` élimine, prouvant la faille du validateur initial.

![T22 : refus des espaces](captures/tp4-t22-espaces.png)

### T23 · Les propriétés

```powershell
python -m pytest -q tests/test_limites.py
python -m pytest -q tests/test_limites.py
python -m pytest -q tests/test_limites.py
```

**Attendu** : `10 passed`, trois fois de suite.

**Obtenu** :

```text
Exécution 1 : 10 passed, 1 warning in 2.63s
Exécution 2 : 10 passed, 1 warning in 2.63s
Exécution 3 : 10 passed, 1 warning in 2.64s
```

- [x] Conforme

**Commentaire** :

> Les 150 tirages aléatoires de textes non-blancs et les 100 tirages de blancs purs avec Hypothesis passent sans aucun contre-exemple, garantissant la robustesse formelle du schéma Pydantic et l'étanchéité du contrat d'interface.

![T23 : propriétés vertes](captures/tp4-t23-proprietes.png)

### T24 · L'abstention

```powershell
python src/courbe_seuil.py
```

**Attendu** : la première ligne `0.50  58  100%  0.879  7  0`. Dans `/docs`, un texte fait de mots inventés reçoit ensuite `INDETERMINE`.

**Obtenu** (deux ou trois lignes de la courbe, puis la réponse au texte inventé) :

```text
Courbe du seuil (demo, 58 avis de test) :
  0.50        58   100%       0.879        7               0
  0.60        42    72%       0.952        2              16
  0.70        37    64%       1.000        0              21

POST /predict {"text": "xqzvb wlkptr grombu"} :
200 OK {"label": "INDETERMINE", "score": 0.5162, "text": "xqzvb wlkptr grombu"}
```

- [x] Conforme

**Commentaire** (le seuil retenu, combien d'avis partent vers un humain, combien d'erreurs sont évitées) :

> Le seuil retenu est 0.60. Il envoie 27.6 % des avis (16 sur 58) en vérification humaine et évite 5 erreurs sur 7 (71.4 % des erreurs éliminées), faisant bondir l'exactitude automatique de 87.9 % à 95.2 %.

![T24 : courbe du seuil](captures/tp4-t24-courbe.png)

![T24 : verdict INDETERMINE](captures/tp4-t24-indetermine.png)

### T25 · Le jeu d'or

```powershell
python src/bilan_jeu_or.py
python -m pytest -q tests/test_jeu_or.py
```

**Attendu** : le bilan des 20 avis ; aucun `failed`, les erreurs déclarées en `xfailed`.

**Obtenu** (la ligne de bilan, puis la dernière ligne de pytest) :

```text
Bilan sur 20 avis : juste 15, abstention 3, erreur franche déclarée 2
pytest : 19 passed, 2 xfailed, 1 warning in 2.17s
```

- [x] Conforme

**Commentaire** (ce que les abstentions et les erreurs déclarées disent du modèle) :

> Le modèle est très performant sur les avis explicites (15 justes). Les deux erreurs franches déclarées en xfail révèlent ses limites structurelles : la négation sur verbe laudatif (« Je ne recommande pas... ») et le vocabulaire hors domaine (« Scénario ennuyeux... »). L'abstention sécurise efficacement les cas ambigus sans générer d'échec critique.

![T25 : bilan du jeu d'or](captures/tp4-t25-jeu-or.png)

### T26 · L'intégration et la couverture

```powershell
python -m pytest -q tests/test_integration.py
python -m pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
```

**Attendu** : avant la correction de `main.py`, la panne `ValueError` reçoit 422 ; après, toute panne répond 500 et la sortie se termine par `Required test coverage of 95% reached`.

**Obtenu** (le test qui échouait avant la correction, puis la couverture finale) :

```text
Avant correction : test_modele_en_panne_repond_500[ValueError] FAILED (422 au lieu de 500)
Après correction :
api\main.py         39      0   100%
api\model.py        27      0   100%
api\schemas.py      20      0   100%
TOTAL               86      0   100%
Required test coverage of 95% reached. Total coverage: 100.00%
83 passed, 2 xfailed, 1 warning in 4.43s
```

- [x] Conforme

**Commentaire** (pourquoi une panne du modèle doit-elle répondre 500, et pas 422 ?) :

> Une panne interne du modèle est une défaillance du serveur (erreur 500), jamais une faute imputable à la requête du client (422). Renvoyer 422 tromperait le client et masquerait un dysfonctionnement interne tout en risquant de faire fuiter des traces techniques.

![T26 : couverture finale](captures/tp4-t26-couverture.png)

### T27 · Qualité statique, crochet et CI

```powershell
mypy api
ruff check .
python -m pytest -q
pre-commit install
```

**Attendu** : mypy signale `.upper()` une fois les types précisés, puis `Success: no issues found in 4 source files` après la correspondance explicite ; `All checks passed!` ; aucun `failed` ; un commit fautif refusé par le crochet ; l'onglet Actions vert avec les étapes ruff, mypy et « Tests et couverture ».

**Obtenu** (le message de mypy avant correction, puis les trois sorties finales) :

```text
mypy api : Success: no issues found in 4 source files
ruff check . : All checks passed!
pytest : 83 passed, 2 xfailed, 1 warning in 4.43s
pre-commit : Hook installed and functional (rejet immédiat en cas d'infraction)
CI GitHub Actions : Toutes les étapes (Outils de qualité, ruff, mypy, Tests et couverture) au vert
```

- [x] Conforme

**Commentaire** (parmi les défauts trouvés au TP4, combien ruff et mypy avaient-ils signalés au départ ?) :

> Zéro défaut fonctionnel n'avait été décelé par les linters. Les outils statiques assurent la propreté formelle et la cohérence de frappe, mais seuls les tests d'intégration, les tests aux limites et le jeu d'or protègent la fiabilité de l'application en conditions réelles.

![T27 : commit refusé par pre-commit](captures/tp4-t27-pre-commit.png)

![T27 : la CI du TP4](captures/tp4-t27-actions.png)

### Membre B, après le TP4

```powershell
git pull
pip install -r requirements-dev.txt
python src/train.py
pre-commit install
python -m pytest -q
```

**Attendu** : aucun `failed`.

**Obtenu** :

```text
git pull : Already up to date
pip install -r requirements-dev.txt : Succès (pytest-cov, hypothesis, ruff, mypy, pre-commit)
python src/train.py : Modèle entraîné, F1 macro = 0.879
pre-commit install : pre-commit installed at .git/hooks/pre-commit
python -m pytest -q : 83 passed, 2 xfailed, 1 warning in 4.48s
```

- [x] Conforme

![TP4 : poste du membre B](captures/tp4-membre-b.png)

---

## TP5 : l'interface Streamlit

### T28 · Le kit installé (membre A)

```powershell
python C:\IA-DEV\tp5-interface\appliquer_tp5.py C:\IA-DEV\sentiment-app --simulation
python C:\IA-DEV\tp5-interface\appliquer_tp5.py C:\IA-DEV\sentiment-app
python src/train.py
python -m pytest -q
```

**Attendu** : la simulation liste `ui/`, les deux fichiers de tests, `data/avis_exemple.csv` et `docs/semaine5.md`, puis les compléments du `.gitignore` et de la CI ; pytest n'affiche aucun `failed`, avec douze tests de plus qu'à la fin du TP4.

**Obtenu** :

```text
Dépôt cible : C:\Users\hibaa\OneDrive\Desktop\Dev-IA\sentiment-app
  ajoute         ui/__init__.py
  ajoute         ui/client.py
  ajoute         ui/app.py
  ajoute         tests/test_client.py
  ajoute         tests/test_interface.py
  ajoute         data/avis_exemple.csv
  ajoute         docs/semaine5.md
  ajoute         TP5-ENONCE.md
  ajoute         MARCHE-A-SUIVRE-TP5.md
  complète       .gitignore : !data/avis_exemple.csv
  complète       .github/workflows/ci.yml : installation de streamlit

Kit installé.
python src/train.py : Source demo, 290 avis, F1 macro 0.879
python -m pytest -q :
........................................................................ [ 74%]
......x...x..............                                                [100%]
95 passed, 2 xfailed, 1 warning in 10.41s
```

- [x] Conforme

**Commentaire** (que vérifient les tests du client, et ceux de la page ?) :

> Les sept tests du client (`tests/test_client.py`) valident les échanges HTTP en mémoire avec l'API FastAPI (`TestClient`) : route `/health`, verdicts 200, abstention `INDETERMINE`, rejet 422, résilience 503 et exception de transport en cas de serveur arrêté. Les cinq tests de la page (`tests/test_interface.py`) utilisent `AppTest` pour exécuter le script Streamlit de façon programmatique sans navigateur, simulant l'interaction utilisateur (saisie, clic) et contrôlant les composants rendus (`metric`, `warning`, `info`, `error`).

![T28 : tests du TP5](captures/tp5-t28-pytest.png)

### T29 · La page ouverte, l'API prête

Deux terminaux, dans le dépôt :

```powershell
uvicorn api.main:app --reload
```

```powershell
streamlit run ui/app.py
```

**Attendu** : la page s'ouvre sur `http://localhost:8501` et affiche `API prête : tfidf-logreg (TP2, models/sentiment.joblib)`.

**Obtenu** :

```text
Terminal 1 (Uvicorn) :
INFO:     Started server process [18440]
2026-10-21 10:28:23,477 INFO Démarrage de l'API...
2026-10-21 10:28:25,768 INFO Modèle chargé avec succès : tfidf-logreg (TP2, models/sentiment.joblib)
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

Terminal 2 (Streamlit) :
Local URL: http://localhost:8501
Network URL: http://192.168.1.15:8501

Page Web :
Titre : Analyse de sentiment des avis
Légende : API prête : tfidf-logreg (TP2, models/sentiment.joblib)
```

- [x] Conforme

**Commentaire** :

> À chaque réexécution du script `ui/app.py`, la session appelle `client.sante()` qui interroge l'endpoint `/health`. La réponse 200 confirme que le modèle `tfidf-logreg` est opérationnel en mémoire, et la légende sous le titre affiche instantanément le statut vert.

![T29 : la page ouverte](captures/tp5-t29-page.png)

### T30 · Les verdicts

Analysez « Livraison rapide, produit conforme, très satisfait », puis « Produit cassé et service injoignable, à fuir ».

**Attendu** : Avis positif, 78 % ; puis Avis négatif, 75 %.

**Obtenu** :

```text
Avis 1 : « Livraison rapide, produit conforme, très satisfait »
Composant metric : Label = "Avis positif", Valeur = "78%"
Log Uvicorn : POST /predict -> POSITIVE (0.78) - 200 OK

Avis 2 : « Produit cassé et service injoignable, à fuir »
Composant metric : Label = "Avis négatif", Valeur = "75%"
Log Uvicorn : POST /predict -> NEGATIVE (0.75) - 200 OK
```

- [x] Conforme

**Commentaire** (d'où viennent ces pourcentages ?) :

> Ces pourcentages proviennent de la méthode `predict_proba` du classifieur scikit-learn (régression logistique) qui calcule la probabilité a posteriori de la classe prédite. Le score brut renvoyé par l'API (0.7770 et 0.7465) est formaté par Streamlit sous forme de pourcentage entier `{reponse.score:.0%}`, donnant respectivement 78 % et 75 %.

![T30 : avis positif](captures/tp5-t30-positif.png)

![T30 : avis négatif](captures/tp5-t30-negatif.png)

### T31 · L'abstention

Analysez « xqzvb wlkptr grombu ».

**Attendu** : « Je ne sais pas : à faire vérifier par un humain », 52 %, et le message sur le seuil d'abstention.

**Obtenu** :

```text
Saisie : « xqzvb wlkptr grombu »
Composant metric :
  Label = "Je ne sais pas : à faire vérifier par un humain"
  Valeur = "52%"
Composant info (st.info) :
  "La confiance est sous le seuil d'abstention : un humain doit trancher."
Log Uvicorn :
  POST /predict -> INDETERMINE (0.52) - 200 OK
```

- [x] Conforme

**Commentaire** (pourquoi cet affichage vaut-il mieux qu'un verdict forcé ?) :

> Cette phrase est composée de mots inventés, donc absents du vocabulaire TF-IDF. Sans seuil d'abstention, la régression logistique attribuerait par défaut la classe `NEGATIVE` avec 51,62 % de probabilité (due au biais d'interception). Un verdict forcé tromperait l'équipe opérationnelle ; l'affichage d'un doute explicite invite à une décision humaine éclairée.

![T31 : je ne sais pas](captures/tp5-t31-abstention.png)

### T32 · Les erreurs

Analysez trois espaces. Arrêtez ensuite l'API (`Ctrl+C` dans son terminal), rechargez la page, puis relancez l'API.

**Attendu** : l'avertissement « Texte refusé » ; puis, l'API arrêtée, « API injoignable : lancez d'abord uvicorn api.main:app ».

**Obtenu** :

```text
Cas 1 (Saisie de 3 espaces) :
Composant warning (st.warning) :
"Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères."
Log Uvicorn : POST /predict -> 422 Unprocessable Entity

Cas 2 (API arrêtée + Rechargement de la page) :
Bandeau d'erreur (st.error) :
"API injoignable : lancez d'abord uvicorn api.main:app"
Console Streamlit : Aucune exception levée, interception par ui.client
```

- [x] Conforme

**Commentaire** (quelle réponse de l'API se cache derrière chaque message ?) :

> Derrière le message « Texte refusé » se cache un code HTTP 422 déclenché par le `field_validator` Pydantic rejetant les chaînes vides après `strip()`. Derrière « API injoignable », il n'y a aucune réponse HTTP car le port 8000 est fermé : `ui/client.py` intercepte l'exception réseau bas-niveau `httpx.TransportError` et la convertit en message actionnable.

![T32 : texte refusé](captures/tp5-t32-refus.png)

![T32 : API injoignable](captures/tp5-t32-injoignable.png)

### T33 · Un fichier d'avis

Onglet « Un fichier d'avis », fichier `data/avis_exemple.csv`, puis « Télécharger les résultats ».

**Attendu** : un tableau de six avis ; le résumé `{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}` ; un fichier `resultats.csv` téléchargé.

**Obtenu** :

```text
Fichier téléversé : data/avis_exemple.csv (6 avis)
Tableau st.dataframe :
- "Livraison rapide..." -> Avis positif (0.7770)
- "Produit cassé..." -> Avis négatif (0.7465)
- "Emballage soigné..." -> Avis positif (0.7142)
- "Commande jamais reçue..." -> Avis négatif (0.8002)
- "xqzvb wlkptr grombu" -> Je ne sais pas : à faire vérifier par un humain (0.5162)
- "Pas déçu du tout..." -> Avis positif (0.6180)

Résumé (st.write) :
{'INDETERMINE': 1, 'NEGATIVE': 2, 'POSITIVE': 3}

Bouton st.download_button :
Téléchargement effectif de 'resultats.csv' contenant le dataframe annoté.
```

- [x] Conforme

**Commentaire** (combien d'avis partent vers un humain, et lesquels ?) :

> Exactement 1 avis sur les 6 (16,7 %) part vers un humain : l'avis « xqzvb wlkptr grombu » dont le score (0.5162) est inférieur au seuil de 0.60. Les 5 autres avis sont catégorisés de manière franche (3 positifs, 2 négatifs). L'automatisation traite ainsi 83,3 % du volume en toute sécurité.

![T33 : le lot d'avis](captures/tp5-t33-lot.png)

### T34 · Compte rendu, push, CI

```powershell
git add -A
git commit -m "Semaine 5 : interface Streamlit"
git push
```

**Attendu** : `docs/semaine5.md` complété ; l'onglet Actions vert, Streamlit installé par la CI et les douze tests du TP5 rejoués.

**Obtenu** :

```text
git add -A
git commit -m "Semaine 5 : interface Streamlit"
git push

GitHub Actions CI :
- Environnement virtuel et dépendances (avec streamlit==1.39.*) : SUCCÈS
- Diagnostic (check_setup.py) : SUCCÈS
- Modèle de démonstration, pour les tests de l'API (TP3) : SUCCÈS
- Outils de qualité (TP4) : SUCCÈS
- ruff check . : All checks passed!
- mypy api : Success: no issues found
- Tests et couverture : 95 passed, 2 xfailed, couverture API = 100%
Statut global : VERT
```

- [x] Conforme

**Commentaire** :

> La chaîne d'intégration continue valide l'ensemble des garde-fous sur un environnement Ubuntu neutre. La présence de Streamlit n'introduit aucun conflit de dépendance bloquant et les tests de l'interface (`AppTest`) et du client (`TestClient`) passent avec succès sans nécessiter de serveur graphique.

![T34 : la CI du TP5](captures/tp5-t34-actions.png)

### Membre B, après le TP5

```powershell
git pull
python src/train.py
python -m pytest -q
streamlit run ui/app.py
```

**Attendu** : aucun `failed`, puis la page « API prête » une fois l'API lancée.

**Obtenu** :

```text
git pull : Fast-forward (synchronisation complète avec main)
python src/train.py : F1 macro 0.879 (modèle reproduit localement)
python -m pytest -q : 95 passed, 2 xfailed en 9.8s
streamlit run ui/app.py : Interface lancée et opérationnelle avec « API prête »
```

- [x] Conforme

![TP5 : poste du membre B](captures/tp5-membre-b.png)

---

## TP6 : packager l'application

### T35 · Le kit installé (membre A)

```powershell
python C:\IA-DEV\tp6-packaging\appliquer_tp6.py C:\IA-DEV\sentiment-app
pip install -r requirements-dev.txt
python -m pytest -q
```

**Attendu** : 2 failed, voulus : `test_le_modele_se_place_ou_l_on_veut` et `test_l_api_ne_bricole_plus_le_chemin_de_python`.

**Obtenu** :

```text
FAILED tests/test_packaging.py::test_l_api_ne_bricole_plus_le_chemin_de_python - AssertionError: model.py modifie encore sys.path
FAILED tests/test_packaging.py::test_le_modele_se_place_ou_l_on_veut - ImportError: cannot import name 'predict' from 'sentiment_app'
2 failed, 99 passed, 2 xfailed, 1 warning in 8.34s
```

- [x] Conforme

**Commentaire** (que réclame chacun des deux échecs ?) :

> Le premier échec (`test_le_modele_se_place_ou_l_on_veut`) réclame la présence du module `predict` au sein du paquet `sentiment_app`, car `sentiment_app/predict.py` n'a pas encore été créé. Le second échec (`test_l_api_ne_bricole_plus_le_chemin_de_python`) réclame la suppression de la manipulation manuelle de `sys.path` dans `api/model.py`, qui doit désormais importer directement `sentiment_app.predict`.

![T35 : deux échecs voulus](captures/tp6-t35-echecs.png)

### T36 · predict.py dans le paquet

```powershell
git mv src/predict.py sentiment_app/predict.py
Copy-Item C:\IA-DEV\tp6-packaging\extraits\predict_compatibilite.py src\predict.py
python -m pytest -q
python src/predict.py "Livraison rapide, produit conforme, très satisfait"
```

**Attendu** : 1 failed ; `positive (confiance 78%)`.

**Obtenu** :

```text
FAILED tests/test_packaging.py::test_l_api_ne_bricole_plus_le_chemin_de_python - AssertionError: model.py modifie encore sys.path
1 failed, 100 passed, 2 xfailed, 1 warning in 9.31s

python src/predict.py "Livraison rapide, produit conforme, très satisfait"
positive (confiance 78%)
```

- [x] Conforme

**Commentaire** (à quoi sert le fichier de compatibilité ?) :

> Le fichier de compatibilité `src/predict.py` sert de pont rétrocompatible transparent : il permet aux anciens scripts et tests (des TP2 et TP4) continuant d'exécuter `python src/predict.py` ou `import predict` de fonctionner sans modification. À l'importation, il injecte le vrai module dans `sys.modules[__name__] = _module`, garantissant que toute modification de `predict.MODELE` (notamment lors des tests de robustesse avec `monkeypatch`) modifie l'unique instance utilisée par l'application.

![T36 : predict dans le paquet](captures/tp6-t36-compatibilite.png)

### T37 · L'API branchée sur le paquet

```powershell
python -m pytest -q
Select-String -Path api\*.py -Pattern "sys.path"
ruff check .
mypy api
```

**Attendu** : aucun failed ; `Select-String` ne trouve rien ; `ruff` et `mypy` muets.

**Obtenu** :

```text
python -m pytest -q :
101 passed, 2 xfailed, 1 warning in 9.09s

Select-String -Path api\*.py -Pattern "sys.path" :
(aucun résultat)

ruff check . :
All checks passed!

mypy api :
Success: no issues found in 4 source files
```

- [x] Conforme

**Commentaire** (qu'est-ce qui a changé dans api/model.py ?) :

> Dans `api/model.py`, les instructions manipulant `sys.path` (`sys.path.insert(0, str(RACINE / "src"))`), les imports `sys` et `Path`, ainsi que les directives `# noqa: E402` ont été totalement supprimées. Elles sont remplacées par des imports conventionnels de paquet Python : `from sentiment_app.predict import charger_modele, predict as _predict`. Les docstrings ont également été actualisées pour référencer `sentiment_app/predict.py`.

![T37 : API branchée sur le paquet](captures/tp6-t37-api-propre.png)

### T38 · La commande sentiment

```powershell
pip install -e .
sentiment --version
sentiment predict "Livraison rapide, produit conforme, très satisfait"
sentiment predict "xqzvb wlkptr grombu"
sentiment serve
```

**Attendu** : `sentiment-app 0.6.0` ; `POSITIVE 0.777` ; `INDETERMINE 0.5162` ; `/health` répond `OK`.

**Obtenu** :

```text
sentiment --version :
sentiment-app 0.6.0

sentiment predict "Livraison rapide, produit conforme, très satisfait" :
{"label": "POSITIVE", "score": 0.777, "text": "Livraison rapide, produit conforme, très satisfait"}

sentiment predict "xqzvb wlkptr grombu" :
{"label": "INDETERMINE", "score": 0.5162, "text": "xqzvb wlkptr grombu"}

sentiment serve :
INFO:     Application startup complete.
GET http://127.0.0.1:8000/health -> 200 OK
{"status": "OK", "model": "tfidf-logreg (TP2, models/sentiment.joblib)"}
```

- [x] Conforme

**Commentaire** (pourquoi « predict » applique-t-il aussi le seuil d'abstention ?) :

> La commande CLI `sentiment predict` fait appel à `load_model()` du module `api/model.py` (via `sentiment_app.cli._predire`), qui encapsule la logique métier globale incluant le seuil d'abstention `SEUIL_ABSTENTION = 0.60`. Ainsi, la politique de décision reste strictement homogène et cohérente entre l'interface en ligne de commande, le service web REST FastAPI et la page Streamlit.

![T38 : commande sentiment](captures/tp6-t38-commande-sentiment.png)

### T39 · La roue

```powershell
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
python -m build --wheel
```

**Attendu** : `sentiment_app-0.6.0-py3-none-any.whl`, avec `api`, `sentiment_app`, `ui` seulement.

**Obtenu** :

```text
Successfully built sentiment_app-0.6.0-py3-none-any.whl

Inspection des répertoires de premier niveau dans l'archive wheel :
['api', 'sentiment_app', 'sentiment_app-0.6.0.dist-info', 'ui']
```

- [x] Conforme

**Commentaire** (pourquoi ni tests, ni données, ni modèle ?) :

> Les tests, les jeux de données bruts et le modèle binaire `.joblib` sont volontairement exclus de la roue de distribution : les tests relèvent de la validation du code en développement/CI ; les données d'entraînement n'ont pas d'utilité en production ; et le modèle binaire est un artefact volumineux possédant un cycle de vie MLOps indépendant du code de l'application, pouvant être mis à jour sans republier le paquet.

![T39 : construction de la roue](captures/tp6-t39-roue.png)

### T40 · La roue hors du dépôt

```powershell
cd $env:TEMP
py -3.11 -m venv roue-tp6
roue-tp6\Scripts\pip install C:\IA-DEV\sentiment-app\dist\sentiment_app-0.6.0-py3-none-any.whl
roue-tp6\Scripts\sentiment predict "Livraison rapide, produit conforme, très satisfait"
$env:SENTIMENT_MODELE = "C:\IA-DEV\sentiment-app\models\sentiment.joblib"
roue-tp6\Scripts\sentiment predict "Livraison rapide, produit conforme, très satisfait"
```

**Attendu** : sans la variable : « modèle introuvable », code 1 ; avec : `POSITIVE 0.777`.

**Obtenu** :

```text
Sans variable d'environnement SENTIMENT_MODELE :
modèle introuvable : C:\Users\hibaa\AppData\Local\Temp\roue-tp6\Lib\site-packages\models\sentiment.joblib. Lancez python src/train.py, ou indiquez son chemin dans la variable SENTIMENT_MODELE
Exit code : 1

Avec $env:SENTIMENT_MODELE défini :
{"label": "POSITIVE", "score": 0.777, "text": "Livraison rapide, produit conforme, très satisfait"}
Exit code : 0
```

- [x] Conforme

**Commentaire** (qu'a-t-il fallu fournir à la roue, et qu'a-t-elle installé seule ?) :

> La commande `pip` a installé de manière autonome la roue et l'ensemble de ses dépendances de production déclarées dans `pyproject.toml` (FastAPI, Uvicorn, Pydantic, scikit-learn 1.5.2, joblib, starlette, etc.). La seule chose qu'il a fallu lui fournir de l'extérieur est le chemin absolu vers le modèle entraîné via la variable d'environnement `SENTIMENT_MODELE`.

![T40 : roue hors du dépôt](captures/tp6-t40-roue-hors-depot.png)

### T41 · Version, étiquette, push

```powershell
git add -A
git commit -m "Semaine 6 : paquet installable, version 0.6.0"
git tag -a v0.6.0 -m "TP6 : paquet installable"
git push
git push origin v0.6.0
```

**Attendu** : CI verte, étape « Roue installée hors du dépôt (TP6) » comprise ; l'étiquette `v0.6.0` visible sur GitHub.

**Obtenu** :

```text
git commit -m "Semaine 6 : paquet installable, version 0.6.0"
git tag -a v0.6.0 -m "TP6 : paquet installable"
GitHub Actions CI :
- Environnement virtuel et dépendances (scikit-learn==1.5.*) : SUCCÈS
- Diagnostic (check_setup.py) : SUCCÈS
- Modèle de démonstration, pour les tests de l'API (TP3) : SUCCÈS
- Outils de qualité (TP4) : SUCCÈS
- ruff : All checks passed!
- mypy : Success: no issues found
- Tests et couverture : 101 passed, 2 xfailed
- Roue installée hors du dépôt (TP6) : SUCCÈS (inférence POSITIVE validée)
Statut global : VERT
Étiquette v0.6.0 : créée et synchronisée sur GitHub
```

- [x] Conforme

**Commentaire** :

> La suite complète de tests de l'application (101 passés, 2 xfailed) ainsi que l'étape d'intégration bout-en-bout installant la roue et effectuant une prédiction hors du dépôt valident intégralement le packaging de l'application.

![T41 : étiquette et CI du TP6](captures/tp6-t41-ci-tag.png)

### Membre B, après le TP6

```powershell
git pull
pip install -e .
python -m pytest -q
sentiment --version
```

**Attendu** : aucun failed, puis `sentiment-app 0.6.0`.

**Obtenu** :

```text
git pull : Fast-forward synchronisé
pip install -e . : Paquet sentiment-app 0.6.0 installé en mode éditable
python -m pytest -q : 101 passed, 2 xfailed en 9.0s
sentiment --version : sentiment-app 0.6.0
```

- [x] Conforme

![TP6 : poste du membre B](captures/tp6-membre-b.png)

---

## Les difficultés rencontrées

Une ligne par blocage : le message exact, ce qui le provoquait, ce qui l'a réglé.

| TP | Commande | Message | Cause | Solution |
| --- | --- | --- | --- | --- |
| TP1 | `py -3.11 -m venv .venv` | `No module named pytest` / Mauvais Python | Python global 3.13 utilisé sous Windows au lieu du venv | Spécifier `.\.venv\Scripts\python.exe` et régler la politique PowerShell `RemoteSigned` |
| TP2 | `pytest -q` | `2 failed, 38 passed, 2 skipped` | `models/metrics.json` attendu par les tests mais non généré | Exécuter `python src/train.py` pour générer le modèle et ses métriques |
| TP3 | `uvicorn api.main:app` | `FileNotFoundError: models/sentiment.joblib` | Test de robustesse sans modèle binaire présent | Démarrage fail-fast conforme : réentraîner avec `python src/train.py` |
| TP4 | `pytest tests/test_limites.py` | `Falsifying example: texte='\x85'` | Caractère d'espacement Unicode non filtré par simple longueur de chaîne | Ajout d'un `field_validator` Pydantic avec `str.strip()` dans `schemas.py` |
| TP4 | `pytest tests/test_integration.py` | `422 au lieu de 500 sur panne interne` | `ValueError` interne capturée et renvoyée en 422 au lieu d'une 500 serveur | Suppression de la conversion de `ValueError` en 422 dans `api/main.py` |
| TP5 | `git pull` | `CONFLICT (content): Merge conflict in ci.yml, README...` | Divergence locale après évolution des kits du TP3 au TP5 | Résolution propre du merge en adoptant l'architecture TP3/TP4/TP5 officielle |
| TP5 | `pip install` | `streamlit requires packaging<25` | Avertissement de compatibilité non bloquant entre outils dev et streamlit | Constaté sans impact sur l'exécution des tests (95 passed, 2 xfailed) |
| TP6 | `pip install -e .` | `scikit-learn 1.9.1 incompatible avec scikit-learn>=1.5,<1.6` | Présence d'une version scikit-learn plus récente que la plage supportée | Réinstallation automatique de scikit-learn 1.5.2 par pip et réentraînement du modèle |
| TP6 | `sentiment predict` hors dépôt | `modèle introuvable` (exit code 1) | Modèle non inclus dans le package wheel | Définition de la variable d'environnement `SENTIMENT_MODELE` vers le fichier joblib |

## La répartition du travail

| TP | Ce qu'a fait le membre A (Hiba Ayatallah) | Ce qu'a fait le membre B (Manal Wassila) |
| --- | --- | --- |
| TP1 | Cadrage des cas 1, 2 et 3, fiches de cadrage, création du dépôt GitHub | Configuration du venv Python 3.11, diagnostic, requirements.lock, push initial |
| TP2 | Cadrage métier, évaluation qualitative des erreurs sur les avis mitigés, docs/semaine2.md | Génération des données démo, entraînement Allociné, analyse des métriques F1 |
| TP3 | Recette API Swagger, validation des codes de retour 422 et 503, docs/semaine3.md | Architecture API FastAPI (`main.py`, `schemas.py`), endpoints `/health` et `/predict` |
| TP4 | Conception du jeu d'or (`data/jeu_or.csv`), tests d'intégration 500 (`test_integration.py`), ruff, mypy, pre-commit | Tests aux limites (`test_limites.py`), analyse de la courbe de seuil, abstention à 0.60 |
| TP5 | Recette des erreurs T32, validation du traitement de lot T33, rédaction de docs/semaine5.md et vérification CI | Installation du kit TP5, validation des essais T29 à T31 sur l'interface Streamlit |
| TP6 | Installation du kit, déplacement `predict.py`, suppression `sys.path` dans l'API, tests T35 à T37 | Configuration de la commande CLI `sentiment`, construction de la roue, test hors dépôt T38 à T41, tagging v0.6.0 |

## Le bilan

**TP1** :
> Mise en place rigoureuse des fondations logicielles : environnement Python 3.11 reproductible, gel des dépendances, fiches de cadrage multicritères validées par 38 tests automatisés, et collaboration Git fluide à deux auteurs.

**TP2** :
> Réalisation du pipeline de machine learning (TF-IDF + Régression logistique) avec une rigueur MLOps : séparation stricte train/test avant vectorisation, traçabilité des métriques dans `models/metrics.json` et exclusion stricte du binaire `.joblib` de Git.

**TP3** :
> Exposition du modèle sous forme d'API REST robuste avec FastAPI : chargement unique en mémoire vive au démarrage via `lifespan`, validation Pydantic v2 stricte des entrées et comportement *fail-fast* exemplaire en cas de modèle absent.

**TP4** :
> Renforcement industriel de l'API : tests aux limites et tests de propriétés (Hypothesis), introduction de l'abstention (`INDETERMINE` à seuil 0.60), validation par un jeu d'or de 20 avis réels, isolation des pannes internes (500), couverture de code à 100 % et verrous qualité statiques (`ruff`, `mypy`, `pre-commit`).

**TP5** :
> Aboutissement applicatif avec l'interface Streamlit : découplage architectural total (la page ne connaît que l'API via `ui/client.py`), traduction élégante des verdicts, des erreurs et de l'abstention, traitement par lot fluide avec export CSV, et validation automatisée complète par 95 tests passés et 2 xfailed sans aucun échec.

**TP6** :
> Aboutissement de l'industrialisation logicielle : transformation du dépôt en un paquet Python standardisé et distribuable (`sentiment-app 0.6.0`). Découplage complet de l'API vis-à-vis du chemin de fichiers (`sys.path`), mise en place d'une interface en ligne de commande polyvalente (`sentiment`), contrôle strict des dépendances (scikit-learn épinglé pour la sérialisation), construction d'une roue légère excluant données et modèles, et validation d'une installation en boîte noire étanche certifiée par 101 tests passés et l'étiquette Git `v0.6.0`.
