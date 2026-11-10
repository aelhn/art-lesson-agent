import asyncio
import sys
from pathlib import Path

from reviewer import review_lesson
from writer import write_lesson

MAX_REVISIONS = 2


# Rédige la leçon, puis la fait relire, avec correctifs au besoin
# Renvoie la leçon, le dernier verdict du relecteur et le total des métriques (coût, durée, tours)
async def create_lesson(artwork: str):
    runs = [] # Les métriques de chaque appel d'agent, rédacteur comme relecteur

    lesson, metrics = await write_lesson(artwork)
    runs.append(metrics)
    review, metrics = await review_lesson(lesson)
    runs.append(metrics)

    revisions = 0 # Tant que le relecteur refuse, le rédacteur corrige (max 2 fois pour l'instant pour limiter le coût)
    while not review.approved and revisions < MAX_REVISIONS:
        print("Problèmes relevés par le relecteur :")
        for problem in review.problems:
            print(f"    - {problem}")
        lesson, metrics = await write_lesson(artwork, lesson, review.problems)
        runs.append(metrics)
        review, metrics = await review_lesson(lesson)
        runs.append(metrics)
        revisions += 1

    # Total sur toute la boucle, révisions comprises : on additionne chaque clé sur tous les appels
    total = {key: sum(run[key] for run in runs) for key in runs[0]}
    return lesson, review, total

def save_lesson(lesson) -> Path: # Enregistre la leçon dans output/ (ignoré par git) et renvoie le chemin du fichier
    Path("output").mkdir(exist_ok=True)  # Le / de Path assemble les morceaux du chemin : output\<titre>.json
    file = Path("output") / f"{lesson.title}.json"
    file.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")
    return file

async def main():
    # Nom de l'oeuvre donné en ligne de commande
    artwork = sys.argv[1] 
    print(f"Rédaction de la leçon: {artwork}")
    lesson, review, metrics = await create_lesson(artwork)

    if review.approved: 
        print("Leçon validée par le relecteur")
    else: 
        print("Attention : la leçon n'est pas validée, relis-la avant de l'utiliser")

    file = save_lesson(lesson)
    print(f"Leçon enregistrée dans {file}")
    print(f"Coût : {metrics['cost_usd']:.4f} $ | Durée des agents : {metrics['duration_ms'] / 1000:.1f} s | Tours : {metrics['num_turns']}")

# Lance le programme seulement si on exécute ce fichier directement.
# Un test qui fait "import main" ne déclenche donc rien.
if __name__ == "__main__":
    asyncio.run(main())