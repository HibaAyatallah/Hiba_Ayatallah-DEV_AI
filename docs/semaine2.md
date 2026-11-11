# Analyse des erreurs du modèle (Semaine 2)

Sur le jeu de test de démonstration (58 avis), le modèle commet 7 erreurs portant exclusivement sur des avis mitigés comportant un retournement d'opinion (dont 2 avis négatifs classés positifs, cas particulièrement critique pour le support client).
Ces erreurs s'expliquent par l'approche en sac de mots (TF-IDF unigrammes) qui ne prend pas en compte l'ordre des mots et ignore les conjonctions de rupture (comme « sauf que ensuite » ou « mais finalement ») dont dépend le sentiment final de l'avis.
Pour y remédier, il faudrait intégrer des n-grammes de mots (bigrammes/trigrammes), enrichir les caractéristiques avec la position des termes dans le texte, ou recourir à des modèles contextuels séquentiels comme les Transformers (ex. CamemBERT) capables de capturer la syntaxe et les dépendances à longue distance.
