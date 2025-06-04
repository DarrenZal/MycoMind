# API Reference

## Core Processing Scripts

### main_etl.py

The primary entry point for knowledge extraction.

```bash
python scripts/main_etl.py [OPTIONS]
```

#### Options

| Option | Description | Required | Example |
|--------|-------------|----------|---------|
| `--config` | Path to configuration file | Yes | `config.json` |
| `--schema` | Path to JSON-LD schema file | Yes | `schemas/personal_knowledge.json` |
| `--source` | Source file or directory | Yes | `document.md` or `/path/to/docs/` |
| `--file-as-entity` | Treat files as entities of specified type | No | `HyphalTip` |
| `--no-index` | Skip indexing after extraction | No | |
| `--dry-run` | Validate configuration without processing | No | |
| `--verbose` | Enable verbose logging | No | |
| `--batch-size` | Override batch size from config | No | `5` |
| `--quality-threshold` | Override quality threshold | No | `0.8` |

#### Examples

```bash
# Basic extraction
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/personal_knowledge.json \
  --source document.md

# File-as-entity mode
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/hyphaltips_schema.json \
  --source /path/to/files \
  --file-as-entity HyphalTip

# Batch processing with custom settings
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/research_schema.json \
  --source /path/to/research_papers/ \
  --batch-size 10 \
  --quality-threshold 0.9
```

### schema_parser.py

Schema validation and management utilities.

```bash
python scripts/schema_parser.py [COMMAND] [OPTIONS]
```

#### Commands

##### validate
Validate a JSON-LD schema file.

```bash
python scripts/schema_parser.py validate schemas/your_schema.json
```

##### create-example
Generate an example schema template.

```bash
python scripts/schema_parser.py create-example my_new_schema.json
```

Options:
- `--entity-types`: Comma-separated list of entity types
- `--include-examples`: Include example entities

##### convert
Convert between schema formats.

```bash
python scripts/schema_parser.py convert \
  --input old_schema.json \
  --output new_schema.json \
  --format jsonld
```

### Graph Database Converters

#### yaml_to_neo4j_converter.py

Convert YAML frontmatter to Neo4j Cypher statements.

```bash
python scripts/yaml_to_neo4j_converter.py [OPTIONS]
```

Options:
- `--schema`: Schema file for context resolution
- `--input`: Directory containing markdown files with YAML frontmatter
- `--output`: Output Cypher file
- `--create-indexes`: Generate index creation statements

```bash
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_schema.json \
  --input vault/extracted_knowledge \
  --output knowledge_graph.cypher \
  --create-indexes
```

#### yaml_to_jsonld_converter.py

Convert YAML frontmatter to JSON-LD for RDF/SPARQL systems.

```bash
python scripts/yaml_to_jsonld_converter.py [OPTIONS]
```

Options:
- `--schema`: Schema file for context resolution
- `--input`: Directory containing markdown files
- `--output`: Output JSON-LD file
- `--format`: Output format (`jsonld`, `turtle`, `n3`)

```bash
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/research_schema.json \
  --input vault/extracted_knowledge \
  --output knowledge_graph.jsonld \
  --format jsonld
```

## Database Management Scripts

### setup_neo4j.py

Neo4j installation and management.

```bash
python scripts/setup_neo4j.py [OPTIONS]
```

#### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--download` | Download and install Neo4j | |
| `--start` | Start Neo4j server | |
| `--stop` | Stop Neo4j server | |
| `--restart` | Restart Neo4j server | |
| `--status` | Check server status | |
| `--logs` | View recent logs | |
| `--install-dir` | Installation directory | `scripts/neo4j` |
| `--version` | Neo4j version to install | `5.15.0` |

#### Examples

```bash
# Complete setup
python scripts/setup_neo4j.py --download --start

# Management
python scripts/setup_neo4j.py --status
python scripts/setup_neo4j.py --restart
python scripts/setup_neo4j.py --logs
```

### setup_fuseki.py

Apache Jena Fuseki installation and management.

```bash
python scripts/setup_fuseki.py [OPTIONS]
```

#### Options

| Option | Description | Example |
|--------|-------------|---------|
| `--download` | Download and install Fuseki | |
| `--start` | Start Fuseki server | |
| `--stop` | Stop Fuseki server | |
| `--status` | Check server status | |
| `--port` | Server port | `3030` |
| `--install-dir` | Installation directory | `fuseki/` |

#### Examples

```bash
# Setup and start
python scripts/setup_fuseki.py --download
python scripts/setup_fuseki.py --start --port 3030

# Management
python scripts/setup_fuseki.py --status
python scripts/setup_fuseki.py --stop
```

### graph_db_client.py

Generic graph database client for Fuseki operations.

```bash
python scripts/graph_db_client.py [COMMAND] [OPTIONS]
```

#### Commands

##### create-dataset
Create a new dataset in Fuseki.

```bash
python scripts/graph_db_client.py create-dataset \
  --name mycomind \
  --endpoint http://localhost:3030
```

##### load
Load RDF data into Fuseki dataset.

```bash
python scripts/graph_db_client.py load \
  --file knowledge_graph.jsonld \
  --dataset mycomind \
  --endpoint http://localhost:3030
```

##### query
Execute SPARQL query.

```bash
python scripts/graph_db_client.py query \
  --sparql "SELECT * WHERE { ?s ?p ?o } LIMIT 10" \
  --dataset mycomind
```

##### interactive
Start interactive SPARQL shell.

```bash
python scripts/graph_db_client.py interactive --dataset mycomind
```

## Configuration Management

### config_manager.py

Configuration loading and validation utilities.

#### Functions

```python
from scripts.config_manager import ConfigManager

# Load configuration
config = ConfigManager.load_config('config.json')

# Validate configuration
ConfigManager.validate_config(config)

# Get environment variables
api_key = ConfigManager.get_env_var('OPENAI_API_KEY')

# Merge configurations
merged = ConfigManager.merge_configs(base_config, override_config)
```

## Utility Scripts

### obsidian_utils.py

Obsidian-specific utilities for markdown generation.

#### Functions

```python
from scripts.obsidian_utils import ObsidianUtils

# Generate markdown with YAML frontmatter
markdown = ObsidianUtils.create_markdown_file(
    entity_data=entity,
    template="default",
    include_metadata=True
)

# Create WikiLinks
wikilink = ObsidianUtils.create_wikilink("Entity Name")

# Sanitize filename
filename = ObsidianUtils.sanitize_filename("Entity: Name!")
```

## Return Codes

All scripts use consistent return codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Schema validation error |
| 4 | API/Network error |
| 5 | File system error |

## Environment Variables

### Required
- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key (if using Claude)

### Optional
- `MYCOMIND_CONFIG`: Default configuration file path
- `MYCOMIND_PROFILE`: Configuration profile to use
- `OBSIDIAN_VAULT_PATH`: Override vault path from config
- `MYCOMIND_LOG_LEVEL`: Override logging level (DEBUG, INFO, WARNING, ERROR)

## Python API Usage

### Direct Integration

```python
from scripts.main_etl import MycoMindETL
from scripts.config_manager import ConfigManager

# Load configuration
config = ConfigManager.load_config('config.json')

# Initialize ETL processor
etl = MycoMindETL(config)

# Process documents
results = etl.process_documents(
    source_path='/path/to/documents',
    schema_path='schemas/my_schema.json'
)

# Access extracted entities
for entity in results.entities:
    print(f"Extracted: {entity.name} ({entity.type})")
```

### Custom Processing Pipeline

```python
from scripts.schema_parser import SchemaParser
from scripts.obsidian_utils import ObsidianUtils

# Load and validate schema
schema = SchemaParser.load_schema('schemas/custom_schema.json')
SchemaParser.validate_schema(schema)

# Process custom content
extractor = EntityExtractor(schema, config)
entities = extractor.extract_from_text(text_content)

# Generate output files
for entity in entities:
    markdown = ObsidianUtils.create_markdown_file(entity)
    # Save markdown file...
```

This API reference provides comprehensive documentation for all MycoMind command-line tools and Python modules.