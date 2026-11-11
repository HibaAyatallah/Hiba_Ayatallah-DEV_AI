"""Tests aux limites du contrat d'entrée (TP4, étape B).

PredictRequest promet un champ « text », chaîne de 1 à 2000 caractères.
Ce fichier vérifie cette promesse à ses frontières, puis au hasard (hypothesis).
"""
import json
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"
pytestmark = pytest.mark.skipif(not MODELE.exists(), reason="modèle non produit : python src/train.py")

CONTRAT = {"POSITIVE", "NEGATIVE", "INDETERMINE"}
# Caractères que str.strip() retire : la règle commune au schéma et à predict()
BLANCS = " \t\n\r\x0b\x0c\x1c\x1d\x1e\x1f\x85\xa0\u1680\u2000\u2003\u2028\u2029\u202f\u205f\u3000"


@pytest.fixture(scope="module")
def client():
    """Portée « module » : l'API démarre une fois pour tout le fichier (hypothesis l'exige)."""
    from fastapi.testclient import TestClient

    from api.main import app

    with TestClient(app) as c:  # le « with » exécute le lifespan : le modèle est chargé
        yield c


def en_json(valeur: object) -> bytes:
    """Corps de requête JSON, sous forme d'octets : permet aussi d'envoyer un corps invalide."""
    return json.dumps(valeur).encode("utf-8")


def forme_standard(corps: dict) -> bool:
    """La liste d'erreurs de FastAPI : des objets avec loc, msg et type."""
    detail = corps.get("detail")
    return isinstance(detail, list) and all({"loc", "msg", "type"} <= set(e) for e in detail)


CAS = [
    pytest.param(en_json({"text": ""}), 422, id="texte-vide"),
    pytest.param(en_json({"text": "   "}), 422, id="espaces-seuls"),
    pytest.param(en_json({"text": "a"}), 200, id="un-caractere"),
    pytest.param(en_json({"text": "a" * 2000}), 200, id="2000-caracteres"),
    pytest.param(en_json({"text": "a" * 2001}), 422, id="2001-caracteres"),
    pytest.param(en_json({}), 422, id="champ-absent"),
    pytest.param(en_json({"text": 42}), 422, id="autre-type"),
    pytest.param(b"pas du json", 422, id="corps-invalide"),
]


@pytest.mark.parametrize("corps, code_attendu", CAS)
def test_frontieres_du_contrat(client, corps, code_attendu):
    reponse = client.post("/predict", content=corps, headers={"Content-Type": "application/json"})
    assert reponse.status_code == code_attendu
    if code_attendu == 422:
        assert forme_standard(reponse.json()), f"422 hors format standard : {reponse.json()}"
    else:
        assert reponse.json()["label"] in CONTRAT


@settings(max_examples=150, deadline=None)
@given(texte=st.text(min_size=1, max_size=2000).filter(lambda s: s.strip()))
def test_tout_texte_non_blanc_recoit_une_reponse(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    assert reponse.json()["label"] in CONTRAT
    assert 0.0 <= reponse.json()["score"] <= 1.0


@settings(max_examples=100, deadline=None)
@given(texte=st.text(alphabet=st.sampled_from(BLANCS), min_size=1, max_size=50))
def test_tout_texte_blanc_est_refuse(client, texte):
    reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 422
    assert forme_standard(reponse.json())
