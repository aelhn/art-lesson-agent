# art-lesson-agent

![Tests](https://github.com/aelhn/art-lesson-agent/actions/workflows/tests.yml/badge.svg)

Agent IA qui rédige des leçons d'initiation à l'art à partir de sources Wikipédia.

On lui donne le nom d'une œuvre, il cherche et lit les articles utiles, rédige une courte leçon avec un quiz, puis un second agent vérifie chaque fait avant validation. La leçon est produite en JSON, prête à être affichée par une application éducative.

## Fonctionnement

```
         main.py (orchestration)
            │
            ├──> Agent rédacteur ──┐
            │      (writer.py)     │      ┌─────────────────────┐
            │                      ├────> │ Serveur MCP         │ ──> API Wikipédia
            │                      │      │ (mcp_server.py)     │
            ├──> Agent relecteur ──┘      │ - search_wikipedia  │
            │      (reviewer.py)          │ - get_article       │
            │                             └─────────────────────┘
            └──> output/<titre>.json
```

1. Le **rédacteur** cherche l'œuvre, lit l'article et rédige la leçon : 3 sections courtes, chacune avec sa source, et 3 questions de quiz.
2. Le **relecteur** relit chaque article cité et vérifie que les faits (dates, noms, chiffres, lieux) y figurent bien.
3. S'il relève des problèmes, le rédacteur corrige, puis le relecteur revérifie (2 corrections au plus).

Les deux agents passent par le même serveur MCP, mais avec des droits différents : le relecteur peut seulement lire, pas chercher.

## Structure du projet

| Fichier | Rôle |
|---|---|
| `mcp_server.py` | Serveur MCP (FastMCP) qui expose les outils Wikipédia |
| `models.py` | Format des données (pydantic) : `Lesson`, `Section`, `QuizQuestion`, `Review` |
| `writer.py` | Agent rédacteur |
| `reviewer.py` | Agent relecteur |
| `main.py` | Point d'entrée et boucle rédaction / relecture |
| `docker_check.py` | client MCP de test pour l’image Docker |
| `tests/` | Tests pytest, sans réseau ni appel à Claude |
| `examples/` | Exemple de leçon générée |
| `Dockerfile` | image du serveur MCP |

## Installation

Python 3.10 ou plus récent.

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

## Authentification

Les agents utilisent le [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview). Le dépôt ne contient aucune clé. Pour lancer l'agent, il faut l'un des accès suivants :

- une session [Claude Code](https://code.claude.com) connectée sur la machine (c'est ce que j'utilise pour ce projet personnel) ;
- une clé API Anthropic dans la variable d'environnement `ANTHROPIC_API_KEY` ;
- Amazon Bedrock, avec `CLAUDE_CODE_USE_BEDROCK=1` et des identifiants AWS.

Le serveur MCP et les tests fonctionnent sans aucun accès à Claude.

## Utilisation

```bash
python main.py "Le Radeau de la Méduse"
```

Exemple de sortie :

```
Rédaction de la leçon: Le Radeau de la Méduse
    outil : mcp__wikipedia__search_wikipedia {'query': 'Le Radeau de la Méduse'}
    outil : mcp__wikipedia__get_article {'title': 'Le Radeau de la Méduse'}
    relecteur : mcp__wikipedia__get_article {'title': 'Le Radeau de la Méduse'}
Leçon validée par le relecteur
Leçon enregistrée dans output\Le Radeau de la Méduse.json
```

La leçon complète est dans [`examples/le_radeau_de_la_meduse.json`](examples/le_radeau_de_la_meduse.json).

## Tests

```bash
pytest
```

Les appels à Wikipédia et aux agents sont remplacés par des faux : les tests sont rapides, gratuits et donnent toujours le même résultat. Ils vérifient :

- les règles de validation des leçons (une leçon vide ou sans artiste est refusée) ;
- les outils MCP (construction des liens, texte coupé, page introuvable) ;
- la boucle de relecture (arrêt si la leçon est validée, renvoi des problèmes au rédacteur, nombre de corrections limité).

## Serveur MCP avec Docker

Le serveur MCP peut être utilisé seul, par n'importe quel client MCP, sans installer Python :

```bash
docker build -t art-lesson-mcp .
python docker_check.py
```

Pour le brancher sur un client (Claude Desktop, Claude Code ou un autre agent), on remplace la commande de lancement par `docker run -i --rm art-lesson-mcp`.

Seul le serveur est conteneurisé. Les agents s'appuient sur une session Claude Code locale, qui ne se transporte pas dans un conteneur. Pour les conteneuriser, il faudrait une clé API ou Amazon Bedrock, que le SDK prend en charge avec une simple variable d'environnement. Je ne l'ai pas fait ici, pour garder un projet personnel sans frais.

## Choix techniques

- **Un enchaînement fixe plutôt qu'un agent autonome.** L'orchestration est écrite en Python : chaque étape est visible et testable. Pour du contenu pédagogique, la fiabilité compte plus que l'autonomie. Le SDK propose aussi des sous-agents, qu'un agent principal pilote lui-même, mais le résultat serait moins prévisible.
- **Un serveur MCP plutôt que des appels directs.** Les outils sont séparés des agents : le même serveur peut être branché sur Claude Desktop, Claude Code ou un autre client MCP, et l'agent ne peut rien faire d'autre que ce qu'il expose.
- **Des sources obligatoires.** Le rédacteur n'a pas le droit d'utiliser sa mémoire, seulement les articles lus avec ses outils, et chaque section garde le lien de sa source. Le relecteur contrôle ensuite les faits.
- **Des garde-fous à chaque niveau :**
  - sortie structurée (`output_format`) : les agents doivent remplir un schéma JSON généré à partir des modèles pydantic, qui revérifient ensuite le résultat ;
  - droits minimaux : aucun outil intégré de Claude Code (`tools=[]`), seuls les outils MCP utiles sont autorisés (`allowed_tools`), les réglages et connecteurs de la machine sont ignorés (`setting_sources=[]`, `strict_mcp_config=True`) ;
  - nombre de tours limité (`max_turns`) et nombre de corrections borné, pour éviter qu'un agent tourne en rond.

## Limites

- Les sources se limitent à Wikipédia en français.
- Le texte d'un article est coupé à 8 000 caractères : un détail situé plus loin dans l'article peut échapper aux agents.
- Le relecteur est lui-même un LLM : il réduit fortement les erreurs mais ne remplace pas une relecture humaine avant publication.

## Pistes d'évolution

- **Base de connaissance** : découper les articles en passages et les indexer avec des embeddings (PostgreSQL + pgvector), pour ne donner aux agents que les passages utiles au lieu d'un texte coupé.
- **D'autres sources** : API de musées (Joconde, Paris Musées), images de Wikimedia Commons.
- **Hébergement** : passer par Amazon Bedrock, ce qui permet de conteneuriser l'agent sans dépendre d'une session locale, et exposer le serveur MCP en HTTP pour plusieurs clients.

## Licence des contenus

Les textes des leçons sont rédigés à partir d'articles de Wikipédia, publiés sous licence [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.fr). Chaque section indique l'article dont elle s'inspire.
