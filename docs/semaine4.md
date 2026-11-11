# Semaine 4 : tests approfondis et qualité, notes du binôme

> Une à deux pages. Uniquement des chiffres issus de nos exécutions.

## 1. Couverture

- **Avant (étape A)** : 91 % de couverture globale sur le paquet `api` (63 instructions couvertes sur 69), 6 lignes jamais exécutées dans `api/main.py` : la ligne 49, les lignes 77 à 79 et les lignes 85 à 87.
- **Pour chacune, le comportement qu'aucun test ne vérifiait** :
  - **Ligne 49** (`raise HTTPException(status_code=503, detail="Modèle non chargé")`) : aucun test ne vérifiait le comportement de l'API si le modèle venait à être retiré de la mémoire (`app.state.classifier is None`) une fois le processus démarré.
  - **Lignes 77 à 79** (`except Exception:` suivi de `raise HTTPException(status_code=500, detail="Erreur interne du serveur")`) : aucun test ne simulait une panne brutale ou une exception inattendue levée par le modèle pendant l'inférence.
  - **Lignes 85 à 87** (`uvicorn.run("api.main:app", ...)`) : le bloc d'exécution directe `if __name__ == "__main__":` n'est jamais sollicité par la suite de tests `pytest`, qui importe l'objet ASGI `app` en mémoire via `TestClient`.
- **Après (étape D)** : 100 % de couverture sur l'ensemble du paquet `api` (86 instructions couvertes sur 86). Lignes légitimement exclues de la mesure : le bloc `if __name__ == "__main__":` (marqué `# pragma: no cover`) car il constitue uniquement le point d'entrée du serveur autonome en environnement de développement local.

## 2. Défauts trouvés

| Symptôme | Test qui l'a révélé | Correction |
| :--- | :--- | :--- |
| Un texte constitué uniquement d'espaces (`"   "`) renvoie un code 422, mais avec un `detail` sous forme d'une simple chaîne (`"texte vide"`) au lieu de la liste standardisée d'objets FastAPI (`[{"loc": ..., "msg": ..., "type": ...}]`). | `test_limites.py::test_frontieres_du_contrat[espaces-seuls]` et propriété hypothesis `test_tout_texte_blanc_est_refuse` | Ajout d'un validateur `@field_validator("text")` dans `api/schemas.py` (`refuser_les_blancs`) rejetant les chaînes vides après `str.strip()`. |
| Les textes sans aucun terme du vocabulaire d'apprentissage (ex. `"xqzvb wlkptr grombu"`) reçoivent une étiquette `NEGATIVE` avec un score de confiance de 0.5162, induisant en erreur les conseillers métier. | Contrôle T24 et analyse de la courbe de seuil (`courbe_seuil.py`). | Implémentation du seuil d'abstention à 0.60 dans `api/model.py` renvoyant l'étiquette `INDETERMINE`. |
| Une exception interne au modèle de type `ValueError("bug interne")` était interceptée par le bloc `except ValueError` et convertie en code 422, laissant fuiter le message technique interne vers le client HTTP. | `test_integration.py::test_modele_en_panne_repond_500[ValueError]` | Suppression du bloc `except ValueError` dans `api/main.py` ; toute panne interne est désormais capturée en 500 générique (`from None`). |
| L'API pouvait démarrer sur un modèle réentraîné avec d'autres étiquettes que `["positive", "negative"]`, brisant silencieusement le contrat d'interface. | `test_integration.py::test_classes_inconnues_l_api_refuse_de_demarrer` | Contrôle de conformité de `modele.classes_` dans `SentimentClassifier.__init__` avec levée de `ValueError` au démarrage. |

## 3. Seuil d'abstention

- **Points observés sur la courbe (`python src/courbe_seuil.py`)** :
  - **Seuil 0.50** : 58 avis traités (100 %), 7 erreurs, exactitude de 87.9 %, 0 avis envoyé à un humain.
  - **Seuil 0.60** : 47 avis traités (81.0 %), 4 erreurs, exactitude de 91.5 %, 11 avis renvoyés à un humain (19.0 %).
  - **Seuil 0.70** : 33 avis traités (56.9 %), 0 erreur, exactitude de 100.0 %, 25 avis renvoyés à un humain (43.1 %).
- **Seuil retenu** : 0.60. Part des avis envoyés à un humain : 19.0 % (11 avis sur 58).
- **Justification** : Le seuil de 0.60 constitue le point d'équilibre optimal entre automatisation et fiabilité. Il permet d'éliminer près de 43 % des erreurs (passant de 7 erreurs à 4) et d'élever l'exactitude de 87.9 % à 91.5 %, tout en maintenant un taux d'automatisation élevé (81.0 %). Choisir 0.70 atteindrait une exactitude de 100 % sur ce jeu de test mais surchargerait les équipes humaines en bloquant plus de 43 % des dossiers.

## 4. Jeu d'or

- **Bilan (`python src/bilan_jeu_or.py`)** : sur 20 avis annotés : 13 avis justes (65.0 %), 5 abstentions (25.0 %), 2 erreurs franches déclarées (10.0 %).
- **Ce que ces chiffres disent du modèle** :
  - Le modèle linéaire TF-IDF capture avec une grande précision les avis marchands directs contenant des adjectifs forts et univoques.
  - Il échoue sur les structures linguistiques complexes :
    1. **La négation portant sur un terme positif** (`"Je ne recommande pas ce vendeur"`) : la présence du terme fréquent `"recommande"` l'emporte sur la négation, générant une prédiction erronée `POSITIVE` (0.67).
    2. **Le changement de domaine thématique** (`"Scénario ennuyeux, je me suis endormi avant la fin"`) : le lexique cinématographique est absent du vocabulaire d'e-commerce, aboutissant à une mauvaise classification (score 0.65).
  - L'abstention joue son rôle de filet de sécurité sur les textes nuancés ou hors domaine (`"Un film magnifique..."`, confiance 0.51 < 0.60, ou `"Arrivé cassé, bravo le transporteur"`, confiance 0.55 < 0.60), évitant une décision algorithmique erronée.

## 5. Outils statiques

- **Remarques au départ** :
  - `ruff` : 21 remarques au total (imports inutilisés tels que `ConfusionMatrixDisplay`, absence de `strict=True` dans les fonctions `zip()`, variable ambiguë `l` dans les tests du TP1, blocs d'imports non ordonnés).
  - `mypy` : `Success: no issues found in 4 source files`. Le code semblait sain, mais cette absence d'alerte provenait du fait que `predict()` renvoyait un `dict` générique sans typage strict, désactivant de fait l'inférence de type approfondie.
- **Défauts de la partie 2 signalés par ruff et mypy** :
  - **Aucun** des quatre défauts identifiés à la partie 2 (incohérence du format 422 sur les blancs, absence de verdict `INDETERMINE` sur le hors-vocabulaire, fuite du message d'erreur interne via 422, et divergence des classes du modèle) n'a été détecté par les outils statiques.
- **Conclusion** :
  - Les analyseurs statiques comme `ruff` et `mypy` sont indispensables pour garantir l'uniformité stylistique, la propreté des dépendances et la solidité des signatures typées. Toutefois, ils sont totalement incapables de détecter les défauts de logique métier, les incohérences de contrats HTTP ou le comportement statistique d'un modèle de Machine Learning. La sécurité et la qualité en production reposent impérativement sur des tests aux limites exhaustifs, du test basé sur les propriétés (Hypothesis), des tests d'intégration réalistes et un jeu d'or soigneusement constitué.
