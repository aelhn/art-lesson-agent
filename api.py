from fastapi import FastAPI
from pydantic import BaseModel, Field

from main import create_lesson
from models import Lesson, Review

# -- API REST : la même boucle rédaction / relecture que main.py, mais appelable en HTTP
app = FastAPI(title="art-lesson-agent")

# Ce que le client envoie. Le nom de l'oeuvre part dans le prompt de l'agent : on refuse le vide et on borne sa longueur
class LessonRequest(BaseModel):
    artwork: str = Field(min_length=1, max_length=200)

# Ce que l'API renvoie : la leçon, le verdict du relecteur et les métriques (coût, durée, tours)
class LessonResponse(BaseModel):
    lesson: Lesson
    review: Review
    metrics: dict

@app.post("/lessons")
async def post_lesson(request: LessonRequest) -> LessonResponse: # FastAPI vérifie la requête avec LessonRequest et renvoie 422 si elle est invalide
    lesson, review, metrics = await create_lesson(request.artwork)
    return LessonResponse(lesson=lesson, review=review, metrics=metrics)
