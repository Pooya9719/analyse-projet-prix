# ==============================================================================
# CONFIGURATION FOR DISNEY / ASTERIX PRICING PROJECT
# ==============================================================================

# 1. File Path & ID Settings
FICHIER_DONNEES = "donnees/Resultats_Questionnaire_Disney_Asterix.csv"
COLONNE_ID = "id_aleatoire"
COLONNE_VERSION = "version"
COLONNE_TEST = "test"  # Used to filter out test entries ('oui')

# 2. Manipulation Check
COLONNE_MANIPULATION = "controle"

# 3. Demographics & Randomization Checks
COLONNES_DEMO_NUM = ["age"]
COLONNES_DEMO_CAT = ["situation_familiale", "situation", "residence", "frequence"]

# 4. Primary A/B Dependent Variable
COLONNE_CHOIX_AB = "choix_ab"

# 5. Van Westendorp Pricing Thresholds (Astérix)
VW_ASTERIX = {
    "trop_bon_marche": "vw_trop_bon_marche_asterix",
    "bonne_affaire": "vw_bonne_affaire_asterix",
    "cher": "vw_cher_asterix",
    "trop_cher": "vw_trop_cher_asterix",
    "incoherence": "incoherent_vw_asterix"
}

# 6. Van Westendorp Pricing Thresholds (Disney)
VW_DISNEY = {
    "trop_bon_marche": "vw_trop_bon_marche_disney",
    "bonne_affaire": "vw_bonne_affaire_disney",
    "cher": "vw_cher_disney",
    "trop_cher": "vw_trop_cher_disney",
    "incoherence": "incoherent_vw_disney"
}

# 7. Importance Scales (1-5 Likert)
ITEMS_IMPORTANCE = [
    "importance_prix",
    "importance_attractions",
    "importance_univers",
    "importance_spectacles",
    "importance_enfants",
    "importance_attente",
    "importance_acces"
]
