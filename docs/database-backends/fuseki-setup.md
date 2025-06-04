# Graph Database Setup and Usage Guide

This guide explains how to set up and use a graph database (Apache Jena Fuseki) with your MycoMind knowledge management system.

## Overview

The complete MycoMind workflow now includes:

1. **Extract**: Process documents and create YAML frontmatter in Markdown files
2. **Convert**: Transform YAML frontmatter back to JSON-LD using schemas
3. **Load**: Import JSON-LD into a graph database for advanced querying
4. **Query**: Use SPARQL to explore and analyze your knowledge graph

## Prerequisites

- Python 3.8+
- Java 11+ (for Fuseki)
- All MycoMind dependencies installed

## Quick Start

### Run the Complete Demo

The fastest way to see MycoMind in action is to run our complete demo:

```bash
# Run the MycoMind demo (includes Fuseki setup, entity extraction, and querying)
python examples/mycomind_demo.py
```

This demo:
- Processes a realistic unstructured text about the MycoMind project
- Extracts a HyphalTip entity and a RegenerativePerson entity (Shawn)
- Converts to JSON-LD using the combined HyphalTips + RegenerativePerson schema
- Loads into Fuseki and demonstrates SPARQL queries

### Manual Setup

If you want to set up components manually:

```bash
cd scripts

# 1. Download and install Fuseki
python setup_fuseki.py --download
python setup_fuseki.py --start

# 2. Convert YAML to JSON-LD
python yaml_to_jsonld_converter.py \
  --schema ../schemas/hyphaltips_mycomind_schema.json \
  --input /path/to/markdown/files \
  --output knowledge_graph.jsonld

# 3. Load data and query
python graph_db_client.py --create-dataset --load knowledge_graph.jsonld
python graph_db_client.py --interactive
```

## Detailed Setup

### Installing Fuseki

The `setup_fuseki.py` script automates the Fuseki installation:

```bash
# Download Fuseki (about 50MB)
python setup_fuseki.py --download

# This will:
# - Download Apache Jena Fuseki 4.10.0
# - Extract it to the fuseki/ directory
# - Create a MycoMind-specific configuration file
```

### Starting the Server

```bash
# Start with default settings (port 3030, 2GB memory)
python setup_fuseki.py --start

# Start with custom settings
python setup_fuseki.py --start --port 3031 --memory 4g

# Check if running
python setup_fuseki.py --status
```

### Server Management

```bash
# Stop the server
python setup_fuseki.py --stop

# Restart the server
python setup_fuseki.py --restart

# View recent logs
python setup_fuseki.py --logs
```

## Data Conversion

### YAML to JSON-LD Conversion

The `yaml_to_jsonld_converter.py` script converts your Markdown files with YAML frontmatter back to JSON-LD format:

```bash
# Basic usage
python yaml_to_jsonld_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --input /path/to/markdown/files \
  --output knowledge_graph.jsonld

# With custom base IRI
python yaml_to_jsonld_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --input /path/to/markdown/files \
  --output knowledge_graph.jsonld \
  --base-iri "https://mycomind.org/kg/"

# Convert single file
python yaml_to_jsonld_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --file person.md \
  --output person.jsonld
```

### What Gets Converted

The converter processes:
- **Entity types** from YAML `type` field
- **Properties** based on schema definitions
- **Relationships** with WikiLink resolution (`[[Entity Name]]` → IRI references)
- **Metadata** (extraction confidence, source files, timestamps)

## Graph Database Operations

### Loading Data

```bash
# Create dataset (first time only)
python graph_db_client.py --create-dataset

# Load JSON-LD data
python graph_db_client.py --load knowledge_graph.jsonld

# Load into named graph
python graph_db_client.py --load knowledge_graph.jsonld --graph-uri "http://mycomind.org/kg/graph"
```

### Querying

#### Interactive Mode

```bash
python graph_db_client.py --interactive
```

This provides a menu-driven interface with:
- Sample queries
- Custom SPARQL input
- Entity search
- Statistics display

#### Command Line Queries

```bash
# Execute query from file
python graph_db_client.py --query queries.sparql

# Execute inline query
python graph_db_client.py --query "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
```

### Sample Queries

The system includes several built-in sample queries:

1. **Count entities by type**
2. **List all HyphalTips**
3. **Find collaborations**
4. **Find projects and their status**
5. **Find entity relationships**
6. **Find most connected entities**
7. **Find orphaned entities**
8. **Knowledge graph statistics**

## SPARQL Query Examples

### Basic Entity Listing

```sparql
# List all entities with their names
SELECT ?entity ?name ?type WHERE {
    ?entity a ?type ;
            myco:name ?name .
    FILTER(STRSTARTS(STR(?type), STR(myco:)))
}
ORDER BY ?name
```

### Relationship Exploration

```sparql
# Find all relationships between entities
SELECT ?entity1 ?name1 ?relationship ?entity2 ?name2 WHERE {
    ?entity1 myco:name ?name1 ;
             ?predicate ?entity2 .
    ?entity2 myco:name ?name2 .
    FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
    BIND(STRAFTER(STR(?predicate), STR(myco:)) as ?relationship)
}
```

### Network Analysis

```sparql
# Find most connected entities
SELECT ?entity ?name (COUNT(?connection) as ?connectionCount) WHERE {
    ?entity myco:name ?name .
    {
        ?entity ?predicate ?connection .
        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
    } UNION {
        ?connection ?predicate ?entity .
        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
    }
}
GROUP BY ?entity ?name
ORDER BY DESC(?connectionCount)
LIMIT 10
```

### Search and Filter

```sparql
# Search entities by name or description
SELECT ?entity ?name ?description WHERE {
    ?entity myco:name ?name .
    OPTIONAL { ?entity myco:description ?description }
    FILTER(
        CONTAINS(LCASE(?name), LCASE("search_term")) ||
        CONTAINS(LCASE(?description), LCASE("search_term"))
    )
}
```

## Web Interface

Once Fuseki is running, you can access the web interface at:
- **Main interface**: http://localhost:3030
- **Dataset management**: http://localhost:3030/dataset.html
- **Query interface**: http://localhost:3030/dataset.html?tab=query&ds=/mycomind

The web interface allows you to:
- Execute SPARQL queries
- Browse datasets
- Upload data files
- View server statistics

## Integration with Your Workflow

### Complete Pipeline

```bash
# 1. Extract entities from documents
python main_etl.py --schema ../schemas/example_schemas/personal_knowledge.json \
                   --source document.txt

# 2. Convert YAML frontmatter to JSON-LD
python yaml_to_jsonld_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --input /path/to/generated/markdown \
  --output knowledge_graph.jsonld

# 3. Load into graph database
python graph_db_client.py --load knowledge_graph.jsonld

# 4. Query and analyze
python graph_db_client.py --interactive
```

### Automated Updates

You can create scripts to automatically update your knowledge graph:

```bash
#!/bin/bash
# update_knowledge_graph.sh

# Convert latest markdown files
python yaml_to_jsonld_converter.py \
  --schema ../schemas/example_schemas/personal_knowledge.json \
  --input /path/to/obsidian/vault \
  --output latest_kg.jsonld

# Clear existing data and reload
python graph_db_client.py --query "CLEAR DEFAULT"
python graph_db_client.py --load latest_kg.jsonld

echo "Knowledge graph updated!"
```

## Advanced Features

### Entity Linking

The graph database enables sophisticated entity linking:

```sparql
# Find potential duplicate entities
SELECT ?entity1 ?name1 ?entity2 ?name2 WHERE {
    ?entity1 myco:name ?name1 .
    ?entity2 myco:name ?name2 .
    FILTER(?entity1 != ?entity2)
    FILTER(LCASE(?name1) = LCASE(?name2))
}
```

### Graph Analytics

```sparql
# Calculate degree centrality
SELECT ?entity ?name (COUNT(?connection) as ?degree) WHERE {
    ?entity myco:name ?name .
    {
        ?entity ?predicate ?connection .
        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
    } UNION {
        ?connection ?predicate ?entity .
        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
    }
}
GROUP BY ?entity ?name
ORDER BY DESC(?degree)
```

### Data Quality Checks

```sparql
# Find entities without descriptions
SELECT ?entity ?name WHERE {
    ?entity myco:name ?name .
    FILTER NOT EXISTS { ?entity myco:description ?description }
}

# Find orphaned entities (no relationships)
SELECT ?entity ?name WHERE {
    ?entity myco:name ?name .
    FILTER NOT EXISTS {
        { ?entity ?predicate ?other . FILTER(STRSTARTS(STR(?predicate), STR(myco:))) }
        UNION
        { ?other ?predicate ?entity . FILTER(STRSTARTS(STR(?predicate), STR(myco:))) }
    }
}
```

## Troubleshooting

### Common Issues

1. **Fuseki won't start**
   - Check Java installation: `java -version`
   - Check port availability: `lsof -i :3030`
   - View logs: `python setup_fuseki.py --logs`

2. **Data loading fails**
   - Validate JSON-LD format
   - Check file permissions
   - Verify dataset exists

3. **Queries return no results**
   - Check if data is loaded: `python graph_db_client.py --query "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }"`
   - Verify prefixes in queries
   - Check entity IRIs

### Performance Tips

1. **Memory allocation**: Increase JVM memory for large datasets
   ```bash
   python setup_fuseki.py --start --memory 4g
   ```

2. **Persistent storage**: For production use, enable TDB2 storage in the config file

3. **Query optimization**: Use LIMIT clauses for exploratory queries

## Next Steps

With your graph database set up, you can:

1. **Build applications** that query your knowledge graph
2. **Create visualizations** of your knowledge network
3. **Implement entity linking** algorithms
4. **Set up automated data pipelines**
5. **Integrate with other tools** via SPARQL endpoints

The graph database provides a powerful foundation for advanced knowledge management and analysis capabilities.
