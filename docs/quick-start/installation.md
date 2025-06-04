# Installation

## Prerequisites

- **Python 3.8+** with pip
- **OpenAI API key** (or compatible LLM service)
- **Java 17 or 21** (if using Neo4j graph database)

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r scripts/requirements.txt
```

### 2. Create Configuration

```bash
# Copy the example configuration
cp examples/config_example.json config.json

# Set your API key
export OPENAI_API_KEY="your-openai-api-key-here"
```

### 3. Update Configuration

Edit `config.json` and set:
- `obsidian.vault_path`: Path to your Obsidian vault or output directory
- Any other preferences (see Configuration Reference for details)

## Verify Installation

```bash
# Test your setup with a dry run
python scripts/main_etl.py \
  --source examples/sample_data/mycomind_project.txt \
  --schema schemas/example_schemas/personal_knowledge.json \
  --config config.json \
  --dry-run
```

## Next Steps

- [First Extraction](first-extraction.md) - Extract your first entities
- [Configuration Basics](configuration-basics.md) - Essential configuration options
- [Troubleshooting](../user-guides/troubleshooting.md) - Common issues and solutions