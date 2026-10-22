import requests
from fastmcp import FastMCP

mcp = FastMCP("wikipedia")

API_URL = "https://fr.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "art-lesson-agent/0.1 (github.com/aelhn)"} # Wikipédia refuse les requêtes sans User-Agent, on indique donc qui on est
MAX_CHARS = 8000

# @mcp.tool transforme la fonction en outil MCP.
# La docstring sert de description : c'est elle que lit Claude pour choisir l'outil.
@mcp.tool 
def search_wikipedia(query: str) -> list[dict]:
    """Search French Wikipedia. Returns up to 5 pages with their title and url."""
    params = {
        "action":"query",
        "list":"search",
        "srsearch":query,
        "srlimit":5,
        "format":"json",
    }
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status() # Lève une erreur si Wikipédia répond autre chose que 200 (OK)
    results = []

    for item in response.json()["query"]["search"]:
        url = "https://fr.wikipedia.org/wiki/" + item["title"].replace(" ", "_") # Remplace les espaces par des underscores dans l'URL
        results.append({"title": item["title"], "url": url})
    return results

@mcp.tool
def get_article(title: str) -> dict:
    """Get the plain text of a French Wikipedia article from its exact title."""
    params = {
        "action":"query",
        "prop":"extracts",  # précise qu'on veut le contenu de la page
        "explaintext":1,    # texte brut, sans HTML
        "redirects":1,      # si le titre n'est pas entièrement correct (ex. "Le Joconde"), renvoie la vraie page quand même
        "titles": title,
        "format": "json",
        "formatversion": 2, # format simplifié, "pages" devient une liste 
    }
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status() # Lève une erreur si Wikipédia répond autre chose que 200 (OK)

    page = response.json()["query"]["pages"][0] # Une seule page voulue, on récup la première à l'id 0
    text = page.get("extract", "") # Si page introuvable, texte vide renvoyé au lieu de l'extract attendu
    url = "https://fr.wikipedia.org/wiki/" + page["title"].replace(" ", "_")

    return {"title": page["title"], "url": url, "text": text[:MAX_CHARS]} # Texte coupé, article entier trop long pour l'agent

# Lancement
if __name__ == "__main__":
    mcp.run()
