import pytest
from pydantic import ValidationError

from models import Lesson


def test_valid_lesson_is_accepted(lesson):
    data = lesson.model_dump()  # l'objet redevient un dictionnaire
    assert Lesson.model_validate(data).artist == "Théodore Géricault"


def test_lesson_without_sections_is_refused(lesson):
    data = lesson.model_dump()
    data["sections"] = []
    
    with pytest.raises(ValidationError): # Le test réussit seulement si pydantic lève une ValidationError
        Lesson.model_validate(data)


def test_empty_artist_is_refused(lesson):
    data = lesson.model_dump()
    data["artist"] = ""
    with pytest.raises(ValidationError):
        Lesson.model_validate(data)