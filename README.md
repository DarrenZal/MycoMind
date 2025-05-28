# MycoMind

A Personal Knowledge Management (PKM) system that performs LLM-driven, ontology-based knowledge extraction into Obsidian vaults. MycoMind transforms unstructured information into structured, interconnected knowledge graphs using user-defined schemas.

## 🌟 Features

- **Ontology-Driven Extraction**: Uses JSON-LD schemas to define knowledge structures
- **Obsidian Integration**: Creates structured Markdown notes with YAML frontmatter
- **LLM-Powered Processing**: Leverages language models for intelligent information extraction
- **Semantic Linking**: Automatically creates `[[WikiLinks]]` for entity relationships
- **Configurable Workflows**: Easy-to-customize ETL pipelines
- **Self-Documenting**: The project uses its own principles to maintain its documentation

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (or compatible LLM service)
- Obsidian vault (optional, for viewing results)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/MycoMind.git
cd MycoMind
```

2. Install dependencies:
```bash
pip install -r scripts/requirements.txt
```

3. Configure your settings:
```bash
cp examples/config_example.json config.json
# Edit config.json with your API keys and paths
```

### Basic Usage

1. Define your knowledge schema in the `schemas/` directory
2. Configure your data sources in `config.json`
3. Run the ETL pipeline:

```bash
python scripts/main_etl.py --config config.json --schema schemas/your_schema.json
```

## 📁 Project Structure

```
MycoMind/
├── README.md                    # This file
├── config.json                  # Configuration file (user-created)
├── docs/                        # Detailed documentation
│   ├── Architecture.md          # System architecture overview
│   ├── Ontology_Design.md       # Schema design principles
│   ├── ETL_Process.md           # Data processing pipeline
│   ├── Configuration.md         # Setup and configuration guide
│   ├── Semantic_Linking.md      # Entity linking strategies
│   └── Querying_Project_KG.md   # Advanced: Project knowledge graph
├── scripts/                     # Core Python modules
│   ├── config_manager.py        # Configuration handling
│   ├── schema_parser.py         # JSON-LD schema processing
│   ├── obsidian_utils.py        # Obsidian note generation
│   ├── main_etl.py             # Main ETL pipeline
│   └── requirements.txt         # Python dependencies
├── schemas/                     # JSON-LD schema definitions
│   └── example_schemas/         # Sample schemas to get started
├── examples/                    # Example configurations and data
│   ├── config_example.json      # Sample configuration
│   └── sample_data/             # Test data for experimentation
└── project_knowledge_graph/     # Advanced: Project's own KG data
    ├── schema.json              # Meta-schema for the project
    ├── mycomind_kg.cypher       # Cypher script for Neo4j import
    └── example_queries.cypher   # Sample queries for exploration
```

## 📖 Documentation

Comprehensive documentation is available in the `/docs` folder:

- **[Architecture](docs/Architecture.md)**: System design and component overview
- **[Ontology Design](docs/Ontology_Design.md)**: How to create effective schemas
- **[ETL Process](docs/ETL_Process.md)**: Understanding the data pipeline
- **[Configuration](docs/Configuration.md)**: Detailed setup instructions
- **[Semantic Linking](docs/Semantic_Linking.md)**: Entity relationship strategies

## 🔬 Advanced Documentation: The Project Knowledge Graph

MycoMind practices what it preaches by maintaining its own documentation and codebase as a queryable knowledge graph. This advanced feature allows power users to perform deep, semantic queries about the project itself.

**What is it?**
- A Neo4j-compatible knowledge graph containing the project's architecture, code structure, and documentation
- Enables complex queries like "Show me all functions that implement schema parsing" or "Find documentation sections related to Obsidian integration"

**Benefits:**
- Deeply queryable documentation beyond simple text search
- Understand complex relationships between code, features, and documentation
- Explore the project's architecture through graph traversal
- See practical examples of the system's own output

**Getting Started:**
This is an optional feature for advanced users. See **[Querying the Project's Knowledge Graph](docs/Querying_Project_KG.md)** for detailed setup instructions and example queries.

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and feel free to submit issues or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Inspired by the principles of Personal Knowledge Management and the Zettelkasten method
- Built on the shoulders of the Obsidian and Neo4j communities
- Powered by modern LLM capabilities for knowledge extraction

---

*MycoMind: Growing knowledge networks, one connection at a time* 🍄🧠
