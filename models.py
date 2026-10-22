from pydantic import BaseModel, Field

# Une partie de la leçon, toujours accompagnée de sa source
class Section(BaseModel):
    heading: str = Field(min_length=1)    # min_length=1 : texte vide refusé
    text: str = Field(min_length=1)
    source_url: str = Field(min_length=1)

# Une question à choix multiples pour vérifier ce qu'on a retenu
class QuizQuestion(BaseModel):
    question: str = Field(min_length=1)
    choices: list[str] = Field(min_length=2)   # au moins 2 choix
    answer: str

# La leçon complète, Pydantic refuse tout JSON qui ne respecte pas le format ci-dessous
class Lesson(BaseModel):
    title: str = Field(min_length=1)
    artist: str = Field(min_length=1)
    year: str
    sections: list[Section] = Field(min_length=1)   # au moins une section
    quiz: list[QuizQuestion] = Field(min_length=1)

class Review(BaseModel):
    approved: bool # True seulement si tout est vérifié
    problems: list[str] # Une phrase par problème, liste vide si tout OK