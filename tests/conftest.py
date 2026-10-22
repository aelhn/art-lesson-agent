import pytest

from models import Lesson

# "fixture" : pytest la donne à tout test qui a un paramètre nommé lesson
@pytest.fixture
def lesson():
    return Lesson(
        title="Le Radeau de la Méduse",
        artist="Théodore Géricault",
        year="1818-1819",
        sections=[{"heading": "Un naufrage", "text": "Un vrai naufrage en 1816.", "source_url": "https://fr.wikipedia.org/wiki/Le_Radeau_de_la_Méduse"}],
        quiz=[{"question": "Quel naufrage ?", "choices": ["La Méduse", "Le Titanic"], "answer": "La Méduse"}],
    )