import sys

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ToolUseBlock, ResultMessage
from models import Lesson

# -- Agent qui écrit la première passe de la leçon
# Le rôle et les règles de l'agent : c'est ici que se joue le prompt engineering
SYSTEM_PROMPT = """Tu es médiateur culturel. Tu rédiges des leçons d'initiation à l'art pour des débutants.
Règles :
- Utilise uniquement les informations des articles Wikipédia obtenus avec tes outils, jamais ta mémoire.
- Cherche d'abord l'œuvre avec search_wikipedia, puis lis l'article avec get_article.
- Chaque section indique dans source_url l'adresse de l'article d'où viennent ses informations.
- 3 sections courtes (80 mots maximum chacune), dans un langage simple.
- 3 questions de quiz avec 3 choix chacune. answer reprend exactement l'un des choix.
"""

async def write_lesson(artwork: str, previous: Lesson = None, problems: list[str] = None) -> Lesson: # previous et problems ne sont remplis que pour une correction
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT, 
        mcp_servers={"wikipedia": {"command": sys.executable, "args": ["mcp_server.py"]}}, # Le SDK lance lui-même notre serveur MCP avec le Python du .venv
        allowed_tools=["mcp__wikipedia__search_wikipedia","mcp__wikipedia__get_article"], # Que deux outils autorisés
        strict_mcp_config=True,     # ignore les connecteurs du compte claude.ai
        tools=[],
        setting_sources=[],         # ignore les réglages privés de Claude Code (ceux présents sur la machine car local)
        max_turns=10,               # limite de sécurité au cas où l'agent tourne en rond
        output_format={"type": "json_schema", "schema": Lesson.model_json_schema()},    # Claude doit remplir exactement le schéma de Lesson
    )

    lesson = None

    prompt = f"Rédige la leçon sur l'oeuvre : {artwork}" # En cas de correction, on lui donne la leçon précédente et les remarques du relecteur
    if previous is not None:
        prompt += "\n\nVoici ta leçon précédente :\n" + previous.model_dump_json(indent=2)
        prompt += "\n\nLe relecteur a relevé ces problèmes, corrige-les :\n"
        for problem in problems:
            prompt += f"- {problem}\n"


    async for message in query(prompt=prompt, options=options): # PS : f"" concatène le texte avec la valeur de la variable
        if isinstance(message, AssistantMessage): # On affiche chaque appel d'outils pour suivre le travail de l'agent
            for block in message.content:
                if isinstance(block, ToolUseBlock) and block.name != "StructuredOutput": # Bloque l'affichage de StructuredOuput. C'est l'outil interne qui met en forme le json, pas utile de le montrer
                    print(f"    outil : {block.name} {block.input}")

        if isinstance(message, ResultMessage): # Le dernier message contient la leçon au format JSON
            if message.structured_output is None:
                raise RuntimeError(f"Aucune leçon renvoyée ({message.subtype})")

            lesson = Lesson.model_validate(message.structured_output) # Transforme le dictionnaire en objet Lesson (et vérifie au passage qu'il est valide)

    return lesson
# --