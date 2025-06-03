# MycoMind Knowledge Graph Query Interface

A knowledge graph management system for MycoMind with multiple query interfaces:

1. **Browser-based SPARQL Interface**: Query your knowledge graph using full SPARQL 1.1 syntax directly in the browser
2. **Neo4j Integration**: Visualize and query your knowledge graph using Neo4j's powerful browser interface
3. **Apache Jena Fuseki Support**: Use standard SPARQL endpoints for advanced querying capabilities

## Features

### Browser-based SPARQL Interface
- **No server required**: Query directly in your browser with SPARQL.js
- **Full SPARQL 1.1 Support**: Execute standard SPARQL queries
- **Entity Details**: Click on entity links to view detailed information
- **Sample Queries**: Pre-defined queries for common use cases
- **File Upload**: Load your own JSON-LD files

### Neo4j Integration
- **Visual Graph Exploration**: Intuitive visualization of your knowledge graph
- **Cypher Query Language**: Powerful and expressive graph querying
- **Built-in Graph Algorithms**: Network analysis, pathfinding, and more
- **Interactive Browser**: Comprehensive web interface for data exploration
- **Easy Setup**: Automated installation and configuration

## How It Works

### Browser-based SPARQL Interface
1. The interface loads JSON-LD data from `mycomind_knowledge_graph.jsonld`
2. The data is parsed into an in-memory RDF store using N3.js
3. SPARQL queries are parsed and executed using SPARQL.js
4. Results are displayed in a table with clickable entity links

### Neo4j Integration
1. YAML frontmatter from Markdown files is converted to Cypher statements
2. Neo4j loads and processes these statements to build the knowledge graph
3. The Neo4j Browser provides visualization and querying capabilities
4. Results can be viewed as tables, graphs, or exported in various formats

## Generating the Knowledge Graph

### For Browser-based SPARQL Interface

Generate a JSON-LD file from Markdown files with YAML frontmatter:

```bash
python scripts/yaml_to_jsonld_converter.py --schema schemas/hyphaltips_mycomind_schema.json --input /path/to/markdown/files --output mycomind_knowledge_graph.jsonld --web-app
```

The `--web-app` option automatically copies the generated JSON-LD file to the web app directory (`docs/web/mycomind_knowledge_graph.jsonld`), making it immediately available for querying in the web interface.

### For Neo4j Integration

Generate Cypher statements from Markdown files with YAML frontmatter:

```bash
python scripts/yaml_to_neo4j_converter.py --schema schemas/hyphaltips_mycomind_schema.json --input /path/to/markdown/files --output knowledge_graph.cypher --browser
```

The `--browser` option attempts to copy the generated Cypher file to the Neo4j import directory, making it available for loading via the `:source` command in the Neo4j Browser.

## Sample Queries

- **Find People**: Find all RegenerativePerson entities with their details
- **Find Projects**: Find all HyphalTip projects and their status
- **Find Organizations**: Find all organizations in the knowledge graph
- **Find Collaborations**: Discover collaboration relationships
- **Find by Location**: Find entities in specific locations
- **Network Analysis**: Find most connected entities

## Usage

1. Open `index.html` in your browser
2. The interface will automatically load the knowledge graph data
3. Select a sample query or write your own SPARQL query
4. Click "Execute Query" to run the query
5. View the results in the table
6. Click on entity links to view detailed information

## Technologies Used

### Browser-based SPARQL Interface
- **N3.js**: JavaScript library for working with RDF data
- **SPARQL.js**: SPARQL 1.1 parser for JavaScript
- **HTML/CSS/JavaScript**: Frontend interface
- **JSON-LD**: Data format for the knowledge graph

### Neo4j Integration
- **Neo4j**: Graph database with visualization capabilities
- **Cypher**: Graph query language
- **Python**: Conversion and setup scripts
- **Neo4j Browser**: Web interface for querying and visualization

## Setup and Usage

### Browser-based SPARQL Interface

For local development, you may encounter CORS issues when trying to load the JSON-LD file. To avoid this, you can:

1. Use a local web server (e.g., `python -m http.server`)
2. The interface now includes a fallback to sample data if the JSON-LD file cannot be loaded

For more detailed information, see the [Web SPARQL Interface documentation](docs/Web_SPARQL_Interface.md).

### Neo4j Integration

To set up and use Neo4j with MycoMind:

1. Install and start Neo4j:
   ```bash
   python scripts/setup_neo4j.py --download
   python scripts/setup_neo4j.py --start
   ```

2. Convert your data to Cypher:
   ```bash
   python scripts/yaml_to_neo4j_converter.py --schema schemas/hyphaltips_mycomind_schema.json --input /path/to/markdown/files --output knowledge_graph.cypher
   ```

3. Load the data in Neo4j Browser:
   - Open http://localhost:7474
   - Run `:source knowledge_graph.cypher`

For more detailed information, see the [Neo4j Database Setup documentation](docs/Neo4j_Database_Setup.md).

### Apache Jena Fuseki (Alternative)

For users who prefer a standard SPARQL endpoint:

1. Install and start Fuseki:
   ```bash
   python scripts/setup_fuseki.py --download
   python scripts/setup_fuseki.py --start
   ```

2. Load your JSON-LD data:
   ```bash
   python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld
   ```

For more detailed information, see the [Graph Database Setup documentation](docs/Graph_Database_Setup.md).

## GitHub Pages Deployment

This interface is designed to be deployed on GitHub Pages. The repository is configured to deploy from the `docs` folder.

The web interface files are located in the `docs/web` directory:
- `docs/web/index.html` - The main web interface file
- `docs/web/mycomind_knowledge_graph.jsonld` - The JSON-LD data file

Visit the live interface at: https://[your-username].github.io/mycomind-kg-interface/web/
