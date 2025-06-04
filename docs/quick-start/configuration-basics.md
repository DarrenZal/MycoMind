# Configuration Basics

## Essential Settings

The main configuration file `config.json` controls all aspects of MycoMind. Here are the key settings to understand:

### LLM Configuration

```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "temperature": 0.1
  }
}
```

**Supported providers**: `openai`, `anthropic`, `custom`

### Output Configuration

```json
{
  "obsidian": {
    "vault_path": "/path/to/your/obsidian/vault",
    "notes_folder": "extracted_knowledge",
    "folder_structure": "by_type",
    "filename_template": "{name}"
  }
}
```

**Folder structures**: `flat`, `by_type`, `by_date`, `by_source`, `custom`

### Processing Options

```json
{
  "processing": {
    "batch_size": 5,
    "enable_caching": true,
    "quality_threshold": 0.7
  }
}
```

## Environment Variables

Store sensitive data in environment variables:

```bash
# Required
export OPENAI_API_KEY="your-key-here"

# Optional alternatives
export ANTHROPIC_API_KEY="your-anthropic-key"
export OBSIDIAN_VAULT_PATH="/path/to/vault"
```

## Configuration Profiles

Create different configs for different use cases:

```bash
# Development with faster/cheaper model
cp config.json config.development.json
# Edit to use gpt-3.5-turbo, smaller batch sizes

# Production with robust settings
cp config.json config.production.json
# Edit for optimized production settings
```

Use specific profiles:

```bash
python scripts/main_etl.py --config config.development.json --source document.md
```

## Common Customizations

### Change Output Location
```json
{
  "obsidian": {
    "vault_path": "./my_knowledge_base",
    "notes_folder": "ai_extracted"
  }
}
```

### Use Different LLM
```json
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key_env": "ANTHROPIC_API_KEY"
  }
}
```

### Adjust Performance
```json
{
  "processing": {
    "batch_size": 10,
    "max_concurrent": 3,
    "chunk_size": 6000
  }
}
```

See [Configuration Reference](../user-guides/configuration-reference.md) for complete options.