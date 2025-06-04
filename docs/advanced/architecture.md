# MycoMind Architecture

## Overview

MycoMind is designed as a modular, extensible system for ontology-driven knowledge extraction. The architecture follows a clear separation of concerns, making it easy to understand, maintain, and extend.

## System Components

### Core Modules

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  config_manager │    │  schema_parser  │    │ obsidian_utils  │
│                 │    │                 │    │                 │
│ • Load config   │    │ • Parse JSON-LD │    │ • Generate MD   │
│ • Validate      │    │ • Validate      │    │ • YAML front    │
│ • Environment   │    │ • Extract types │    │ • WikiLinks     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │    main_etl     │
                    │                 │
                    │ • Orchestrate   │
                    │ • LLM calls     │
                    │ • Data flow     │
                    │ • Error handle  │
                    └─────────────────┘
```

### Data Flow Architecture

```
Input Sources → Schema Definition → LLM Processing → Structured Output → Obsidian Notes
     │               │                    │               │              │
     │               │                    │               │              │
  Raw text,       JSON-LD           Entity extraction,  YAML + content   Markdown files
  documents,      ontology          relationship         with semantic    with WikiLinks
  APIs, etc.      specification     identification       structure        and metadata
```

## Design Principles

### 1. Modularity
Each component has a single responsibility and can be tested/modified independently:
- **config_manager**: Configuration and environment management
- **schema_parser**: Ontology definition and validation
- **obsidian_utils**: Output formatting and file generation
- **main_etl**: Orchestration and LLM interaction

### 2. Extensibility
The system is designed to accommodate future enhancements:
- Plugin architecture for new data sources
- Configurable LLM providers
- Multiple output formats beyond Obsidian
- Advanced semantic linking strategies

### 3. Configuration-Driven
All behavior is controlled through configuration files:
- No hard-coded paths or API endpoints
- Environment-specific settings
- Schema-driven processing rules
- Flexible output formatting

## Component Details

### Configuration Manager (`config_manager.py`)

**Purpose**: Centralized configuration handling with validation and environment management.

**Key Functions**:
- Load and validate configuration files
- Manage environment variables and secrets
- Provide configuration access to other modules
- Handle configuration inheritance and overrides

**Configuration Schema**:
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key_env": "OPENAI_API_KEY"
  },
  "obsidian": {
    "vault_path": "/path/to/vault",
    "notes_folder": "extracted_knowledge"
  },
  "processing": {
    "batch_size": 10,
    "max_retries": 3
  }
}
```

### Schema Parser (`schema_parser.py`)

**Purpose**: Parse and validate JSON-LD schemas that define the knowledge structure.

**Key Functions**:
- Load JSON-LD schema files
- Validate schema syntax and semantics
- Extract entity types and relationship definitions
- Provide schema information to the ETL process

**Schema Structure**:
```json
{
  "@context": "https://schema.org/",
  "@type": "Schema",
  "entities": {
    "Person": {
      "properties": ["name", "email", "organization"],
      "relationships": ["knows", "worksFor"]
    },
    "Organization": {
      "properties": ["name", "industry", "location"],
      "relationships": ["employs", "partnerWith"]
    }
  }
}
```

### Obsidian Utils (`obsidian_utils.py`)

**Purpose**: Generate Obsidian-compatible Markdown files with proper formatting and linking.

**Key Functions**:
- Create YAML frontmatter with extracted metadata
- Format content with proper Markdown structure
- Generate `[[WikiLinks]]` for entity relationships
- Handle file naming and organization

**Output Format**:
```markdown
---
type: Person
name: "John Doe"
organization: "[[Acme Corp]]"
tags: ["person", "engineering"]
created: 2024-01-15
---

# John Doe

John is a software engineer at [[Acme Corp]] who specializes in...

## Relationships
- Works for: [[Acme Corp]]
- Knows: [[Jane Smith]], [[Bob Johnson]]
```

### Main ETL (`main_etl.py`)

**Purpose**: Orchestrate the entire extraction, transformation, and loading process.

**Key Functions**:
- Coordinate all system components
- Manage LLM interactions and prompt engineering
- Handle data processing pipelines
- Implement error handling and retry logic
- Provide progress tracking and logging

**Processing Pipeline**:
1. Load configuration and schema
2. Prepare input data
3. Construct LLM prompts with schema context
4. Process data through LLM
5. Parse and validate LLM responses
6. Generate Obsidian notes
7. Handle errors and retries

## Future Architecture Considerations

### Meta-Knowledge Graph Generation

A future `build_project_kg.py` module will:
- Parse Python AST to extract code structure
- Analyze Markdown documentation
- Map relationships between code and docs
- Generate Cypher scripts for Neo4j import

### Advanced Semantic Linking

Evolution from current one-step LLM approach to two-step process:
1. **Entity Extraction**: Identify entities in text
2. **Entity Resolution**: Link entities to existing knowledge base

### Plugin Architecture

Future plugin system will support:
- Custom data source connectors
- Alternative LLM providers
- Different output formats
- Custom processing steps

## Error Handling Strategy

### Graceful Degradation
- Continue processing when individual items fail
- Provide detailed error logs for debugging
- Implement configurable retry mechanisms

### Validation Layers
- Configuration validation at startup
- Schema validation before processing
- Output validation before file creation
- LLM response validation with fallbacks

## Performance Considerations

### Batch Processing
- Process multiple items in single LLM calls
- Implement configurable batch sizes
- Balance throughput vs. memory usage

### Caching Strategy
- Cache LLM responses for identical inputs
- Store processed schemas for reuse
- Implement configurable cache expiration

### Monitoring and Logging
- Structured logging for all operations
- Performance metrics collection
- Error rate tracking and alerting

This architecture provides a solid foundation for the current system while maintaining flexibility for future enhancements and the eventual integration of the meta-knowledge graph capabilities.
