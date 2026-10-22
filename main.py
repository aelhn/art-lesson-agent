import asyncio
import sys
from pathlib import Path

from writer import write_lesson

async def main():
    # Nom de l'oeuvre donné en ligne de commande
    artwork = sys.argv[1]
    print(f"Rédaction de la leçon: {artwork}")
    lesson = await write_lesson(artwork)

    # On enregistre la leçon dans output/ (ignoré par git)
    Path("output").mkdir(exist_ok=True)
    file = Path("output") / f"{lesson.title}.json" # PS : le / de Path assemble les morceaux du chemin : output\<titre>.json
    file.write_text(lesson.model_dump_json(indent=2), encoding="utf-8")
    print(f"Leçon enregistrée dans {file}")

asyncio.run(main())