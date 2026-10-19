# -*- coding: utf-8 -*-
"""Fabrique donnees/exemple.csv : un jeu FICTIF qui a la forme d'un export de questionnaire de prix.

Il sert à une seule chose : montrer le format attendu et vérifier que les scripts tournent.
Ce ne sont pas des données à analyser à la place des vôtres.

Le scénario : un coffret de chocolats vendu 45 €, présenté de deux façons tirées au sort.
  A : « fabriqué à la main par un artisan chocolatier »   B : la même description, sans la mention artisanale.
On y a glissé le désordre habituel : doublons, membres du M1, contrôle d'attention raté,
seuils de Van Westendorp dans le désordre, réponses de Gabor-Granger incohérentes.

Lancer :  python donnees/fabriquer_exemple.py
"""
import os

import numpy as np
import pandas as pd

GRAINE = 2026
N = 190
rng = np.random.default_rng(GRAINE)


def likert(latent, charge=0.8, centre=4.3, etendue=1.25):
    """Un item de 1 à 7 qui mesure une variable latente centrée réduite, avec du bruit."""
    brut = centre + etendue * (charge * latent + np.sqrt(1 - charge ** 2) * rng.normal(size=len(latent)))
    return np.clip(np.round(brut), 1, 7).astype(int)


condition = rng.choice(["A", "B"], size=N)
artisan = (condition == "A").astype(float)

# les variables latentes : l'attitude envers les chocolats existe avant l'étude ;
# la valeur perçue dépend de la version vue ; l'intention dépend des deux
attitude = rng.normal(size=N)
valeur = 0.225 * (artisan - artisan.mean()) / artisan.std() + 0.35 * attitude + rng.normal(scale=0.85, size=N)
valeur = (valeur - valeur.mean()) / valeur.std()
intention = 0.50 * valeur + 0.30 * attitude + rng.normal(scale=0.75, size=N)
intention = (intention - intention.mean()) / intention.std()

d = pd.DataFrame({
    "session_id": [f"s{i:03d}" for i in range(1, N + 1)],
    "ts": pd.date_range("2026-10-12 09:00", periods=N, freq="57min").strftime("%Y-%m-%dT%H:%M:%S+02:00"),
    "condition": condition,
    "filtre_m1": np.where(rng.random(N) < 0.04, "oui", "non"),
    "attention": np.where(rng.random(N) < 0.05, "rate", "ok"),
})

# le contrôle de manipulation : « Ce coffret m'a semblé fait à la main, par un artisan » (1 à 7)
d["manip"] = np.clip(np.round(3.5 + 1.9 * artisan + rng.normal(scale=1.3, size=N)), 1, 7).astype(int)

# Van Westendorp : quatre seuils en euros, qui montent avec la valeur perçue ;
# chaque répondant donne des seuils croissants, séparés par des écarts qui varient d'une personne à l'autre
centre = 50 + 7 * valeur + rng.normal(scale=8, size=N)
d["vw_trop_bon_marche"] = np.round(centre * 0.45 + rng.normal(scale=4, size=N)).astype(int)
d["vw_bon_marche"] = d["vw_trop_bon_marche"] + np.round(centre * 0.25 * rng.uniform(0.6, 1.4, N)).astype(int)
d["vw_cher"] = d["vw_bon_marche"] + np.round(centre * 0.40 * rng.uniform(0.6, 1.4, N)).astype(int)
d["vw_trop_cher"] = d["vw_cher"] + np.round(centre * 0.30 * rng.uniform(0.6, 1.4, N)).astype(int)
# un prix accepté au plus, pour Gabor-Granger
consentement = centre * 1.05 + rng.normal(scale=8, size=N)
for p in (15, 30, 45, 60, 75):
    d[f"achat_{p}"] = np.where(consentement >= p, "Oui", "Non")

# les échelles (1 à 7) : attitude (att_3 est inversé), valeur perçue, intention d'achat
for i, ch in ((1, 0.82), (2, 0.78), (3, 0.74)):
    d[f"att_{i}"] = likert(attitude, ch)
d["att_3"] = 8 - d["att_3"]
for i, ch in ((1, 0.84), (2, 0.80), (3, 0.78)):
    d[f"val_{i}"] = likert(valeur, ch)
for i, ch in ((1, 0.86), (2, 0.82), (3, 0.79)):
    d[f"int_{i}"] = likert(intention, ch, centre=3.9)

d["frequence"] = rng.choice(["jamais", "moins_1_mois", "1_mois", "2_3_mois", "1_semaine_plus"], size=N, p=[.08, .30, .32, .20, .10])
d["age"] = np.clip(np.round(rng.normal(34, 12, size=N)), 18, 75).astype(int)
d["genre"] = rng.choice(["F", "H"], size=N, p=[.55, .45])

# le désordre habituel
inv = rng.choice(N, size=7, replace=False)                      # seuils de Van Westendorp inversés
d.loc[inv, ["vw_bon_marche", "vw_cher"]] = d.loc[inv, ["vw_cher", "vw_bon_marche"]].values
inc = rng.choice(N, size=5, replace=False)                      # accepte 60 € mais refuse 30 €
d.loc[inc, "achat_30"], d.loc[inc, "achat_60"] = "Non", "Oui"
doublons = d.sample(6, random_state=GRAINE)                     # double clic sur « Envoyer »
d = pd.concat([d, doublons]).sort_values("ts").reset_index(drop=True)

sortie = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exemple.csv")
d.to_csv(sortie, index=False, encoding="utf-8")
print(f"{sortie} : {len(d)} lignes, {d.shape[1]} colonnes")
