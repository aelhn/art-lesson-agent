from fastmcp import Client

import mcp_server
from mcp_server import mcp

# Imite une réponse de requests, sans appeler Internet
class FakeResponse:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass  # une fausse réponse est toujours OK

    def json(self):
        return self.data

async def test_search_returns_titles_and_urls(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return FakeResponse({"query": {"search": [{"title": "Le Radeau de la Méduse"}]}})

    monkeypatch.setattr(mcp_server.requests, "get", fake_get) # Pendant ce test, requests.get est remplacé par notre faux

    async with Client(mcp) as client:
        result = await client.call_tool("search_wikipedia", {"query": "Méduse"})

    assert result.data == [
        {"title": "Le Radeau de la Méduse", "url": "https://fr.wikipedia.org/wiki/Le_Radeau_de_la_Méduse"}
    ]

async def test_article_text_is_cut(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return FakeResponse({"query": {"pages": [{"title": "Test", "extract": "a" * 20000}]}}) # Un article de 20 000 caractères

    monkeypatch.setattr(mcp_server.requests, "get", fake_get)

    async with Client(mcp) as client:
        result = await client.call_tool("get_article", {"title": "Test"})

    assert len(result.data["text"]) == mcp_server.MAX_CHARS

async def test_missing_article_gives_empty_text(monkeypatch):
    def fake_get(url, params, headers, timeout):
        return FakeResponse({"query": {"pages": [{"title": "Page inconnue", "missing": True}]}}) # Une page qui n'existe pas n'a pas de clé "extract"

    monkeypatch.setattr(mcp_server.requests, "get", fake_get)

    async with Client(mcp) as client:
        result = await client.call_tool("get_article", {"title": "Page inconnue"})

    assert result.data["text"] == ""