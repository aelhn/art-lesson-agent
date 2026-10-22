import asyncio
from fastmcp import Client
from mcp_server import mcp

async def main():
    async with Client(mcp) as client:
        result = await client.call_tool("search_wikipedia", {"query": "Radeau de la Méduse"})
        print(result.data)
        
        first_title = result.data[0]["title"] # On récupère l'article de la première page trouvée
        article = await client.call_tool("get_article", {"title": first_title})
        print(article.data["url"])
        print(article.data["text"][:300]) # Les 300 premiers caractères suffisent pour vérifier si test OK

asyncio.run(main())