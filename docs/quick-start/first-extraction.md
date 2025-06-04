# Your First Knowledge Extraction

## Basic Entity Extraction

Extract entities from the sample document:

```bash
python scripts/main_etl.py \
  --source examples/sample_data/mycomind_project.txt \
  --schema schemas/example_schemas/personal_knowledge.json \
  --config config.json
```

This creates structured markdown files with YAML frontmatter in your configured output directory.

## Processing Modes

### Standard Mode: New Entity Notes
Creates separate notes for each extracted entity:

```bash
# Process a single file
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source document.md

# Process multiple files
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source /path/to/documents/
```

**Output**: New notes in `your_vault/mycomind_extracted/` organized by entity type.

### File-as-Entity Mode: Enhance Original Files
Adds rich YAML frontmatter to existing files:

```bash
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/hyphaltips_schema.json \
  --source /path/to/files \
  --file-as-entity HyphalTip
```

**Output**: Enhanced files in `your_vault/mycomind_processed/` with preserved content.

## Validate Results

Check the generated files in your output directory for:
- YAML frontmatter with extracted properties
- WikiLink relationships (`[[Entity Name]]`)
- Extraction metadata and confidence scores

## Next Steps

- Try different schemas from the `schemas/` directory
- Create custom schemas for your domain
- Set up graph database querying (see Database Backends section)