# MycoMind: Personal Knowledge Management System

An AI-powered knowledge graph system that transforms unstructured text into queryable, visual knowledge networks. MycoMind combines LLM capabilities with graph database technologies to create semantic representations of your knowledge.

## Graph Database Backends

MycoMind supports two powerful graph database backends:

1. **🔥 Neo4j Integration** (Recommended): Visual graph exploration with Cypher queries and built-in web interface
2. **Apache Jena Fuseki Support**: Standard SPARQL endpoints for semantic web applications with web-based querying

## Features

### 🚀 **AI-Powered Entity Extraction**
- **LLM Integration**: Uses OpenAI GPT models to identify entities and relationships
- **Schema-Driven**: JSON-LD ontologies define extraction targets
- **Obsidian Compatible**: Generates markdown files with YAML frontmatter
- **Configurable**: Multiple LLM providers and extraction parameters

### 🔥 **Neo4j Integration**
- **Visual Graph Exploration**: Interactive node-link diagrams with expandable details
- **Cypher Query Language**: Powerful and intuitive graph querying syntax
- **Built-in Web Interface**: Neo4j Browser at http://localhost:7474
- **Graph Analytics**: Network analysis, pathfinding, centrality measures
- **Automated Setup**: One-command installation and configuration

### 🌐 **Apache Jena Fuseki Support**
- **SPARQL 1.1 Compliance**: Full semantic web standards support
- **Web Interface**: Built-in query interface at http://localhost:3030
- **JSON-LD Export**: Standard linked data format
- **Federation**: Connect with other SPARQL endpoints

## How It Works

### 📄 **Text to Knowledge Graph Pipeline**
1. **Input**: Unstructured text documents (txt, md, pdf, docx, html)
2. **AI Extraction**: LLM identifies entities and relationships based on your schema
3. **Structured Output**: Generates Obsidian-compatible markdown with YAML frontmatter
4. **Graph Database**: Converts to Neo4j Cypher or JSON-LD for Fuseki
5. **Query & Explore**: Visual exploration and querying through web interfaces

### 🔥 **Neo4j Workflow**
1. YAML frontmatter → Cypher CREATE statements
2. Automated Neo4j server setup and configuration
3. Data loading via cypher-shell or Neo4j Browser
4. Interactive visualization and Cypher querying

### 🌐 **Fuseki Workflow**
1. YAML frontmatter → JSON-LD knowledge graph
2. Automated Fuseki server setup and dataset creation
3. Data loading via SPARQL UPDATE
4. Standards-compliant SPARQL 1.1 querying

## Quick Start

### 🏃‍♂️ **Get Started in 5 Minutes**

```bash
# 1. Install dependencies
pip install -r scripts/requirements.txt

# 2. Setup configuration (add your OpenAI API key)
cp docs/examples/config_example.json config.json

# 3. Extract entities from sample data
python scripts/main_etl.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --source docs/examples/sample_data/mycomind_project.txt \
  --no-index

# 4A. For Neo4j (Recommended)
python scripts/setup_neo4j.py --download && python scripts/setup_neo4j.py --start
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output knowledge_graph.cypher
# Load: Open http://localhost:7474 and run :source knowledge_graph.cypher

# 4B. Or for Fuseki + SPARQL
python scripts/setup_fuseki.py --download && python scripts/setup_fuseki.py --start
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output knowledge_graph.jsonld
python scripts/graph_db_client.py --create-dataset --load knowledge_graph.jsonld
```

### 📚 **Full Tutorial**

For a complete step-by-step guide with sample queries, see: [**docs/examples/STEP_BY_STEP_EXAMPLE.md**](docs/examples/STEP_BY_STEP_EXAMPLE.md)

## Sample Queries

### 🔥 **Neo4j Cypher Examples**

```cypher
// Find all people and their roles
MATCH (person:RegenerativePerson) 
RETURN person.name, person.location, person.currentRole;

// Discover collaboration networks
MATCH (p1)-[:COLLABORATESWITH]-(p2) 
RETURN p1.name, p2.name;

// Find most connected entities
MATCH (n)-[r]-() 
RETURN n.name, count(r) as connections 
ORDER BY connections DESC;
```

### 🌐 **SPARQL Examples**

```sparql
PREFIX myco: <http://mycomind.org/kg/ontology/>

# Find all people with their details
SELECT ?name ?location ?role WHERE {
    ?person a myco:RegenerativePerson ;
            myco:name ?name ;
            myco:location ?location ;
            myco:currentRole ?role .
}

# Find active projects
SELECT ?project ?description WHERE {
    ?project a myco:HyphalTip ;
             myco:name ?project ;
             myco:description ?description ;
             myco:activityStatus "alive" .
}
```

### 🧠 **Meta-Queries: Explore MycoMind's Own Code**

```cypher
// Find all Python functions in the codebase
MATCH (f:PythonFunction)-[:DEFINED_IN]->(m:PythonModule)
RETURN f.name as Function, m.name as Module, f.signature
ORDER BY Module, Function;

// Discover feature implementations
MATCH (feature:Feature)<-[:IMPLEMENTS]-(code:PythonFunction)
RETURN feature.name as Feature, collect(code.name) as ImplementedBy;

// Analyze documentation coverage
MATCH (f:PythonFunction)
WHERE NOT EXISTS((f)<-[:DESCRIBES]-(:DocSection))
RETURN f.name as UndocumentedFunction, f.source_file as File;
```

**Full query collections with 50+ examples in the [step-by-step guide](docs/examples/STEP_BY_STEP_EXAMPLE.md) and [project knowledge graph docs](docs/Querying_Project_KG.md)!**

## Core Technologies

### 🤖 **AI & Language Processing**
- **OpenAI GPT Models**: Entity extraction and relationship identification
- **Schema-driven Prompting**: JSON-LD ontologies guide AI extraction
- **Configurable LLM Pipeline**: Support for multiple providers and models

### 🔥 **Neo4j Stack**
- **Neo4j Community 5.15.0**: High-performance graph database
- **Cypher**: Declarative graph query language
- **Neo4j Browser**: Built-in web interface for visualization and querying
- **Python neo4j Driver**: Programmatic database access

### 🌐 **Semantic Web Stack**
- **Apache Jena Fuseki**: SPARQL 1.1 compliant triple store
- **JSON-LD**: Linked data format for knowledge graphs
- **RDF/RDFS**: Resource Description Framework standards
- **Python rdflib**: RDF manipulation and SPARQL execution

### 🔧 **Supporting Technologies**
- **Python 3.8+**: Core application framework
- **YAML + Markdown**: Human-readable structured documents
- **Obsidian Compatible**: PKM integration and visualization

### 🧠 **Meta-Knowledge: Project Self-Analysis**
- **Self-Documenting**: MycoMind analyzes its own codebase to create a queryable knowledge graph
- **Code Architecture Queries**: Explore function dependencies, component relationships, and documentation coverage
- **"Dogfooding" Demonstration**: Real-world example of AI + knowledge graphs for software understanding
- **Advanced Use Case**: Query the project's own structure, find refactoring opportunities, trace features to implementation

## Documentation

| Topic | Description | Link |
|-------|-------------|------|
| **Getting Started** | Complete tutorial with sample data | [docs/examples/STEP_BY_STEP_EXAMPLE.md](docs/examples/STEP_BY_STEP_EXAMPLE.md) |
| **🧠 Project Knowledge Graph** | **Query MycoMind's own codebase as a knowledge graph** | [docs/Querying_Project_KG.md](docs/Querying_Project_KG.md) |
| **Architecture** | System design and components | [docs/Architecture.md](docs/Architecture.md) |
| **Configuration** | Settings and environment setup | [docs/Configuration.md](docs/Configuration.md) |
| **ETL Process** | Data extraction and transformation | [docs/ETL_Process.md](docs/ETL_Process.md) |
| **Neo4j Setup** | Graph database installation and usage | [docs/Neo4j_Database_Setup.md](docs/Neo4j_Database_Setup.md) |
| **Fuseki Setup** | SPARQL endpoint setup and querying | [docs/Graph_Database_Setup.md](docs/Graph_Database_Setup.md) |
| **Schema Design** | Creating custom ontologies | [docs/Ontology_Design.md](docs/Ontology_Design.md) |

## Requirements

- **Python 3.8+**
- **Java 17 or 21** (for Neo4j/Fuseki)
- **OpenAI API Key** (or compatible LLM service)
- **4GB+ RAM** recommended for graph databases

## License & Contributing

This project demonstrates modern AI + knowledge graph integration patterns. Contributions welcome!

---

**🚀 Ready to build your knowledge graph?** Start with the [**Step-by-Step Tutorial**](docs/examples/STEP_BY_STEP_EXAMPLE.md)!
