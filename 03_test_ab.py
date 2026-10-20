# -*- coding: utf-8 -*-
"""Étape 3 : le test A/B. La version vue change-t-elle la réponse ?

Le test dépend de la nature de la variable dépendante (réglée dans config.py, VARIABLES_DEPENDANTES) :
  un nombre (un seuil de prix, un score)  -> test de Welch, taille d'effet d de Cohen
  oui / non (achèterait ou pas)           -> test du chi², taille d'effet V de Cramer
Avant tout : les deux groupes se ressemblent-ils ? Le tirage au sort doit les avoir rendus comparables.

Lancer :  python 03_test_ab.py
"""
import pandas as pd
from scipy import stats

import config as C
from outils import charger_propre, chi2, nb, p_txt, puissance, titre, welch

d = charger_propre()

titre("Le tirage au sort a-t-il fonctionné ?")
for col in ("age", "genre", "frequence"):
    if col not in d:
        continue
    if pd.api.types.is_numeric_dtype(d[col]):
        r = welch(d, col, col)
        print(f"  {col} : {nb(r['moy_a'])} contre {nb(r['moy_b'])}, {p_txt(r['p'])}")
    else:
        khi, p, _, _ = stats.chi2_contingency(pd.crosstab(d[C.CONDITION], d[col]))
        print(f"  {col} : chi² = {nb(khi)}, {p_txt(p)}")
print("  Une différence significative ici signale un tirage déséquilibré : à dire, et à garder en tête.")

titre("Les tests")
for col, (libelle, nature) in C.VARIABLES_DEPENDANTES.items():
    if col not in d:
        print(f"  {col} : colonne absente, ignorée")
        continue
    r = welch(d, col, libelle) if nature == "quanti" else chi2(d, col, libelle)
    print("\n" + r["phrase"])
    if nature != "quanti":
        print(r["tableau"].rename(index=C.VERSIONS).to_string())

n = d[C.CONDITION].value_counts()
titre("La puissance")
pw_petit, pw_moyen = puissance(n.iloc[0], n.iloc[1], 0.2), puissance(n.iloc[0], n.iloc[1], 0.5)
print(f"Avec {n.iloc[0]} et {n.iloc[1]} répondants, le test détecte un effet moyen (d = 0,5) {nb(pw_moyen * 100, 0)} fois sur 100,")
print(f"et un petit effet (d = 0,2) {nb(pw_petit * 100, 0)} fois sur 100.")
print("Sous 80 %, un résultat non significatif ne prouve pas l'absence d'effet : écrivez-le.")
