# -*- coding: utf-8 -*-
"""Étape 1 : nettoyer. On retire ce qui ne doit pas entrer dans l'analyse, et on garde la trace de chaque retrait.

Lancer :  python 01_nettoyer.py
Produit : sorties/donnees_propres.csv (les données à analyser) et sorties/journal_nettoyage.csv
"""
import os

import pandas as pd

import config as C
from outils import SORTIES, charger_brut, nettoyer, titre

brut = charger_brut()
titre("Votre fichier")
print(f"{len(brut)} lignes, {brut.shape[1]} colonnes : {', '.join(brut.columns)}")

propre, journal = nettoyer(brut)

titre("Le nettoyage, étape par étape")
for raison, retires, reste in journal:
    print(f"  {raison:<62} {('- ' + str(retires)) if retires else '':>6}   reste {reste}")
if C.ITEMS_INVERSES:
    print(f"\n  Items inversés recodés en ({C.ECHELLE_MAX} + 1) - réponse : {', '.join(C.ITEMS_INVERSES)}")

titre("Les versions après nettoyage")
print(propre[C.CONDITION].value_counts().rename(index=C.VERSIONS).to_string())

propre.to_csv(os.path.join(SORTIES, "donnees_propres.csv"), index=False, encoding="utf-8")
pd.DataFrame(journal, columns=["etape", "retires", "reste"]).to_csv(os.path.join(SORTIES, "journal_nettoyage.csv"), index=False, encoding="utf-8")
print("\nÀ écrire dans votre dossier : le nombre de réponses reçues, chaque retrait et sa raison, le nombre final par version.")
print("Fichiers : sorties/donnees_propres.csv, sorties/journal_nettoyage.csv")
