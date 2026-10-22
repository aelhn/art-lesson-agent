import asyncio 
from fastmcp import Client

# Le client lance le conteneur et lui parle par stdio (standard input/ouput), comme le ferait l'agent
config = {"mcpServers": {"wikipedia": {"command": "docker", "args": ["run", "-i", "--rm", "art-lesson-mcp"]}}}

async def main():
    async with Client(config) as client:
        tools = await client.list_tools()
        print([tool.name for tool in tools])
        result = await client.call_tool("search_wikipedia", {"query": "Joconde"})
        print(result.data[0])

asyncio.run(main())