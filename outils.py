# -*- coding: utf-8 -*-
"""Les fonctions communes aux scripts. On n'a pas besoin de les modifier : tout se règle dans config.py."""
import math
import os

import numpy as np
import pandas as pd
from scipy import stats

import config as C

ICI = os.path.dirname(os.path.abspath(__file__))
SORTIES = os.path.join(ICI, "sorties")
os.makedirs(SORTIES, exist_ok=True)


# ---- affichage -----------------------------------------------------------------------
def titre(txt):
    print("\n" + txt.upper() + "\n" + "=" * len(txt))


def nb(v, dec=2):
    """Un nombre à la française : 1 234,56."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "—"
    return f"{v:,.{dec}f}".replace(",", " ").replace(".", ",")


def p_txt(p):
    return "p < 0,001" if p < 0.001 else f"p = {nb(p, 3)}"


def qualif(v, seuils=(0.2, 0.5, 0.8)):
    """Le mot qui va avec une taille d'effet, d'après les seuils usuels de Cohen."""
    v = abs(v)
    noms = ["négligeable", "petit", "moyen", "fort"]
    return noms[sum(v >= s for s in seuils)]


def enregistrer(fig, nom):
    chemin = os.path.join(SORTIES, nom)
    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    print(f"  graphique enregistré : sorties/{nom}")


# ---- les données ------------------------------------------------------------------------
def charger_brut():
    chemin = C.FICHIER if os.path.isabs(C.FICHIER) else os.path.join(ICI, C.FICHIER)
    return pd.read_csv(chemin, sep=C.SEPARATEUR)


def charger_propre():
    """Les données nettoyées par 01_nettoyer.py ; si elles n'existent pas encore, on nettoie d'abord."""
    chemin = os.path.join(SORTIES, "donnees_propres.csv")
    if not os.path.exists(chemin):
        print("(sorties/donnees_propres.csv absent : nettoyage lancé d'abord)")
        d, _ = nettoyer(charger_brut())
        d.to_csv(chemin, index=False, encoding="utf-8")
    d = pd.read_csv(chemin)
    d["condition_A"] = (d[C.CONDITION].astype(str) == list(C.VERSIONS)[0]).astype(int)
    return d


def nettoyer(d):
    """Retire, étape par étape, ce qui ne doit pas entrer dans l'analyse, et garde la trace de chaque retrait."""
    journal = [("Réponses reçues", 0, len(d))]

    def etape(masque_a_retirer, raison):
        nonlocal d
        n = int(masque_a_retirer.sum())
        d = d[~masque_a_retirer].copy()
        journal.append((raison, n, len(d)))

    if C.IDENTIFIANT and C.IDENTIFIANT in d:
        etape(d.duplicated(C.IDENTIFIANT, keep="first"), "doublons (même identifiant)")
    for col, valeur, raison in C.FILTRES:
        if col in d:
            etape(d[col].astype(str) == str(valeur), raison)
    if C.VAN_WESTENDORP:
        v = [C.VAN_WESTENDORP[k] for k in ("trop_bon_marche", "bon_marche", "cher", "trop_cher")]
        croissant = (d[v].diff(axis=1).iloc[:, 1:] >= 0).all(axis=1)
        etape(~croissant, "Van Westendorp : seuils qui ne montent pas")
    if C.GABOR_GRANGER:
        prix = sorted(C.GABOR_GRANGER)
        oui = pd.DataFrame({p: d[C.GABOR_GRANGER[p]].astype(str) == C.OUI_GG for p in prix})
        incoherent = (oui.astype(int).diff(axis=1).iloc[:, 1:] > 0).any(axis=1)   # un Oui après un Non, à prix plus élevé
        etape(incoherent, "Gabor-Granger : accepte un prix plus haut qu'un prix refusé")
    for item in C.ITEMS_INVERSES:
        if item in d:
            d[item] = C.ECHELLE_MAX + 1 - d[item]
    return d, journal


def groupes(d, col):
    """Les valeurs de col dans chaque version, dans l'ordre de VERSIONS."""
    return [d.loc[d[C.CONDITION].astype(str) == v, col].dropna() for v in C.VERSIONS]


# ---- comparer deux versions --------------------------------------------------------------
def d_cohen(a, b):
    return (a.mean() - b.mean()) / math.sqrt((a.var() + b.var()) / 2)


def welch(d, col, libelle):
    a, b = groupes(d, col)
    lev = stats.levene(a, b)
    r = stats.ttest_ind(a, b, equal_var=False)
    eff = d_cohen(a, b)
    va, vb = [C.VERSIONS[k] for k in C.VERSIONS]
    sig = r.pvalue < C.SEUIL
    phrase = (f"{libelle} : {nb(a.mean())} en version {va} (n = {len(a)}) contre {nb(b.mean())} en version {vb} (n = {len(b)}) ; "
              f"t de Welch = {nb(r.statistic)}, {p_txt(r.pvalue)}, d de Cohen = {nb(eff)} ({qualif(eff)}). "
              + ("La différence est significative." if sig else "La différence n'est pas significative."))
    return {"moy_a": a.mean(), "moy_b": b.mean(), "n_a": len(a), "n_b": len(b), "levene_p": lev.pvalue,
            "t": r.statistic, "ddl": r.df, "p": r.pvalue, "d": eff, "phrase": phrase}


def chi2(d, col, libelle):
    tab = pd.crosstab(d[C.CONDITION].astype(str), d[col].astype(str)).reindex(list(C.VERSIONS))
    khi, p, ddl, attendus = stats.chi2_contingency(tab, correction=False)
    v = math.sqrt(khi / (tab.values.sum() * (min(tab.shape) - 1)))
    parts = (tab.get(C.OUI_GG, pd.Series(0, index=tab.index)) / tab.sum(axis=1) * 100)
    va, vb = [C.VERSIONS[k] for k in C.VERSIONS]
    phrase = (f"{libelle} : {nb(parts.iloc[0], 0)} % en version {va} contre {nb(parts.iloc[1], 0)} % en version {vb} ; "
              f"chi² = {nb(khi)}, {ddl} ddl, {p_txt(p)}, V de Cramer = {nb(v)} ({qualif(v, (0.1, 0.3, 0.5))}). "
              + ("Le lien est significatif." if p < C.SEUIL else "Le lien n'est pas significatif.")
              + (" Attention : au moins une case a moins de 5 effectifs attendus, le chi² n'est pas fiable." if (attendus < 5).any() else ""))
    return {"tableau": tab, "chi2": khi, "p": p, "ddl": ddl, "v": v, "phrase": phrase}


def puissance(n_a, n_b, effet=0.5):
    """La probabilité de détecter un effet de taille donnée avec ces effectifs (test t, seuil de 5 %)."""
    from statsmodels.stats.power import TTestIndPower
    return TTestIndPower().power(effet, n_a, C.SEUIL, ratio=n_b / n_a)


def effet_detectable(n_a, n_b, puissance_visee=0.8):
    """Le plus petit effet (d de Cohen) que ces effectifs détectent avec la puissance visée : l'analyse de sensibilité."""
    from statsmodels.stats.power import TTestIndPower
    return TTestIndPower().solve_power(None, nobs1=n_a, alpha=C.SEUIL, power=puissance_visee, ratio=n_b / n_a)


# ---- Van Westendorp et Gabor-Granger ---------------------------------------------------------
def courbes_vw(d, grille=None):
    vw = C.VAN_WESTENDORP
    if grille is None:
        hi = np.nanpercentile(d[vw["trop_cher"]], 97)
        grille = np.linspace(0, hi, 400)
    n = len(d)
    c = pd.DataFrame({"prix": grille})
    c["trop_bon_marche"] = [(d[vw["trop_bon_marche"]] >= p).sum() / n for p in grille]
    c["bon_marche"] = [(d[vw["bon_marche"]] >= p).sum() / n for p in grille]
    c["cher"] = [(d[vw["cher"]] <= p).sum() / n for p in grille]
    c["trop_cher"] = [(d[vw["trop_cher"]] <= p).sum() / n for p in grille]
    return c


def croisement(c, a, b):
    """Le prix où la courbe a croise la courbe b (interpolation linéaire).
    Si les deux courbes se touchent sur un palier (toutes deux à 0 %, par exemple), on prend le milieu du palier."""
    diff = (c[a] - c[b]).values
    prix = c["prix"].values
    signe = np.sign(diff)
    depart = next((s for s in signe if s != 0), 0)
    for i in range(1, len(diff)):
        if signe[i] != 0 and signe[i] != depart:
            j = i - 1
            while j >= 0 and signe[j] == 0:
                j -= 1
            if j < i - 1:                                   # un palier où les courbes se confondent
                return (prix[j + 1] + prix[i - 1]) / 2
            return prix[j] + (prix[i] - prix[j]) * diff[j] / (diff[j] - diff[i])
    return float("nan")


def points_vw(c):
    return {"PMC": croisement(c, "trop_bon_marche", "cher"),       # point marginal de bon marché : bas de la zone
            "OPP": croisement(c, "trop_bon_marche", "trop_cher"),  # prix optimal
            "IPP": croisement(c, "bon_marche", "cher"),            # prix d'indifférence
            "PME": croisement(c, "bon_marche", "trop_cher")}       # point marginal de cherté : haut de la zone


def gabor_granger(d):
    prix = sorted(C.GABOR_GRANGER)
    taux = [(d[C.GABOR_GRANGER[p]].astype(str) == C.OUI_GG).mean() for p in prix]
    t = pd.DataFrame({"prix": prix, "taux": taux})
    t["ca_par_repondant"] = t.prix * t.taux
    t["marge_par_repondant"] = (t.prix - C.COUT_VARIABLE) * t.taux
    return t


# ---- les échelles -------------------------------------------------------------------------
def alpha_cronbach(x):
    x = x.dropna()
    k = x.shape[1]
    return k / (k - 1) * (1 - x.var(ddof=1).sum() / x.sum(axis=1).var(ddof=1))


def description_mesure():
    return "\n".join(f"{nom} =~ " + " + ".join(items) for nom, items in C.ECHELLES.items())


def ajuster(description, d):
    import semopy
    m = semopy.Model(description)
    m.fit(d)
    return m


def indices_ajustement(m):
    """CFI, TLI, RMSEA donnés par semopy ; SRMR recalculé à partir des matrices observée et reproduite."""
    import semopy
    s = semopy.calc_stats(m).T["Value"]
    obs = np.asarray(m.mx_cov)
    rep = np.asarray(m.calc_sigma()[0])
    sd = np.sqrt(np.diag(obs))
    resid = (obs - rep) / np.outer(sd, sd)
    tri = np.tril_indices_from(resid)
    srmr = float(np.sqrt(np.mean(resid[tri] ** 2)))
    return {"chi2": float(s["chi2"]), "ddl": float(s["DoF"]), "p_chi2": float(s["chi2 p-value"]),
            "cfi": min(1.0, float(s["CFI"])), "tli": float(s["TLI"]), "rmsea": float(s["RMSEA"]), "srmr": srmr}


def poids_standardises(m):
    t = m.inspect(std_est=True)
    t = t[(t.op == "~") & (t.rval.isin(list(C.ECHELLES)))]
    return t[["rval", "lval", "Est. Std", "p-value"]].rename(columns={"rval": "construit", "lval": "item", "Est. Std": "poids", "p-value": "p"})


def fiabilite_composite(poids):
    s = poids.sum()
    return s ** 2 / (s ** 2 + (1 - poids ** 2).sum())


def ave(poids):
    return (poids ** 2).mean()


def htmt(d):
    """Hétérotrait-monotrait : corrélation moyenne entre items de deux construits,
    rapportée à la corrélation moyenne des items à l'intérieur de chacun."""
    r = d[[i for items in C.ECHELLES.values() for i in items]].corr().abs()
    noms = list(C.ECHELLES)

    def mono(items):
        sous = r.loc[items, items].values
        return sous[np.triu_indices_from(sous, 1)].mean()

    out = pd.DataFrame(index=noms, columns=noms, dtype=float)
    for i, a in enumerate(noms):
        for b in noms[i + 1:]:
            hetero = r.loc[C.ECHELLES[a], C.ECHELLES[b]].values.mean()
            out.loc[b, a] = hetero / math.sqrt(mono(C.ECHELLES[a]) * mono(C.ECHELLES[b]))
    return out


def scores_moyens(d):
    """Le score de chaque construit : la moyenne de ses items (après recodage des items inversés)."""
    d = d.copy()
    for nom, items in C.ECHELLES.items():
        d[nom] = d[items].mean(axis=1)
    return d


def mediation_bootstrap(d, x, m, y, controles=(), n=5000, graine=2026):
    """Médiation simple (PROCESS, modèle 4) : a = effet de x sur m, b = effet de m sur y à x constant,
    effet indirect a × b, et son intervalle de confiance à 95 % par bootstrap percentile."""
    cols = [x, m, y, *controles]
    v = d[cols].dropna().to_numpy(float)
    X, M, Y, W = v[:, 0], v[:, 1], v[:, 2], v[:, 3:]

    def coefs(X, M, Y, W):
        un = np.ones((len(X), 1))
        a = np.linalg.lstsq(np.column_stack([un, X, W]), M, rcond=None)[0][1]
        cb = np.linalg.lstsq(np.column_stack([un, X, M, W]), Y, rcond=None)[0]
        return a, cb[2], cb[1]

    a, b, c_direct = coefs(X, M, Y, W)
    rng = np.random.default_rng(graine)
    ab = []
    for _ in range(n):
        i = rng.integers(0, len(X), len(X))
        aa, bb, _ = coefs(X[i], M[i], Y[i], W[i])
        ab.append(aa * bb)
    bas, haut = np.percentile(ab, [2.5, 97.5])
    return {"a": a, "b": b, "ab": a * b, "direct": c_direct, "bas": bas, "haut": haut, "n": len(X), "tirages": n}
