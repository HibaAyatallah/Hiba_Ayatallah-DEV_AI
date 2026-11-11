# Fiche de cadrage : Ordonnances incomplètes en pharmacie

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Repérer les champs obligatoires manquants sur une ordonnance avant sa vérification par le pharmacien.
## Utilisateur final (obligatoire)

Le pharmacien ou le préparateur qui contrôle l'ordonnance et contacte le prescripteur si une information nécessaire manque.
## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Les champs exigés et leurs formats peuvent être définis par une liste de contrôle vérifiable. (d) Une omission peut conduire à une délivrance inadaptée : le système doit signaler les manques, sans décider qu'une ordonnance est médicalement sûre.
## Données nécessaires et leur origine (obligatoire)

Une liste des champs requis, validée par des professionnels et fondée sur les règles applicables, ainsi que des ordonnances fictives créées pour les essais. Aucune ordonnance réelle ni donnée identifiable de patient ne sera utilisée.
## Métrique de succès et seuil d'acceptation (obligatoire)

Sur un jeu d'essai fictif vérifié par un pharmacien, détecter au moins 99 % des champs obligatoires manquants et ne manquer aucune omission considérée critique. Tout écart bloque le déploiement jusqu'à correction et nouvelle vérification.
## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Un oubli non signalé pourrait retarder une vérification importante. Le pharmacien examine chaque alerte et reste seul décisionnaire avant toute délivrance; l'outil ne valide et ne transmet aucune ordonnance automatiquement.
## Risques éthiques ou de confidentialité (obligatoire)

Les ordonnances contiennent des données de santé particulièrement sensibles. Les essais utiliseront des données fictives; en usage réel, seules les données indispensables seraient accessibles dans un environnement autorisé, sans envoi à un service externe.
## Approche écartée et pourquoi (facultatif)

Le machine learning est écarté pour ce contrôle initial, car une liste de champs explicite est plus traçable et aucun jeu d'ordonnances annotées n'est établi pour le projet.

