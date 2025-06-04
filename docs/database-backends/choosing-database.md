# Choosing a Graph Database Backend

MycoMind supports two graph database backends for storing and querying your knowledge graphs. Each has distinct advantages depending on your use case.

## Neo4j (Recommended)

**Best for**: Interactive exploration, visual graph analysis, property graphs

### Advantages
- **Visual graph browser** with interactive node-link exploration
- **Cypher query language** - intuitive, SQL-like syntax
- **Property graph model** - rich node and relationship properties
- **Built-in graph algorithms** for network analysis
- **Excellent performance** for traversal queries
- **Strong community** and extensive documentation

### Use Cases
- Personal knowledge management with visual exploration
- Research projects requiring network analysis
- Business intelligence with relationship mapping
- Social network analysis
- Recommendation systems

### Getting Started
```bash
# Install and start Neo4j
python scripts/setup_neo4j.py --download
python scripts/setup_neo4j.py --start

# Convert data to Cypher format
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/your_schema.json \
  --input vault/extracted_knowledge \
  --output knowledge_graph.cypher
```

Access Neo4j Browser at http://localhost:7474

## Apache Jena Fuseki

**Best for**: Semantic web applications, RDF compliance, federated queries

### Advantages
- **SPARQL endpoint** - W3C standard query language
- **RDF/JSON-LD storage** - semantic web compatible
- **Federated queries** - combine multiple knowledge sources
- **Ontology reasoning** - infer new knowledge from existing data
- **Standards compliance** - integrates with semantic web ecosystem
- **Lightweight** - minimal resource requirements

### Use Cases
- Academic research requiring semantic web standards
- Integration with existing RDF datasets
- Ontology-driven knowledge systems
- Federated knowledge bases
- Compliance with semantic web standards

### Getting Started
```bash
# Install and start Fuseki
python scripts/setup_fuseki.py --download
python scripts/setup_fuseki.py --start --port 3030

# Convert data to JSON-LD format
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/your_schema.json \
  --input vault/extracted_knowledge \
  --output knowledge_graph.jsonld

# Load data into Fuseki
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load knowledge_graph.jsonld
```

Access Fuseki interface at http://localhost:3030

## Comparison

| Feature | Neo4j | Fuseki |
|---------|-------|---------|
| **Query Language** | Cypher | SPARQL |
| **Data Model** | Property Graph | RDF Triples |
| **Visualization** | Built-in Browser | Basic Interface |
| **Performance** | Excellent for traversals | Good for queries |
| **Standards** | Property Graph | W3C Semantic Web |
| **Learning Curve** | Moderate | Steep |
| **Resource Usage** | Higher | Lower |
| **Ecosystem** | Large | Semantic Web |

## Migration Between Backends

You can switch between backends by re-converting your extracted YAML frontmatter:

### From Neo4j to Fuseki
```bash
# Convert existing Cypher data to JSON-LD
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/your_schema.json \
  --input vault/extracted_knowledge \
  --output knowledge_graph.jsonld

# Load into Fuseki
python scripts/graph_db_client.py --load knowledge_graph.jsonld
```

### From Fuseki to Neo4j
```bash
# Convert existing JSON-LD data to Cypher
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/your_schema.json \
  --input vault/extracted_knowledge \
  --output knowledge_graph.cypher

# Load into Neo4j
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p '' < knowledge_graph.cypher
```

## Recommendations

### Choose Neo4j if you:
- Want visual graph exploration
- Prefer intuitive query syntax
- Need interactive data discovery
- Plan to use graph algorithms
- Are building user-facing applications

### Choose Fuseki if you:
- Need semantic web standards compliance
- Want to integrate with existing RDF data
- Require federated queries across datasets
- Are building academic research systems
- Prefer lightweight deployment

Both backends can store the same knowledge extracted by MycoMind - the choice depends on your querying and integration requirements.