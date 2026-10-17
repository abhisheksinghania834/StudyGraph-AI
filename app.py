import os
from flask import Flask, jsonify, render_template, request
from falkordb import FalkorDB

app = Flask(__name__)
GRAPH_NAME = os.getenv("FALKORDB_GRAPH", "studygraph")

def graph():
    return FalkorDB(host=os.getenv("FALKORDB_HOST", "localhost"),
                    port=int(os.getenv("FALKORDB_PORT", "6379")),
                    password=os.getenv("FALKORDB_PASSWORD") or None).select_graph(GRAPH_NAME)

def query(cypher, params=None):
    return graph().query(cypher, params or {}).result_set

def seed():
    g = graph()
    g.query("""
    MERGE (:Subject {name:'Physics'})
    MERGE (:Subject {name:'Mathematics'})
    MERGE (:Subject {name:'Computer Science'})
    MERGE (:Concept {name:'Thermodynamics', difficulty:'Intermediate', description:'Heat, work, temperature, and energy transformations.'})
    MERGE (:Concept {name:'First Law of Thermodynamics', difficulty:'Intermediate', description:'Energy is conserved in a thermodynamic process.'})
    MERGE (:Concept {name:'Basic Algebra', difficulty:'Beginner', description:'Variables, equations, and algebraic manipulation.'})
    MERGE (:Concept {name:'Functions', difficulty:'Beginner', description:'Inputs, outputs, and mappings between sets.'})
    MERGE (:Concept {name:'Cypher Basics', difficulty:'Beginner', description:'Querying graph patterns with Cypher.'})
    MERGE (:Concept {name:'Graph Databases', difficulty:'Intermediate', description:'Representing entities and relationships as a property graph.'})
    MERGE (:Resource {title:'Thermodynamics reference', kind:'Reference', url:'https://en.wikipedia.org/wiki/Thermodynamics'})
    MERGE (:Resource {title:'Algebra reference', kind:'Reference', url:'https://en.wikipedia.org/wiki/Algebra'})
    MERGE (:Resource {title:'FalkorDB documentation', kind:'Documentation', url:'https://docs.falkordb.com/'})
    """)
    g.query("""
    MATCH (s:Subject {name:'Physics'}),(c:Concept {name:'Thermodynamics'}) MERGE (s)-[:COVERS]->(c);
    MATCH (c:Concept {name:'Thermodynamics'}),(p:Concept {name:'First Law of Thermodynamics'}) MERGE (c)-[:INCLUDES]->(p);
    MATCH (s:Subject {name:'Mathematics'}),(c:Concept {name:'Basic Algebra'}) MERGE (s)-[:COVERS]->(c);
    MATCH (s:Subject {name:'Mathematics'}),(c:Concept {name:'Functions'}) MERGE (s)-[:COVERS]->(c);
    MATCH (a:Concept {name:'Basic Algebra'}),(b:Concept {name:'Functions'}) MERGE (a)-[:PREREQUISITE_FOR]->(b);
    MATCH (s:Subject {name:'Computer Science'}),(c:Concept {name:'Graph Databases'}) MERGE (s)-[:COVERS]->(c);
    MATCH (a:Concept {name:'Cypher Basics'}),(b:Concept {name:'Graph Databases'}) MERGE (a)-[:PREREQUISITE_FOR]->(b);
    MATCH (c:Concept {name:'Thermodynamics'}),(r:Resource {title:'Thermodynamics reference'}) MERGE (c)-[:HAS_RESOURCE]->(r);
    MATCH (c:Concept {name:'Basic Algebra'}),(r:Resource {title:'Algebra reference'}) MERGE (c)-[:HAS_RESOURCE]->(r);
    MATCH (c:Concept {name:'Graph Databases'}),(r:Resource {title:'FalkorDB documentation'}) MERGE (c)-[:HAS_RESOURCE]->(r);
    """)
@app.get("/")
def home():
    return render_template("index.html")
@app.get("/api/health")
def health():
    try:
        return jsonify(ok=True, graph=GRAPH_NAME, nodes=query("MATCH (n) RETURN count(n)")[0][0])
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 503
@app.post("/api/seed")
def seed_api():
    try:
        seed()
        return jsonify(ok=True, message="Sample study graph loaded.")
    except Exception as e:
        return jsonify(error=str(e)), 503
@app.get("/api/stats")
def stats():
    try:
        return jsonify(nodes=query("MATCH (n) RETURN count(n)")[0][0],
                       relationships=query("MATCH ()-[r]->() RETURN count(r)")[0][0],
                       subjects=query("MATCH (s:Subject) RETURN count(s)")[0][0],
                       concepts=query("MATCH (c:Concept) RETURN count(c)")[0][0])
    except Exception as e:
        return jsonify(error=str(e)), 503
@app.get("/api/search")
def search():
    term = request.args.get("q", "").strip()
    if not term:
        return jsonify(results=[])
    try:
        data = query("""
        MATCH (c:Concept)
        WHERE toLower(c.name) CONTAINS toLower($term) OR toLower(coalesce(c.description,'')) CONTAINS toLower($term)
        OPTIONAL MATCH (s:Subject)-[:COVERS]->(c)
        OPTIONAL MATCH (c)-[:HAS_RESOURCE]->(r:Resource)
        RETURN DISTINCT c.name,c.difficulty,c.description,collect(DISTINCT s.name),collect(DISTINCT r{.title,.kind,.url})
        ORDER BY c.name LIMIT 20
        """, {"term":term})
        return jsonify(results=[{"name":r[0],"difficulty":r[1],"description":r[2],"subjects":r[3] or [],
                                 "resources":[x for x in (r[4] or []) if x and x.get("title")]} for r in data])
    except Exception as e:
        return jsonify(error=str(e)), 503
@app.get("/api/path")
def path():
    start, end = request.args.get("from","").strip(), request.args.get("to","").strip()
    if not start or not end:
        return jsonify(error="Provide both from and to concepts."), 400
    try:
        result = query("""
        MATCH (a:Concept {name:$start}),(b:Concept {name:$end})
        MATCH p=shortestPath((a)-[:PREREQUISITE_FOR*0..8]-(b))
        RETURN [n IN nodes(p) | n.name] AS path LIMIT 1
        """, {"start":start,"end":end})
        return jsonify(found=bool(result), path=result[0][0] if result else [],
                       message="No prerequisite path found." if not result else "Path found.")
    except Exception as e:
        return jsonify(error=str(e)), 503
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","5000")), debug=False)
