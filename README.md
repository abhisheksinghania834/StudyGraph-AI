# StudyGraph AI

StudyGraph AI is a graph-powered study exploration prototype built with Flask and [FalkorDB](https://www.falkordb.com/). Students can search concepts, retrieve linked learning resources, inspect graph statistics, and find paths between concepts through prerequisite relationships.

**Current scope:** graph-backed search and path finding. It is not yet an LLM-powered agent, and it has not yet been deployed to a public live URL. The bundled concepts and links are illustrative sample data.

## Graph model

- `Subject`: a subject such as Physics or Mathematics.
- `Concept`: a topic, with name, difficulty, and description.
- `Resource`: a public reference linked to a concept.
- `COVERS`: Subject → Concept.
- `PREREQUISITE_FOR`: Concept → Concept.
- `INCLUDES`: Concept → Concept.
- `HAS_RESOURCE`: Concept → Resource.

## Run locally

Requires Docker Engine/Desktop and Docker Compose.

```bash
docker compose up --build
```

Open http://localhost:5000 and click **Load sample graph**. Search for Thermodynamics, Algebra, or Graph Databases. Try the path finder with Basic Algebra and Functions.

Stop with `docker compose down`. The named volume retains data. `docker compose down -v` removes that volume and its stored graph data.

## API

- `GET /api/health` — check database connectivity.
- `POST /api/seed` — load repeatable sample data.
- `GET /api/stats` — count nodes and relationships.
- `GET /api/search?q=algebra` — search concepts and linked resources.
- `GET /api/path?from=Basic%20Algebra&to=Functions` — find a path.

See [queries/schema.cypher](queries/schema.cypher) for example Cypher queries.

## Security and project status

Do not commit production credentials. The local prototype has no authentication or rate limiting and should not be exposed publicly without hardening. Resource URLs are illustrative references, not a vetted curriculum. Run and test the app before relying on it in a presentation.

AI assistance was used to draft portions of the code; the project owner should review and understand it before submission.

## References

- [FalkorDB documentation](https://docs.falkordb.com/)
- [FalkorDB Cypher reference](https://docs.falkordb.com/cypher/)
