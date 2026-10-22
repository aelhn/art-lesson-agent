# Image de base : un Linux minimal avec Python déjà installé
FROM python:3.13-slim

# Dossier de travail dans le conteneur
WORKDIR /app

# Le serveur n'a besoin que de FastMCP et requests (pas du SDK Claude)
RUN pip install --no-cache-dir fastmcp requests

# On copie uniquement le serveur
COPY mcp_server.py .

# Commande lancée au démarrage du conteneur
CMD ["python", "mcp_server.py"]