# MycoMind Knowledge Graph Query Interface

A browser-based SPARQL querying interface for the MycoMind knowledge graph. This interface allows you to query the knowledge graph using SPARQL-like syntax without requiring Java or external SPARQL endpoints like Fuseki.

## Features

- **Browser-based**: No server-side components required
- **SPARQL Querying**: Execute SPARQL-like queries against your knowledge graph
- **Entity Details**: Click on entity links to view detailed information
- **Sample Queries**: Pre-defined queries for common use cases
- **File Upload**: Load your own JSON-LD files

## How It Works

1. The interface loads JSON-LD data from `mycomind_knowledge_graph.jsonld`
2. The data is parsed into an in-memory RDF store using rdflib.js
3. SPARQL-like queries are executed against the in-memory store
4. Results are displayed in a table with clickable entity links

## Generating the Knowledge Graph

The JSON-LD file can be generated from Markdown files with YAML frontmatter using the Python script:

```bash
python scripts/yaml_to_jsonld_converter.py --schema schemas/hyphaltips_mycomind_schema.json --input /path/to/markdown/files --output mycomind_knowledge_graph.jsonld
```

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

- **rdflib.js**: JavaScript library for working with RDF data
- **HTML/CSS/JavaScript**: Frontend interface
- **JSON-LD**: Data format for the knowledge graph

## Local Development

For local development, you may encounter CORS issues when trying to load the JSON-LD file. To avoid this, you can:

1. Use a local web server (e.g., `python -m http.server`)
2. Upload a JSON-LD file using the file input

## GitHub Pages Deployment

This interface is designed to be deployed on GitHub Pages. The repository is configured to deploy from the `docs` folder.

The web interface files are located in the `docs/web` directory:
- `docs/web/index.html` - The main web interface file
- `docs/web/mycomind_knowledge_graph.jsonld` - The JSON-LD data file

Visit the live interface at: https://[your-username].github.io/mycomind-kg-interface/web/
