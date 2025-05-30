"""
Schema Parser for MycoMind

This module handles parsing and validation of JSON-LD schemas that define
the knowledge structure for entity extraction. It provides utilities for
loading schemas, validating their structure, and extracting entity type
and relationship definitions for use in the ETL process.

Future Enhancement: This module will be analyzed by the future build_project_kg.py
script to automatically generate knowledge graph representations of the schema
definitions and their relationships to the codebase.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from jsonschema import validate, ValidationError
import re

logger = logging.getLogger(__name__)


@dataclass
class SchemaValidationError(Exception):
    """Raised when schema validation fails."""
    message: str
    errors: List[str]


@dataclass
class EntityDefinition:
    """Represents an entity type definition from a schema."""
    name: str
    description: str
    properties: Dict[str, Dict[str, Any]]
    relationships: Dict[str, Dict[str, Any]]
    required_properties: List[str]
    
    def get_property_names(self) -> List[str]:
        """Get list of all property names."""
        return list(self.properties.keys())
    
    def get_relationship_names(self) -> List[str]:
        """Get list of all relationship names."""
        return list(self.relationships.keys())
    
    def is_property_required(self, property_name: str) -> bool:
        """Check if a property is required."""
        return property_name in self.required_properties


@dataclass
class SchemaDefinition:
    """Represents a complete schema definition."""
    name: str
    description: str
    version: str
    context: Dict[str, Any]
    entities: Dict[str, EntityDefinition]
    
    def get_entity_names(self) -> List[str]:
        """Get list of all entity type names."""
        return list(self.entities.keys())
    
    def get_entity(self, name: str) -> Optional[EntityDefinition]:
        """Get entity definition by name."""
        return self.entities.get(name)
    
    def validate_relationship_targets(self) -> List[str]:
        """Validate that all relationship targets reference valid entity types."""
        errors = []
        entity_names = set(self.entities.keys())
        
        for entity_name, entity in self.entities.items():
            for rel_name, rel_def in entity.relationships.items():
                target = rel_def.get('target')
                if target and target not in entity_names:
                    errors.append(
                        f"Entity '{entity_name}' relationship '{rel_name}' "
                        f"references unknown target '{target}'"
                    )
        
        return errors


class SchemaParser:
    """
    Parser for JSON-LD schemas used in MycoMind knowledge extraction.
    
    Handles loading, validating, and providing access to schema definitions
    that define entity types, properties, and relationships for the ETL process.
    """
    
    def __init__(self):
        """Initialize the schema parser."""
        self.schemas: Dict[str, SchemaDefinition] = {}
        
        # JSON Schema for validating MycoMind schemas
        self.validation_schema = {
            "type": "object",
            "required": ["@context", "entities"],
            "properties": {
                "@context": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "object"}
                    ]
                },
                "@type": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "version": {"type": "string"},
                "entities": {
                    "type": "object",
                    "patternProperties": {
                        "^[A-Z][a-zA-Z0-9]*$": {
                            "type": "object",
                            "properties": {
                                "@type": {"type": "string"},
                                "description": {"type": "string"},
                                "properties": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                                            "type": "object",
                                            "required": ["type"],
                                            "properties": {
                                                "type": {"type": "string"},
                                                "description": {"type": "string"},
                                                "required": {"type": "boolean"},
                                                "format": {"type": "string"},
                                                "enum": {"type": "array"},
                                                "items": {"type": "string"},
                                                "minLength": {"type": "integer"},
                                                "maxLength": {"type": "integer"}
                                            }
                                        }
                                    }
                                },
                                "relationships": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^[a-zA-Z][a-zA-Z0-9_]*$": {
                                            "type": "object",
                                            "required": ["target"],
                                            "properties": {
                                                "target": {"type": "string"},
                                                "description": {"type": "string"},
                                                "bidirectional": {"type": "boolean"},
                                                "inverse": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    
    def load_schema(self, schema_path: str) -> SchemaDefinition:
        """
        Load and parse a schema from a JSON file.
        
        Args:
            schema_path: Path to the schema file
            
        Returns:
            Parsed schema definition
            
        Raises:
            SchemaValidationError: If schema is invalid
            FileNotFoundError: If schema file doesn't exist
        """
        try:
            if not Path(schema_path).exists():
                raise FileNotFoundError(f"Schema file not found: {schema_path}")
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            # Validate against JSON Schema
            self._validate_schema_structure(schema_data)
            
            # Parse into structured format
            schema_def = self._parse_schema_data(schema_data, schema_path)
            
            # Validate semantic consistency
            self._validate_schema_semantics(schema_def)
            
            # Cache the schema
            self.schemas[schema_path] = schema_def
            
            logger.info(f"Schema loaded successfully: {schema_path}")
            return schema_def
            
        except json.JSONDecodeError as e:
            raise SchemaValidationError(
                f"Invalid JSON in schema file: {schema_path}",
                [str(e)]
            )
        except Exception as e:
            logger.error(f"Failed to load schema {schema_path}: {e}")
            raise
    
    def _validate_schema_structure(self, schema_data: Dict[str, Any]) -> None:
        """
        Validate schema structure against JSON Schema.
        
        Args:
            schema_data: Raw schema data
            
        Raises:
            SchemaValidationError: If validation fails
        """
        try:
            validate(instance=schema_data, schema=self.validation_schema)
        except ValidationError as e:
            raise SchemaValidationError(
                "Schema structure validation failed",
                [e.message]
            )
    
    def _parse_schema_data(self, schema_data: Dict[str, Any], schema_path: str) -> SchemaDefinition:
        """
        Parse raw schema data into structured format.
        
        Args:
            schema_data: Raw schema data
            schema_path: Path to schema file (for error reporting)
            
        Returns:
            Parsed schema definition
        """
        # Extract basic schema information
        name = schema_data.get("name", Path(schema_path).stem)
        description = schema_data.get("description", "")
        version = schema_data.get("version", "1.0.0")
        context = schema_data.get("@context", {})
        
        # Parse entities
        entities = {}
        entities_data = schema_data.get("entities", {})
        
        for entity_name, entity_data in entities_data.items():
            entity_def = self._parse_entity_definition(entity_name, entity_data)
            entities[entity_name] = entity_def
        
        return SchemaDefinition(
            name=name,
            description=description,
            version=version,
            context=context,
            entities=entities
        )
    
    def _parse_entity_definition(self, entity_name: str, entity_data: Dict[str, Any]) -> EntityDefinition:
        """
        Parse entity definition from schema data.
        
        Args:
            entity_name: Name of the entity type
            entity_data: Entity definition data
            
        Returns:
            Parsed entity definition
        """
        description = entity_data.get("description", "")
        
        # Parse properties
        properties = {}
        properties_data = entity_data.get("properties", {})
        required_properties = []
        
        for prop_name, prop_data in properties_data.items():
            properties[prop_name] = prop_data
            if prop_data.get("required", False):
                required_properties.append(prop_name)
        
        # Parse relationships
        relationships = {}
        relationships_data = entity_data.get("relationships", {})
        
        for rel_name, rel_data in relationships_data.items():
            relationships[rel_name] = rel_data
        
        return EntityDefinition(
            name=entity_name,
            description=description,
            properties=properties,
            relationships=relationships,
            required_properties=required_properties
        )
    
    def _validate_schema_semantics(self, schema_def: SchemaDefinition) -> None:
        """
        Validate semantic consistency of the schema.
        
        Args:
            schema_def: Schema definition to validate
            
        Raises:
            SchemaValidationError: If validation fails
        """
        errors = []
        
        # Validate relationship targets
        target_errors = schema_def.validate_relationship_targets()
        errors.extend(target_errors)
        
        # Validate entity naming conventions
        for entity_name in schema_def.get_entity_names():
            if not re.match(r'^[A-Z][a-zA-Z0-9]*$', entity_name):
                errors.append(f"Entity name '{entity_name}' should start with uppercase letter")
        
        # Validate property naming conventions
        for entity_name, entity in schema_def.entities.items():
            for prop_name in entity.get_property_names():
                if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', prop_name):
                    errors.append(
                        f"Property name '{prop_name}' in entity '{entity_name}' "
                        "should start with letter and contain only letters, numbers, and underscores"
                    )
        
        # Validate relationship naming conventions
        for entity_name, entity in schema_def.entities.items():
            for rel_name in entity.get_relationship_names():
                if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', rel_name):
                    errors.append(
                        f"Relationship name '{rel_name}' in entity '{entity_name}' "
                        "should start with letter and contain only letters, numbers, and underscores"
                    )
        
        if errors:
            raise SchemaValidationError("Schema semantic validation failed", errors)
    
    def get_schema(self, schema_path: str) -> Optional[SchemaDefinition]:
        """
        Get cached schema or load from file.
        
        Args:
            schema_path: Path to schema file
            
        Returns:
            Schema definition or None if not found
        """
        if schema_path in self.schemas:
            return self.schemas[schema_path]
        
        try:
            return self.load_schema(schema_path)
        except Exception as e:
            logger.error(f"Failed to load schema {schema_path}: {e}")
            return None
    
    def build_extraction_prompt(self, schema_def: SchemaDefinition) -> str:
        """
        Build LLM prompt instructions based on schema definition.
        
        Args:
            schema_def: Schema definition
            
        Returns:
            Formatted prompt instructions for entity extraction
        """
        prompt_parts = [
            f"SCHEMA: {schema_def.name}",
            f"Description: {schema_def.description}",
            "",
            "ENTITY TYPES:"
        ]
        
        for entity_name, entity in schema_def.entities.items():
            prompt_parts.append(f"\n{entity_name}:")
            if entity.description:
                prompt_parts.append(f"  Description: {entity.description}")
            
            # Properties section
            if entity.properties:
                prompt_parts.append("  Properties:")
                for prop_name, prop_def in entity.properties.items():
                    required_marker = " (REQUIRED)" if entity.is_property_required(prop_name) else ""
                    prop_type = prop_def.get('type', 'string')
                    prop_desc = prop_def.get('description', '')
                    
                    prompt_parts.append(f"    - {prop_name} ({prop_type}){required_marker}: {prop_desc}")
                    
                    # Add enum values if specified
                    if 'enum' in prop_def:
                        enum_values = ', '.join(prop_def['enum'])
                        prompt_parts.append(f"      Allowed values: {enum_values}")
            
            # Relationships section
            if entity.relationships:
                prompt_parts.append("  Relationships:")
                for rel_name, rel_def in entity.relationships.items():
                    target = rel_def.get('target', 'Unknown')
                    rel_desc = rel_def.get('description', '')
                    prompt_parts.append(f"    - {rel_name} → {target}: {rel_desc}")
        
        return "\n".join(prompt_parts)
    
    def extract_entity_types(self, schema_def: SchemaDefinition) -> List[str]:
        """
        Extract list of entity type names from schema.
        
        Args:
            schema_def: Schema definition
            
        Returns:
            List of entity type names
        """
        return schema_def.get_entity_names()
    
    def get_required_properties(self, schema_def: SchemaDefinition, entity_type: str) -> List[str]:
        """
        Get required properties for an entity type.
        
        Args:
            schema_def: Schema definition
            entity_type: Entity type name
            
        Returns:
            List of required property names
        """
        entity = schema_def.get_entity(entity_type)
        return entity.required_properties if entity else []
    
    def get_relationship_targets(self, schema_def: SchemaDefinition, entity_type: str) -> Dict[str, str]:
        """
        Get relationship targets for an entity type.
        
        Args:
            schema_def: Schema definition
            entity_type: Entity type name
            
        Returns:
            Dictionary mapping relationship names to target entity types
        """
        entity = schema_def.get_entity(entity_type)
        if not entity:
            return {}
        
        return {
            rel_name: rel_def.get('target', '')
            for rel_name, rel_def in entity.relationships.items()
        }
    
    def validate_extracted_entity(
        self, 
        entity_data: Dict[str, Any], 
        schema_def: SchemaDefinition
    ) -> Tuple[bool, List[str]]:
        """
        Validate an extracted entity against the schema.
        
        Args:
            entity_data: Extracted entity data
            schema_def: Schema definition
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check if entity type exists
        entity_type = entity_data.get('type')
        if not entity_type:
            errors.append("Entity missing 'type' field")
            return False, errors
        
        entity_def = schema_def.get_entity(entity_type)
        if not entity_def:
            errors.append(f"Unknown entity type: {entity_type}")
            return False, errors
        
        # Validate required properties
        properties = entity_data.get('properties', {})
        for required_prop in entity_def.required_properties:
            if required_prop not in properties:
                errors.append(f"Missing required property: {required_prop}")
        
        # Validate property types and constraints
        for prop_name, prop_value in properties.items():
            if prop_name in entity_def.properties:
                prop_def = entity_def.properties[prop_name]
                prop_errors = self._validate_property_value(prop_name, prop_value, prop_def)
                errors.extend(prop_errors)
        
        # Validate relationships
        relationships = entity_data.get('relationships', {})
        for rel_name, rel_targets in relationships.items():
            if rel_name in entity_def.relationships:
                # Skip validation for empty arrays or None values
                if rel_targets is None or (isinstance(rel_targets, list) and len(rel_targets) == 0):
                    continue
                rel_def = entity_def.relationships[rel_name]
                rel_errors = self._validate_relationship_value(rel_name, rel_targets, rel_def)
                errors.extend(rel_errors)
            else:
                errors.append(f"Unknown relationship: {rel_name}")
        
        return len(errors) == 0, errors
    
    def _validate_property_value(
        self, 
        prop_name: str, 
        prop_value: Any, 
        prop_def: Dict[str, Any]
    ) -> List[str]:
        """Validate a property value against its definition."""
        errors = []
        expected_type = prop_def.get('type', 'string')
        
        # Type validation
        if expected_type == 'string' and not isinstance(prop_value, str):
            errors.append(f"Property '{prop_name}' should be string, got {type(prop_value).__name__}")
        elif expected_type == 'integer' and not isinstance(prop_value, int):
            errors.append(f"Property '{prop_name}' should be integer, got {type(prop_value).__name__}")
        elif expected_type == 'number' and not isinstance(prop_value, (int, float)):
            errors.append(f"Property '{prop_name}' should be number, got {type(prop_value).__name__}")
        elif expected_type == 'array' and not isinstance(prop_value, list):
            errors.append(f"Property '{prop_name}' should be array, got {type(prop_value).__name__}")
        
        # Enum validation
        if 'enum' in prop_def and prop_value not in prop_def['enum']:
            allowed_values = ', '.join(prop_def['enum'])
            errors.append(f"Property '{prop_name}' value '{prop_value}' not in allowed values: {allowed_values}")
        
        # String length validation
        if isinstance(prop_value, str):
            if 'minLength' in prop_def and len(prop_value) < prop_def['minLength']:
                errors.append(f"Property '{prop_name}' too short (min: {prop_def['minLength']})")
            if 'maxLength' in prop_def and len(prop_value) > prop_def['maxLength']:
                errors.append(f"Property '{prop_name}' too long (max: {prop_def['maxLength']})")
        
        return errors
    
    def _validate_relationship_value(
        self, 
        rel_name: str, 
        rel_targets: Any, 
        rel_def: Dict[str, Any]
    ) -> List[str]:
        """Validate a relationship value against its definition."""
        errors = []
        
        # Ensure targets are in the correct format (string or list of strings)
        if isinstance(rel_targets, str):
            targets = [rel_targets]
        elif isinstance(rel_targets, list):
            targets = rel_targets
        else:
            errors.append(f"Relationship '{rel_name}' should be string or array of strings")
            return errors
        
        # Validate WikiLink format
        for target in targets:
            if not isinstance(target, str):
                errors.append(f"Relationship '{rel_name}' target should be string")
                continue
            
            # Check WikiLink format
            if not (target.startswith('[[') and target.endswith(']]')):
                errors.append(f"Relationship '{rel_name}' target '{target}' should be WikiLink format [[Entity Name]]")
        
        return errors
    
    def create_example_schema(self, output_path: str) -> None:
        """
        Create an example schema file for reference.
        
        Args:
            output_path: Path where to create the example schema
        """
        example_schema = {
            "@context": {
                "@vocab": "https://schema.org/",
                "myco": "https://mycomind.org/schema/"
            },
            "@type": "Schema",
            "name": "Personal Knowledge Schema",
            "description": "Example schema for extracting personal and professional knowledge",
            "version": "1.0.0",
            "entities": {
                "Person": {
                    "@type": "Class",
                    "description": "An individual person",
                    "properties": {
                        "name": {
                            "type": "string",
                            "required": True,
                            "description": "Full name of the person"
                        },
                        "email": {
                            "type": "string",
                            "format": "email",
                            "description": "Email address"
                        },
                        "role": {
                            "type": "string",
                            "description": "Professional role or title"
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
                            "description": "Personal or professional acquaintance",
                            "bidirectional": True
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
                            "required": True,
                            "description": "Organization name"
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
                },
                "Concept": {
                    "@type": "Class",
                    "description": "A key concept or idea",
                    "properties": {
                        "name": {
                            "type": "string",
                            "required": True,
                            "description": "Concept name"
                        },
                        "definition": {
                            "type": "string",
                            "description": "Definition or explanation"
                        },
                        "domain": {
                            "type": "string",
                            "description": "Domain or field of study"
                        }
                    },
                    "relationships": {
                        "relatedTo": {
                            "target": "Concept",
                            "description": "Related concept"
                        },
                        "exemplifiedBy": {
                            "target": "Person",
                            "description": "Person who exemplifies this concept"
                        }
                    }
                }
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(example_schema, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Example schema created at {output_path}")


if __name__ == "__main__":
    # Example usage and testing
    import sys
    
    parser = SchemaParser()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "create-example":
            output_path = sys.argv[2] if len(sys.argv) > 2 else "example_schema.json"
            parser.create_example_schema(output_path)
            print(f"Example schema created at {output_path}")
        elif sys.argv[1] == "validate":
            schema_path = sys.argv[2] if len(sys.argv) > 2 else "schema.json"
            try:
                schema_def = parser.load_schema(schema_path)
                print(f"Schema '{schema_def.name}' is valid!")
                print(f"Entity types: {', '.join(schema_def.get_entity_names())}")
            except Exception as e:
                print(f"Schema validation failed: {e}")
                sys.exit(1)
        elif sys.argv[1] == "prompt":
            schema_path = sys.argv[2] if len(sys.argv) > 2 else "schema.json"
            try:
                schema_def = parser.load_schema(schema_path)
                prompt = parser.build_extraction_prompt(schema_def)
                print("Generated extraction prompt:")
                print("=" * 50)
                print(prompt)
            except Exception as e:
                print(f"Failed to generate prompt: {e}")
                sys.exit(1)
    else:
        print("Usage:")
        print("  python schema_parser.py create-example [path]")
        print("  python schema_parser.py validate [path]")
        print("  python schema_parser.py prompt [path]")
