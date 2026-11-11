"""Tests de l'interface de démonstration (TP3).

Ils portent sur les fonctions pures de ui/helpers.py, pas sur l'affichage :
Streamlit n'est pas lancé pendant les tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"
sys.path.insert(0, str(RACINE / "ui"))


@pytest.fixture(scope="module")
def predire():
    if not MODELE.exists():
        pytest.skip("models/sentiment.joblib absent sur ce poste (normal en CI)")
    from helpers import charger_predicteur
    return charger_predicteur()


def test_helpers_importables():
    """L'interface se charge sans Streamlit : la logique est bien séparée de l'affichage."""
    import helpers
    for nom in ["charger_predicteur", "classer", "predire_lot", "resumer"]:
        assert hasattr(helpers, nom), f"fonction manquante : {nom}"


def test_classer_ajoute_un_verdict(predire):
    from helpers import classer
    r = classer("Service impeccable, je recommande", predire)
    assert {"label", "score", "verdict", "incertain"} <= set(r)
    assert r["verdict"] in {"positive", "negative", "à vérifier"}
    with pytest.raises(ValueError):
        classer("   ", predire)


def test_lot_et_resume(predire):
    from helpers import predire_lot, resumer
    df = pd.DataFrame({"review": [
        "Produit cassé, service injoignable",
        "Livraison rapide, très satisfait",
        "",
    ]})
    sortie = predire_lot(df, predire)
    assert len(sortie) == 2, "les lignes vides doivent être écartées"
    assert {"prediction", "confiance", "verdict"} <= set(sortie.columns)
    r = resumer(sortie)
    assert r["total"] == 2 and 0 <= r["part_negatifs"] <= 100
    with pytest.raises(KeyError):
        predire_lot(pd.DataFrame({"texte": ["a"]}), predire)


def test_analyse_avis_positive(predire):
    from helpers import classer_avis
    resultat = classer_avis("Service impeccable et livraison très rapide !", predicteur=predire)
    assert resultat["label"] == "positive"
    assert resultat["score"] >= 0.5
    assert resultat["verdict"] == "positive"


def test_analyse_avis_avec_seuil_incertain(predire):
    from helpers import classer_avis
    resultat = classer_avis("Produit correct mais pas exceptionnel", seuil=0.999, predicteur=predire)
    assert resultat["verdict"] == "à vérifier"
    assert 0.0 <= resultat["score"] <= 1.0


def test_traitement_lot_et_resume(predire):
    from helpers import resumer_lot, traiter_fichier_csv
    dataframe = pd.DataFrame({
        "review": [
            "Service impeccable et livraison très rapide !",
            "Produit cassé et service client injoignable",
            "Très bien, mais pas parfait",
        ]
    })
    traite = traiter_fichier_csv(dataframe, seuil=0.60, predicteur=predire)
    resume = resumer_lot(traite)

    assert set(traite.columns) >= {"review", "label", "score", "verdict", "automatique"}
    assert resume["total"] == 3
    assert resume["positifs"] + resume["negatifs"] + resume["a_verifier"] == 3
    assert resume["taux_a_verifier"] >= 0.0
