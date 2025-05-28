# ETL Process Guide

## Overview

The ETL (Extract, Transform, Load) process is the core of MycoMind's knowledge extraction pipeline. It takes unstructured input data, applies ontology-driven transformation using LLMs, and loads the results into structured Obsidian notes.

## Process Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EXTRACT   │───▶│ TRANSFORM   │───▶│    LOAD     │───▶│   VERIFY    │
│             │    │             │    │             │    │             │
│ • Read data │    │ • LLM call  │    │ • Generate  │    │ • Validate  │
│ • Parse     │    │ • Parse     │    │   Markdown  │    │ • Error     │
│ • Validate  │    │ • Structure │    │ • Save file │    │   handling  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

## Extract Phase

### Data Source Types

#### Text Documents
- **Markdown files**: Direct processing of existing notes
- **PDF documents**: Text extraction with metadata preservation
- **Word documents**: Content extraction with formatting awareness
- **Plain text**: Simple text processing

#### Web Sources
- **URLs**: Web page content extraction
- **RSS feeds**: Automated content ingestion
- **APIs**: Structured data from external services

#### Structured Data
- **JSON/YAML**: Configuration and metadata files
- **CSV**: Tabular data processing
- **Database exports**: Bulk data processing

### Input Preprocessing

#### Text Cleaning
```python
def preprocess_text(text: str) -> str:
    """Clean and normalize input text for processing."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    
    # Remove or replace problematic characters
    text = text.replace('\x00', '')  # Remove null bytes
    
    # Preserve important formatting markers
    text = preserve_markdown_structure(text)
    
    return text.strip()
```

#### Content Segmentation
- **Chunk size optimization**: Balance context vs. processing efficiency
- **Semantic boundaries**: Respect paragraph and section breaks
- **Overlap handling**: Maintain context across chunks

#### Metadata Extraction
```python
def extract_metadata(source: str) -> Dict[str, Any]:
    """Extract metadata from various source types."""
    metadata = {
        'source_type': detect_source_type(source),
        'created_date': get_creation_date(source),
        'file_size': get_file_size(source),
        'encoding': detect_encoding(source)
    }
    
    # Source-specific metadata
    if metadata['source_type'] == 'pdf':
        metadata.update(extract_pdf_metadata(source))
    elif metadata['source_type'] == 'web':
        metadata.update(extract_web_metadata(source))
    
    return metadata
```

## Transform Phase

### LLM Prompt Engineering

#### Base Prompt Template
```python
EXTRACTION_PROMPT = """
You are an expert knowledge extraction system. Your task is to analyze the provided text and extract structured information according to the given schema.

SCHEMA:
{schema_definition}

EXTRACTION RULES:
1. Extract only information explicitly present in the text
2. Use exact entity names when creating WikiLinks: [[Entity Name]]
3. Maintain consistency in entity naming across extractions
4. Include confidence scores for uncertain extractions
5. Preserve important context and relationships

INPUT TEXT:
{input_text}

OUTPUT FORMAT:
Return a JSON object with the following structure:
{{
  "entities": [
    {{
      "type": "EntityType",
      "properties": {{...}},
      "relationships": {{...}},
      "confidence": 0.95,
      "source_context": "relevant text snippet"
    }}
  ],
  "metadata": {{
    "extraction_date": "2024-01-15T10:30:00Z",
    "schema_version": "1.0.0",
    "processing_notes": "any relevant notes"
  }}
}}
"""
```

#### Schema-Specific Prompts
```python
def build_schema_prompt(schema: Dict[str, Any]) -> str:
    """Build schema-specific extraction instructions."""
    prompt_parts = []
    
    for entity_type, definition in schema['entities'].items():
        prompt_parts.append(f"\n{entity_type}:")
        prompt_parts.append(f"  Description: {definition.get('description', '')}")
        
        # Properties
        if 'properties' in definition:
            prompt_parts.append("  Properties:")
            for prop, prop_def in definition['properties'].items():
                required = " (REQUIRED)" if prop_def.get('required') else ""
                prompt_parts.append(f"    - {prop}: {prop_def.get('description', '')}{required}")
        
        # Relationships
        if 'relationships' in definition:
            prompt_parts.append("  Relationships:")
            for rel, rel_def in definition['relationships'].items():
                target = rel_def.get('target', 'Unknown')
                prompt_parts.append(f"    - {rel} → {target}: {rel_def.get('description', '')}")
    
    return "\n".join(prompt_parts)
```

### LLM Response Processing

#### Response Validation
```python
def validate_llm_response(response: str, schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate LLM response against schema requirements."""
    errors = []
    
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    
    # Validate structure
    if 'entities' not in data:
        errors.append("Missing 'entities' field")
    
    # Validate entities
    for entity in data.get('entities', []):
        entity_errors = validate_entity(entity, schema)
        errors.extend(entity_errors)
    
    return len(errors) == 0, errors
```

#### Entity Resolution
```python
def resolve_entities(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Resolve entity references and create consistent naming."""
    entity_map = {}
    resolved_entities = []
    
    # First pass: collect all entity names
    for entity in entities:
        name = entity['properties'].get('name', '')
        canonical_name = normalize_entity_name(name)
        entity_map[name] = canonical_name
    
    # Second pass: update references
    for entity in entities:
        resolved_entity = resolve_entity_references(entity, entity_map)
        resolved_entities.append(resolved_entity)
    
    return resolved_entities
```

### Relationship Processing

#### WikiLink Generation
```python
def generate_wikilinks(entity: Dict[str, Any]) -> Dict[str, Any]:
    """Convert relationship references to WikiLinks."""
    if 'relationships' not in entity:
        return entity
    
    for rel_type, targets in entity['relationships'].items():
        if isinstance(targets, list):
            entity['relationships'][rel_type] = [f"[[{target}]]" for target in targets]
        elif isinstance(targets, str):
            entity['relationships'][rel_type] = f"[[{targets}]]"
    
    return entity
```

#### Relationship Validation
```python
def validate_relationships(entities: List[Dict[str, Any]], schema: Dict[str, Any]) -> List[str]:
    """Validate that relationships conform to schema definitions."""
    errors = []
    entity_names = {e['properties'].get('name') for e in entities}
    
    for entity in entities:
        entity_type = entity.get('type')
        if entity_type not in schema['entities']:
            continue
        
        allowed_relationships = schema['entities'][entity_type].get('relationships', {})
        
        for rel_type, targets in entity.get('relationships', {}).items():
            if rel_type not in allowed_relationships:
                errors.append(f"Invalid relationship '{rel_type}' for {entity_type}")
                continue
            
            # Validate target types
            expected_target_type = allowed_relationships[rel_type].get('target')
            # Additional validation logic here...
    
    return errors
```

## Load Phase

### Obsidian Note Generation

#### YAML Frontmatter Creation
```python
def create_frontmatter(entity: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """Generate YAML frontmatter for Obsidian note."""
    frontmatter = {
        'type': entity.get('type'),
        'created': datetime.now().isoformat(),
        'source': metadata.get('source_file'),
        'schema_version': metadata.get('schema_version')
    }
    
    # Add entity properties
    frontmatter.update(entity.get('properties', {}))
    
    # Add relationships
    if 'relationships' in entity:
        frontmatter.update(entity['relationships'])
    
    # Add extraction metadata
    if 'confidence' in entity:
        frontmatter['extraction_confidence'] = entity['confidence']
    
    return yaml.dump(frontmatter, default_flow_style=False)
```

#### Content Generation
```python
def generate_note_content(entity: Dict[str, Any], metadata: Dict[str, Any]) -> str:
    """Generate the main content of the Obsidian note."""
    content_parts = []
    
    # Title
    name = entity['properties'].get('name', 'Unnamed Entity')
    content_parts.append(f"# {name}")
    
    # Description
    if 'description' in entity['properties']:
        content_parts.append(f"\n{entity['properties']['description']}")
    
    # Source context
    if 'source_context' in entity:
        content_parts.append(f"\n## Source Context\n\n> {entity['source_context']}")
    
    # Relationships section
    if 'relationships' in entity:
        content_parts.append("\n## Relationships")
        for rel_type, targets in entity['relationships'].items():
            if isinstance(targets, list):
                target_list = ", ".join(targets)
            else:
                target_list = targets
            content_parts.append(f"- **{rel_type.title()}**: {target_list}")
    
    # Metadata section
    content_parts.append(f"\n## Metadata")
    content_parts.append(f"- **Extracted**: {metadata.get('extraction_date', 'Unknown')}")
    content_parts.append(f"- **Source**: {metadata.get('source_file', 'Unknown')}")
    
    return "\n".join(content_parts)
```

#### File Organization
```python
def organize_output_files(entities: List[Dict[str, Any]], config: Dict[str, Any]) -> Dict[str, str]:
    """Organize output files according to configuration."""
    file_paths = {}
    base_path = config['obsidian']['vault_path']
    notes_folder = config['obsidian']['notes_folder']
    
    for entity in entities:
        entity_type = entity.get('type', 'Unknown')
        entity_name = entity['properties'].get('name', 'Unnamed')
        
        # Create type-based subdirectories
        type_folder = os.path.join(base_path, notes_folder, entity_type.lower())
        os.makedirs(type_folder, exist_ok=True)
        
        # Generate safe filename
        safe_name = sanitize_filename(entity_name)
        file_path = os.path.join(type_folder, f"{safe_name}.md")
        
        # Handle name conflicts
        counter = 1
        while os.path.exists(file_path):
            file_path = os.path.join(type_folder, f"{safe_name}_{counter}.md")
            counter += 1
        
        file_paths[entity_name] = file_path
    
    return file_paths
```

## Error Handling and Recovery

### Retry Mechanisms
```python
def process_with_retry(
    data: str, 
    schema: Dict[str, Any], 
    max_retries: int = 3
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """Process data with retry logic for failed extractions."""
    
    for attempt in range(max_retries):
        try:
            # Attempt processing
            result = extract_entities(data, schema)
            
            # Validate result
            is_valid, errors = validate_extraction_result(result, schema)
            
            if is_valid:
                return True, result, []
            else:
                # Log validation errors
                logger.warning(f"Attempt {attempt + 1} failed validation: {errors}")
                
                # Modify prompt for retry
                if attempt < max_retries - 1:
                    schema = adjust_schema_for_retry(schema, errors)
        
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with exception: {e}")
            
            if attempt == max_retries - 1:
                return False, {}, [str(e)]
    
    return False, {}, ["Max retries exceeded"]
```

### Partial Success Handling
```python
def handle_partial_extraction(
    entities: List[Dict[str, Any]], 
    errors: List[str]
) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Handle cases where some entities are successfully extracted."""
    
    valid_entities = []
    warnings = []
    
    for entity in entities:
        try:
            # Validate individual entity
            if validate_single_entity(entity):
                valid_entities.append(entity)
            else:
                warnings.append(f"Skipped invalid entity: {entity.get('properties', {}).get('name', 'Unknown')}")
        except Exception as e:
            warnings.append(f"Error processing entity: {e}")
    
    return valid_entities, warnings
```

## Performance Optimization

### Batch Processing
```python
def process_in_batches(
    data_items: List[str], 
    schema: Dict[str, Any], 
    batch_size: int = 5
) -> List[Dict[str, Any]]:
    """Process multiple data items in batches for efficiency."""
    
    all_results = []
    
    for i in range(0, len(data_items), batch_size):
        batch = data_items[i:i + batch_size]
        
        # Combine batch items for single LLM call
        combined_input = "\n\n---DOCUMENT SEPARATOR---\n\n".join(batch)
        
        # Process batch
        batch_result = extract_entities(combined_input, schema)
        
        # Split results back to individual items
        individual_results = split_batch_results(batch_result, len(batch))
        all_results.extend(individual_results)
    
    return all_results
```

### Caching Strategy
```python
def get_cached_result(input_hash: str, schema_hash: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached extraction result if available."""
    cache_key = f"{input_hash}:{schema_hash}"
    return cache.get(cache_key)

def cache_result(input_hash: str, schema_hash: str, result: Dict[str, Any]) -> None:
    """Cache extraction result for future use."""
    cache_key = f"{input_hash}:{schema_hash}"
    cache.set(cache_key, result, ttl=3600)  # 1 hour TTL
```

## Quality Assurance

### Validation Checkpoints
1. **Input validation**: Verify data format and schema compatibility
2. **Processing validation**: Check LLM response format and content
3. **Output validation**: Ensure generated files are valid Markdown
4. **Relationship validation**: Verify entity links are resolvable

### Quality Metrics
```python
def calculate_quality_metrics(
    entities: List[Dict[str, Any]], 
    source_text: str
) -> Dict[str, float]:
    """Calculate quality metrics for extracted entities."""
    
    metrics = {
        'entity_count': len(entities),
        'avg_confidence': sum(e.get('confidence', 0) for e in entities) / len(entities),
        'relationship_density': calculate_relationship_density(entities),
        'coverage_ratio': calculate_text_coverage(entities, source_text)
    }
    
    return metrics
```

This comprehensive ETL process ensures reliable, high-quality knowledge extraction while maintaining flexibility for different data sources and use cases.
