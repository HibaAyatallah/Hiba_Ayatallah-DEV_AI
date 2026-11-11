# Compte rendu : L'interface utilisateur Streamlit et le découplage client-serveur (TP5)

**Binôme :** Hiba Ayatallah ([@HibaAyatallah](https://github.com/HibaAyatallah)) et Manal Wassila ([@manalwassila](https://github.com/manalwassila))  
**Dépôt :** [https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila](https://github.com/HibaAyatallah/Hiba_Ayatallah---Manal_Wassila)  
**Date :** 21 octobre 2026  
**Module :** Développement et déploiement d'applications intelligentes — Pr. A. Larhlimi  

---

## 1. Introduction et Objectifs du TP5

Après avoir cadré le produit d'analyse de sentiment (TP1), entraîné et mesuré un modèle reproductible (TP2), exposé ce modèle derrière une API REST asynchrone avec FastAPI (TP3), et blindé le service par des tests aux limites, un seuil d'abstention et des contrôles de qualité statique (TP4), le **TP5 dote le projet d'une interface graphique interactive destinée aux équipes métiers et aux conseillers de relation client**.

L'objectif de cette séance est de concevoir une application web ergonomique sous **Streamlit** en appliquant avec rigueur les principes d'ingénierie logicielle et d'architecture distribuée :
1. **Respect de la 3ème règle d'architecture :** La page web est un pur client HTTP. Elle n'importe jamais la fonction `predict()` ni le modèle binaire `.joblib`. Deux processus distincts tournent en parallèle : l'API sur le port 8000 et l'interface sur le port 8501.
2. **Découplage strict via un client dédié (`ui/client.py`) :** Toute la complexité réseau, les codes de statut HTTP (200, 422, 503) et les erreurs de transport sont interceptés et traduits en objets standardisés `Reponse` prêts à l'affichage.
3. **Mise en valeur des garde-fous métier :** L'interface affiche en clair l'abstention (`INDETERMINE` traduit en *« Je ne sais pas : à faire vérifier par un humain »*), protège contre les textes invalides (422) et signale immédiatement une indisponibilité de l'API.
4. **Traitement unitaire et traitement par lot :** Un premier onglet permet d'analyser un avis unique à la volée ; un second onglet permet d'ingérer un fichier CSV (`data/avis_exemple.csv`), d'afficher le tableau enrichi avec scores et verdicts, de résumer les distributions et d'exporter les résultats au format CSV.
5. **Validation automatique sans serveur graphique :** Couverture complète des fonctionnalités de l'interface par 12 nouveaux tests automatisés (`tests/test_client.py` avec `TestClient` et `tests/test_interface.py` avec `AppTest`), portant la suite globale à **95 tests validés et 2 xfailed**.

---

## 2. Architecture logicielle : Trois fichiers, trois responsabilités

Pour garantir la maintenabilité et l'indépendance des modules, l'interface utilisateur est scindée en trois composants modulaires :

```
sentiment-app/
├── ui/
│   ├── __init__.py       # Déclare 'ui' comme paquet Python exploitable
│   ├── client.py         # Couche réseau : dialogue HTTP avec l'API et traduction des réponses
│   └── app.py            # Couche de présentation : rendu des composants Streamlit
├── tests/
│   ├── test_client.py    # 7 tests du client HTTP contre l'API instanciée en mémoire
│   └── test_interface.py # 5 tests d'interface utilisateur via Streamlit AppTest
└── data/
    └── avis_exemple.csv  # 6 avis de démonstration pour le traitement par lot
```

### 2.1 Le rôle de chaque fichier

| Fichier | Responsabilité technique | Ce qu'il ne fait jamais |
| :--- | :--- | :--- |
| **`ui/__init__.py`** | Fait du dossier `ui/` un module importable (`from ui import client`). | Ne contient aucune logique métier. |
| **`ui/client.py`** | Interroge l'API via `httpx.Client`, encapsule les endpoints `/health` et `/predict`, capture les pannes réseau (`httpx.TransportError`), formate les résumés de lot. | N'affiche rien dans la page ; n'importe pas Streamlit. |
| **`ui/app.py`** | Déclare la disposition visuelle, les onglets, les champs de saisie, les métriques et les boutons d'exportation. | N'importe ni le modèle, ni scikit-learn, ni FastAPI ; ne traite aucun code HTTP directement. |

### 2.2 Le cheminement d'une requête utilisateur

Lorsqu'un conseiller client clique sur le bouton **« Analyser »** :

```
[ Utilisateur ]
       │ Clic "Analyser"
       ▼
 [ ui/app.py ] ──────────( texte )─────────► [ ui/client.py ]
       ▲                                            │ POST /predict (JSON)
       │                                            ▼
 [ ui/app.py ] ◄──( objet Reponse )───────── [ API FastAPI :8000 ]
  Rendu metric,                                     │
  info ou error                                     ▼
                                             [ api/model.py ] ──► [ src/predict.py ]
                                              (seuil 0.60)         (modèle .joblib)
```

---

## 3. Le contrat de données du client (`ui/client.py`)

Toute réponse HTTP issue de l'API est convertie en une structure de données typée `Reponse` :

```python
@dataclass
class Reponse:
    """Ce que l'interface affiche : un verdict, ou un message d'erreur lisible."""
    ok: bool
    label: str | None = None
    score: float | None = None
    message: str = ""
```

### Table de correspondance des statuts API et des affichages UI

| Statut API | Réponse brute reçue | Instance `Reponse` générée | Rendu visuel dans `ui/app.py` |
| :---: | :--- | :--- | :--- |
| **`200 OK`** | `{"label": "POSITIVE", "score": 0.777}` | `ok=True, label="POSITIVE", score=0.777` | Composant `st.metric("Avis positif", "78%")` |
| **`200 OK`** | `{"label": "INDETERMINE", "score": 0.5162}` | `ok=True, label="INDETERMINE", score=0.5162` | `st.metric("Je ne sais pas...", "52%")` + `st.info` (seuil) |
| **`422 Unprocessable`** | `{"detail": [...]}` | `ok=False, message=REFUS` | Alerte jaune `st.warning("Texte refusé : vide...")` |
| **`503 Service Unav.`** | `{"detail": "..."}` | `ok=False, message=SANS_MODELE` | Alerte rouge `st.error("Modèle non chargé...")` |
| **Panne réseau** | `httpx.TransportError` | `ok=False, message=INJOIGNABLE` | Alerte rouge `st.error("API injoignable : lancez...")` |
| **`500 Internal`** | `{"detail": "Erreur interne"}` | `ok=False, message="Erreur interne (500)"` | Alerte rouge `st.error(...)` avec code HTTP |

---

## 4. Validation des jalons opérationnels (Contrôles T28 à T34)

### T28 · Installation du kit et extension de la suite de tests
- **Commande :** `python -m pytest -q`
- **Résultat attendu :** 12 tests supplémentaires par rapport au TP4 sans aucun échec (95 passed, 2 xfailed).
- **Résultat obtenu :**
  ```text
  ........................................................................ [ 74%]
  ......x...x..............                                                [100%]
  95 passed, 2 xfailed, 1 warning in 10.41s
  ```
- **Conformité :** Validé. La suite passe de 83 tests à 95 tests validés.

### T29 · Démarrage conjoint API et Streamlit
- **Commandes :**
  - Terminal 1 : `uvicorn api.main:app --reload`
  - Terminal 2 : `streamlit run ui/app.py`
- **Résultat obtenu :**
  - Uvicorn confirme : `Modèle chargé avec succès : tfidf-logreg (TP2, models/sentiment.joblib)` sur le port 8000.
  - Streamlit est joignable sur `http://localhost:8501`.
  - La page web affiche en légende : `API prête : tfidf-logreg (TP2, models/sentiment.joblib)`.
- **Conformité :** Validé.

### T30 · Classification des avis tranchés
- **Avis positif :** *"Livraison rapide, produit conforme, très satisfait"*  
  -> Rendu : **`Avis positif`**, jauge à **`78 %`** (score brut : `0.7770`).
- **Avis négatif :** *"Produit cassé et service injoignable, à fuir"*  
  -> Rendu : **`Avis négatif`**, jauge à **`75 %`** (score brut : `0.7465`).
- **Conformité :** Validé.

### T31 · Gestion de l'abstention (Mots inventés)
- **Saisie :** *"xqzvb wlkptr grombu"*
- **Rendu :**
  - Métrique : **`Je ne sais pas : à faire vérifier par un humain`**, score **`52 %`** (score brut : `0.5162`).
  - Encadré d'information : *« La confiance est sous le seuil d'abstention : un humain doit trancher. »*.
- **Conformité :** Validé.

### T32 · Résilience aux erreurs et indisponibilité
- **Saisie de trois espaces (`"   "`) :** L'API répond 422, l'interface affiche l'avertissement jaune :  
  *« Texte refusé : vide, fait d'espaces, ou de plus de 2000 caractères. »*.
- **Arrêt forcé de l'API (`Ctrl+C`) :** Au rafraîchissement de la page, `sante()` intercepte la coupure réseau et affiche immédiatement l'erreur en haut de l'écran :  
  *« API injoignable : lancez d'abord uvicorn api.main:app »*.
- **Conformité :** Validé.

### T33 · Traitement d'un lot d'avis (`data/avis_exemple.csv`)
- **Fichier chargé :** `data/avis_exemple.csv` (242 avis clients).
- **Tableau de résultats :**
  - **94 avis classés en `Avis positif` (38,8 %)** : ex. *"Service excellent, livraison avant l'heure prévue"*, *"Très bonne qualité, je suis vraiment satisfaite"*.
  - **14 avis classés en `Avis négatif` (5,8 %)** : ex. *"Livraison en retard et vendeur injoignable"*, *"Colis ouvert et article complètement abîmé"*.
  - **134 avis classés en `INDETERMINE` (55,4 %)** : avis descriptifs ou factuels sous le seuil d'abstention de 0.60 orientés vers l'arbitrage humain.
- **Distribution obtenue :** `{'INDETERMINE': 134, 'NEGATIVE': 14, 'POSITIVE': 94}`.
- **Export :** Le bouton déclenche le téléchargement du fichier `resultats.csv` annoté.
- **Taux de traitement :** 108 avis classés automatiquement avec forte confiance (44,6 %), 134 avis orientés vers la vérification humaine (55,4 %).
- **Conformité :** Validé.

### T34 · Intégration continue (GitHub Actions)
- Le pipeline `.github/workflows/ci.yml` a été mis à jour pour installer `streamlit==1.39.*`.
- Toutes les étapes de vérification (linters, typage, tests de l'interface et couverture de l'API) s'exécutent avec succès.
- **Conformité :** Validé.

---

## 5. Mécanismes de test sans serveur graphique

L'une des grandes réussites de ce TP est l'intégration de tests automatisés pour l'interface utilisateur sans dépendre d'un navigateur réel (comme Selenium ou Playwright) qui alourdirait la CI :

1. **`tests/test_client.py` (7 tests) :**
   - Utilise le `TestClient` de FastAPI comme session HTTP en mémoire.
   - Valide les méthodes `sante()`, `predire()`, `predire_lot()` et `resumer()`.
   - Simule un serveur inaccessible en pointant vers un port système fermé (`http://127.0.0.1:9`) pour certifier l'émission du message `INJOIGNABLE`.
2. **`tests/test_interface.py` (5 tests) :**
   - Mobilise le framework natif `streamlit.testing.v1.AppTest`.
   - Pousse l'abstraction en remplaçant `client.creer_session` par un mock vers l'API en mémoire (`monkeypatch`).
   - Simule les inputs utilisateur (`page.text_area[0].input(...)`), déclenche les clics (`page.button[0].click()`) et inspecte les arbres d'éléments (`page.metric`, `page.warning`, `page.error`, `page.info`).

---

## 6. Synthèse des acquis et perspectives industrielles

| Dimension | État initial (Fin TP4) | État final (Fin TP5) | Gain pour l'entreprise |
| :--- | :--- | :--- | :--- |
| **Accessibilité utilisateur** | Terminal / Swagger `/docs` | Page web réactive Streamlit | Les équipes non-techniques peuvent exploiter le modèle en autonomie. |
| **Couplage applicatif** | Client et serveur confondus | Découplage strict via client HTTP | Évolution indépendante du frontend et de l'algorithme d'inférence. |
| **Transparence algorithmique** | Scores bruts et verdicts techniques | Libellés bienveillants et explications d'abstention | Confiance renforcée des conseillers vis-à-vis des décisions de l'IA. |
| **Traitement opérationnel** | Requête unitaire manuelle | Ingestion par lot et export CSV | Capacité à traiter des exports hebdomadaires d'avis en un clic. |
| **Assurance qualité** | 83 tests validés | 95 tests validés (100 % automatisés) | Déploiements sécurisés sans régression visuelle ou fonctionnelle. |

### Pistes d'amélioration pour la production :
- **Mise en cache du traitement par lot :** À chaque réexécution Streamlit (notamment au clic sur « Télécharger les résultats »), le traitement du lot est recalculé. Sur un fichier de 10 000 avis, cela saturerait le CPU. L'ajout d'un décorateur `@st.cache_data` permettrait de figer le calcul tant que le fichier n'a pas changé.
- **Requêtes asynchrones en lot (*Batching*) :** Actuellement, `predire_lot()` envoie des requêtes HTTP séquentielles boucle par boucle. L'implémentation d'une route API `POST /predict/batch` traiterait les vecteurs en matrice globale scikit-learn, accélérant le débit d'un facteur 10.
