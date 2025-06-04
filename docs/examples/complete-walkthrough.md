# MycoMind Complete Walkthrough

This comprehensive guide walks you through the complete MycoMind workflow using the included sample data. You'll transform unstructured text into a queryable, visual knowledge graph using AI and graph database technologies.

## Prerequisites

1. **Java 17 or 21** installed (for Neo4j graph database)
2. **OpenAI API key** (or compatible LLM service)  
3. **Python dependencies** installed: `pip install -r scripts/requirements.txt`

## Choose Your Graph Database Backend

MycoMind supports two graph database backends:

- **🔥 Neo4j** (Recommended) - Visual graph exploration with Cypher queries
- **🌐 Apache Jena Fuseki** - Standard SPARQL endpoint for semantic web applications

This guide covers **Neo4j** as the primary option, with Fuseki instructions at the end.

## Part 1: Quick Setup and Data Processing

### Step 1: Setup Configuration

```bash
# Copy the example configuration
cp examples/config_example.json config.json

# Set your API key
export OPENAI_API_KEY="your-openai-api-key-here"

# Edit config.json to update:
# 1. Replace "your_openai_api_key_here" with your actual API key (or use env var above)
# 2. Update "vault_path": "./demo_vault" to your desired output location
#    For this demo: "./demo_vault" (creates a demo_vault folder)
#    Or use your Obsidian vault: "/Users/yourname/Documents/MyObsidianVault"
```

### Step 2: Extract Entities with AI

Process the sample document that contains unstructured text about the MycoMind project:

```bash
# Run the ETL pipeline to extract entities from unstructured text
python scripts/main_etl.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --source examples/sample_data/mycomind_project.txt \
  --no-index
```

**What this does:**
- Uses AI to identify entities (HyphalTip, RegenerativePerson, Organization)
- Creates markdown files with YAML frontmatter in your configured output directory
- Extracts relationships between entities (collaborations, memberships, etc.)

**Expected Output:**
- `MycoMind.md` - A HyphalTip entity with project details
- `Shawn.md` - A RegenerativePerson entity with location and expertise
- Each file has rich YAML frontmatter with structured data

## Part 2: Neo4j Graph Database Setup

### Step 3: Install and Start Neo4j

```bash
# Download and install Neo4j
python scripts/setup_neo4j.py --download

# Start the Neo4j server
python scripts/setup_neo4j.py --start
```

**What this does:**
- Downloads Neo4j Community Edition 5.15.0
- Configures it for MycoMind (disables auth, sets memory limits)
- Starts the server on http://localhost:7474 (Bolt: bolt://localhost:7687)

### Step 4: Convert to Graph Format

```bash
# Convert the generated markdown files to Cypher statements
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output mycomind_knowledge_graph.cypher
```

**What this does:**
- Processes all markdown files with YAML frontmatter
- Resolves WikiLinks (`[[Shawn]]` → proper entity references)
- Generates Cypher CREATE statements for Neo4j

### Step 5: Load Data into Neo4j

```bash
# Load the Cypher statements into Neo4j
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p '' < mycomind_knowledge_graph.cypher
```

**If the above command completes but you don't see data**, try loading just the entities:

```bash
# Alternative: Import only the CREATE statements for entities
grep "^CREATE (" mycomind_knowledge_graph.cypher | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

**Verify data was loaded:**

```bash
# Check that entities were created
echo "MATCH (n) RETURN labels(n) as entity_types, count(n) as count ORDER BY count DESC;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

## Part 3: Query and Explore Your Knowledge Graph

### Neo4j Browser (Recommended)

Open http://localhost:7474 in your browser for visual graph exploration and querying.

### Command Line Interface

```bash
# Quick queries via command line
echo "MATCH (n) RETURN count(n) as total_nodes;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''

# Interactive shell
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

### Essential Cypher Queries

**Note:** Since the ETL pipeline uses AI, the exact entities extracted may vary between runs. These queries work with common entity types and relationships.

#### Overview Queries

```cypher
// Count all nodes by type
MATCH (n) 
RETURN labels(n) as entity_types, count(n) as count
ORDER BY count DESC;

// Count all relationships by type
MATCH ()-[r]->() 
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;

// Show all entities with their names
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

// Find people in specific locations
MATCH (person:RegenerativePerson) 
WHERE person.location CONTAINS "Portland" OR person.location CONTAINS "Seattle"
RETURN person.name as name, person.location as location, person.currentRole as role;
```

#### Find Projects

```cypher
// Find all projects/tips with their status
MATCH (tip:HyphalTip) 
RETURN tip.name as name, 
       tip.description as description, 
       tip.activityStatus as status
ORDER BY name;

// Find active projects
MATCH (tip:HyphalTip) 
WHERE tip.activityStatus = "alive" OR tip.activityStatus = "active"
RETURN tip.name as name, tip.description as description;
```

#### Find Organizations

```cypher
// Find all organizations
MATCH (org:Organization) 
RETURN org.name as name, org.description as description
ORDER BY name;

// Find organizations and their members
MATCH (org:Organization)-[:HASMEMBER]->(member)
RETURN org.name as organization, member.name as member_name
ORDER BY organization, member_name;
```

#### Relationship Analysis

```cypher
// Find all collaboration relationships
MATCH (entity1)-[:COLLABORATOR|:COLLABORATESWITH]-(entity2)
RETURN entity1.name as collaborator1, entity2.name as collaborator2
ORDER BY collaborator1, collaborator2;

// Find all relationships in the graph
MATCH (n1)-[r]-(n2) 
RETURN n1.name as entity1, type(r) as relationship, n2.name as entity2
ORDER BY entity1, relationship, entity2;

// Find entities with the most connections
MATCH (n)-[r]-() 
RETURN n.name as entity, labels(n)[0] as type, count(r) as connections
ORDER BY connections DESC
LIMIT 10;
```

#### Advanced Queries

```cypher
// Find paths between entities
MATCH path = (start)-[*1..3]-(end)
WHERE start.name CONTAINS "MycoMind" AND end.name CONTAINS "Transition"
RETURN path
LIMIT 5;

// Find entities that are both members and collaborators
MATCH (person)-[:MEMBEROF]->(org), (person)-[:COLLABORATESWITH]->(project)
RETURN person.name as person, org.name as organization, project.name as project;

// Geographic analysis
MATCH (n) 
WHERE exists(n.location)
RETURN n.location as location, count(n) as entity_count, collect(n.name) as entities
ORDER BY entity_count DESC;
```

## Part 4: Database Management

### Neo4j Management Commands

```bash
# Check server status
python scripts/setup_neo4j.py --status

# Stop the server
python scripts/setup_neo4j.py --stop

# Restart the server
python scripts/setup_neo4j.py --restart

# View recent logs
python scripts/setup_neo4j.py --logs
```

### Reset Neo4j Database

If you need to completely reset your Neo4j database:

#### Method 1: Database Reset via Cypher (Recommended)

```bash
# Connect to Neo4j shell
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''

# Then run these commands in order:
# 1. Drop all indexes and constraints first
CALL db.indexes() YIELD name CALL db.index.drop(name);
CALL db.constraints() YIELD name CALL db.constraint.drop(name);

# 2. Delete all data
MATCH (n) DETACH DELETE n;

# 3. Verify everything is clean
MATCH (n) RETURN count(n) as remaining_nodes;
```

#### Method 2: Complete Database Directory Removal

```bash
# Stop Neo4j first
python scripts/setup_neo4j.py --stop

# Remove the entire data directory
rm -rf scripts/neo4j/neo4j-community-5.15.0/data/

# Restart Neo4j (creates fresh database)
python scripts/setup_neo4j.py --start
```

### Graph Analytics

```cypher
// Analyze graph structure
CALL db.stats.retrieve('GRAPH') YIELD data RETURN data;

// Find shortest paths between entities
MATCH (start:RegenerativePerson {name: "Shawn"}), 
      (end:HyphalTip)
MATCH path = shortestPath((start)-[*..5]-(end))
RETURN path;

// Degree centrality (most connected entities)
MATCH (n)-[r]-()
RETURN n.name as entity, labels(n)[0] as type, count(r) as degree
ORDER BY degree DESC
LIMIT 10;
```

## Part 5: Expected Results

After completing this workflow, you should have:

### 📊 Data Loaded
- **3+ entities** (exact number depends on AI extraction)
- **HyphalTip projects** like "MycoMind: Personal Knowledge Management System"
- **RegenerativePerson entities** like "Shawn" with location and role information
- **Organization entities** like "Transition Towns"
- **5+ relationships** connecting these entities

### 🔗 Relationships Discovered
- **Collaboration** relationships between people and projects
- **Membership** relationships between people and organizations
- **Geographic connections** based on location data
- **Project ownership** and contribution patterns

### 🌐 Visualization
- **Interactive graph** in Neo4j Browser showing node-link networks
- **Expandable nodes** with detailed properties
- **Relationship paths** showing how entities connect
- **Query results** in both table and graph formats

## Part 6: Process Your Own Data

### Standard Mode (New Entity Notes)

```bash
# Process your documents
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/personal_knowledge.json \
  --source /path/to/your/documents/
```

### File-as-Entity Mode (Enhance Original Files)

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

## Alternative: Apache Jena Fuseki + SPARQL

If you prefer semantic web standards and SPARQL querying:

### Setup Fuseki

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
4. See [troubleshooting guide](../user-guides/troubleshooting.md) for specific errors

## Next Steps

1. **Scale up**: Process your own document collections
2. **Customize**: Create domain-specific schemas
3. **Integrate**: Build applications that query your knowledge graph
4. **Explore**: Use graph algorithms for network analysis and knowledge discovery

**🎉 Congratulations!** You've successfully built an AI-powered knowledge graph system that transforms unstructured text into queryable, visual knowledge networks!