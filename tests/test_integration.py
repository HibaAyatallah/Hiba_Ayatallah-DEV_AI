"""Tests d'intégration : l'API telle qu'elle tourne vraiment (TP4, étape D)."""
from pathlib import Path

import pytest

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")


@pytest.fixture
def client_demarre():
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        yield client


class ModeleEnPanne:
    """Remplace le classifier : lève l'exception qu'on lui donne à chaque prédiction."""

    model_name = "modèle en panne (test)"

    def __init__(self, erreur: Exception) -> None:
        self.erreur = erreur

    def predict(self, text: str) -> dict:
        raise self.erreur


def test_demarrage_reel_charge_le_modele():
    """D.1 : un client ouvert par « with » exécute le lifespan."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as client:
        reponse = client.get("/health")
    assert reponse.status_code == 200
    assert "TP2" in reponse.json()["model"]


def test_modele_absent_l_api_refuse_de_demarrer(monkeypatch, tmp_path):
    """D.2 : le contrôle T20 du TP3, devenu automatique."""
    from fastapi.testclient import TestClient

    import predict as module_predict  # src/ est dans sys.path depuis l'import de api.model
    from api.main import app

    monkeypatch.setattr(module_predict, "MODELE", tmp_path / "absent.joblib")
    module_predict.charger_modele.cache_clear()  # sinon le modèle déjà chargé resterait en cache
    try:
        with pytest.raises(FileNotFoundError):
            with TestClient(app):
                pass
    finally:
        module_predict.charger_modele.cache_clear()


def test_modele_non_charge_repond_503(client_demarre, monkeypatch):
    """D.3 : l'API démarrée, le modèle retiré."""
    from api.main import app

    monkeypatch.setattr(app.state, "classifier", None)
    assert client_demarre.get("/health").status_code == 503
    assert client_demarre.post("/predict", json={"text": "Très bien"}).status_code == 503


@pytest.mark.parametrize("erreur", [RuntimeError("bug interne"), ValueError("bug interne")],
                         ids=["RuntimeError", "ValueError"])
def test_modele_en_panne_repond_500(client_demarre, monkeypatch, erreur):
    """D.4 : une panne du modèle est l'affaire du serveur (500), jamais du client (422)."""
    from api.main import app

    monkeypatch.setattr(app.state, "classifier", ModeleEnPanne(erreur))
    reponse = client_demarre.post("/predict", json={"text": "Très bien"})
    assert reponse.status_code == 500
    assert "bug interne" not in reponse.text, "le message interne a fuité vers le client"


def test_classes_inconnues_l_api_refuse_de_demarrer(monkeypatch):
    """E.3 : un modèle réentraîné sur d'autres étiquettes est refusé au démarrage."""
    from fastapi.testclient import TestClient

    import api.model as module_api
    from api.main import app

    class ModeleEtranger:
        classes_ = ["neg", "pos"]

    monkeypatch.setattr(module_api, "charger_modele", lambda: ModeleEtranger())
    with pytest.raises(ValueError, match="classes inconnues"):
        with TestClient(app):
            pass
