# -*- coding: utf-8 -*-
"""Étape 2 : le contrôle de manipulation. Les répondants ont-ils perçu la différence entre A et B ?

Si la version A est censée paraître plus artisanale, ceux qui l'ont vue doivent la juger plus artisanale
que ceux qui ont vu B. On le vérifie par un test de Welch sur la question de contrôle.
Sans cette vérification, un test A/B non significatif ne veut rien dire : la variation a-t-elle échoué,
ou est-elle simplement passée inaperçue ?

Lancer :  python 02_manipulation.py
"""
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import config as C
from outils import charger_propre, enregistrer, groupes, nb, titre, welch

if not C.MANIPULATION:
    raise SystemExit("Pas de contrôle de manipulation dans config.py (MANIPULATION = None) : étape sautée.")

d = charger_propre()
titre("Le contrôle de manipulation")
print(C.MANIPULATION_LIBELLE)
r = welch(d, C.MANIPULATION, "Score au contrôle de manipulation")
print("\n" + r["phrase"])

haute = C.VERSIONS[C.VERSION_ATTENDUE_HAUTE]
bon_sens = (r["moy_a"] > r["moy_b"]) == (C.VERSION_ATTENDUE_HAUTE == list(C.VERSIONS)[0])
titre("Verdict")
if r["p"] < C.SEUIL and bon_sens:
    print(f"Manipulation réussie : la version {haute} est bien perçue comme attendu.")
    print("Vous pouvez interpréter le test A/B (étape 3) comme l'effet de votre variation.")
elif r["p"] < C.SEUIL:
    print("Manipulation inversée : la différence est perçue, mais dans le mauvais sens. Relisez vos deux versions avant tout.")
else:
    print("Manipulation non vérifiée : les répondants n'ont pas perçu de différence nette entre les versions.")
    print("Un test A/B non significatif ne prouvera donc pas que la variation est sans effet ; écrivez-le.")
print("On n'exclut PAS les répondants qui ont « raté » la manipulation : ce serait casser le tirage au sort.")

# le graphique : la moyenne de chaque version, avec chaque répondant en point
fig, ax = plt.subplots(figsize=(6, 3.2))
for k, (code, vals) in enumerate(zip(C.VERSIONS, groupes(d, C.MANIPULATION))):
    ax.scatter(vals + np.random.default_rng(k).uniform(-0.15, 0.15, len(vals)), k + np.random.default_rng(k + 9).uniform(-0.2, 0.2, len(vals)), alpha=0.3, s=18)
    ax.plot([vals.mean()] * 2, [k - 0.3, k + 0.3], color="black", lw=3)
    ax.text(vals.mean(), k + 0.38, f"moyenne {nb(vals.mean())}", ha="center")
ax.set_yticks([0, 1], [f"version {v}" for v in C.VERSIONS.values()])
ax.set_xlabel(C.MANIPULATION_LIBELLE)
ax.set_ylim(-0.6, 1.8)
enregistrer(fig, "02_manipulation.png")
