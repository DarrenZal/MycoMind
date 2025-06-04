# Ontology Design Guide

## Introduction

Ontologies are the foundation of MycoMind's knowledge extraction capabilities. They define the structure, relationships, and semantics of your knowledge domain, enabling the LLM to extract information in a consistent and meaningful way.

## What is an Ontology in MycoMind?

An ontology in MycoMind is a JSON-LD schema that defines:
- **Entity Types**: The kinds of things you want to extract (Person, Organization, Concept, etc.)
- **Properties**: Attributes that describe entities (name, date, description, etc.)
- **Relationships**: How entities connect to each other (knows, worksFor, influences, etc.)
- **Constraints**: Rules about how properties and relationships should be used

## JSON-LD Schema Structure

### Basic Schema Template

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "myco": "https://mycomind.org/schema/"
  },
  "@type": "Schema",
  "name": "Personal Knowledge Schema",
  "description": "Schema for extracting personal and professional knowledge",
  "version": "1.0.0",
  "entities": {
    "Person": {
      "@type": "Class",
      "description": "An individual person",
      "properties": {
        "name": {
          "type": "string",
          "required": true,
          "description": "Full name of the person"
        },
        "email": {
          "type": "string",
          "format": "email",
          "description": "Email address"
        },
        "expertise": {
          "type": "array",
          "items": "string",
          "description": "Areas of expertise or specialization"
        }
      },
      "relationships": {
        "knows": {
          "target": "Person",
          "description": "Personal or professional acquaintance"
        },
        "worksFor": {
          "target": "Organization",
          "description": "Current employment relationship"
        }
      }
    },
    "Organization": {
      "@type": "Class",
      "description": "A company, institution, or group",
      "properties": {
        "name": {
          "type": "string",
          "required": true
        },
        "industry": {
          "type": "string",
          "description": "Primary industry or sector"
        },
        "location": {
          "type": "string",
          "description": "Primary location or headquarters"
        }
      },
      "relationships": {
        "employs": {
          "target": "Person",
          "description": "Employment relationship"
        },
        "partnersWith": {
          "target": "Organization",
          "description": "Business partnership"
        }
      }
    }
  }
}
```

## Design Principles

### 1. Start Simple, Evolve Gradually

Begin with a minimal schema covering your core entities:
- Identify 3-5 primary entity types
- Define essential properties for each
- Add key relationships
- Expand iteratively based on results

### 2. Be Specific but Flexible

**Good**: `expertise: ["machine learning", "natural language processing"]`
**Better**: Use controlled vocabularies when possible, but allow free text for discovery

### 3. Design for Your Use Case

Consider how you'll use the extracted knowledge:
- **Research**: Focus on concepts, sources, and methodologies
- **Professional**: Emphasize people, organizations, and projects
- **Learning**: Highlight topics, resources, and learning paths

## Entity Type Design Patterns

### Core Entity Types

#### Person
```json
"Person": {
  "properties": {
    "name": {"type": "string", "required": true},
    "role": {"type": "string"},
    "expertise": {"type": "array", "items": "string"},
    "contact": {"type": "object"}
  },
  "relationships": {
    "knows": {"target": "Person"},
    "worksFor": {"target": "Organization"},
    "authorOf": {"target": "Document"}
  }
}
```

#### Concept
```json
"Concept": {
  "properties": {
    "name": {"type": "string", "required": true},
    "definition": {"type": "string"},
    "domain": {"type": "string"},
    "complexity": {"type": "string", "enum": ["basic", "intermediate", "advanced"]}
  },
  "relationships": {
    "relatedTo": {"target": "Concept"},
    "prerequisiteFor": {"target": "Concept"},
    "exemplifiedBy": {"target": "Example"}
  }
}
```

#### Project
```json
"Project": {
  "properties": {
    "name": {"type": "string", "required": true},
    "status": {"type": "string", "enum": ["planning", "active", "completed", "archived"]},
    "startDate": {"type": "string", "format": "date"},
    "description": {"type": "string"}
  },
  "relationships": {
    "ledBy": {"target": "Person"},
    "involvedOrganization": {"target": "Organization"},
    "usesConcept": {"target": "Concept"}
  }
}
```

### Domain-Specific Patterns

#### Academic Research
```json
"ResearchPaper": {
  "properties": {
    "title": {"type": "string", "required": true},
    "abstract": {"type": "string"},
    "publicationDate": {"type": "string", "format": "date"},
    "venue": {"type": "string"},
    "doi": {"type": "string"}
  },
  "relationships": {
    "authoredBy": {"target": "Person"},
    "cites": {"target": "ResearchPaper"},
    "addresses": {"target": "ResearchQuestion"}
  }
}
```

#### Business Intelligence
```json
"Market": {
  "properties": {
    "name": {"type": "string", "required": true},
    "size": {"type": "string"},
    "growthRate": {"type": "number"},
    "keyTrends": {"type": "array", "items": "string"}
  },
  "relationships": {
    "serves": {"target": "Organization"},
    "competesWith": {"target": "Market"},
    "influences": {"target": "Product"}
  }
}
```

## Relationship Design

### Relationship Types

#### Hierarchical Relationships
- `partOf` / `contains`
- `parentOf` / `childOf`
- `manages` / `reportsTo`

#### Associative Relationships
- `relatedTo` / `associatedWith`
- `influences` / `influencedBy`
- `collaboratesWith`

#### Temporal Relationships
- `precedes` / `follows`
- `enables` / `requires`
- `evolvedFrom` / `evolvedTo`

### Bidirectional vs. Unidirectional

**Bidirectional** (automatically inferred):
```json
"knows": {
  "target": "Person",
  "bidirectional": true
}
```

**Unidirectional** (explicit direction):
```json
"manages": {
  "target": "Person",
  "inverse": "managedBy"
}
```

## Property Design Best Practices

### Data Types

#### String Properties
```json
"name": {
  "type": "string",
  "required": true,
  "maxLength": 100
}
```

#### Controlled Vocabularies
```json
"priority": {
  "type": "string",
  "enum": ["low", "medium", "high", "critical"]
}
```

#### Structured Data
```json
"contact": {
  "type": "object",
  "properties": {
    "email": {"type": "string", "format": "email"},
    "phone": {"type": "string"},
    "linkedin": {"type": "string", "format": "uri"}
  }
}
```

#### Arrays and Lists
```json
"tags": {
  "type": "array",
  "items": "string",
  "uniqueItems": true
}
```

### Validation Rules

#### Required Fields
```json
"name": {
  "type": "string",
  "required": true,
  "minLength": 1
}
```

#### Format Validation
```json
"email": {
  "type": "string",
  "format": "email"
},
"website": {
  "type": "string",
  "format": "uri"
},
"date": {
  "type": "string",
  "format": "date"
}
```

## Schema Evolution Strategies

### Version Management

```json
{
  "@context": "...",
  "version": "2.1.0",
  "previousVersions": ["1.0.0", "2.0.0"],
  "changelog": {
    "2.1.0": "Added expertise property to Person entity",
    "2.0.0": "Restructured relationship definitions"
  }
}
```

### Backward Compatibility

- Add new optional properties rather than modifying existing ones
- Use property aliases for renamed fields
- Provide migration scripts for major changes

### Incremental Enhancement

1. **Phase 1**: Core entities with basic properties
2. **Phase 2**: Add relationships between entities
3. **Phase 3**: Introduce specialized entity types
4. **Phase 4**: Add complex properties and validation rules

## Common Schema Patterns

### Knowledge Management Schema
```json
{
  "entities": {
    "Note": {
      "properties": {
        "title": {"type": "string", "required": true},
        "content": {"type": "string"},
        "created": {"type": "string", "format": "datetime"},
        "tags": {"type": "array", "items": "string"}
      },
      "relationships": {
        "references": {"target": "Note"},
        "about": {"target": "Concept"}
      }
    },
    "Source": {
      "properties": {
        "title": {"type": "string", "required": true},
        "url": {"type": "string", "format": "uri"},
        "type": {"type": "string", "enum": ["book", "article", "video", "podcast"]}
      },
      "relationships": {
        "citedBy": {"target": "Note"},
        "authoredBy": {"target": "Person"}
      }
    }
  }
}
```

### Project Management Schema
```json
{
  "entities": {
    "Task": {
      "properties": {
        "title": {"type": "string", "required": true},
        "status": {"type": "string", "enum": ["todo", "in-progress", "done"]},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "dueDate": {"type": "string", "format": "date"}
      },
      "relationships": {
        "assignedTo": {"target": "Person"},
        "partOf": {"target": "Project"},
        "dependsOn": {"target": "Task"}
      }
    }
  }
}
```

## Testing and Validation

### Schema Validation Checklist

- [ ] All required properties are defined
- [ ] Relationship targets exist as entity types
- [ ] Property types are valid JSON Schema types
- [ ] Enum values are comprehensive
- [ ] Bidirectional relationships are properly defined

### Testing with Sample Data

Create test documents that exercise your schema:
1. Simple cases with minimal properties
2. Complex cases with multiple relationships
3. Edge cases with unusual data patterns
4. Error cases with invalid data

### Iterative Refinement

1. **Extract** knowledge using your initial schema
2. **Review** the generated notes for quality and completeness
3. **Identify** missing entities, properties, or relationships
4. **Refine** the schema based on findings
5. **Re-extract** and compare results

## Schema Documentation

### Inline Documentation
```json
"Person": {
  "@type": "Class",
  "description": "An individual person in the knowledge domain",
  "examples": [
    "Researchers, colleagues, authors, experts"
  ],
  "usage": "Use for any individual who contributes knowledge or expertise"
}
```

### External Documentation
- Maintain a schema changelog
- Document design decisions and rationale
- Provide examples for each entity type
- Include migration guides for schema updates

This comprehensive approach to ontology design ensures that your MycoMind system can effectively capture and structure the knowledge that matters most to your specific domain and use cases.
