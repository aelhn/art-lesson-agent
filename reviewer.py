import sys

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock, ResultMessage

from models import Lesson, Review

# -- Agent qui vérifie la leçon du rédacteur
REVIEW_PROMPT = """Tu es vérificateur de faits. On te donne une leçon d'art au format JSON.
Règles :
- Pour chaque section, lis l'article de source_url avec get_article. Le titre est la fin de l'URL, avec des espaces à la place des _.
- Vérifie que chaque fait (date, nom, chiffre, lieu) apparaît bien dans l'article.
- Vérifie que chaque réponse du quiz est juste d'après les sections.
- approved vaut true seulement si tout est vérifié. Sinon, décris chaque problème dans problems, en une phrase précise.
"""

async def review_lesson(lesson: Lesson) -> Review:
    options = ClaudeAgentOptions(
        system_prompt = REVIEW_PROMPT,
        mcp_servers={"wikipedia": {"command": sys.executable, "args": ["mcp_server.py"]}},
        allowed_tools=["mcp__wikipedia__get_article"], # Le relecteur n'a besoin que de lire les articles, pas de les chercher
        strict_mcp_config=True,
        tools=[],
        setting_sources=[],
        max_turns= 10,
        output_format={"type": "json_schema", "schema": Review.model_json_schema()},
    )

    review = None
    prompt = "Vérifie cette leçon :\n" + lesson.model_dump_json(indent=2)

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock) and block.name != "StructuredOutput":
                    print(f"    relecteur : {block.name} {block.input}")

        if isinstance(message, ResultMessage):
            if message.structured_output is None:
                raise RuntimeError(f"Aucun verdict renvoyé ({message.subtype})")
            review = Review.model_validate(message.structured_output)

    return review