# Compte rendu : Tests approfondis, qualité logicielle et garde-fous (TP4)

**Binôme :** Hiba Ayatallah ([@HibaAyatallah](https://github.com/HibaAyatallah)) et Manal Wassila ([@manalwassila](https://github.com/manalwassila))  
**Dépôt :** [https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila](https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila)  
**Date :** 21 octobre 2026  
**Module :** Développement et déploiement d'applications intelligentes — Pr. A. Larhlimi  

---

## 1. Introduction et Objectifs du TP4

Alors que les TP précédents ont permis de cadrer le besoin métier (TP1), d'entraîner et évaluer un modèle linéaire de traitement du langage naturel (TP2) et de l'exposer sous forme d'API REST avec FastAPI (TP3), le **TP4 marque le passage du prototype expérimental à l'application logicielle robuste prête pour la production**.

L'objectif cardinal du TP4 n'est pas d'ajouter de nouvelles fonctionnalités visibles pour l'utilisateur, mais d'**éprouver la résistance du service, de traquer ses failles aux frontières, et d'installer un arsenal de garde-fous automatisés** :
1. **Sécuriser le contrat d'interface (HTTP & Pydantic)** : garantir que toute entrée aberrante ou malicieuse est rejetée de manière uniforme avec un code HTTP 422 standardisé, sans jamais faire tomber le serveur.
2. **Gérer l'incertitude algorithmique (Abstention)** : introduire un troisième verdict métier, `INDETERMINE`, lorsque le modèle manque de confiance, et éliminer le biais statistique sur les textes dépourvus de vocabulaire connu.
3. **Valider les cas réels complexes (Jeu d'or)** : soumettre l'algorithme à 20 avis rédigés manuellement par le binôme, comportant des pièges linguistiques (négations, ironie, avis mitigés, décalages lexicaux).
4. **Isoler et protéger le serveur (Intégration & Résilience)** : simuler des pannes matérielles ou logicielles du modèle pour s'assurer qu'elles renvoient un code HTTP 500 générique sans faire fuiter de détails techniques internes (*fail-safe*).
5. **Automatiser l'exigence de qualité (Linters, Typage & CI)** : verrouiller le dépôt avec `ruff`, `mypy`, `pre-commit` et imposer un seuil de couverture de code de 95 % en Intégration Continue.

---

## 2. Le contrat d'entrée et les tests aux limites (Contrôles T22 & T23)

### 2.1 Le diagnostic du problème initial
Au TP3, la route `POST /predict` s'appuyait sur la validation native de Pydantic (`min_length=1`). Deux faiblesses majeures subsistaient :
- **Incohérence du format de réponse 422 :** Lorsqu'un client transmettait une chaîne vide `""` ou un type invalide `42`, Pydantic interceptait la faute et retournait une liste structurée d'objets `[{"loc": ..., "msg": ..., "type": ...}]`. En revanche, une chaîne composée uniquement d'espaces (`"   "`) passait le filtre de Pydantic car sa longueur était supérieure à 1 ; elle était ensuite interceptée plus bas par le `predict()` du TP2 qui levait un `ValueError("texte vide")`. Ce dernier était capturé par `api/main.py` et renvoyé sous la forme d'un dictionnaire brut `{"detail": "texte vide"}`. Le client recevait donc deux formats de 422 différents pour une même classe d'erreur.
- **Faille aux caractères blancs exotiques :** La fonction Python standard `str.strip()` élimine de nombreux caractères d'espacement Unicode que la simple vérification de longueur de chaîne ne filtre pas.

### 2.2 Tests paramétrés aux frontières (`tests/test_limites.py`)
Nous avons conçu un jeu de test paramétré couvrant 8 cas stricts aux frontières du contrat d'interface :

```python
CAS = [
    pytest.param(en_json({"text": ""}), 422, id="texte-vide"),
    pytest.param(en_json({"text": "   "}), 422, id="espaces-seuls"),
    pytest.param(en_json({"text": "a"}), 200, id="un-caractere"),
    pytest.param(en_json({"text": "a" * 2000}), 200, id="2000-caracteres"),
    pytest.param(en_json({"text": "a" * 2001}), 422, id="2001-caracteres"),
    pytest.param(en_json({}), 422, id="champ-absent"),
    pytest.param(en_json({"text": 42}), 422, id="autre-type"),
    pytest.param(b"pas du json", 422, id="corps-invalide"),
]
```

Chaque rejet en 422 est explicitement validé par la fonction `forme_standard(corps)` qui vérifie que `detail` est bien une liste d'objets comportant impérativement les clés `loc`, `msg` et `type`.

### 2.3 Tests basés sur les propriétés (*Property-Based Testing* avec Hypothesis)
Pour dépasser l'échantillonnage manuel, nous avons mobilisé la bibliothèque `hypothesis` afin de générer aléatoirement des centaines d'exemples de requêtes :
1. **Propriété 1 (Textes valides) :** Tout texte de 1 à 2000 caractères contenant au moins un caractère non blanc (`filter(lambda s: s.strip())`) doit impérativement recevoir un code HTTP 200, une étiquette valide du contrat (`POSITIVE`, `NEGATIVE`, `INDETERMINE`) et un score normalisé entre 0.0 et 1.0 (150 tirages aléatoires).
2. **Propriété 2 (Textes blancs purs) :** Tout texte composé exclusivement de caractères d'espacement parmi la table `BLANCS` (espaces insécables, tabulations, sauts de ligne, espaces idéographiques, caractère NEL `\x85`) doit recevoir un code HTTP 422 sous forme standardisée (100 tirages aléatoires).

> **Le contre-exemple déniché par Hypothesis :**  
> Lors de l'exécution initiale, Hypothesis a instantanément mis en défaut l'API avec le contre-exemple minimal `texte='\x85'`. Ce caractère Unicode (Next Line) était ignoré par la validation de surface de l'API mais nettoyé par `str.strip()` dans le modèle, confirmant la nécessité d'un filtre strict en amont.

### 2.4 La correction dans `api/schemas.py`
Le correctif a consisté à intégrer un validateur de champ Pydantic v2 sur le schéma de requête :

```python
@field_validator("text")
@classmethod
def refuser_les_blancs(cls, valeur: str) -> str:
    """Même règle que predict() du TP2 (str.strip) : un texte fait de blancs est vide."""
    if not valeur.strip():
        raise ValueError("texte vide une fois les blancs retirés")
    return valeur
```

**Résultat :** `tests/test_limites.py` passe de `2 failed, 8 passed` à **`10 passed` avec succès**, validé trois fois d'affilée (Contrôles T22 et T23).

---

## 3. L'arbitrage du seuil d'abstention et le Jeu d'or (Contrôles T24 & T25)

### 3.1 Le problème des textes sans vocabulaire
En soumettant à l'API un texte inventé ou dépourvu de tout mot-clé de la langue française (`"xqzvb wlkptr grombu"`), l'API du TP3 renvoyait :
```json
{"label": "NEGATIVE", "score": 0.5162, "text": "xqzvb wlkptr grombu"}
```
Ce comportement paradoxal s'explique mathématiquement : aucun terme n'étant présent dans le dictionnaire TF-IDF, le vecteur de caractéristiques est strictement nul. Le modèle applique alors uniquement l'ordonnée à l'origine (*intercept*) de la régression logistique, qui penche légèrement du côté négatif (0.5162 contre 0.4838). Donner une prédiction tranchée sur un avis que le modèle est incapable de comprendre représente un danger majeur en production.

### 3.2 Analyse de la courbe du seuil d'abstention
Le script [src/courbe_seuil.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/src/courbe_seuil.py) évalue l'impact d'un seuil de confiance minimal sur le jeu de test de démonstration (58 avis) :

| Seuil | Réponses automatiques | Part traitée | Exactitude | Erreurs restantes | Avis renvoyés à l'humain |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **0.50** | 58 | 100.0 % | 87.9 % | 7 | 0 (0.0 %) |
| **0.55** | 47 | 81.0 % | 91.5 % | 4 | 11 (19.0 %) |
| **0.60** | **42** | **72.4 %** | **95.2 %** | **2** | **16 (27.6 %)** |
| **0.65** | 41 | 70.7 % | 97.6 % | 1 | 17 (29.3 %) |
| **0.70** | 37 | 63.8 % | 100.0 % | 0 | 21 (36.2 %) |

**Justification du seuil retenu (0.60) :**
- Le seuil de **0.60** réalise le compromis idéal pour notre cas d'usage de relation client : il élimine **71.4 % des erreurs** (les erreurs chutent de 7 à seulement 2) et porte l'exactitude de 87.9 % à 95.2 %, tout en automatisant près de trois quarts des avis reçus (72.4 %).
- Fixer le seuil à 0.70 permettrait certes d'atteindre 100 % d'exactitude sur le lot de test, mais au prix de bloquer plus d'un tiers du trafic (36.2 %), provoquant un engorgement contre-productif de l'équipe de conseillers humains.

### 3.3 Implémentation du verdict `INDETERMINE`
Dans [api/model.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/api/model.py), nous avons défini la constante `SEUIL_ABSTENTION = 0.60` et adapté la méthode de prédiction :
```python
def predict(self, text: str) -> Prediction:
    r = _predict(text)
    label: Label = "INDETERMINE" if r["score"] < SEUIL_ABSTENTION else CORRESPONDANCE[r["label"]]
    return {"label": label, "score": r["score"], "text": text[:100]}
```
Désormais, toute requête sans vocabulaire ou ambiguë reçoit immédiatement :
```json
200 OK
{"label": "INDETERMINE", "score": 0.5162, "text": "xqzvb wlkptr grombu"}
```

### 3.4 Constitution et validation du Jeu d'or (`data/jeu_or.csv`)
Un « Jeu d'or » (*Golden Dataset*) est une collection de référence d'avis rédigés manuellement par le binôme, jamais vus par le modèle pendant son entraînement, permettant de mesurer sa pertinence métier.

Notre jeu d'or contient **20 avis**, dont **6 cas réputés difficiles** :
1. **Négation simple :** *"Pas déçu du tout, je recommande"* $\rightarrow$ Attendu `POSITIVE` (Score: 0.62, prédiction juste).
2. **Négation trompeuse (Erreur connue déclarée) :** *"Je ne recommande pas ce vendeur"* $\rightarrow$ Attendu `NEGATIVE`. Prédit à tort `POSITIVE` (0.69). Le sac de mots retient la forte présence du terme *"recommande"* et ignore la portée négative de *"ne... pas"*. Déclaré en `xfail(strict=True)`.
3. **Ironie :** *"Arrivé cassé, bravo le transporteur"* $\rightarrow$ Attendu `NEGATIVE` (Score: 0.63, prédiction juste grâce au poids prépondérant de *"cassé"*).
4. **Avis mitigé :** *"Parfait au déballage, sauf que ensuite il se casse au bout de deux utilisations"* $\rightarrow$ Attendu `NEGATIVE` (Score: 0.89, prédiction juste).
5. **Autre domaine (Cinéma, abstention) :** *"Un film magnifique, les acteurs sont excellents"* $\rightarrow$ Attendu `POSITIVE` (Score: 0.56 < 0.60 $\rightarrow$ `INDETERMINE`, l'abstention prévient l'erreur).
6. **Autre domaine (Cinéma, erreur connue déclarée) :** *"Scénario ennuyeux, je me suis endormi avant la fin"* $\rightarrow$ Attendu `NEGATIVE`. Le vocabulaire cinématographique étant absent du corpus e-commerce, le modèle hésite et classe positivement (0.66). Déclaré en `xfail(strict=True)`.

**Bilan d'exécution ([src/bilan_jeu_or.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/src/bilan_jeu_or.py)) :**
- **15 avis justes** (75.0 %)
- **3 abstentions** (15.0 %)
- **2 erreurs franches déclarées** (10.0 %)
- **0 erreur franche imprévue**

La suite [tests/test_jeu_or.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/tests/test_jeu_or.py) affiche : **`19 passed, 2 xfailed in 2.17s`** (aucun échec).

---

## 4. Tests d'intégration et Couverture de Code (Contrôle T26)

### 4.1 Scénarios d'intégration réels (`tests/test_integration.py`)
Contrairement aux tests unitaires isolés, les tests d'intégration valident l'API dans ses conditions réelles d'exploitation :
- **Démarrage réel (`test_demarrage_reel_charge_le_modele`) :** validation de l'exécution complète du contexte asynchrone `lifespan`.
- **Modèle manquant au démarrage (`test_modele_absent_l_api_refuse_de_demarrer`) :** le contrôle T20 est automatisé via `monkeypatch`. L'API lève bien `FileNotFoundError` et refuse net d'ouvrir son port.
- **Modèle déchargé en cours d'exécution (`test_modele_non_charge_repond_503`) :** si `app.state.classifier` devient `None`, l'API répond systématiquement avec le code HTTP 503 (*Service Unavailable*).
- **Gestion des pannes du modèle (`test_modele_en_panne_repond_500`) :** injection d'un mock `ModeleEnPanne` levant une `RuntimeError` ou une `ValueError("bug interne")`.
- **Protection contre les modèles tiers (`test_classes_inconnues_l_api_refuse_de_demarrer`) :** si un modèle tiers avec des classes différentes (ex. `["neg", "pos"]`) est injecté, l'API refuse de démarrer dès le constructeur.

### 4.2 Sécurisation des codes d'erreur et suppression de fuite d'information
Au TP3, `api/main.py` capturait `ValueError` pour renvoyer du 422. En cas de bug interne du modèle levant une `ValueError`, l'API renvoyait un code 422 et exposait le message interne d'erreur au client.

Nous avons corrigé cette faille de sécurité :
```python
try:
    result = clf.predict(request.text)
except Exception:
    logger.exception("Erreur lors de la prédiction")
    raise HTTPException(status_code=500, detail="Erreur interne du serveur") from None
```
Grâce à `from None`, l'API masque la pile d'appels technique, journalise l'anomalie côté serveur et renvoie un code HTTP 500 neutre.

### 4.3 Mesure de couverture de test (`pytest-cov`)
L'exécution de la suite de tests avec analyse de couverture donne un résultat parfait :

```text
Name             Stmts   Miss  Cover   Missing
----------------------------------------------
api\main.py         39      0   100%
api\model.py        27      0   100%
api\schemas.py      20      0   100%
----------------------------------------------
TOTAL               86      0   100%

Required test coverage of 95% reached. Total coverage: 100.00%
83 passed, 2 xfailed, 1 warning in 4.43s
```
L'exclusion de la commande `if __name__ == "__main__":` via `# pragma: no cover` est pleinement justifiée car elle concerne le lancement direct en console locale, non exécutable sous pytest.

---

## 5. Qualité statique, Typage strict et CI (Contrôle T27)

### 5.1 Typage rigoureux avec `mypy`
Initialement, `mypy api` ne levait aucune alerte car `src/predict.py` retournait un simple dictionnaire non typé (`dict`), traité comme `Any`.

Pour verrouiller les types, nous avons introduit :
- Un `TypedDict Resultat` dans [src/predict.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/src/predict.py) (`label: str`, `score: float`).
- Un `TypedDict Prediction` dans [api/model.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/api/model.py).
- Un type `Label = Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]` dans [api/schemas.py](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/api/schemas.py).

`mypy api` a immédiatement révélé que la méthode `.upper()` sur le retour du modèle n'était pas garantie de correspondre aux types littéraux. Nous l'avons remplacée par le dictionnaire de correspondance explicite `CORRESPONDANCE`, validé dès le chargement du modèle. `mypy api` affiche désormais :
```text
Success: no issues found in 4 source files
```

### 5.2 Linter et formateur avec `ruff`
Nous avons passé au crible l'ensemble du projet avec `ruff check .` :
- Élimination des imports inutilisés (`sklearn.metrics.ConfusionMatrixDisplay`).
- Sécurisation des boucles parallèles `zip(..., strict=True)` dans `src/evaluate.py`.
- Renommage de la variable ambiguë `l` en `ligne` dans `tests/test_cadrage.py` et `tests/test_environment.py`.
- Tri et structuration des blocs d'imports selon PEP 8.
- Résultat : **`All checks passed!`** sur la totalité de l'arborescence.

### 5.3 Crochet de pré-commit (`pre-commit`)
Le fichier [.pre-commit-config.yaml](file:///c:/Users/manal/OneDrive/Desktop/Dev-AI/sentiment-app/.pre-commit-config.yaml) a été installé dans les crochets Git locaux (`pre-commit install`). À chaque tentative de `git commit`, les linters `ruff` et `mypy` s'exécutent automatiquement et bloquent la transaction en cas de non-respect des règles.

### 5.4 Extension de l'Intégration Continue (`.github/workflows/ci.yml`)
Le workflow GitHub Actions intègre désormais la chaîne complète de qualification logicielle :
```yaml
      - name: Modèle de démonstration, pour les tests de l'API (TP3)
        run: . .venv/bin/activate && python src/make_demo.py && python src/train.py
      - name: Outils de qualité (TP4)
        run: . .venv/bin/activate && pip install -r requirements-dev.txt
      - name: ruff
        run: . .venv/bin/activate && ruff check .
      - name: mypy
        run: . .venv/bin/activate && mypy api
      - name: Tests et couverture
        run: . .venv/bin/activate && pytest -q --cov=api --cov-report=term-missing --cov-fail-under=95
```

---

## 6. Synthèse des résultats et Bilan des Contrôles

| Contrôle | Objet du contrôle | Résultat mesuré | Conformité |
| :---: | :--- | :--- | :---: |
| **T21** | Point de départ TP4 | `1 failed, 51 passed, 1 skipped` ; 91 % couverture ; mypy vert | Conforme |
| **T22** | Rejet standardisé des blancs | `{"text": "   "}` renvoie un code 422 avec détail structuré | Conforme |
| **T23** | Propriétés Hypothesis | `10 passed` validé 3 fois consécutives sans contre-exemple | Conforme |
| **T24** | Abstention sur hors-vocabulaire | `"xqzvb wlkptr grombu"` classé `INDETERMINE` (seuil 0.60) | Conforme |
| **T25** | Jeu d'or (20 avis) | 15 justes, 3 abstentions, 2 erreurs déclarées $\rightarrow$ **0 failed** | Conforme |
| **T26** | Intégration et résilience 500 | `test_integration.py` vert ; couverture `api/` : **100.00 %** | Conforme |
| **T27** | Linters, types et suite complète | `ruff` : 0 faute ; `mypy` : 0 faute ; **83 passed, 2 xfailed** | Conforme |

### Enseignement méthodologique majeur du TP4
L'expérience du TP4 démontre la complémentarité impérative des outils de qualité logicielle :
- **Les outils statiques (`ruff`, `mypy`)** sont rapides et indispensables pour maintenir la syntaxe, la lisibilité et la cohérence des contrats de types. Cependant, ils n'ont détecté **aucun** des défauts majeurs de notre application (incohérence des codes d'erreur, absence d'abstention probabiliste, fuite d'informations de debug, modèle tiers incompatible).
- **Les tests dynamiques avancés (tests aux limites, Hypothesis, tests d'intégration et jeu d'or)** sont les seuls mécanismes capables de valider le comportement effectif d'un système intelligent face à l'imprévu et de garantir son étanchéité en environnement de production.
