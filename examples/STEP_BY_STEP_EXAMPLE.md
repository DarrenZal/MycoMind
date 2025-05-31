# MycoMind Step-by-Step Example

This guide walks you through the complete MycoMind workflow using the included sample data. You'll start with unstructured text and end up with a queryable knowledge graph.

## Prerequisites

1. **Java 11+** installed (for Fuseki graph database)
2. **OpenAI API key** (or compatible LLM service)
3. **Python dependencies** installed: `pip install -r scripts/requirements.txt`

## Step 1: Setup Configuration

```bash
# Copy the example configuration
cp examples/config_example.json config.json

# Edit config.json and make these changes:
# 1. Change "your_openai_api_key_here" to your actual OpenAI API key
# 2. Update "vault_path": "/path/to/your/obsidian/vault" to your actual vault path
#    For example: "/Users/yourname/Documents/MyObsidianVault"
#    Or create a new directory: "/Users/yourname/MycoMind/knowledge_vault"
```

## Step 2: Process Unstructured Text with AI Extraction

We'll use the sample document `examples/sample_data/mycomind_project.txt` which contains unstructured text about the MycoMind project and mentions collaboration with "Shawn".

```bash
# Run the ETL pipeline to extract entities from unstructured text
python scripts/main_etl.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --source examples/sample_data/mycomind_project.txt \
  --no-index
```

This will:
- Use AI to identify entities (HyphalTip, RegenerativePerson, etc.)
- Create markdown files with YAML frontmatter in your configured output directory
- Extract relationships between entities (e.g., collaboration between MycoMind and Shawn)

**Expected Output:**
- `MycoMind.md` - A HyphalTip entity with project details
- `Shawn.md` - A RegenerativePerson entity with location, expertise, etc.
- Each file will have YAML frontmatter with structured data

## Step 3: Convert YAML Frontmatter to JSON-LD

```bash
# Convert the generated markdown files to a knowledge graph
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input /path/to/your/obsidian/vault \
  --output mycomind_knowledge_graph.jsonld
```

Replace `/path/to/your/obsidian/vault` with the actual path from your `config.json`.

This will:
- Process all markdown files with YAML frontmatter
- Resolve WikiLinks (`[[Shawn]]` → proper IRI references)
- Generate a complete JSON-LD knowledge graph

## Step 4: Set Up Graph Database

```bash
# Download and install Apache Jena Fuseki
cd scripts
python setup_fuseki.py --download

# Start the Fuseki server
python setup_fuseki.py --start

# Verify it's running
python setup_fuseki.py --status
```

You should see:
- Fuseki server running on http://localhost:3030
- Web interface accessible for manual queries

## Step 5: Load Data into Graph Database

```bash
# Create the dataset and load your knowledge graph
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld
```

## Step 6: Query Your Knowledge Graph

### Interactive Querying

```bash
# Start the interactive query interface
python scripts/graph_db_client.py --interactive
```

This provides a menu with:
- Sample queries
- Custom SPARQL input
- Entity search
- Statistics

### Sample Queries to Try

1. **Find all HyphalTips:**
```sparql
SELECT ?tip ?name ?description ?status WHERE {
    ?tip a myco:HyphalTip ;
         myco:name ?name .
    OPTIONAL { ?tip myco:description ?description }
    OPTIONAL { ?tip myco:activityStatus ?status }
}
```

2. **Find RegenerativePerson entities:**
```sparql
SELECT ?person ?name ?location ?expertise WHERE {
    ?person a myco:RegenerativePerson ;
            myco:name ?name .
    OPTIONAL { ?person myco:location ?location }
    OPTIONAL { ?person myco:expertise ?expertise }
}
```

3. **Discover collaboration relationships:**
```sparql
SELECT ?entity1 ?name1 ?entity2 ?name2 WHERE {
    ?entity1 myco:name ?name1 ;
             myco:collaborator ?entity2 .
    ?entity2 myco:name ?name2 .
}
```

4. **Find people in Portland:**
```sparql
SELECT ?person ?name ?role WHERE {
    ?person a myco:RegenerativePerson ;
            myco:name ?name ;
            myco:location "Portland" .
    OPTIONAL { ?person myco:currentRole ?role }
}
```

### Web Interface Queries

You can also use the Fuseki web interface at http://localhost:3030:
1. Go to "dataset.html"
2. Select the "mycomind" dataset
3. Click the "query" tab
4. Enter SPARQL queries and execute them

## Step 7: Explore Advanced Features

### Network Analysis
```sparql
# Find most connected entities
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

### Entity Search
```bash
# Search for entities containing "semantic"
python scripts/graph_db_client.py --interactive
# Then choose "search" and enter "semantic"
```

## Expected Results

After completing this workflow, you should have:

1. **Extracted Entities:**
   - MycoMind (HyphalTip) - active project with AI and knowledge graph focus
   - Shawn (RegenerativePerson) - Portland-based developer with semantic web expertise

2. **Discovered Relationships:**
   - Collaboration between MycoMind project and Shawn
   - Shawn's expertise in semantic web technologies
   - Connection to regenerative systems and community resilience

3. **Queryable Knowledge Graph:**
   - SPARQL endpoint for complex queries
   - Web interface for exploration
   - Programmatic access via Python client

## Troubleshooting

### Java Version Issues
If Fuseki fails to start with Java version errors:
```bash
# Check your Java version
java -version

# Fuseki 4.10.0 requires Java 11+
# Install Java 11+ or use an older Fuseki version
```

### No Entities Extracted
If the ETL pipeline doesn't extract entities:
- Verify your OpenAI API key is correct
- Check that the schema file exists and is valid
- Ensure the source document contains recognizable entities

### SPARQL Queries Return No Results
- Verify data was loaded: `SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }`
- Check entity IRIs and prefixes
- Use the web interface to browse the data structure

## Next Steps

Once you have your knowledge graph running:

1. **Process your own documents** by pointing the ETL pipeline at your files
2. **Create custom schemas** for your specific knowledge domains
3. **Build applications** that query your knowledge graph
4. **Set up automated pipelines** to keep your graph updated
5. **Explore visualization tools** to see your knowledge network

This workflow demonstrates the complete journey from unstructured text to semantic knowledge graphs using modern AI and semantic web technologies!
