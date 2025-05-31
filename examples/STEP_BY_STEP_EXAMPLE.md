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
# 2. Update "vault_path": "/path/to/your/obsidian/vault" to your desired output path
#    For this demo, you can use: "./demo_vault" (creates a demo_vault folder)
#    Or use your existing Obsidian vault: "/Users/yourname/Documents/MyObsidianVault"
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

### Prerequisites Check

First, verify you have Java 11+ installed:

```bash
# Check Java version
java -version

# Should show version 11 or higher
# If you have Java 8, you'll need to upgrade for Fuseki to work
```

**If you have Java 11+:**

```bash
# Load your knowledge graph into Fuseki
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld

# Start interactive querying
python scripts/graph_db_client.py --interactive
```

**If you have Java 8 (like many macOS systems):**

You can still explore your JSON-LD file directly or use alternative tools. The queries below show what you could run once you upgrade Java.

### Sample Queries to Try

Based on our test data, here are queries that work with the generated knowledge graph:

1. **Find all HyphalTips:**
```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?tip ?name ?description ?status WHERE {
    ?tip a myco:HyphalTip ;
         myco:name ?name .
    OPTIONAL { ?tip myco:description ?description }
    OPTIONAL { ?tip myco:activityStatus ?status }
}
```

**Expected Results:**
- MycoMind: Personal Knowledge Management System (status: alive)
- public external organizational AI agent (status: alive)

2. **Find RegenerativePerson entities:**
```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?person ?name ?location ?role WHERE {
    ?person a myco:RegenerativePerson ;
            myco:name ?name .
    OPTIONAL { ?person myco:location ?location }
    OPTIONAL { ?person myco:currentRole ?role }
}
```

**Expected Results:**
- Shawn (location: Portland, role: Developer)

3. **Discover collaboration relationships:**
```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?entity1 ?name1 ?entity2 ?name2 WHERE {
    ?entity1 myco:name ?name1 ;
             myco:collaborator ?entity2 .
    ?entity2 myco:name ?name2 .
}
```

**Expected Results:**
- MycoMind collaborates with Shawn

4. **Find people in Portland:**
```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?person ?name ?role WHERE {
    ?person a myco:RegenerativePerson ;
            myco:name ?name ;
            myco:location "Portland" .
    OPTIONAL { ?person myco:currentRole ?role }
}
```

**Expected Results:**
- Shawn (role: Developer)

5. **Find organizations and their relationships:**
```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

SELECT ?org ?orgName ?member ?memberName WHERE {
    ?org a myco:Organization ;
         myco:name ?orgName ;
         myco:hasMember ?member .
    ?member myco:name ?memberName .
}
```

**Expected Results:**
- Transition Towns has member Shawn

### Web Interface Queries

**If you have Java 11+ and Fuseki running:**

You can use the Fuseki web interface at http://localhost:3030:
1. Go to "dataset.html"
2. Select the "mycomind" dataset
3. Click the "query" tab
4. Enter SPARQL queries and execute them

### Testing Queries Without Fuseki

If you can't run Fuseki, you can still:

1. **Examine the JSON-LD file directly:**
```bash
# Pretty print the knowledge graph
python -m json.tool mycomind_knowledge_graph.jsonld
```

2. **Use online SPARQL tools:**
- Upload your JSON-LD to tools like YASGUI or Apache Jena online
- Test queries in a web-based environment

3. **Use Python RDFLib for local querying:**
```python
from rdflib import Graph

# Load the knowledge graph
g = Graph()
g.parse("mycomind_knowledge_graph.jsonld", format="json-ld")

# Run a simple query
results = g.query("""
    PREFIX myco: <http://mycomind.org/kg/ontology/>
    SELECT ?name WHERE {
        ?person a myco:RegenerativePerson ;
                myco:name ?name .
    }
""")

for row in results:
    print(row)
```

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
