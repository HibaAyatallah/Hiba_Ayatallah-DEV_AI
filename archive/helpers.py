"""Fonctions pures de l'interface : chargement du modèle, prédiction, résumé.

Séparées de app.py pour être testables sans lancer Streamlit.
Supporte à la fois l'API officielle du TP3 et les helpers compatibles.
"""
from __future__ import annotations

import sys
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
DEFAULT_SEUIL_INCERTITUDE = 0.60
SEUIL_INCERTITUDE = DEFAULT_SEUIL_INCERTITUDE   # en dessous, on affiche « à vérifier »


def charger_predicteur():
    """Renvoie la fonction predict() du TP2, ou lève FileNotFoundError."""
    if not MODELE.exists():
        raise FileNotFoundError(
            "models/sentiment.joblib absent : lancez d'abord python src/train.py"
        )
    sys.path.insert(0, str(RACINE / "src"))
    from predict import predict  # noqa: E402  (import tardif : le modèle doit exister)
    return predict


def classer(texte: str, predicteur=None) -> dict[str, Any]:
    """Prédiction enrichie d'un verdict lisible par un non-spécialiste."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("texte vide")
    if predicteur is None:
        predicteur = charger_predicteur()
    resultat = dict(predicteur(texte))
    score = float(resultat["score"])
    incertain = score < SEUIL_INCERTITUDE
    resultat["incertain"] = incertain
    resultat["verdict"] = "à vérifier" if incertain else str(resultat["label"])
    return resultat


def predire_lot(df: pd.DataFrame, predicteur=None, colonne: str = "review") -> pd.DataFrame:
    """Ajoute les colonnes prediction, confiance et verdict à un tableau d'avis."""
    if colonne not in df.columns:
        raise KeyError(f"colonne '{colonne}' absente du fichier")
    if predicteur is None:
        predicteur = charger_predicteur()
    lignes = [classer(str(t), predicteur) for t in df[colonne].fillna("") if str(t).strip()]
    if not lignes:
        raise ValueError("aucun avis exploitable dans le fichier")
    sortie = df.loc[df[colonne].fillna("").astype(str).str.strip() != ""].copy()
    sortie["prediction"] = [item["label"] for item in lignes]
    sortie["confiance"] = [round(item["score"], 3) for item in lignes]
    sortie["verdict"] = [item["verdict"] for item in lignes]
    return sortie


def resumer(df: pd.DataFrame) -> dict[str, int | float]:
    """Les trois chiffres que l'équipe relation client regarde en premier."""
    negatifs = int((df["prediction"] == "negative").sum())
    a_verifier = int((df["verdict"] == "à vérifier").sum())
    total = len(df)
    return {
        "total": total,
        "negatifs": negatifs,
        "part_negatifs": round(100 * negatifs / total, 1) if total else 0.0,
        "a_verifier": a_verifier,
        "confiance_moyenne": round(float(df["confiance"].mean()), 3) if total else 0.0,
    }


# --- Fonctions utilitaires compatibles et aliases pour le traitement par lot ---

def classer_avis(texte: str, seuil: float = DEFAULT_SEUIL_INCERTITUDE, predicteur=None) -> dict[str, Any]:
    """Classification avec seuil configurable."""
    if not isinstance(texte, str) or not texte.strip():
        raise ValueError("Le texte ne peut pas être vide.")
    if predicteur is None:
        predicteur = charger_predicteur()
    resultat = predicteur(texte)
    score = float(resultat["score"])
    label = str(resultat["label"])
    verdict = "à vérifier" if score < float(seuil) else label
    return {
        "label": label,
        "score": score,
        "verdict": verdict,
        "seuil": float(seuil),
        "automatique": score >= float(seuil),
        "incertain": score < float(seuil),
    }


def traiter_fichier_csv(fichier: Any, seuil: float = DEFAULT_SEUIL_INCERTITUDE, predicteur=None) -> pd.DataFrame:
    """Lit un CSV ou DataFrame et ajoute les métadonnées de prédiction."""
    if isinstance(fichier, pd.DataFrame):
        dataframe = fichier.copy()
    elif hasattr(fichier, "read"):
        contenu = fichier.read()
        if isinstance(contenu, bytes):
            contenu = contenu.decode("utf-8")
        dataframe = pd.read_csv(StringIO(contenu))
    else:
        dataframe = pd.read_csv(fichier)

    if "review" not in dataframe.columns:
        raise ValueError("Le fichier doit contenir une colonne 'review'.")

    lignes = []
    for avis in dataframe["review"].fillna(""):
        pred = classer_avis(str(avis), seuil=seuil, predicteur=predicteur)
        lignes.append(pred)

    df_res = dataframe.copy()
    df_res["label"] = [item["label"] for item in lignes]
    df_res["score"] = [item["score"] for item in lignes]
    df_res["verdict"] = [item["verdict"] for item in lignes]
    df_res["automatique"] = [item["automatique"] for item in lignes]
    return df_res.sort_values("score", ascending=False, kind="mergesort").reset_index(drop=True)


def resumer_lot(dataframe: pd.DataFrame) -> dict[str, int | float]:
    """Résumé statistique d'un lot d'avis."""
    if dataframe.empty:
        return {"total": 0, "positifs": 0, "negatifs": 0, "a_verifier": 0, "taux_a_verifier": 0.0}
    total = int(len(dataframe))
    a_verifier = int((dataframe["verdict"] == "à vérifier").sum())
    positifs = int((dataframe["verdict"] == "positive").sum())
    negatifs = int((dataframe["verdict"] == "negative").sum())
    return {
        "total": total,
        "positifs": positifs,
        "negatifs": negatifs,
        "a_verifier": a_verifier,
        "taux_a_verifier": round(a_verifier / total, 4) if total else 0.0,
    }


def exporter_csv(dataframe: pd.DataFrame) -> str:
    """Export au format CSV textuel."""
    return dataframe.to_csv(index=False)


analyser_avis = classer_avis
traiter_lot = traiter_fichier_csv
resumer_avis = resumer_lot
exporter_resultats = exporter_csv

__all__ = [
    "DEFAULT_SEUIL_INCERTITUDE",
    "SEUIL_INCERTITUDE",
    "charger_predicteur",
    "classer",
    "predire_lot",
    "resumer",
    "classer_avis",
    "analyser_avis",
    "traiter_fichier_csv",
    "traiter_lot",
    "resumer_lot",
    "resumer_avis",
    "exporter_csv",
    "exporter_resultats",
]
