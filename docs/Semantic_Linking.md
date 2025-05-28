# Semantic Linking Guide

## Overview

Semantic linking is the process of creating meaningful connections between entities in your knowledge graph. MycoMind uses a combination of LLM-driven entity recognition and WikiLink formatting to establish these connections, enabling rich navigation and discovery within your Obsidian vault.

## Current Implementation: One-Step LLM Approach

### How It Works

MycoMind currently uses a **single-step approach** where the LLM simultaneously:
1. Extracts entities from the input text
2. Identifies relationships between entities
3. Formats entity references as `[[WikiLinks]]`

This approach is efficient and works well for most use cases, providing immediate semantic linking without requiring a separate entity resolution step.

### LLM Prompt for Semantic Linking

```python
SEMANTIC_LINKING_PROMPT = """
When extracting entities and relationships, follow these linking rules:

1. ENTITY NAMING CONSISTENCY:
   - Use the most complete and formal name for entities
   - Example: "Dr. Jane Smith" not "Jane" or "Smith"
   - For organizations: "Stanford University" not "Stanford"

2. WIKILINK FORMATTING:
   - Format all entity references as [[Entity Name]]
   - Use exact entity names: [[John Doe]], [[Microsoft Corporation]]
   - Maintain consistency across all extractions

3. RELATIONSHIP LINKING:
   - In YAML frontmatter, use WikiLinks for relationship values
   - Example: worksFor: "[[Stanford University]]"
   - For multiple relationships: knows: ["[[Alice Johnson]]", "[[Bob Smith]]"]

4. CROSS-REFERENCE VALIDATION:
   - Ensure all referenced entities are also extracted as primary entities
   - If you reference [[Company X]], also extract Company X as a separate entity
"""
```

### Example Output

```yaml
---
type: Person
name: "Dr. Jane Smith"
role: "Research Scientist"
worksFor: "[[Stanford University]]"
knows: ["[[Dr. Bob Johnson]]", "[[Prof. Alice Chen]]"]
collaboratesOn: ["[[AI Ethics Project]]", "[[Neural Networks Research]]"]
---

# Dr. Jane Smith

Dr. Jane Smith is a research scientist at [[Stanford University]] specializing in artificial intelligence ethics...

## Relationships
- **Works For**: [[Stanford University]]
- **Knows**: [[Dr. Bob Johnson]], [[Prof. Alice Chen]]
- **Collaborates On**: [[AI Ethics Project]], [[Neural Networks Research]]
```

## Entity Resolution Strategies

### Name Normalization

```python
def normalize_entity_name(name: str) -> str:
    """Normalize entity names for consistent linking."""
    # Remove extra whitespace
    name = re.sub(r'\s+', ' ', name.strip())
    
    # Handle common title variations
    name = re.sub(r'\bDr\.?\s+', 'Dr. ', name)
    name = re.sub(r'\bProf\.?\s+', 'Prof. ', name)
    name = re.sub(r'\bMr\.?\s+', 'Mr. ', name)
    name = re.sub(r'\bMs\.?\s+', 'Ms. ', name)
    
    # Handle organization suffixes
    name = re.sub(r'\s+(Inc|Corp|LLC|Ltd)\.?$', r' \1.', name)
    
    return name
```

### Alias Management

```python
def create_entity_aliases(entity: Dict[str, Any]) -> List[str]:
    """Generate common aliases for an entity."""
    aliases = []
    name = entity['properties'].get('name', '')
    
    if entity['type'] == 'Person':
        # Generate name variations
        parts = name.split()
        if len(parts) >= 2:
            # First name + Last name
            aliases.append(f"{parts[0]} {parts[-1]}")
            # Last name only (for common references)
            aliases.append(parts[-1])
            # First name only (for informal references)
            aliases.append(parts[0])
    
    elif entity['type'] == 'Organization':
        # Common abbreviations
        words = name.split()
        if len(words) > 1:
            # Acronym
            acronym = ''.join(word[0].upper() for word in words if word[0].isupper())
            if len(acronym) > 1:
                aliases.append(acronym)
    
    return aliases
```

### Relationship Validation

```python
def validate_semantic_links(entities: List[Dict[str, Any]]) -> List[str]:
    """Validate that all WikiLinks reference existing entities."""
    errors = []
    entity_names = {e['properties'].get('name') for e in entities}
    
    for entity in entities:
        # Check relationships in YAML frontmatter
        for rel_type, targets in entity.get('relationships', {}).items():
            if isinstance(targets, list):
                target_list = targets
            else:
                target_list = [targets]
            
            for target in target_list:
                # Extract entity name from WikiLink
                if target.startswith('[[') and target.endswith(']]'):
                    target_name = target[2:-2]
                    if target_name not in entity_names:
                        errors.append(f"Unresolved link: {target} in {entity['properties'].get('name')}")
    
    return errors
```

## Advanced Linking Strategies

### Contextual Entity Resolution

```python
def resolve_entity_context(
    entity_mention: str, 
    context: str, 
    existing_entities: List[Dict[str, Any]]
) -> Optional[str]:
    """Resolve entity mentions using context clues."""
    
    # Look for exact matches first
    for entity in existing_entities:
        if entity['properties'].get('name') == entity_mention:
            return entity['properties']['name']
    
    # Look for partial matches with context validation
    candidates = []
    for entity in existing_entities:
        entity_name = entity['properties'].get('name', '')
        if entity_mention.lower() in entity_name.lower():
            # Validate using context
            if validate_entity_context(entity, context):
                candidates.append(entity_name)
    
    # Return best match or None
    return candidates[0] if len(candidates) == 1 else None

def validate_entity_context(entity: Dict[str, Any], context: str) -> bool:
    """Validate entity match using contextual information."""
    # Check if entity properties appear in context
    for prop_value in entity['properties'].values():
        if isinstance(prop_value, str) and prop_value.lower() in context.lower():
            return True
    return False
```

### Temporal Relationship Linking

```python
def create_temporal_links(entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create temporal relationships between entities."""
    
    # Sort entities by date if available
    dated_entities = []
    for entity in entities:
        date_fields = ['date', 'created', 'published', 'startDate']
        entity_date = None
        
        for field in date_fields:
            if field in entity['properties']:
                entity_date = parse_date(entity['properties'][field])
                break
        
        if entity_date:
            dated_entities.append((entity, entity_date))
    
    dated_entities.sort(key=lambda x: x[1])
    
    # Create temporal relationships
    for i, (entity, date) in enumerate(dated_entities):
        if 'relationships' not in entity:
            entity['relationships'] = {}
        
        # Link to previous entity
        if i > 0:
            prev_entity = dated_entities[i-1][0]
            if 'precedes' not in entity['relationships']:
                entity['relationships']['precedes'] = []
            entity['relationships']['precedes'].append(f"[[{prev_entity['properties']['name']}]]")
        
        # Link to next entity
        if i < len(dated_entities) - 1:
            next_entity = dated_entities[i+1][0]
            if 'follows' not in entity['relationships']:
                entity['relationships']['follows'] = []
            entity['relationships']['follows'].append(f"[[{next_entity['properties']['name']}]]")
    
    return entities
```

## Future Enhancement: Two-Step Approach

### Planned Architecture

The future two-step approach will separate entity extraction from entity resolution:

#### Step 1: Entity Extraction
```python
def extract_entities_only(text: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract entities without resolving relationships."""
    prompt = f"""
    Extract entities from the text according to the schema.
    Do NOT create relationships or WikiLinks yet.
    Focus only on identifying and extracting entity properties.
    
    Schema: {schema}
    Text: {text}
    """
    # Process with LLM and return raw entities
```

#### Step 2: Entity Resolution and Linking
```python
def resolve_and_link_entities(
    entities: List[Dict[str, Any]], 
    knowledge_base: KnowledgeBase
) -> List[Dict[str, Any]]:
    """Resolve entities against existing knowledge base and create links."""
    
    for entity in entities:
        # Resolve against existing entities
        resolved_entity = knowledge_base.resolve_entity(entity)
        
        # Create relationships
        relationships = identify_relationships(entity, knowledge_base)
        
        # Format as WikiLinks
        entity['relationships'] = format_as_wikilinks(relationships)
    
    return entities
```

### Benefits of Two-Step Approach

1. **Better Entity Resolution**: Can leverage existing knowledge base for disambiguation
2. **Improved Consistency**: Centralized entity resolution ensures consistent naming
3. **Relationship Discovery**: Can identify implicit relationships not mentioned in text
4. **Quality Control**: Separate validation of extraction vs. linking quality

## Link Quality Assessment

### Quality Metrics

```python
def assess_link_quality(entities: List[Dict[str, Any]]) -> Dict[str, float]:
    """Assess the quality of semantic links."""
    
    total_entities = len(entities)
    total_relationships = sum(len(e.get('relationships', {})) for e in entities)
    resolved_links = 0
    unresolved_links = 0
    
    entity_names = {e['properties'].get('name') for e in entities}
    
    for entity in entities:
        for rel_type, targets in entity.get('relationships', {}).items():
            if isinstance(targets, list):
                target_list = targets
            else:
                target_list = [targets]
            
            for target in target_list:
                if target.startswith('[[') and target.endswith(']]'):
                    target_name = target[2:-2]
                    if target_name in entity_names:
                        resolved_links += 1
                    else:
                        unresolved_links += 1
    
    return {
        'entity_count': total_entities,
        'relationship_count': total_relationships,
        'link_resolution_rate': resolved_links / (resolved_links + unresolved_links) if (resolved_links + unresolved_links) > 0 else 0,
        'avg_relationships_per_entity': total_relationships / total_entities if total_entities > 0 else 0
    }
```

### Link Validation Rules

```python
VALIDATION_RULES = {
    'require_bidirectional': True,  # If A knows B, B should know A
    'validate_entity_types': True,  # Person can only work for Organization
    'check_temporal_consistency': True,  # Events should have logical temporal order
    'require_source_evidence': True,  # Links should be supported by source text
}

def validate_link_rules(entities: List[Dict[str, Any]], rules: Dict[str, bool]) -> List[str]:
    """Validate semantic links against quality rules."""
    errors = []
    
    if rules.get('require_bidirectional'):
        errors.extend(check_bidirectional_relationships(entities))
    
    if rules.get('validate_entity_types'):
        errors.extend(check_entity_type_compatibility(entities))
    
    if rules.get('check_temporal_consistency'):
        errors.extend(check_temporal_consistency(entities))
    
    return errors
```

## Best Practices

### Entity Naming
1. **Use full, formal names** for primary entity identification
2. **Maintain consistency** across all extractions
3. **Handle titles and honorifics** consistently
4. **Normalize organization names** with proper suffixes

### Relationship Modeling
1. **Be explicit** about relationship directions
2. **Use schema-defined relationships** whenever possible
3. **Validate relationship targets** exist as entities
4. **Consider temporal aspects** of relationships

### WikiLink Formatting
1. **Always use double brackets**: `[[Entity Name]]`
2. **Use exact entity names** as they appear in the knowledge base
3. **Avoid nested brackets** or special characters
4. **Maintain case sensitivity** for proper nouns

### Quality Assurance
1. **Validate all links** before generating final output
2. **Check for orphaned entities** (entities with no relationships)
3. **Verify bidirectional relationships** where appropriate
4. **Monitor link resolution rates** as a quality metric

This semantic linking approach ensures that your MycoMind knowledge graph maintains high-quality, navigable connections between entities while remaining flexible enough to handle diverse content types and domains.
