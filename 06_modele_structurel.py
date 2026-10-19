# -*- coding: utf-8 -*-
"""Étape 6 : le modèle structurel. Une fois les construits validés (étape 5), on estime les liens entre eux.

Le modèle est écrit dans config.py (MODELE_STRUCTUREL). Celui de l'exemple :
  la version vue agit sur la valeur perçue, qui agit sur l'intention d'achat ; l'attitude joue sur les deux.
C'est une médiation : l'effet de la version sur l'intention passe par la valeur perçue.

Lancer :  python 06_modele_structurel.py
"""
import config as C
from outils import ajuster, charger_propre, description_mesure, indices_ajustement, nb, p_txt, titre

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

if ("condition_A", "Valeur") in coef and ("Valeur", "Intention") in coef:
    titre("L'effet indirect (médiation)")
    a, b = coef[("condition_A", "Valeur")], coef[("Valeur", "Intention")]
    print(f"  version A -> valeur perçue -> intention : a × b = {nb(a)} × {nb(b)} = {nb(a * b)} (en écarts-types)")
    print("  Pour le tester, l'intervalle de confiance de a × b s'obtient par bootstrap ;")
    print("  la macro PROCESS d'Andrew Hayes (modèle 4) le fait directement.")
