# Fiche de cadrage : Priorisation des avis négatifs

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Repérer et classer les avis clients négatifs afin que l'équipe du service client puisse les traiter en priorité.
## Utilisateur final (obligatoire)

Les agents du service client ou de la qualité, qui examinent les avis signalés et décident de la réponse à apporter.
## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(a) Des avis déjà classés par l'équipe, ou un échantillon annoté par celle-ci, permettent d'entraîner et d'évaluer un classifieur. (c) Un modèle léger peut traiter un grand volume à faible coût; (d) les erreurs de classement seront corrigées par un agent avant toute action envers le client.
## Données nécessaires et leur origine (obligatoire)

Des avis publics ou fournis avec autorisation, associés à une étiquette de sentiment attribuée par l'équipe; les noms, coordonnées, numéros de commande et autres identifiants doivent être supprimés avant traitement.
## Métrique de succès et seuil d'acceptation (obligatoire)

Sur un jeu de test séparé des données d'entraînement, viser un F1 macro d'au moins 0,85 et un rappel d'au moins 0,90 pour les avis négatifs. Le test doit inclure les principales langues et catégories d'avis réellement prises en charge.
## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un avis négatif manqué peut retarder une prise en charge, tandis qu'un faux signal mobilise inutilement un agent. L'équipe vérifie les avis classés avant de répondre; le modèle ne publie ni réponse ni décision automatiquement.
## Risques éthiques ou de confidentialité (obligatoire)

Les avis peuvent contenir des informations personnelles ou refléter des biais de langue et de style. Il faut anonymiser les données, mesurer les performances par langue lorsque le volume le permet et limiter l'accès aux avis aux agents autorisés.
## Approche écartée et pourquoi (facultatif)

Les règles par mots-clés risquent de manquer le sarcasme et les formulations variées; un modèle génératif seul serait plus coûteux et moins constant pour une tâche répétitive de classement.

