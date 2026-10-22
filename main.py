import asyncio
import sys
from pathlib import Path

from reviewer import review_lesson
from writer import write_lesson

MAX_REVISIONS = 2

async def main():
    # Nom de l'oeuvre donné en ligne de commande
    artwork = sys.argv[1]
    print(f"Rédaction de la leçon: {artwork}")
    lesson = await write_lesson(artwork)
    review = await review_lesson(lesson)

    revisions = 0 # Tant que le relecteur refuse, le rédacteur corrige (max 2 fois pour l'instant pour limiter le coût)
    while not review.approved and revisions < MAX_REVISIONS:
        print("Problèmes relevés par le relecteur :")
        for problem in review.problems:
            print(f"    - {problem}")
        lesson = await write_lesson(artwork, lesson, review.problems)
        review = await review_lesson(lesson)
        revisions += 1
    if review.approved: 
        print("Leçon validée par le relecteur")
    else: 
        print("Attention : la leçon n'est pas validée, relis-la avant de l'utiliser")
        
    # On enregistre la leçon dans output/ (ignoré par git)
    Path("output").mkdir(exist_ok=True)
    file = Path("output") / f"{lesson.title}.json" # PS : le / de Path assemble les morceaux du chemin : output\<titre>.json
    file.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")
    print(f"Leçon enregistrée dans {file}")

asyncio.run(main())