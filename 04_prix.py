# -*- coding: utf-8 -*-
"""Étape 4 : le prix psychologique. Van Westendorp trace la zone acceptable, Gabor-Granger choisit un prix dedans.

Lancer :  python 04_prix.py
Produit : sorties/04_van_westendorp.png, sorties/04_gabor_granger.png
"""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config as C
from outils import charger_propre, courbes_vw, enregistrer, gabor_granger, nb, points_vw, titre

d = charger_propre()
U = C.UNITE

if C.VAN_WESTENDORP:
    titre("Van Westendorp")
    c = courbes_vw(d)
    pts = points_vw(c)
    print(f"  Zone de prix acceptable : de {nb(pts['PMC'], 1)} {U} (PMC) à {nb(pts['PME'], 1)} {U} (PME)")
    print(f"  Prix optimal (OPP)      : {nb(pts['OPP'], 1)} {U}")
    print(f"  Prix d'indifférence (IPP) : {nb(pts['IPP'], 1)} {U}")
    print(f"  Prix actuel             : {nb(C.PRIX_ACTUEL, 1)} {U} -> "
          + ("dans la zone" if pts["PMC"] <= C.PRIX_ACTUEL <= pts["PME"] else "HORS de la zone"))
    titre("Van Westendorp, version par version")
    for code, nom in C.VERSIONS.items():
        sous = d[d[C.CONDITION].astype(str) == code]
        p2 = points_vw(courbes_vw(sous, c["prix"]))
        print(f"  version {nom} (n = {len(sous)}) : zone {nb(p2['PMC'], 1)} à {nb(p2['PME'], 1)} {U}, OPP {nb(p2['OPP'], 1)} {U}")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    for col, lab, st in (("trop_bon_marche", "trop bon marché", "--"), ("bon_marche", "bon marché", "-"),
                         ("cher", "cher", "-"), ("trop_cher", "trop cher", "--")):
        ax.plot(c.prix, c[col] * 100, st, label=lab)
    ax.axvspan(pts["PMC"], pts["PME"], alpha=0.1)
    for i, k in enumerate(("PMC", "OPP", "IPP", "PME")):     # étiquettes en quinconce, pour qu'elles ne se chevauchent pas
        ax.axvline(pts[k], color="grey", lw=0.8)
        ax.text(pts[k], 103 + 6 * (i % 2), f"{k} {nb(pts[k], 1)}", ha="center", fontsize=8)
    ax.axvline(C.PRIX_ACTUEL, color="black", lw=1.2, ls=":")
    ax.text(C.PRIX_ACTUEL, 50, f" prix actuel {nb(C.PRIX_ACTUEL, 0)} {U}", fontsize=8)
    ax.set_ylim(-3, 114)
    ax.set_xlabel(f"prix ({U})")
    ax.set_ylabel("% de répondants")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, frameon=False)
    enregistrer(fig, "04_van_westendorp.png")

if C.GABOR_GRANGER:
    titre("Gabor-Granger")
    g = gabor_granger(d)
    for _, r in g.iterrows():
        print(f"  {nb(r.prix, 0):>4} {U} : {nb(r.taux * 100, 0):>3} % achèteraient   "
              f"CA par répondant {nb(r.ca_par_repondant)} {U}   marge par répondant {nb(r.marge_par_repondant)} {U}")
    best = g.loc[g.marge_par_repondant.idxmax()]
    print(f"\n  Prix qui maximise la marge (coût variable {nb(C.COUT_VARIABLE, 0)} {U}) : {nb(best.prix, 0)} {U}")
    print("  Rappel : c'est une intention déclarée, pas un taux d'achat réel.")

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(g.prix, g.ca_par_repondant, "o-", label="chiffre d'affaires par répondant")
    ax.plot(g.prix, g.marge_par_repondant, "o-", label="marge par répondant")
    ax.set_xlabel(f"prix proposé ({U})")
    ax.annotate(f"marge maximale à {nb(best.prix, 0)} {U}", (best.prix, best.marge_par_repondant),
                xytext=(0, -28), textcoords="offset points", ha="center", fontsize=8, arrowprops={"arrowstyle": "->"})
    ax.set_ylabel(f"{U} par répondant")
    ax.legend()
    enregistrer(fig, "04_gabor_granger.png")
