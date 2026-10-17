// StudyGraph AI model: Subject, Concept, Resource
MATCH (s:Subject)-[:COVERS]->(c:Concept)
RETURN s.name AS subject, c.name AS concept, c.difficulty AS level
ORDER BY subject, concept;

// Find resources for a concept
MATCH (c:Concept {name:'Thermodynamics'})-[:HAS_RESOURCE]->(r:Resource)
RETURN c.name, r.title, r.kind, r.url;

// Prerequisite edges
MATCH (a:Concept)-[:PREREQUISITE_FOR]->(b:Concept)
RETURN a.name AS prerequisite, b.name AS next_concept;

// Count graph nodes and edges
MATCH (n) RETURN labels(n) AS labels, count(*) AS total;
MATCH ()-[r]->() RETURN type(r) AS relationship, count(*) AS total;
