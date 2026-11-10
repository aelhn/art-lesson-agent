from fastapi.testclient import TestClient

import api
from models import Review

# TestClient envoie de vraies requêtes HTTP à l'API, mais sans lancer de serveur
client = TestClient(api.app)

def test_post_lesson_returns_lesson_review_and_metrics(monkeypatch, lesson):
    async def fake_create_lesson(artwork):
        return lesson, Review(approved=True, problems=[]), {"cost_usd": 0.04, "duration_ms": 4000, "num_turns": 12}

    # La vraie boucle d'agents est remplacée par un faux : ni Claude, ni Wikipédia
    monkeypatch.setattr(api, "create_lesson", fake_create_lesson)

    response = client.post("/lessons", json={"artwork": "Le Radeau de la Méduse"})

    assert response.status_code == 200
    data = response.json()
    assert data["lesson"]["artist"] == "Théodore Géricault"
    assert data["review"]["approved"] is True
    assert data["metrics"] == {"cost_usd": 0.04, "duration_ms": 4000, "num_turns": 12}


def test_empty_artwork_is_refused(monkeypatch):
    calls = []

    async def fake_create_lesson(artwork):
        calls.append(artwork)

    monkeypatch.setattr(api, "create_lesson", fake_create_lesson)

    response = client.post("/lessons", json={"artwork": ""})

    assert response.status_code == 422 # 422 : requête invalide, refusée par FastAPI
    assert calls == [] # les agents n'ont pas été lancés, donc rien n'a été payé
