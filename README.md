# MycoMind

A comprehensive Personal Knowledge Management (PKM) system that transforms unstructured information into queryable knowledge graphs. MycoMind combines AI-powered entity extraction, semantic web technologies, and graph databases to create living, interconnected knowledge networks.

## 🌟 Key Features

- **🧠 AI-Powered Knowledge Extraction**: Uses large language models to automatically identify entities, relationships, and concepts from unstructured text
- **📝 Obsidian-Compatible**: Generates markdown files with YAML frontmatter that work seamlessly in Obsidian vaults with WikiLink support
- **🕸️ Semantic Web Integration**: Built on JSON-LD, RDF, and SPARQL standards for maximum interoperability
- **📊 Multiple Query Options**: JavaScript web interface (no Java required) + Apache Jena Fuseki for advanced users
- **🔗 Intelligent Entity Linking**: Automatically resolves WikiLinks (`[[Entity Name]]`) and connects related entities across your knowledge base
- **📝 Schema-Driven Architecture**: Flexible ontology system supporting custom knowledge domains
- **🔄 Complete ETL Pipeline**: From raw text to structured knowledge graphs with full provenance tracking
- **🌐 Standards-Based**: Compatible with Schema.org, Murmurations, and other semantic web vocabularies
- **📱 Multiple Output Formats**: Markdown with YAML frontmatter, JSON-LD, RDF, and more

## 🚀 Quick Start

### 🎯 Complete Step-by-Step Example

Follow our comprehensive guide to experience the full workflow:

**[📖 Step-by-Step Example Guide](examples/STEP_BY_STEP_EXAMPLE.md)**

This guide walks you through:
- **AI Entity Extraction**: Process unstructured text about the MycoMind project
- **YAML Frontmatter Generation**: Create structured markdown files
- **JSON-LD Conversion**: Transform to semantic web standards
- **Graph Database Setup**: Install and configure Apache Jena Fuseki
- **SPARQL Querying**: Discover relationships and analyze your knowledge network

Uses realistic sample data including HyphalTip and RegenerativePerson entities with collaboration relationships.

### 📋 Full Installation

```bash
# Clone and install
git clone https://github.com/yourusername/MycoMind.git
cd MycoMind
pip install -r scripts/requirements.txt

# Optional: Configure for live AI extraction
cp examples/config_example.json config.json
# Edit config.json with your LLM API keys
```

## 🏗️ Architecture Overview

MycoMind implements a modern knowledge management architecture:

```
📄 Unstructured Text
    ↓ (AI Extraction)
🧩 Structured Entities (YAML/JSON)
    ↓ (Schema Conversion)
🌐 JSON-LD Knowledge Graph
    ↓ (Database Loading)
📊 SPARQL-Queryable Graph Database
    ↓ (Analysis & Discovery)
🔍 Insights & Connections
```

### Core Components

1. **Entity Extraction Engine** (`main_etl.py`)
   - LLM-powered text processing
   - Schema-guided extraction
   - Confidence scoring and validation

2. **Knowledge Graph Converter** (`yaml_to_jsonld_converter.py`)
   - YAML frontmatter to JSON-LD transformation
   - WikiLink resolution to proper IRIs
   - Schema-aware data type handling

3. **Graph Database Client** (`graph_db_client.py`)
   - Apache Jena Fuseki integration
   - SPARQL query interface
   - Interactive exploration tools

4. **Schema System** (`schemas/`)
   - JSON-LD ontology definitions
   - Support for custom knowledge domains
   - Extensible entity and relationship models

## 🎯 Use Cases

### Personal Knowledge Management
- Transform your notes into a queryable knowledge graph
- Discover hidden connections between ideas and projects
- Track relationships between people, organizations, and concepts

### Research & Academia
- Extract entities from research papers and documents
- Build domain-specific knowledge graphs
- Perform semantic analysis across large document collections

### Organizational Knowledge
- Create institutional memory systems
- Map expertise networks and collaboration patterns
- Enable semantic search across organizational content

### Community Mapping
- Model regenerative economy networks (using RegenerativePerson schema)
- Track community relationships and resource flows
- Support collective intelligence initiatives

## 🔧 Advanced Features

### Schema Flexibility
```bash
# Use built-in schemas
python scripts/main_etl.py --schema schemas/hyphaltips_mycomind_schema.json --source document.txt

# Create custom schemas for your domain
python scripts/main_etl.py --schema schemas/your_custom_schema.json --source data/
```

### Knowledge Graph Querying

**Option 1: JavaScript Web Interface (Recommended)**
```bash
# Open browser-based query interface - no Java required!
open web_query_interface.html
```
- Beautiful, responsive web interface
- Load JSON-LD files directly in browser
- Sample queries and SPARQL editor
- Works on any system with a modern browser

**Option 2: Fuseki Graph Database (Advanced)**
```bash
# Set up Fuseki server (requires Java 11+)
python scripts/setup_fuseki.py --download
python scripts/setup_fuseki.py --start

# Load and query your knowledge graph
python scripts/graph_db_client.py --load knowledge_graph.jsonld
python scripts/graph_db_client.py --interactive
```

### SPARQL Query Examples
```sparql
# Find most connected entities
SELECT ?entity ?name (COUNT(?connection) as ?degree) WHERE {
    ?entity myco:name ?name .
    { ?entity ?predicate ?connection } UNION { ?connection ?predicate ?entity }
    FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
}
GROUP BY ?entity ?name
ORDER BY DESC(?degree)

# Discover collaboration networks
SELECT ?person1 ?name1 ?person2 ?name2 WHERE {
    ?person1 a myco:RegenerativePerson ; myco:name ?name1 ;
             myco:collaboratesWith ?person2 .
    ?person2 myco:name ?name2 .
}
```

## 📊 Supported Schemas

MycoMind includes several built-in schemas:

- **HyphalTips**: Personal projects and ideas with lifecycle tracking
- **RegenerativePerson**: Extended person schema for regenerative economy mapping
- **Organizations**: Institutions, companies, and community groups
- **Custom Schemas**: Easy to create domain-specific ontologies

## 🌐 Standards Compliance

Built on established semantic web standards:
- **JSON-LD**: W3C standard for linked data
- **RDF**: Resource Description Framework
- **SPARQL**: Query language for graph databases
- **Schema.org**: Common vocabulary for structured data
- **Murmurations**: Network mapping and discovery protocol

## 📁 Project Structure

```
MycoMind/
├── 🎯 examples/
│   ├── mycomind_demo.py           # Complete workflow demonstration
│   └── sample_data/
│       └── mycomind_project.txt   # Realistic example document
├── 🧠 scripts/                    # Core processing engine
│   ├── main_etl.py               # AI extraction pipeline
│   ├── yaml_to_jsonld_converter.py # Knowledge graph conversion
│   ├── graph_db_client.py        # Database operations
│   └── setup_fuseki.py           # Graph database setup
├── 🗂️ schemas/                   # Knowledge ontologies
│   └── hyphaltips_mycomind_schema.json # Combined schema
├── 📚 docs/                      # Comprehensive documentation
│   ├── Graph_Database_Setup.md   # Database setup guide
│   ├── Architecture.md           # System design
│   └── [other guides]
└── 🔧 [configuration files]
```

## 📖 Documentation

- **[Graph Database Setup](docs/Graph_Database_Setup.md)**: Complete guide to Fuseki and SPARQL
- **[Architecture](docs/Architecture.md)**: System design and components
- **[Ontology Design](docs/Ontology_Design.md)**: Creating effective schemas
- **[Configuration](docs/Configuration.md)**: Setup and customization

## 🚀 What's Next?

MycoMind is actively evolving with planned features:
- **Visualization Tools**: Interactive graph exploration interfaces
- **Advanced Entity Linking**: ML-powered entity resolution
- **Federation Support**: Connect multiple knowledge graphs
- **Real-time Updates**: Live synchronization with document changes
- **API Endpoints**: RESTful access to knowledge graph operations

## 🤝 Contributing

We welcome contributions! MycoMind is designed to be:
- **Extensible**: Easy to add new schemas and processors
- **Modular**: Components can be used independently
- **Standards-Based**: Built on open semantic web technologies

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by the Zettelkasten method and Personal Knowledge Management principles
- Built on the semantic web stack (RDF, SPARQL, JSON-LD)
- Powered by modern LLM capabilities for knowledge extraction
- Supports the regenerative economy through Murmurations integration

---

*MycoMind: Transforming information into interconnected knowledge* 🍄🧠🌐
