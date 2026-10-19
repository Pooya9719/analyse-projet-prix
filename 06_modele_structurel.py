# -*- coding: utf-8 -*-
"""Étape 6 : le modèle structurel. Une fois les construits validés (étape 5), on estime les liens entre eux.

Le modèle est écrit dans config.py (MODELE_STRUCTUREL). Celui de l'exemple :
  la version vue agit sur la valeur perçue, qui agit sur l'intention d'achat ; l'attitude joue sur les deux.
C'est une médiation : l'effet de la version sur l'intention passe par la valeur perçue.
Elle se teste par bootstrap (réglage MEDIATION dans config.py).

Lancer :  python 06_modele_structurel.py
"""
import config as C
from outils import (ajuster, charger_propre, description_mesure, indices_ajustement, mediation_bootstrap, nb, p_txt,
                    scores_moyens, titre)

d = charger_propre()
desc = description_mesure() + "\n" + C.MODELE_STRUCTUREL
titre("Le modèle complet : mesure + structure")
print(desc.strip())

m = ajuster(desc, d)
fit = indices_ajustement(m)
print(f"\n  CFI = {nb(fit['cfi'])}   TLI = {nb(fit['tli'])}   RMSEA = {nb(fit['rmsea'])}   SRMR = {nb(fit['srmr'])}")

titre("Les liens entre construits")
t = m.inspect(std_est=True)
struct = t[(t.op == "~") & (~t.rval.isin([i for its in C.ECHELLES.values() for i in its]))
           & (t.lval.isin(list(C.ECHELLES)))]
coef = {}
for _, r in struct.iterrows():
    coef[(r.rval, r.lval)] = r["Est. Std"]
    pv = float(r["p-value"]) if r["p-value"] != "-" else float("nan")
    print(f"  {r.rval:>12} -> {r.lval:<12} bêta standardisé = {nb(r['Est. Std'])}   {p_txt(pv)}")

if C.MEDIATION:
    x, med, y, ctrl = C.MEDIATION
    titre("L'effet indirect (médiation)")
    if (x, med) in coef and (med, y) in coef:
        a, b = coef[(x, med)], coef[(med, y)]
        print(f"  Dans le modèle : {x} -> {med} -> {y} : a × b = {nb(a)} × {nb(b)} = {nb(a * b)} (en écarts-types)")
    r = mediation_bootstrap(scores_moyens(d), x, med, y, ctrl)
    print(f"\n  Comme PROCESS (modèle 4), sur les scores moyens, {r['tirages']} tirages bootstrap, n = {r['n']} :")
    print(f"    a = {nb(r['a'])}   b = {nb(r['b'])}   effet indirect a × b = {nb(r['ab'])}   "
          f"IC 95 % [{nb(r['bas'])} ; {nb(r['haut'])}]   effet direct c' = {nb(r['direct'])}")
    if r["bas"] > 0 or r["haut"] < 0:
        print(f"  -> l'intervalle ne contient pas 0 : l'effet de {x} sur {y} passe bien, en partie au moins, par {med}.")
    else:
        print("  -> l'intervalle contient 0 : pas de médiation démontrée.")
