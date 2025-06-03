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
  --output mycomind_knowledge_graph.jsonld
```

This will:
- Process all markdown files with YAML frontmatter in the `demo_vault/extracted_knowledge/project/` directory
- Resolve WikiLinks (`[[Shawn]]` → proper IRI references)
- Generate a complete JSON-LD knowledge graph

## Step 4: Set Up Graph Database

We recommend using Apache Jena Fuseki for this step. However, if you encounter issues with Fuseki, you can consider using alternative SPARQL engines such as:

*   **GraphDB** (Ontotext): A commercial product with a free version, offering a user-friendly web interface.
*   **Stardog**: Another commercial product with a free version, providing a web-based workbench.

**Instructions for Apache Jena Fuseki:**

```bash
# Download and install Apache Jena Fuseki
cd scripts
python setup_fuseki.py --download

# Start the Fuseki server on port 3031
python setup_fuseki.py --start --port 3031

# Verify it's running
python setup_fuseki.py --status
```

You should see:
- Fuseki server running on http://localhost:3031
- Web interface accessible for manual queries

**Alternative SPARQL Engines:**

If you encounter issues with Apache Jena Fuseki, you can consider using alternative SPARQL engines such as:

*   **GraphDB** (Ontotext): A commercial product with a free version, offering a user-friendly web interface. Download from: [https://www.ontotext.com/products/graphdb/](https://www.ontotext.com/products/graphdb/)
*   **Stardog**: Another commercial product with a free version, providing a web-based workbench. Download from: [https://www.stardog.com/](https://www.stardog.com/)

Please refer to their respective documentation for installation and setup instructions. Once you have installed and set up GraphDB or Stardog, follow their instructions to create a new repository or database and load the `mycomind_knowledge_graph.jsonld` file into it. Then, try running some of the sample queries provided in **Step 6: Query Your Knowledge Graph** to verify that the data has been loaded correctly.

## Step 5: Load Data into Graph Database

```bash
# Create the dataset and load your knowledge graph
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld
```

## Step 6: Query Your Knowledge Graph

### 💻 Option 1: JavaScript Command-Line Interface (Node.js)

**No Java required! Command-line interface using the same JavaScript engine.**

```bash
# Install Node.js dependencies (one-time setup)
npm install @comunica/query-sparql

# Interactive querying
node scripts/js_query_client.js --load mycomind_knowledge_graph.jsonld --interactive

# Execute specific queries
node scripts/js_query_client.js --load mycomind_knowledge_graph.jsonld --query "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
```

This provides:
- Command-line SPARQL querying without Java
- Interactive menu with sample queries
- Same JavaScript engine as the web interface
- Formatted table output
- Support for custom queries

### 🖥️ Option 2: Fuseki Graph Database (Java 11+ Required)

**Check your Java version first:**

```bash
# Check Java version
java -version

# Should show version 11 or higher
# If you have Java 8, use the JavaScript interface above instead
```

**If you have Java 11+:**

```bash
# Load your knowledge graph into Fuseki
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld

# Start interactive querying
python scripts/graph_db_client.py --interactive
```

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

### Fuseki Startup Issues - Troubleshooting

If Fuseki fails to start, you may encounter a `java.net.BindException: Address already in use` error. This means that the port Fuseki is trying to use is already occupied by another application. Here's a comprehensive set of debugging steps to identify the root cause:

**1. Verify Port Availability:**

   *   Before starting Fuseki, pick a port (e.g., 3031 or a less common one like 13031).
   *   Open your Mac's Terminal and run: `lsof -i :3031` (replace 3031 with your chosen port).
   *   If this command shows any output: Note the PID and command. That process is using the port. You'll need to stop it (e.g., `kill <PID>`) or choose a different port for Fuseki.
   *   If this command shows no output: The port should be free. Proceed to the next steps.

**2. Run Fuseki Directly from Terminal:**

   *   This bypasses the Python script and can give clearer error messages directly from Fuseki.
   *   Open Terminal.
   *   Set your `JAVA_HOME` (ensure it's active in your current shell session):
        *   `export JAVA_HOME="/Users/darrenzal/.sdkman/candidates/java/current"`
        *   `export PATH="$JAVA_HOME/bin:$PATH"`
   *   Navigate to your Fuseki installation directory:
        *   `cd /Users/darrenzal/MycoMind/fuseki/apache-jena-fuseki-4.10.0`
   *   Try to start Fuseki with your chosen verified free port and specify localhost for the host:
        *   `java -Xmx2g -jar fuseki-server.jar --host 127.0.0.1 --port 3031 --config /Users/darrenzal/MycoMind/fuseki/mycomind-config.ttl --verbose`
        *   (Replace 3031 if you chose a different port. Using `--host 127.0.0.1` tells Fuseki to only listen on the loopback interface).
   *   Carefully observe all output in the terminal. Look for any error messages.

**3. Inspect the Fuseki Configuration File:**

   *   The file `/Users/darrenzal/MycoMind/fuseki/mycomind-config.ttl` defines your datasets and server configuration.
   *   Open this file in a text editor.
   *   Look for any directives that explicitly set a port (e.g., `fuseki:port`, `jetty:port`) or define multiple server instances.
   *   For testing purposes only: If you suspect the config file, you could try running Fuseki with a very minimal or default configuration (if available from Jena examples) to see if it starts.

**4. Check Java Version:**

   *   Ensure your Java version is compatible. Apache Jena 4.10.0 requires Java 11 or later.
   *   Run: `/Users/darrenzal/.sdkman/candidates/java/current/bin/java -version`
   *   Confirm it shows a version like OpenJDK 11, 17, 21, etc.

**5. Look for Detailed Fuseki Logs:**

   *   Fuseki might generate its own logs, often in a `logs` subdirectory within its installation folder or as specified in a `log4j2.properties` file. These logs might provide more detailed error context.

**6. macOS Firewall:**

   *   Go to `System Settings -> Network -> Firewall`.
   *   If it's enabled, try temporarily disabling it briefly for testing purposes to see if Fuseki starts.
   *   If this resolves the issue, you'll need to add an explicit rule to allow incoming connections for Java or the specific port Fuseki uses.

**7. Restart Your Mac:**

   *   Sometimes, network resources can get into a strange state, and a full restart can clear these up.

**Note:** If you are still encountering issues, try running the Fuseki server directly from the terminal as described in step 2. This can often provide more detailed error messages and help pinpoint the root cause of the problem.

### Java Version Issues
If Fuseki fails to start with Java version errors:

```bash
# Check your Java version
java -version
```

The output should show version 11 or higher. If you see a version lower than 11, you need to install a more recent version of Java.

**Installing Java 11+ (Example using SDKMAN!):**

1. **Install SDKMAN!** (if you don't have it already):
   ```bash
   curl -s "https://get.sdkman.io" | bash
   source "$HOME/.sdkman/bin/sdkman-init.sh"
   ```

2. **Install a suitable Java version (e.g., Temurin 17):**
   ```bash
   sdk install java 17-temurin
   ```

3. **Verify the installation:**
   ```bash
   java -version
   ```

   Make sure the output now shows a version 11 or higher.

**Note:** The exact steps for installing Java may vary depending on your operating system and preferred package manager.

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
