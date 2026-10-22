import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

async def main():
    options = ClaudeAgentOptions(
        system_prompt="Tu es guide de musée. Réponds en deux phrases.",
        max_turns=1,
    )
    async for message in query(prompt="Présente la Joconde.", options=options):
        print(type(message).__name__)
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)

asyncio.run(main()) # Démarre l'ensemble. Le SDK lance Claude Code en fond et attend sa réponse sans bloquer le programme (mode asynchrone)
