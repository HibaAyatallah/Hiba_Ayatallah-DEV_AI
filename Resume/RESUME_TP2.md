# Compte rendu : Du cadrage au modèle de sentiment (TP1 & TP2)

**Binôme :** Hiba Ayatallah ([@HibaAyatallah](https://github.com/HibaAyatallah)) et Manal Wassila ([@ManalWassila](https://github.com/ManalWassila))  
**Dépôt :** [https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila](https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila)  
**Date :** 14 octobre 2026  
**Module :** Développement et déploiement d'applications intelligentes — Pr. A. Larhlimi  

---

## 1. Le besoin et son cadrage

### 1.1 Le problème métier
Une équipe de relation client reçoit chaque jour plusieurs milliers d'avis de consommateurs (produits, livraisons, support technique) et les traite historiquement selon une file d'attente FIFO (premier arrivé, premier servi). Cette organisation conduit à laisser des clients mécontents sans réponse pendant plusieurs jours, augmentant le risque d'insatisfaction grave, d'attrition (*churn*) et de dégradation de la réputation de l'entreprise. L'objectif est de mettre en place un système capable d'identifier automatiquement et d'extraire les avis négatifs pour les placer en tête de file de traitement, tout en réorientant les cas incertains vers un contrôle humain.

### 1.2 Justification de l'approche technique pour le Cas 3 (Avis négatifs)
L'analyse comparative des approches d'ingénierie logicielle et d'intelligence artificielle nous a conduits à retenir le **Machine Learning supervisé classique** (traitement du langage naturel par classification statistique) plutôt que des règles métier statiques ou un modèle génératif lourd :

- **(a) Données étiquetées gratuites et abondantes :** Les plateformes d'e-commerce et de collecte d'avis associent naturellement chaque retour textuel à une note chiffrée (de 1 à 5 étoiles). Il est trivial de convertir ces notes en étiquettes binaires supervisées (1–2 étoiles = négatif, 4–5 étoiles = positif), ce qui élimine tout coût d'annotation manuelle.
- **(c) Coût par requête et volumétrie :** Avec un flux continu de plusieurs milliers d'avis quotidiens, l'utilisation d'un grand modèle de langage génératif (LLM par API commerciale) engendrerait une facture d'inférence prohibitive et une latence excessive. À l'inverse, un modèle de classification linéaire (TF-IDF + Régression Logistique) offre un coût d'inférence quasi nul, tourne localement sur CPU standard en quelques millisecondes par requête, et absorbe de fortes variations de charge sans surcoût.
- **(d) Conséquence modérée d'une erreur :** La classification ne prend pas de décision médicale ou juridique irréversible ; elle réordonne une file d'attente d'agents humains. Si un avis positif est temporairement priorisé, le préjudice est minime. Si un avis négatif est manqué, il finit de toute manière par être traité selon l'ordre conventionnel. Le risque opérationnel est donc faible et parfaitement tolérable, d'autant plus qu'un seuil de confiance permet d'isoler les avis ambigus.
- **(b) Explicabilité et auditabilité :** Bien qu'un modèle de Machine Learning soit une approximation statistique, les coefficients d'une régression logistique couplée à des n-grammes restent transparents : il est possible d'extraire les mots-clés qui ont pesé le plus lourd dans la décision, assurant une traçabilité suffisante pour les superviseurs métier.

---

## 2. L'architecture du dépôt

### 2.1 Organisation modulaire du projet
Le projet suit une organisation stricte séparant le code, les données, les spécifications, la tuyauterie de tests et les métriques d'évaluation :

```text
sentiment-app/
├── README.md, TP1-ENONCE.md, TP2-ENONCE.md, MARCHE-A-SUIVRE.md, TESTS.md
├── requirements.txt, requirements.lock, .gitignore, pytest.ini
├── .github/workflows/ci.yml       # Intégration continue automatisée (GitHub Actions)
├── docs/                          # Fiches de cadrage TP1, analyses de semaines
│   ├── cadrage/                   # cas1-pharmacie.md, cas2-reglement.md, cas3-avis-negatifs.md
│   ├── semaine2.md                # Analyse qualitative des erreurs du modèle
│   └── compte-rendu.md            # Synthèse globale du projet
├── src/                           # Code source métier du modèle
│   ├── make_demo.py               # Générateur du jeu d'avis de démonstration
│   ├── train.py                   # Entraînement et sérialisation (démo & Allociné)
│   ├── evaluate.py                # Rapport de classification et matrice de confusion
│   └── predict.py                 # Fonction d'inférence pour la production
├── tests/                         # Suite de tests automatisés (42 tests passés au TP2)
│   ├── test_environment.py       # Validation de l'environnement virtuel et des versions
│   ├── test_cadrage.py           # Conformité des fiches de cadrage
│   ├── test_git_history.py       # Vérification du travail collaboratif (deux auteurs)
│   └── test_model.py             # Validation des métriques et du comportement du modèle
├── models/                        # Artefacts de modélisation
│   ├── .gitkeep                   # Maintien du dossier dans Git
│   └── metrics.json               # Métriques validées et versionnées
└── data/                          # Données d'entraînement et d'évaluation
    ├── sample_reviews.csv         # Échantillon de test
    └── demo_reviews.csv          # Données de démo (régénérables, ignorées par Git)
```

### 2.2 Stratégie MLOps : ce qui est versionné vs non versionné
L'un des enseignements cardinaux de la démarche MLOps réside dans la gestion des trois types d'artefacts du projet :

1. **Le code et les configurations (Versionnés dans Git) :** Les scripts Python (`src/`), les tests unitaires (`tests/`), les workflows CI (`.github/`), les fiches de cadrage et `requirements.txt` constituent la propriété intellectuelle reproductible.
2. **L'environnement d'exécution (`.venv/` — Non versionné) :** Pesant plusieurs centaines de mégaoctets et dépendant du système d'exploitation hôte, il ne doit jamais être commité. Il est fidèlement reconstruit par `pip install -r requirements.txt`.
3. **Les données volumineuses et le modèle (`data/demo_reviews.csv`, `models/sentiment.joblib` — Non versionnés) :** 
   - `demo_reviews.csv` se régénère en une seconde via `python src/make_demo.py`.
   - `sentiment.joblib` pèse plusieurs mégaoctets, s'avère binaire (donc inadapté aux diffs Git) et peut être ré-entraîné à l'identique grâce au paramètre `random_state=42`. Il est donc exclu via le fichier `.gitignore`.

### 2.3 Pourquoi `models/metrics.json` est-il versionné alors que `models/sentiment.joblib` ne l'est pas ?
Cette séparation reflète le principe central de la validation en intégration continue (CI) :
- **Transporter la preuve de la qualité, pas le poids de l'artefact :** En CI, le serveur d'intégration (GitHub Actions) exécute les tests sur une machine neuve et éphémère. Il n'a pas besoin de posséder le modèle lourd pour garantir son niveau de qualité : il lit simplement `models/metrics.json` et valide que le $F_1$ macro dépasse le seuil contractuel de 0.85 (`test_f1_au_dessus_du_seuil`).
- **Traçabilité historique des performances :** Chaque commit modifiant l'entraînement documente l'évolution chiffrée de la qualité (taille du jeu, date, exactitude, rappel négatif). Git permet ainsi d'auditer les régressions de performance du modèle au fil des itérations, sans polluer l'historique avec des binaires volumineux.

---

## 3. Le modèle

### 3.1 Pipeline et reproductibilité
Le modèle d'apprentissage est encapsulé dans un `Pipeline` scikit-learn unifié associant :
1. **Un vectoriseur textuel `TfidfVectorizer` :**
   - Extraction de n-grammes de mots : unigrammes et bigrammes (`ngram_range=(1, 2)`).
   - Fréquence minimale documentaire : `min_df=2` pour filtrer le bruit et les fautes d'orthographe uniques.
   - Pondération sublinéaire (`sublinear_tf=True`) pour amortir l'influence des mots excessivement répétés.
2. **Un classifieur linéaire `LogisticRegression` :**
   - Optimisation avec équilibrage automatique des classes (`class_weight="balanced"`).
   - Convergence assurée par `max_iter=1000`.
   - Graine aléatoire fixée à `random_state=42`.

> **Bonne pratique méthodologique critique :** Le découpage en sous-ensembles d'apprentissage et de test (`train_test_split`, 80 % train / 20 % test, stratifié sur la cible) est exécuté **strictement avant toute vectorisation**. Cela garantit l'étanchéité absolue du jeu de test et évite toute fuite d'information (*data leakage*) qui gonflerait artificiellement les métriques d'évaluation.

### 3.2 Résultats comparatifs : Démonstration vs Allociné

| Métrique / Caractéristique | Jeu de Démonstration (`demo`) | Vrai Jeu Public (`allocine`) |
| :--- | :---: | :---: |
| **Volume total d'avis** | 290 avis | 20 000 avis |
| **Répartition de classe** | 145 négatifs / 145 positifs (50/50) | 10 204 négatifs / 9 796 positifs |
| **Taille de l'entraînement ($X_{train}$)** | 232 avis | 16 000 avis |
| **Taille du test ($X_{test}$)** | 58 avis | 4 000 avis |
| **Taille du vocabulaire appris** | 316 termes | **149 529 termes** |
| **Exactitude globale (*Accuracy*)** | 87.93 % | **92.05 %** |
| **Score $F_1$ macro** | **0.879** | **0.9205** (seuil exigé : 0.85) |
| **Rappel sur la classe négative** | **93.10 %** (27 / 29) | **91.13 %** |
| **Précision sur la classe négative** | 84.38 % (27 / 32) | 93.19 % |

Sur le jeu de données Allociné, le volume d'apprentissage multiplié par près de 70 permet d'enrichir considérablement le lexique (près de 150 000 n-grammes). Le modèle atteint un $F_1$ macro de **0.9205**, surpassant très confortablement le seuil d'acceptation requis de 0.85.

### 3.3 Analyse détaillée de la matrice de confusion (Jeu de démo)
Sur les 58 avis du jeu de test de démonstration, la matrice de confusion observée est la suivante :

```text
                  Prédiction : negative    Prédiction : positive
Vérité : negative                   27                        2
Vérité : positive                    5                       24
```

- **Ligne 1 (Vérité = Avis Négatif, 29 exemples) :**
  - **27 Vrais Négatifs (TN) :** 93.1 % des avis négatifs sont correctement détectés et placés immédiatement dans la file de traitement prioritaire.
  - **2 Faux Positifs (FP / Erreur critique pour le métier) :** 2 avis réellement négatifs ont été pris pour des avis positifs. Dans le scénario de relation client, ces deux clients mécontents subiront le délai de traitement ordinaire au lieu d'une prise en charge accélérée.
- **Ligne 2 (Vérité = Avis Positif, 29 exemples) :**
  - **5 Faux Négatifs (FN) :** 5 avis positifs ont été classés à tort comme négatifs. Cela encombre légèrement la file prioritaire mais ne lèse aucun client mécontent.
  - **24 Vrais Positifs (TP) :** 82.8 % des clients satisfaits sont correctement catégorisés.

---

## 4. L'analyse des erreurs

### 4.1 Typologie et inventaire des erreurs
Sur le jeu de test de 58 avis de démonstration, le modèle commet exactement **7 erreurs**. L'examen systématique de ces 7 cas révèle une régularité frappante : **100 % des erreurs surviennent sur des avis dits « mitigés »**, c'est-à-dire des avis combinant deux sentiments opposés avec une conjonction de retournement.

Exemples concrets extraits de nos données d'évaluation :
1. **Vérité = positive | Prédit = negative :**  
   *« Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme à la description. »*
2. **Vérité = positive | Prédit = negative :**  
   *« Commande jamais reçue et remboursement en attente au début, sauf que ensuite je recommande vivement. »*
3. **Vérité = negative | Prédit = positive :**  
   *« Service impeccable et livraison en avance sur le papier, sauf que ensuite produit cassé à l'arrivée. »*

### 4.2 Le mécanisme sous-jacent : l'absence d'ordre du sac de mots
L'architecture TF-IDF repose sur l'hypothèse du « sac de mots » (*bag-of-words*) :
- Le modèle compte la fréquence et la spécificité des termes, mais **ignore totalement la syntaxe, la chronologie et l'ordre des propositions**.
- Dans la phrase 3, le modèle additionne les poids positifs forts de *« impeccable »*, *« service »*, *« livraison en avance »* et les confronte au terme négatif *« cassé »*. La somme algébrique des coefficients penche du côté positif.
- Le modèle est incapable d'interpréter le rôle pivot de la locution *« sauf que ensuite »* ou *« mais finalement »*, qui annule sémantiquement la première partie du texte au profit de la conclusion. Pour un sac de mots, *« bon puis mauvais »* et *« mauvais puis bon »* produisent exactement le même vecteur de représentation.

### 4.3 Pistes de remédiation technique
Pour surmonter cette limitation structurelle sans dénaturer les performances, plusieurs évolutions seraient envisageables :
1. **Pondération positionnelle :** Accorder un coefficient multiplicateur plus élevé aux n-grammes situés dans le dernier tiers du texte (zone où se cristallise généralement le jugement de synthèse).
2. **Règles de segmentation par rupture lexicale :** Scinder l'avis au niveau des connecteurs d'opposition (*mais*, *cependant*, *or*, *sauf que*, *finalement*) et surpondérer le segment terminal.
3. **Modèles de langue contextuels séquentiels (Transformers) :** Recourir à un modèle pré-entraîné pour le français tel que **CamemBERT** ou **FlauBERT**. Grâce aux mécanismes d'attention bidirectionnelle et aux encodages positionnels, ces architectures capturent nativement la structure syntaxique et les retournements d'opinion. 

*Pourquoi ce n'était pas le sujet du TP2 :* L'objectif de la séance était d'établir une ligne de base reproductible (*baseline*), d'outiller l'évaluation en continu et de comprendre avec précision les limites d'un modèle simple, plutôt que de complexifier prématurément l'architecture.

---

## 5. L'interface et le seuil d'incertitude (Cadrage pré-TP3)

Le modèle de classification probabiliste fournit pour chaque avis un score de confiance (probabilité calibrée via la sigmoïde de la régression logistique). 

### 5.1 L'arbitrage du seuil d'incertitude
Plutôt que d'appliquer aveuglément un seuil binaire strict à $p = 0.50$ (où un avis prédit négatif à 50.1 % serait traité avec la même certitude qu'un avis à 99 %), la conception de l'application introduit un statut intermédiaire : **« à vérifier »**.

- **À un seuil bas (0.50) :** Le modèle tranche systématiquement seul. Les avis mitigés reçoivent un verdict catégorique souvent erroné, ce qui réintroduit les faux positifs critiques au sein du support client.
- **À un seuil élevé (0.75 ou 0.80) :** Le modèle ne prend de décision que sur des cas évidents. Un volume massif d'avis est renvoyé vers les agents humains, annulant le bénéfice de l'automatisation.
- **Le compromis cible retenu (0.60) :** Dès lors que la confiance du modèle descend sous 60 %, l'avis est étiqueté « à vérifier par un agent ». Ce réglage isole les cas ambigus (notamment les avis mitigés) tout en automatisant en toute sécurité plus de 80 % des flux nets.

Cette logique fera l'objet de l'implémentation complète lors du **TP3** sous forme d'une interface web interactive développée avec **Streamlit**.

---

## 6. Ce qui a échoué (Difficultés réelles et résolutions)

Conformément aux exigences de transparence méthodologique, voici les trois incidents majeurs rencontrés au cours des TP1 et TP2 :

1. **Absence de Pytest dans l'environnement Python global Windows :**
   - *Symptôme :* Lors de la première tentative d'exécution, la commande `python -m pytest -q` a renvoyé l'erreur `C:\Python313\python.exe: No module named pytest`.
   - *Cause :* La session PowerShell utilisait par défaut l'interpréteur système global (Python 3.13) dans lequel les dépendances du projet n'avaient pas été installées.
   - *Résolution :* Ciblage explicite de l'exécutable Python situé dans l'environnement virtuel du projet : `.\.venv\Scripts\python.exe -m pytest -q`.
2. **Échec initial de Contrôle C1 suite à l'application du kit TP2 :**
   - *Symptôme :* `2 failed, 38 passed, 2 skipped`.
   - *Cause :* Le script `appliquer_tp2.py` ajoute de nouveaux tests dans `test_model.py` qui recherchent le fichier `models/metrics.json`. Comme aucun entraînement n'avait encore eu lieu, l'absence du fichier générait deux échecs.
   - *Résolution :* Ce comportement était explicitement prévu par le protocole du cours. L'exécution de `python src/train.py` a généré le fichier `metrics.json`, transformant ces échecs en tests validés.
3. **Conflit de désynchronisation lors du push Git après le TP2 :**
   - *Symptôme :* Lors de la tentative de `git push`, Git a rejeté la transaction avec le message `! [rejected] main -> main (fetch first)`.
   - *Cause :* La collaboratrice du binôme avait téléversé un document de synthèse (`Resume/RESUME_TP1.pdf`) directement via l'interface web de GitHub, faisant diverger la branche distante `origin/main` de la branche locale.
   - *Résolution :* Nous avons exécuté un `git fetch origin` pour rapatrier les modifications distantes, suivi d'un `git rebase origin/main` pour rejouer proprement notre commit de TP2 au sommet de l'historique sans créer de commit de merge parasite. Le push ultérieur s'est achevé avec succès.

---

## 7. Ce que nous ferions autrement

Avec le recul acquis et dans le contexte d'une équipe produit industrielle :
1. **Adopter DVC (*Data Version Control*) :** Pour la traçabilité des jeux de données volumineux et des fichiers modèles binaires (`.joblib`), l'association de Git avec DVC adossé à un stockage d'objets (S3, GCS) permettrait de versionner fidèlement les données sans surcharger le dépôt de code.
2. **Modélisation hybride à base de règles et de ML :** Avant d'envoyer le texte au classifieur TF-IDF, un module de prétraitement syntaxique basé sur des expressions régulières ou spaCy pourrait détecter les expressions d'opposition forte (*« sauf que »*, *« mais finalement »*) afin de découper l'avis et d'orienter le modèle vers la conclusion réelle.
3. **Surveillance de la dérive (*Data & Concept Drift*) :** En production, le vocabulaire des consommateurs évolue (apparition de nouveaux produits, nouveaux bugs récurrents). Nous mettrions en place un calcul périodique de dérive de distribution (ex. via Evidently AI) déclenchant un ré-entraînement automatisé si la performance du modèle fléchit sur les données récentes.

---

## 8. Répartition du travail au sein du binôme

| Membre | Contributions et tâches prises en charge |
| :--- | :--- |
| **Hiba Ayatallah** (Membre A) | Cadrage des cas métiers (cas 1, 2 et 3), vérification de la conformité des fiches markdown, gestion du dépôt GitHub distant, documentation de synthèse de projet et validation croisée des métriques. |
| **Manal Wassila** (Membre B) | Mise en place de l'environnement virtuel local, exécution des scripts de génération de démo et d'entraînement Allociné, analyse des erreurs du modèle, validation des 42 tests pytest et synchronisation du dépôt Git. |

---

## Outils d'aide à la rédaction

Conformément à la politique d’intégrité académique, nous déclarons avoir utilisé l’assistant d’IA Antigravity uniquement pour nous aider à corriger certaines erreurs et à rédiger le compte rendu, l’ensemble du travail technique et des résultats ayant été réalisé, vérifié et validé par nos soins.
