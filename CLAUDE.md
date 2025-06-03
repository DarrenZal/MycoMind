# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MycoMind is a Personal Knowledge Management (PKM) system that uses ontology-driven knowledge extraction to transform unstructured data into structured knowledge graphs. It combines LLM capabilities with semantic web technologies to create queryable knowledge representations in Obsidian-compatible format.

## Core Architecture

The system follows a modular design with clear separation of concerns:

- **main_etl.py**: Main orchestrator that coordinates all components and manages LLM interactions
- **config_manager.py**: Centralized configuration handling with environment variable management
- **schema_parser.py**: JSON-LD schema handling and validation
- **obsidian_utils.py**: Generates Obsidian-compatible Markdown with YAML frontmatter and WikiLinks
- **yaml_to_jsonld_converter.py**: Converts YAML frontmatter to queryable JSON-LD knowledge graphs

## Development Commands

### Setup
```bash
pip install -r scripts/requirements.txt
cp examples/config_example.json config.json
export OPENAI_API_KEY="your-key-here"
```

### Core Processing
```bash
# Standard entity extraction
python scripts/main_etl.py --config config.json --schema schemas/personal_knowledge.json --source document.md

# File-as-entity mode (enhances existing files)
python scripts/main_etl.py --config config.json --schema schemas/hyphaltips_schema.json --source /path/to/files --file-as-entity HyphalTip

# Generate knowledge graph
python scripts/yaml_to_jsonld_converter.py --schema schemas/hyphaltips_mycomind_schema.json --input /path/to/vault/extracted_knowledge --output mycomind_knowledge_graph.jsonld
```

### Development Server
```bash
python -m http.server  # For web interface at docs/web/
```

## Key Patterns

### Dual Processing Modes
- **Standard mode**: Creates new structured notes in `mycomind_extracted/`
- **File-as-entity mode**: Enhances original files with YAML frontmatter while preserving content

### Configuration-Driven Design
All behavior is controlled through JSON configuration files with support for multiple profiles (default, development, production). Configuration includes LLM settings, Obsidian integration, and processing options.

### Schema-Based Extraction
Uses JSON-LD ontologies to define entity types and relationships. Schemas are located in `/schemas/` and follow semantic web standards with Schema.org vocabulary integration.

### Robust Error Handling
Implements retry mechanisms for LLM calls, graceful degradation for partial successes, and comprehensive logging. LLM temperature is set to 0.0 for deterministic results.

## File Organization

- **Scripts**: Main processing logic in `/scripts/`
- **Schemas**: JSON-LD ontology definitions in `/schemas/`
- **Web Interface**: Browser-based SPARQL querying in `/docs/web/`
- **Examples**: Sample configurations and data in `/examples/`
- **Project KG**: Meta-knowledge system in `/project_knowledge_graph/`

## Important Notes

- Always validate schema changes using `schema_parser.py validate`
- Web interface requires serving via HTTP server to avoid CORS issues
- Configuration supports environment variables for sensitive data like API keys
- The system maintains compatibility with Obsidian vault structure and WikiLink conventions