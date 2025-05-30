# Getting Started with MycoMind

Welcome to MycoMind! This guide will help you get up and running with the Personal Knowledge Management system for ontology-driven knowledge extraction.

## Quick Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt
```

### 2. Set Up Configuration

```bash
# Copy the example configuration
cp examples/config_example.json config.json

# Edit the configuration file
# - Set your OpenAI API key in environment variable: OPENAI_API_KEY
# - Update the obsidian.vault_path to point to your Obsidian vault
```

### 3. Set Environment Variables

```bash
# Add to your shell profile (.bashrc, .zshrc, etc.)
export OPENAI_API_KEY="your-openai-api-key-here"
```

## Basic Usage

### Extract Knowledge from a Document

```bash
# Run the ETL pipeline on the sample document
python scripts/main_etl.py \
  --source examples/sample_data/sample_document.txt \
  --schema schemas/example_schemas/personal_knowledge.json \
  --config config.json
```

### Validate Your Configuration

```bash
# Test your configuration without processing
python scripts/main_etl.py \
  --source examples/sample_data/sample_document.txt \
  --schema schemas/example_schemas/personal_knowledge.json \
  --config config.json \
  --dry-run
```

### Create a Custom Schema

```bash
# Generate an example schema to start from
python scripts/schema_parser.py create-example my_schema.json

# Validate your schema
python scripts/schema_parser.py validate my_schema.json
```

## Project Structure Overview

```
MycoMind/
├── README.md                    # Main project documentation
├── GETTING_STARTED.md          # This file
├── config.json                 # Your configuration (create from example)
├── docs/                       # Detailed documentation
├── scripts/                    # Core Python modules
├── schemas/                    # JSON-LD schema definitions
├── examples/                   # Example configurations and data
└── project_knowledge_graph/    # Advanced: Project's own knowledge graph
```

## Key Files to Know

- **`scripts/main_etl.py`**: Main entry point for knowledge extraction
- **`config.json`**: Your system configuration (create from `examples/config_example.json`)
- **`schemas/example_schemas/personal_knowledge.json`**: Example schema for personal knowledge
- **`examples/sample_data/sample_document.txt`**: Sample document for testing

## Processing Modes

### Standard Mode: Extract Entities to New Notes
Creates new structured notes for each extracted entity:

```bash
# Process a single file
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source document.md

# Process a directory of files
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source /path/to/documents/
```

**Output**: Creates new notes in `/your/vault/mycomind_extracted/` organized by entity type.

### File-as-Entity Mode: Enhance Original Files
Updates your original files with rich YAML frontmatter while preserving content:

```bash
# Process HyphalTips (or any entity type)
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/hyphaltips_schema.json \
  --source /path/to/files \
  --file-as-entity HyphalTip

# Auto-detect entity type
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source /path/to/files \
  --file-as-entity
```

**Output**: Creates enhanced versions in `/your/vault/mycomind_processed/` with:
- Rich YAML frontmatter with extracted properties
- Relationship links as `[[WikiLinks]]`
- Extraction metadata and confidence scores
- Original content preserved

## Common Use Cases

### 1. Extract from Meeting Notes
```bash
python scripts/main_etl.py \
  --source path/to/meeting_notes.md \
  --schema schemas/example_schemas/personal_knowledge.json
```

### 2. Process Research Papers
```bash
python scripts/main_etl.py \
  --source path/to/research_paper.pdf \
  --schema schemas/example_schemas/personal_knowledge.json
```

### 3. Extract from Web Articles
```bash
python scripts/main_etl.py \
  --source "https://example.com/article" \
  --schema schemas/example_schemas/personal_knowledge.json
```

## Configuration Tips

### LLM Providers
- **OpenAI**: Set `llm.provider` to `"openai"` and `OPENAI_API_KEY` environment variable
- **Anthropic**: Set `llm.provider` to `"anthropic"` and `ANTHROPIC_API_KEY` environment variable
- **Custom**: Set `llm.provider` to `"custom"` and configure `llm.base_url`

### Obsidian Integration
- Set `obsidian.vault_path` to your Obsidian vault directory
- Choose folder structure: `"flat"`, `"by_type"`, `"by_date"`, or `"custom"`
- Customize filename templates with variables like `{name}`, `{type}`, `{date}`

### Processing Options
- Adjust `processing.batch_size` based on your LLM rate limits
- Enable `processing.enable_caching` to avoid reprocessing the same content
- Set `processing.quality_threshold` to filter low-confidence extractions

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   # Check if environment variable is set
   echo $OPENAI_API_KEY
   
   # Set it temporarily
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Obsidian Vault Path Issues**
   ```bash
   # Verify the path exists
   ls -la "/path/to/your/obsidian/vault"
   
   # Update config.json with correct path
   ```

3. **Schema Validation Errors**
   ```bash
   # Validate your schema
   python scripts/schema_parser.py validate path/to/schema.json
   ```

### Getting Help

1. **Check the logs**: Look in `logs/mycomind.log` for detailed error messages
2. **Use verbose mode**: Add `--verbose` to see detailed processing information
3. **Validate components**: Use `--dry-run` to test configuration without processing

## Next Steps

1. **Read the Documentation**: Explore the `/docs` folder for detailed guides
2. **Customize Your Schema**: Create schemas tailored to your specific domain
3. **Explore Advanced Features**: Learn about the project knowledge graph in `/project_knowledge_graph`
4. **Join the Community**: Contribute to the project and share your use cases

## Advanced: Project Knowledge Graph

For power users, MycoMind includes its own knowledge graph that documents the project structure:

1. **Install Neo4j**: Download from [neo4j.com](https://neo4j.com/download/)
2. **Load the Graph**: Import `project_knowledge_graph/mycomind_kg.cypher`
3. **Explore**: Use queries from `project_knowledge_graph/example_queries.cypher`

See `docs/Querying_Project_KG.md` for detailed instructions.

---

Happy knowledge extracting! 🍄🧠
