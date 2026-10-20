# Analyser une étude de prix

Squelette d'analyse d'une étude de prix par questionnaire : un test A/B entre
deux versions d'une offre, le prix psychologique (Van Westendorp,
Gabor-Granger) et, si elles ont été posées, des échelles de mesure.

Ce n'est pas une boîte noire à faire tourner : c'est un point de départ que vous
lisez, adaptez à votre questionnaire, et dont vous devez pouvoir expliquer
chaque ligne de résultat dans votre rapport.

## Ce que contient le dépôt

| Fichier | Ce qu'il fait |
|---|---|
| `config.py` | **le seul fichier à adapter** : vos noms de colonnes, vos versions, vos prix, vos échelles |
| `01_nettoyer.py` | retire doublons, répondants filtrés, contrôles d'attention ratés, réponses de prix incohérentes ; garde un journal |
| `02_manipulation.py` | le contrôle de manipulation : la différence entre A et B a-t-elle été perçue ? |
| `03_test_ab.py` | le test A/B : Welch pour un nombre, chi² pour un oui / non, avec taille d'effet et puissance |
| `04_prix.py` | les courbes de Van Westendorp (zone acceptable) et la table de Gabor-Granger (marge) |
| `05_echelles.py` | fiabilité et validité de vos échelles : alpha, CFA, fiabilité composite, AVE, HTMT |
| `06_modele_structurel.py` | les liens entre construits, une fois les échelles validées |
| `outils.py` | les fonctions communes ; vous n'avez pas à y toucher |
| `donnees/exemple.csv` | un jeu **fictif** (coffret de chocolats à 45 €, version artisanale contre standard), fabriqué par `donnees/fabriquer_exemple.py` |

Les résultats s'écrivent à l'écran ; les graphiques et les tableaux dans `sorties/`.

## Faire tourner l'exemple

Il faut Python 3.11 ou plus récent et les bibliothèques de `requirements.txt`.
Sur votre machine (dans un environnement virtuel, de préférence), dans Google
Colab ou avec un agent qui code : à vous de choisir. Puis, dans l'ordre :

```
python 01_nettoyer.py
python 02_manipulation.py
python 03_test_ab.py
python 04_prix.py
python 05_echelles.py
python 06_modele_structurel.py
```

Faites tourner l'exemple **avant** de toucher à quoi que ce soit : vous saurez à
quoi ressemble une sortie normale.

## Passer à vos données

1. Exportez vos réponses en CSV, une ligne par répondant, et posez le fichier
   dans `donnees/`.
2. Ouvrez `config.py` et remplacez les réglages un par un en regardant les noms
   de colonnes de votre fichier. Ce que vous n'avez pas posé (pas
   d'échelle, pas de Gabor-Granger) se met à `None` ou à une liste vide :
   l'étape est sautée.
3. Relancez les scripts **un à la fois**, dans l'ordre, et lisez chaque sortie
   avant de passer à la suivante. Une erreur sur un nom de colonne se corrige
   dans `config.py`, pas dans les scripts.
4. Si votre questionnaire diffère (trois versions au lieu de deux, une autre
   variable dépendante, un autre modèle), adaptez : c'est un squelette.

## Vos données restent chez vous

Les réponses de vos répondants sont des données personnelles. Le
`.gitignore` exclut tout `donnees/` sauf l'exemple, et tout `sorties/` : si vous
copiez ce dépôt sur GitHub, vérifiez avant chaque envoi qu'aucun export n'y
part.

## Les seuils utilisés

Ils sont réglés dans `config.py` (`SEUILS_MESURE`) et suivent les usages en
marketing :

| Indicateur | Seuil | Source |
|---|---|---|
| poids standardisé d'un item | ≥ 0,70 | Hair et al. (2019) |
| alpha de Cronbach, fiabilité composite | ≥ 0,70 | Nunnally (1978) ; Fornell et Larcker (1981) |
| AVE (validité convergente) | ≥ 0,50 | Fornell et Larcker (1981) |
| HTMT (validité discriminante) | ≤ 0,85 | Henseler, Ringle et Sarstedt (2015) |
| CFI, TLI | ≥ 0,90 | Hu et Bentler (1999), version souple |
| RMSEA, SRMR | ≤ 0,08 | Hu et Bentler (1999) |

Pour le prix : Van Westendorp (1976) pour les quatre seuils et leurs croisements,
Gabor et Granger (1966) pour la courbe d'acceptation par prix.
