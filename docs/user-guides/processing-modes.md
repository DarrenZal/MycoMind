# Processing Modes

MycoMind offers two distinct processing modes to handle different knowledge extraction workflows.

## Standard Mode: Extract Entities to New Notes

Creates new structured notes for each extracted entity, organized in a dedicated folder.

### How It Works
1. Analyzes source documents using AI
2. Extracts entities according to your schema
3. Creates new markdown files with YAML frontmatter
4. Organizes files by entity type or other criteria

### Usage
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

### Output Structure
```
your_vault/
└── mycomind_extracted/
    ├── Person/
    │   ├── John_Smith.md
    │   └── Jane_Doe.md
    ├── Organization/
    │   └── Acme_Corp.md
    └── Concept/
        └── Machine_Learning.md
```

### When to Use
- Building a new knowledge base from scratch
- Extracting entities for classification and analysis
- Creating reference materials from unstructured content
- Building entity-centric knowledge systems

## File-as-Entity Mode: Enhance Original Files

Updates your original files with rich YAML frontmatter while preserving the original content.

### How It Works
1. Treats each file as an entity of a specific type
2. Extracts properties and relationships from file content
3. Adds structured YAML frontmatter to the original file
4. Preserves all original content below the frontmatter

### Usage
```bash
# Specify entity type explicitly
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/hyphaltips_schema.json \
  --source /path/to/files \
  --file-as-entity HyphalTip

# Auto-detect entity type from schema
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source /path/to/files \
  --file-as-entity
```

### Output Example
**Before** (`project_notes.md`):
```markdown
# MycoMind Project

This is a personal knowledge management system...
```

**After** (`mycomind_processed/project_notes.md`):
```markdown
---
name: MycoMind Project
type: HyphalTip
description: Personal knowledge management system using AI and graph databases
activityStatus: alive
collaborators:
  - "[[Shawn]]"
tags:
  - AI
  - knowledge-management
  - graph-database
extraction_metadata:
  confidence: 0.95
  source: project_notes.md
  extracted_at: 2024-01-15T10:30:00Z
---

# MycoMind Project

This is a personal knowledge management system...
```

### When to Use
- Enhancing existing note collections (Obsidian vaults, etc.)
- Adding metadata to project documentation
- Structuring personal knowledge bases
- Converting unstructured files to knowledge graph entities

## Comparison

| Aspect | Standard Mode | File-as-Entity Mode |
|--------|---------------|-------------------|
| **Output** | New entity files | Enhanced original files |
| **Organization** | By entity type | Preserves source structure |
| **Content** | Entity-focused | Original content + metadata |
| **Use Case** | New knowledge base | Enhance existing files |
| **File Count** | May create many files | One-to-one with source |

## Configuration Options

### Output Folder Structure

**Standard Mode:**
```json
{
  "obsidian": {
    "notes_folder": "extracted_knowledge",
    "folder_structure": "by_type"
  }
}
```

**File-as-Entity Mode:**
```json
{
  "obsidian": {
    "notes_folder": "mycomind_processed",
    "folder_structure": "flat"
  }
}
```

### Filename Templates

**Standard Mode:**
```json
{
  "obsidian": {
    "filename_template": "{name}"
  }
}
```

**File-as-Entity Mode:**
```json
{
  "obsidian": {
    "filename_template": "{source_filename}",
    "preserve_extension": true
  }
}
```

## Advanced Options

### Batch Processing
```bash
# Process multiple directories
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source /path/to/docs1 \
  --source /path/to/docs2 \
  --source /path/to/docs3
```

### Quality Control
```bash
# Only process high-confidence extractions
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source documents/ \
  --min-confidence 0.8
```

### Selective Processing
```bash
# Only extract specific entity types
python scripts/main_etl.py \
  --config config.json \
  --schema schemas/your_schema.json \
  --source documents/ \
  --entity-types Person,Organization
```

## Best Practices

### Standard Mode
- Use clear, descriptive entity names in your schema
- Organize output by entity type for easier navigation
- Consider using consistent naming conventions
- Review extracted entities for quality before graph conversion

### File-as-Entity Mode
- Ensure your schema matches the content type of your files
- Backup original files before processing
- Use descriptive file names that will become entity names
- Validate YAML frontmatter syntax after processing

### Both Modes
- Start with small test batches to verify configuration
- Use appropriate schemas for your content domain
- Monitor extraction quality and adjust prompts if needed
- Regular backup your processed results