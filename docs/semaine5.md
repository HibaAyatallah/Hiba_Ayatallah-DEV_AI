# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

L'interface n'importe jamais `predict()` ni le fichier `sentiment.joblib` afin de respecter la **troisième règle d'architecture du projet : la séparation stricte entre la couche de présentation et la couche de décision**. L'interface Streamlit (`ui/app.py`) agit comme un pur client HTTP qui délègue tous ses échanges réseau au module `ui/client.py` en dialoguant exclusivement avec les endpoints `/health` et `/predict` de l'API FastAPI.

Ce découpage apporte trois bénéfices techniques essentiels :
1. **Découplage architectural et évolutivité :** Un réentraînement du modèle (mise à jour des poids TF-IDF, substitution par un transformeur ou un modèle plus performant) ou le déplacement de l'API vers un serveur cloud distant n'impose aucune modification de code dans la page web. Seule la variable d'environnement `API_URL` change.
2. **Gestion optimale de la mémoire :** Une application Streamlit réexécute l'intégralité de son script Python à chaque action de l'utilisateur (saisie, clic, téléversement). Si l'interface chargeait directement le modèle binaire `.joblib`, elle multiplierait les accès disque et la charge mémoire. Avec l'architecture en deux services, le modèle est instancié une seule fois en mémoire par le gestionnaire de cycle de vie ASGI (`lifespan`) d'Uvicorn.
3. **Consommation multi-clients :** L'API sert de point d'entrée unique et centralisé, réutilisable sans friction par l'interface web, de futurs agents autonomes ou des scripts batch internes.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Quand la confiance estimée par le modèle est inférieure au seuil d'abstention (`SEUIL_ABSTENTION = 0.60`), l'API renvoie le verdict `INDETERMINE`. L'interface web intercepte cette étiquette et affiche :
- Un libellé clair et bienveillant dans le composant métrique : **« Je ne sais pas : à faire vérifier par un humain »**, accompagné du score de confiance réel (par exemple 52 %).
- Un encadré informatif contextuel (`st.info`) : *« La confiance est sous le seuil d'abstention : un humain doit trancher. »*.

Cet affichage est incomparablement plus fiable qu'un verdict forcé. Sur des avis ambigus, mitigés ou hors-vocabulaire (comme la chaîne inventée `"xqzvb wlkptr grombu"` dont la projection TF-IDF est entièrement nulle), une régression logistique sans seuil basculerait arbitrairement du côté de l'ordonnée à l'origine (ici `NEGATIVE` à 51,62 %). Forcer une prédiction dans cette zone grise tromperait les équipes relation client en donnant une illusion de certitude. L'abstention formalise l'humilité algorithmique du système et protège l'entreprise contre des erreurs opérationnelles critiques en orientant systématiquement les dossiers douteux vers un arbitrage humain.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

Lorsque l'API FastAPI est arrêtée ou inaccessible, le module `ui/client.py` intercepte l'exception de transport (`httpx.TransportError`) et retourne un objet `Reponse(ok=False, message=INJOIGNABLE)`. Dès le rechargement de la page, la fonction `sante()` interroge `/health` : la page détecte l'absence de service et affiche en haut de l'écran un bandeau d'alerte rouge (`st.error`) explicite et orienté action :  
**« API injoignable : lancez d'abord uvicorn api.main:app »**.  
L'application ne plante jamais, n'affiche aucune trace de débogage interne (*stacktrace*) et guide l'opérateur sur la commande exacte à lancer.

Dans le cas du traitement par lot du fichier `data/avis_exemple.csv` (composé de 242 avis clients réels et variés : éloges, réclamations, avis mitigés et retours factuels) :
- **94 avis** sont classés en **`Avis positif`** (38,8 %) : ex. *"Service excellent, livraison avant l'heure prévue"*, *"Très bonne qualité, je suis vraiment satisfaite"*.
- **14 avis** sont classés en **`Avis négatif`** (5,8 %) : ex. *"Livraison en retard et vendeur injoignable"*, *"Colis ouvert et article complètement abîmé"*.
- **134 avis sur 242 (soit 55,4 % du lot)** partent vers une revue humaine avec le verdict **`INDETERMINE`** :
  - Il s'agit d'avis neutres, purement descriptifs ou factuels (ex. *"Commande reçue aujourd'hui, je vais la tester"*, *"Le colis est posé devant la porte"*, *"Le produit est disponible en trois tailles"*). Leur projection TF-IDF ne contient aucun terme fortement polarisé et leur score de confiance reste sous le seuil d'abstention de 0.60.

Le résumé affiché à l'écran est `{'INDETERMINE': 134, 'NEGATIVE': 14, 'POSITIVE': 94}`. Ce volume illustre parfaitement le rôle protecteur de l'abstention sur des retours d'utilisateurs non polarisés.

