# Complete MycoMind Walkthrough

This comprehensive guide walks you through the complete MycoMind workflow from installation to advanced querying using the included sample data.

## Prerequisites

1. **Java 17 or 21** installed (for Neo4j graph database)
2. **OpenAI API key** (or compatible LLM service)
3. **Python dependencies** installed: `pip install -r scripts/requirements.txt`

## Part 1: Quick Setup

### 1. Configuration Setup

```bash
# Copy the example configuration
cp examples/config_example.json config.json

# Set your API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Edit config.json to update vault_path to your desired output location
# For this demo: "./demo_vault"
```

### 2. Process Sample Data

Extract entities from the sample document:

```bash
python scripts/main_etl.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --source examples/sample_data/mycomind_project.txt \
  --no-index
```

**Expected Output**: Structured markdown files with YAML frontmatter:
- `MycoMind.md` - A HyphalTip entity with project details
- `Shawn.md` - A RegenerativePerson entity with location and expertise
- Each file has rich YAML frontmatter with extracted properties

## Part 2: Graph Database Setup (Neo4j)

### 3. Install and Start Neo4j

```bash
# Download and install Neo4j
python scripts/setup_neo4j.py --download

# Start the Neo4j server
python scripts/setup_neo4j.py --start
```

Access the Neo4j Browser at http://localhost:7474

### 4. Convert to Graph Format

```bash
# Convert markdown files to Cypher statements
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output mycomind_knowledge_graph.cypher
```

### 5. Load Data into Neo4j

```bash
# Load the Cypher statements into Neo4j
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p '' < mycomind_knowledge_graph.cypher
```

**Verify data loaded**:
```bash
echo "MATCH (n) RETURN labels(n) as types, count(n) as count ORDER BY count DESC;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

## Part 3: Querying Your Knowledge Graph

### Essential Queries

#### Overview Queries
```cypher
// Count all nodes by type
MATCH (n) 
RETURN labels(n) as entity_types, count(n) as count
ORDER BY count DESC;

// Show all entities with names
MATCH (n) 
WHERE exists(n.name)
RETURN labels(n)[0] as type, n.name as name, n.description as description
ORDER BY type, name;
```

#### Find People
```cypher
// Find all people with their details
MATCH (person:RegenerativePerson) 
RETURN person.name as name, 
       person.location as location, 
       person.currentRole as role,
       person.bio as bio
ORDER BY name;
```

#### Find Projects
```cypher
// Find all projects/tips
MATCH (tip:HyphalTip) 
RETURN tip.name as name, 
       tip.description as description, 
       tip.activityStatus as status
ORDER BY name;
```

#### Find Relationships
```cypher
// Find all collaborations
MATCH (entity1)-[:COLLABORATOR|:COLLABORATESWITH]-(entity2)
RETURN entity1.name as collaborator1, entity2.name as collaborator2
ORDER BY collaborator1, collaborator2;

// Find entities with most connections
MATCH (n)-[r]-() 
RETURN n.name as entity, labels(n)[0] as type, count(r) as connections
ORDER BY connections DESC
LIMIT 10;
```

### Advanced Queries

```cypher
// Find shortest paths between entities
MATCH path = (start)-[*1..3]-(end)
WHERE start.name CONTAINS "MycoMind" AND end.name CONTAINS "Transition"
RETURN path
LIMIT 5;

// Geographic analysis
MATCH (n) 
WHERE exists(n.location)
RETURN n.location as location, count(n) as entity_count, collect(n.name) as entities
ORDER BY entity_count DESC;
```

## Part 4: Advanced Features

### Processing Your Own Files

#### Standard Mode (New Entity Notes)
```bash
# Process your documents
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/personal_knowledge.json \
  --source /path/to/your/documents/
```

#### File-as-Entity Mode (Enhance Original Files)
```bash
# Enhance existing files with YAML frontmatter
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/hyphaltips_schema.json \
  --source /path/to/files \
  --file-as-entity HyphalTip
```

### Custom Schema Creation

```bash
# Generate example schema
python scripts/schema_parser.py create-example my_custom_schema.json

# Validate your schema
python scripts/schema_parser.py validate my_custom_schema.json
```

### Database Management

```bash
# Check Neo4j status
python scripts/setup_neo4j.py --status

# Stop Neo4j
python scripts/setup_neo4j.py --stop

# Reset database (warning: deletes all data)
python scripts/setup_neo4j.py --stop && \
rm -rf scripts/neo4j/neo4j-community-5.15.0/data/ && \
python scripts/setup_neo4j.py --start
```

## Part 5: Alternative Database Backend (Fuseki/SPARQL)

### Setup Apache Jena Fuseki

```bash
# Download and install Fuseki
python scripts/setup_fuseki.py --download

# Start Fuseki server
python scripts/setup_fuseki.py --start --port 3030
```

### Convert to JSON-LD

```bash
# Convert to JSON-LD format instead of Cypher
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output mycomind_knowledge_graph.jsonld
```

### Load and Query with SPARQL

```bash
# Create dataset and load data
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld

# Interactive SPARQL queries
python scripts/graph_db_client.py --interactive
```

Access the Fuseki web interface at http://localhost:3030

## Troubleshooting

### Common Issues

#### No Entities Extracted
- Verify OpenAI API key is set correctly
- Check schema file exists and is valid
- Ensure source document contains recognizable entities

#### Neo4j Connection Issues
- Verify Java 17+ is installed: `java -version`
- Check if port 7474 is available: `lsof -i :7474`
- Review Neo4j logs: `python scripts/setup_neo4j.py --logs`

#### Empty Query Results
- Verify data was loaded: `MATCH (n) RETURN count(n);`
- Check node labels: `CALL db.labels();`
- Use Neo4j Browser for visual exploration

### Getting Help

1. Check logs in `logs/mycomind.log`
2. Use `--verbose` flag for detailed output
3. Test with `--dry-run` to validate configuration
4. See troubleshooting guide for specific error solutions

## Next Steps

1. **Scale up**: Process your own document collections
2. **Customize**: Create domain-specific schemas
3. **Integrate**: Build applications that query your knowledge graph
4. **Explore**: Use graph algorithms for network analysis and knowledge discovery

**🎉 Congratulations!** You've successfully built an AI-powered knowledge graph system that transforms unstructured text into queryable, visual knowledge networks!