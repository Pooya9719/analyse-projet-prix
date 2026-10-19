# -*- coding: utf-8 -*-
"""Étape 5 : vos échelles mesurent-elles bien ce qu'elles prétendent mesurer ?

On vérifie, dans l'ordre :
  1. la fiabilité : les items d'un même construit vont-ils dans le même sens ? (alpha, fiabilité composite)
  2. le modèle de mesure : l'analyse factorielle confirmatoire (CFA) reproduit-elle vos données ? (poids, ajustement)
  3. la validité convergente : chaque construit explique-t-il l'essentiel de ses items ? (AVE)
  4. la validité discriminante : deux construits sont-ils bien distincts ? (HTMT)
Les seuils sont dans config.py (SEUILS_MESURE).

Lancer :  python 05_echelles.py
"""
import os

import pandas as pd

import config as C
from outils import (SORTIES, ajuster, alpha_cronbach, ave, charger_propre, description_mesure, fiabilite_composite, htmt,
                    indices_ajustement, nb, poids_standardises, titre)

if not C.ECHELLES:
    raise SystemExit("Pas d'échelle dans config.py (ECHELLES vide) : étape sautée.")

S = C.SEUILS_MESURE
d = charger_propre()
items = [i for its in C.ECHELLES.values() for i in its]
d = d.dropna(subset=items)

titre("Le modèle de mesure (CFA)")
print(description_mesure())
m = ajuster(description_mesure(), d)
fit = indices_ajustement(m)
print(f"\n  chi² = {nb(fit['chi2'])} pour {nb(fit['ddl'], 0)} ddl")
ok_fit = fit["cfi"] >= S["cfi"] and fit["tli"] >= S["tli"] and fit["rmsea"] <= S["rmsea"] and fit["srmr"] <= S["srmr"]
print(f"  CFI = {nb(fit['cfi'])} (≥ {nb(S['cfi'])})   TLI = {nb(fit['tli'])} (≥ {nb(S['tli'])})   "
      f"RMSEA = {nb(fit['rmsea'])} (≤ {nb(S['rmsea'])})   SRMR = {nb(fit['srmr'])} (≤ {nb(S['srmr'])})")
print("  -> ajustement " + ("satisfaisant" if ok_fit else "insuffisant : regardez d'abord les poids faibles ci-dessous"))

titre("Les poids de chaque item")
p = poids_standardises(m)
for _, r in p.iterrows():
    alerte = "" if r.poids >= S["poids"] else f"   < {nb(S['poids'])} : item faible"
    print(f"  {r['construit']:<12} {r['item']:<10} {nb(r['poids'])}{alerte}")

titre("Fiabilité et validité convergente")
lignes = []
for nom, its in C.ECHELLES.items():
    w = p.loc[p.construit == nom, "poids"]
    lignes.append({"construit": nom, "alpha": alpha_cronbach(d[its]), "CR": fiabilite_composite(w), "AVE": ave(w)})
t = pd.DataFrame(lignes)
for _, r in t.iterrows():
    ok = r.alpha >= S["alpha"] and r.CR >= S["cr"] and r.AVE >= S["ave"]
    print(f"  {r.construit:<12} alpha = {nb(r.alpha)}   CR = {nb(r.CR)}   AVE = {nb(r.AVE)}   " + ("ok" if ok else "À REVOIR"))
print(f"  seuils : alpha et CR ≥ {nb(S['alpha'])}, AVE ≥ {nb(S['ave'])}")

titre("Validité discriminante (HTMT)")
h = htmt(d)
print(h.round(2).fillna("").to_string())
mx = h.max().max()
print(f"\n  HTMT maximum = {nb(mx)} -> " + (f"construits bien distincts (≤ {nb(S['htmt'])})" if mx <= S["htmt"]
                                          else f"deux construits se confondent (> {nb(S['htmt'])})"))
t.to_csv(os.path.join(SORTIES, "05_mesure.csv"), index=False)
print("\nTableau enregistré : sorties/05_mesure.csv")
