# Neo4j Database Setup and Usage Guide

This guide explains how to set up and use Neo4j with your MycoMind knowledge management system.

## Overview

The complete MycoMind workflow with Neo4j includes:

1. **Extract**: Process documents and create YAML frontmatter in Markdown files
2. **Convert**: Transform YAML frontmatter to Neo4j Cypher statements using schemas
3. **Load**: Import Cypher statements into Neo4j for advanced querying and visualization
4. **Query**: Use Cypher to explore and analyze your knowledge graph in the Neo4j Browser

## Prerequisites

- Python 3.8+
- **Java 17 or Java 21** (required for Neo4j 5.x)
- All MycoMind dependencies installed

> **Important**: Neo4j 5.x specifically requires Java 17 or Java 21. It will not work with older Java versions like Java 8 or Java 11.
> 
> To check your Java version:
> ```bash
> java -version
> ```
> 
> If you need to install or update Java, visit [Oracle Java Downloads](https://www.oracle.com/java/technologies/downloads/) or use your system's package manager.

## Quick Start

### Run the Complete Workflow

```bash
cd scripts

# 1. Download and install Neo4j
python setup_neo4j.py --download
python setup_neo4j.py --start

# 2. Convert YAML to Cypher (automatically uses config.json settings)
python yaml_to_neo4j_converter.py --browser

# 3. Load data and query in Neo4j Browser
# Open http://localhost:7474 in your browser
# Run: :source knowledge_graph.cypher
```

## Detailed Setup

### Installing Neo4j

The `setup_neo4j.py` script automates the Neo4j installation:

```bash
# Download Neo4j (about 300MB)
python setup_neo4j.py --download

# This will:
# - Download Neo4j Community Edition 5.15.0
# - Extract it to the neo4j/ directory
# - Create a MycoMind-specific configuration
```

### Starting the Server

```bash
# Start with default settings (2GB memory)
python setup_neo4j.py --start

# Start with custom settings
python setup_neo4j.py --start --memory 4g

# Check if running
python setup_neo4j.py --status
```

### Server Management

```bash
# Stop the server
python setup_neo4j.py --stop

# Restart the server
python setup_neo4j.py --restart

# View recent logs
python setup_neo4j.py --logs
```

## Data Conversion

### YAML to Cypher Conversion

The `yaml_to_neo4j_converter.py` script converts your Markdown files with YAML frontmatter to Neo4j Cypher statements:

```bash
# Simplest usage - automatically uses settings from config.json
python yaml_to_neo4j_converter.py --browser

# Basic usage with explicit parameters
python yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output knowledge_graph.cypher

# With custom base IRI
python yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output knowledge_graph.cypher \
  --base-iri "https://mycomind.org/kg/"

# Convert single file
python yaml_to_neo4j_converter.py \
  --file demo_vault/extracted_knowledge/hyphaltip/mycomind_personal_knowledge_management_system.md \
  --output person.cypher

# With custom configuration file
python yaml_to_neo4j_converter.py \
  --config custom_config.json \
  --browser
```

### Automatic Configuration

The script automatically:

1. **Reads configuration** from `config.json` to find your Obsidian vault path
2. **Uses default schema** (`schemas/hyphaltips_mycomind_schema.json`) if not specified
3. **Finds Markdown files** in the configured vault path and notes folder
4. **Generates Cypher statements** for entities and relationships
5. **Automatically locates** the Neo4j import directory when using `--browser`

### What Gets Converted

The converter processes:
- **Entity types** from YAML `type` field
- **Properties** based on schema definitions
- **Relationships** with WikiLink resolution (`[[Entity Name]]` → IRI references)
- **Metadata** (extraction confidence, source files, timestamps)
- **Placeholder nodes** for referenced entities that don't exist yet

## Neo4j Database Operations

### Loading Data

Once Neo4j is running, you can load the generated Cypher statements:

1. Open Neo4j Browser at http://localhost:7474
2. Connect with default credentials (neo4j/neo4j) or without authentication if disabled
3. Load the Cypher file using the `:source` command:

```cypher
:source knowledge_graph.cypher
```

Alternatively, you can copy and paste the Cypher statements directly into the Neo4j Browser.

### Querying with Cypher

#### Basic Entity Listing

```cypher
// List all entities with their names
MATCH (n)
WHERE n.name IS NOT NULL
RETURN n.name, labels(n) AS type
ORDER BY n.name
```

#### Relationship Exploration

```cypher
// Find all relationships between entities
MATCH (a)-[r]->(b)
WHERE a.name IS NOT NULL AND b.name IS NOT NULL
RETURN a.name, type(r) AS relationship, b.name
```

#### Network Analysis

```cypher
// Find most connected entities
MATCH (n)-[r]-()
WHERE n.name IS NOT NULL
RETURN n.name, count(r) AS connections
ORDER BY connections DESC
LIMIT 10
```

#### Search and Filter

```cypher
// Search entities by name or description
MATCH (n)
WHERE n.name IS NOT NULL
  AND (n.name CONTAINS "search_term" OR n.description CONTAINS "search_term")
RETURN n.name, n.description
```

## Neo4j Browser Features

The Neo4j Browser provides several powerful features:

### Visualization

Neo4j Browser automatically visualizes query results as a graph, allowing you to:
- See entity relationships visually
- Expand nodes to explore connections
- Customize the appearance of nodes and relationships
- Save visualizations as images

### Query Management

- Save favorite queries
- View query history
- Share queries with others
- Export results in various formats (CSV, JSON)

### Data Exploration

- View node and relationship properties
- Execute built-in graph algorithms
- Use the visual query builder
- Access database metadata

## Integration with Your Workflow

### Complete Pipeline

```bash
# 1. Extract entities from documents
python main_etl.py --schema ../schemas/example_schemas/personal_knowledge.json \
                   --source document.txt

# 2. Convert YAML frontmatter to Cypher
python yaml_to_neo4j_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --input /path/to/generated/markdown \
  --output knowledge_graph.cypher

# 3. Start Neo4j (if not already running)
python setup_neo4j.py --start

# 4. Load data into Neo4j
# Open Neo4j Browser and run: :source knowledge_graph.cypher
```

### Automated Updates

You can create scripts to automatically update your knowledge graph:

```bash
#!/bin/bash
# update_knowledge_graph.sh

# Convert latest markdown files
python yaml_to_neo4j_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --input /path/to/obsidian/vault \
  --output latest_kg.cypher

# Clear existing data and reload
# (Requires Neo4j Browser to be open)
echo "// Clear existing data and load new data" > reload_script.cypher
echo "MATCH (n) DETACH DELETE n;" >> reload_script.cypher
cat latest_kg.cypher >> reload_script.cypher

# Copy to Neo4j import directory
cp reload_script.cypher ~/neo4j/import/

echo "Knowledge graph update script prepared!"
echo "Open Neo4j Browser and run: :source reload_script.cypher"
```

## Advanced Features

### Entity Linking

Neo4j enables sophisticated entity linking:

```cypher
// Find potential duplicate entities
MATCH (a), (b)
WHERE a.name IS NOT NULL AND b.name IS NOT NULL
  AND a <> b
  AND toLower(a.name) = toLower(b.name)
RETURN a.name, labels(a) AS type_a, b.name, labels(b) AS type_b
```

### Graph Analytics

Neo4j provides built-in graph algorithms for advanced analysis:

```cypher
// Calculate degree centrality
MATCH (n)-[r]-()
WHERE n.name IS NOT NULL
RETURN n.name, count(r) AS degree
ORDER BY degree DESC
LIMIT 10

// Find shortest path between entities
MATCH path = shortestPath((a)-[*]-(b))
WHERE a.name = "Entity A" AND b.name = "Entity B"
RETURN path
```

### Data Quality Checks

```cypher
// Find entities without descriptions
MATCH (n)
WHERE n.name IS NOT NULL
  AND n.description IS NULL
RETURN n.name, labels(n) AS type

// Find orphaned entities (no relationships)
MATCH (n)
WHERE NOT (n)-[]-()
RETURN n.name, labels(n) AS type
```

## Comparing Neo4j and Fuseki

MycoMind supports both Neo4j and Apache Jena Fuseki as graph database options:

| Feature | Neo4j | Fuseki |
|---------|-------|--------|
| **Query Language** | Cypher | SPARQL |
| **Visualization** | Built-in, interactive | Requires additional tools |
| **Setup Complexity** | Moderate | Moderate |
| **Memory Usage** | Higher | Lower |
| **RDF Support** | Limited | Native |
| **Graph Algorithms** | Extensive built-in | Limited |
| **Browser Interface** | Comprehensive | Basic |
| **Data Format** | Property Graph | RDF Triples/Quads |

Choose Neo4j if you prioritize:
- Visual exploration of your knowledge graph
- Built-in graph algorithms
- A comprehensive browser interface

Choose Fuseki if you prioritize:
- Standard RDF and SPARQL compliance
- Lower memory footprint
- Integration with other RDF tools

## Troubleshooting

### Common Issues

1. **Neo4j won't start**
   - Check Java installation: `java -version`
   - Check port availability: `lsof -i :7474` and `lsof -i :7687`
   - View logs: `python setup_neo4j.py --logs`

2. **Data loading fails**
   - Validate Cypher syntax
   - Check file permissions
   - Ensure Neo4j is running

3. **Browser can't connect**
   - Verify Neo4j is running: `python setup_neo4j.py --status`
   - Check if ports 7474 and 7687 are accessible
   - Try connecting with `http://localhost:7474` instead of `127.0.0.1`

### Performance Tips

1. **Memory allocation**: Increase JVM memory for large datasets
   ```bash
   python setup_neo4j.py --start --memory 4g
   ```

2. **Indexing**: Create indexes for frequently queried properties
   ```cypher
   CREATE INDEX ON :EntityType(property)
   ```

3. **Query optimization**: Use parameters and EXPLAIN/PROFILE for complex queries

## Next Steps

With your Neo4j database set up, you can:

1. **Build applications** that query your knowledge graph using the Neo4j drivers
2. **Create custom visualizations** of your knowledge network
3. **Implement entity linking** algorithms
4. **Set up automated data pipelines**
5. **Integrate with other tools** via the Neo4j API

The Neo4j graph database provides a powerful foundation for advanced knowledge management, visualization, and analysis capabilities.
