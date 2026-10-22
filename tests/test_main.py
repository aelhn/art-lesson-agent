import main
from models import Review

async def test_approved_lesson_is_not_rewritten(monkeypatch, lesson):
    calls = []  # on note chaque appel pour vérifier l'enchaînement

    async def fake_write(artwork, previous=None, problems=None):
        calls.append("write")
        return lesson

    async def fake_review(lesson_to_check):
        calls.append("review")
        return Review(approved=True, problems=[])

    # Les vrais agents sont remplacés par les faux pendant ce test
    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review = await main.create_lesson("Le Radeau de la Méduse")

    assert review.approved
    assert calls == ["write", "review"]


async def test_problems_are_sent_back_to_the_writer(monkeypatch, lesson):
    received = []
    # Le relecteur refuse une fois, puis valide
    reviews = [Review(approved=False, problems=["Date fausse"]), Review(approved=True, problems=[])]

    async def fake_write(artwork, previous=None, problems=None):
        received.append(problems)
        return lesson

    async def fake_review(lesson_to_check):
        return reviews.pop(0)  # renvoie les verdicts dans l'ordre

    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review = await main.create_lesson("Le Radeau de la Méduse")

    assert review.approved
    # 1er passage sans problème, 2e avec la remarque du relecteur
    assert received == [None, ["Date fausse"]]


async def test_revisions_are_limited(monkeypatch, lesson):
    calls = []

    async def fake_write(artwork, previous=None, problems=None):
        calls.append("write")
        return lesson

    async def fake_review(lesson_to_check): # Un relecteur qui refuse toujours
        return Review(approved=False, problems=["Toujours faux"])

    monkeypatch.setattr(main, "write_lesson", fake_write)
    monkeypatch.setattr(main, "review_lesson", fake_review)

    result, review = await main.create_lesson("Le Radeau de la Méduse")

    assert not review.approved
    
    assert calls.count("write") == 1 + main.MAX_REVISIONS # 1 rédaction de départ + 2 corrections au plus