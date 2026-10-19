# -*- coding: utf-8 -*-
"""LE SEUL FICHIER À ADAPTER À VOTRE PROJET.

Chaque réglage dit à quoi correspondent les colonnes de VOTRE export.
Les valeurs ci-dessous sont celles du fichier d'exemple (donnees/exemple.csv) :
remplacez-les une par une, en regardant les noms de colonnes de votre fichier.
Un réglage dont vous n'avez pas l'équivalent se met à None (ou à une liste vide) :
l'étape correspondante est alors sautée, et le script le dit.
"""

# ---- le fichier ------------------------------------------------------------------
FICHIER = "donnees/exemple.csv"       # votre export, en CSV (une ligne par répondant)
SEPARATEUR = ","                      # "," en général ; ";" pour un CSV exporté d'Excel en français
IDENTIFIANT = "session_id"            # la colonne qui identifie un répondant (sert à repérer les doublons)

# ---- les filtres de nettoyage ----------------------------------------------------
# chaque filtre : (colonne, valeur à EXCLURE, raison écrite dans le journal)
FILTRES = [
    ("filtre_m1", "oui", "membre du M1 : connaît l'étude"),
    ("attention", "rate", "contrôle d'attention raté"),
]

# ---- le test A/B ------------------------------------------------------------------
CONDITION = "condition"               # la colonne qui dit quelle version le répondant a vue
VERSIONS = {"A": "artisanale", "B": "standard"}   # code dans le fichier : nom lisible

# le contrôle de manipulation : la question qui mesure si la différence a été perçue
MANIPULATION = "manip"                # None si vous n'en avez pas
MANIPULATION_LIBELLE = "« Ce coffret m'a semblé fait à la main, par un artisan » (1 à 7)"
VERSION_ATTENDUE_HAUTE = "A"          # la version qui DEVRAIT obtenir le score le plus haut

# ---- la mesure du prix --------------------------------------------------------------
PRIX_ACTUEL = 45                      # le prix auquel l'offre est vendue aujourd'hui (ou envisagé)
COUT_VARIABLE = 18                    # ce que coûte une unité vendue (votre TD 2 de Prix)
UNITE = "€"

# Van Westendorp : les quatre seuils, dans cet ordre (None si vous ne l'avez pas posé)
VAN_WESTENDORP = {
    "trop_bon_marche": "vw_trop_bon_marche",
    "bon_marche": "vw_bon_marche",
    "cher": "vw_cher",
    "trop_cher": "vw_trop_cher",
}

# Gabor-Granger : prix proposé -> colonne ; OUI_GG = la réponse qui veut dire « j'achète »
GABOR_GRANGER = {15: "achat_15", 30: "achat_30", 45: "achat_45", 60: "achat_60", 75: "achat_75"}
OUI_GG = "Oui"

# les variables dépendantes du test A/B : colonne -> (libellé, nature)
# nature : "quanti" (un nombre : test de Welch) ou "binaire" (oui / non : test du chi²)
VARIABLES_DEPENDANTES = {
    "vw_trop_cher": ("Seuil « trop cher » (Van Westendorp)", "quanti"),
    "achat_45": ("Achèterait au prix actuel (Gabor-Granger)", "binaire"),
}

# ---- les échelles -------------------------------------------------------------------
ECHELLE_MAX = 7                       # 5 pour une échelle de 1 à 5, 7 pour une échelle de 1 à 7
ITEMS_INVERSES = ["att_3"]            # items formulés à l'envers, recodés en (MAX + 1) - réponse

# chaque construit : son nom (sans espace ni accent) -> ses items ; trois items au moins
ECHELLES = {
    "Attitude": ["att_1", "att_2", "att_3"],
    "Valeur": ["val_1", "val_2", "val_3"],
    "Intention": ["int_1", "int_2", "int_3"],
}

# le modèle structurel : qui explique quoi, une ligne par variable expliquée.
# « condition_A » est créée par les scripts : 1 si le répondant a vu la version A, 0 sinon.
MODELE_STRUCTUREL = """
Valeur ~ condition_A + Attitude
Intention ~ Valeur + Attitude
"""

# ---- les seuils de lecture (ne pas toucher sans raison) --------------------------------
SEUIL = 0.05
SEUILS_MESURE = {
    "poids": 0.70,          # poids standardisé de chaque item sur son construit
    "alpha": 0.70,          # alpha de Cronbach
    "cr": 0.70,             # fiabilité composite (CR, ou oméga)
    "ave": 0.50,            # variance moyenne extraite
    "htmt": 0.85,           # validité discriminante
    "cfi": 0.90, "tli": 0.90, "rmsea": 0.08, "srmr": 0.08,
}
