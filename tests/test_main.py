import pytest

import main
from models import Review

# Métriques renvoyées par chaque faux agent, pour vérifier le total
FAKE_METRICS = {"cost_usd": 0.01, "duration_ms": 1000, "num_turns": 3}

async def test_approved_lesson_is_not_rewritten(monkeypatch, lesson):
    calls = []  # on note chaque appel pour vérifier l'enchaînement

    async def fake_write(artwork, previous=None, problems=None):
        calls.append("write")
        return lesson, FAKE_METRICS

    async def fake_review(lesson_to_check):
        calls.append("review")
        return Review(approved=True, problems=[]), FAKE_METRICS

    # Les vrais agents sont remplacés par les faux pendant ce test
    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review, metrics = await main.create_lesson("Le Radeau de la Méduse")

    assert review.approved
    assert calls == ["write", "review"]


async def test_problems_are_sent_back_to_the_writer(monkeypatch, lesson):
    received = []
    # Le relecteur refuse une fois, puis valide
    reviews = [Review(approved=False, problems=["Date fausse"]), Review(approved=True, problems=[])]

    async def fake_write(artwork, previous=None, problems=None):
        received.append(problems)
        return lesson, FAKE_METRICS

    async def fake_review(lesson_to_check):
        return reviews.pop(0), FAKE_METRICS  # renvoie les verdicts dans l'ordre

    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review, metrics = await main.create_lesson("Le Radeau de la Méduse")

    assert review.approved
    # 1er passage sans problème, 2e avec la remarque du relecteur
    assert received == [None, ["Date fausse"]]


async def test_revisions_are_limited(monkeypatch, lesson):
    calls = []

    async def fake_write(artwork, previous=None, problems=None):
        calls.append("write")
        return lesson, FAKE_METRICS

    async def fake_review(lesson_to_check): # Un relecteur qui refuse toujours
        return Review(approved=False, problems=["Toujours faux"]), FAKE_METRICS

    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review, metrics = await main.create_lesson("Le Radeau de la Méduse")

    assert not review.approved

    assert calls.count("write") == 1 + main.MAX_REVISIONS # 1 rédaction de départ + 2 corrections au plus


async def test_metrics_are_summed_over_the_loop(monkeypatch, lesson):
    # Le relecteur refuse une fois, puis valide : 2 rédactions + 2 relectures = 4 appels
    reviews = [Review(approved=False, problems=["Date fausse"]), Review(approved=True, problems=[])]

    async def fake_write(artwork, previous=None, problems=None):
        return lesson, FAKE_METRICS

    async def fake_review(lesson_to_check):
        return reviews.pop(0), FAKE_METRICS

    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review, metrics = await main.create_lesson("Le Radeau de la Méduse")

    assert metrics["cost_usd"] == pytest.approx(4 * 0.01) # approx : additionner des décimaux ne tombe pas toujours juste (0.1 + 0.2 != 0.3)
    assert metrics["duration_ms"] == 4 * 1000
    assert metrics["num_turns"] == 4 * 3
