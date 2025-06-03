#!/usr/bin/env python3
"""
YAML to JSON-LD Converter for MycoMind

This script converts YAML frontmatter from Markdown files back to JSON-LD format
using the original schema definitions. It's the reverse operation of the ETL pipeline
that extracts entities and creates YAML frontmatter.

Usage:
    python yaml_to_jsonld_converter.py --schema schemas/example_schemas/personal_knowledge.json --input /path/to/markdown/files --output output.jsonld
    python yaml_to_jsonld_converter.py --schema schemas/example_schemas/personal_knowledge.json --file single_file.md --output output.jsonld
    python yaml_to_jsonld_converter.py --schema schemas/example_schemas/personal_knowledge.json --input /path/to/markdown/files --output output.jsonld --web-app
"""

import os
import re
import yaml
import json
import argparse
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from urllib.parse import quote

# Import MycoMind modules
from schema_parser import SchemaParser, SchemaDefinition

logger = logging.getLogger(__name__)


class YAMLToJSONLDConverter:
    """
    Converts YAML frontmatter from Markdown files back to JSON-LD format
    using the original schema definitions.
    """
    
    def __init__(self, schema_path: str, base_iri: str = "http://mycomind.org/kg/"):
        """
        Initialize the converter.
        
        Args:
            schema_path: Path to the schema definition file
            base_iri: Base IRI for generating resource URIs
        """
        self.schema_parser = SchemaParser()
        self.schema_def = self.schema_parser.load_schema(schema_path)
        self.base_iri = base_iri
        self.resource_base = f"{base_iri}resource/"
        self.ontology_base = f"{base_iri}ontology/"
        
        # Track processed entities
        self.entities = []
        self.entity_names_to_iris = {}
        
        logger.info(f"Loaded schema: {self.schema_def.name}")
    
    def extract_frontmatter(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Extract YAML frontmatter from a Markdown file.
        
        Args:
            filepath: Path to the Markdown file
            
        Returns:
            Parsed YAML frontmatter or None if not found
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for YAML frontmatter
            if not content.startswith("---"):
                return None
            
            # Split content to extract frontmatter
            parts = content.split("---", 2)
            if len(parts) < 3:
                return None
            
            frontmatter = yaml.safe_load(parts[1])
            return frontmatter if frontmatter else None
            
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")
            return None
    
    def generate_iri(self, name: str, entity_type: str = None) -> str:
        """
        Generate an IRI for an entity.
        
        Args:
            name: Entity name
            entity_type: Entity type (optional)
            
        Returns:
            Generated IRI
        """
        # Sanitize name for IRI
        sanitized_name = re.sub(r'[^\w\s-]', '', name)
        sanitized_name = re.sub(r'\s+', '_', sanitized_name)
        encoded_name = quote(sanitized_name)
        
        if entity_type:
            return f"{self.resource_base}{entity_type}/{encoded_name}"
        else:
            return f"{self.resource_base}{encoded_name}"
    
    def resolve_wikilink(self, wikilink: str) -> str:
        """
        Resolve a WikiLink to an IRI.
        
        Args:
            wikilink: WikiLink in format [[Entity Name]]
            
        Returns:
            Resolved IRI
        """
        if wikilink.startswith('[[') and wikilink.endswith(']]'):
            entity_name = wikilink[2:-2]
            
            # Check if we already have an IRI for this entity
            if entity_name in self.entity_names_to_iris:
                return self.entity_names_to_iris[entity_name]
            
            # Generate new IRI
            iri = self.generate_iri(entity_name)
            self.entity_names_to_iris[entity_name] = iri
            return iri
        
        return wikilink
    
    def convert_property_value(self, value: Any, property_def: Dict[str, Any]) -> Any:
        """
        Convert a property value based on its schema definition.
        
        Args:
            value: The value to convert
            property_def: Property definition from schema
            
        Returns:
            Converted value
        """
        prop_type = property_def.get('type', 'string')
        
        if isinstance(value, list):
            return [self.convert_property_value(v, property_def) for v in value]
        
        if isinstance(value, str):
            # Handle WikiLinks
            if value.startswith('[[') and value.endswith(']]'):
                return {"@id": self.resolve_wikilink(value)}
            
            # Handle different data types
            if prop_type == 'string':
                return value
            elif prop_type == 'integer':
                try:
                    return int(value)
                except ValueError:
                    return value
            elif prop_type == 'number':
                try:
                    return float(value)
                except ValueError:
                    return value
            elif prop_type == 'boolean':
                if value.lower() in ['true', 'yes', '1']:
                    return True
                elif value.lower() in ['false', 'no', '0']:
                    return False
                return value
        
        return value
    
    def convert_relationship_value(self, value: Any) -> Any:
        """
        Convert a relationship value to proper JSON-LD format.
        
        Args:
            value: The relationship value
            
        Returns:
            Converted value with @id references
        """
        if isinstance(value, list):
            return [self.convert_relationship_value(v) for v in value]
        
        if isinstance(value, str):
            if value.startswith('[[') and value.endswith(']]'):
                return {"@id": self.resolve_wikilink(value)}
            else:
                # Assume it's an entity name that should be converted to IRI
                iri = self.generate_iri(value)
                self.entity_names_to_iris[value] = iri
                return {"@id": iri}
        
        return value
    
    def convert_frontmatter_to_jsonld(self, frontmatter: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
        """
        Convert YAML frontmatter to JSON-LD entity.
        
        Args:
            frontmatter: Parsed YAML frontmatter
            filename: Source filename for generating IRI
            
        Returns:
            JSON-LD entity or None if conversion fails
        """
        try:
            # Get entity type
            entity_type = frontmatter.get('type')
            if not entity_type:
                logger.warning(f"No entity type found in {filename}")
                return None
            
            # Check if entity type exists in schema
            if entity_type not in self.schema_def.entities:
                logger.warning(f"Unknown entity type '{entity_type}' in {filename}")
                return None
            
            entity_def = self.schema_def.entities[entity_type]
            entity_schema = {
                'properties': entity_def.properties if hasattr(entity_def, 'properties') else {},
                'relationships': entity_def.relationships if hasattr(entity_def, 'relationships') else {}
            }
            
            # Generate IRI for this entity
            entity_name = frontmatter.get('name', Path(filename).stem)
            entity_iri = self.generate_iri(entity_name, entity_type)
            self.entity_names_to_iris[entity_name] = entity_iri
            
            # Start building JSON-LD entity
            jsonld_entity = {
                "@id": entity_iri,
                "@type": f"{self.ontology_base}{entity_type}"
            }
            
            # Convert properties
            for prop_name, prop_value in frontmatter.items():
                if prop_name in ['type', 'created', 'source', 'extraction_date', 
                               'extraction_confidence', 'schema_version', 'tags']:
                    # Skip metadata properties
                    continue
                
                # Check if it's a defined property in the schema
                if prop_name in entity_schema.get('properties', {}):
                    prop_def = entity_schema['properties'][prop_name]
                    converted_value = self.convert_property_value(prop_value, prop_def)
                    jsonld_entity[f"{self.ontology_base}{prop_name}"] = converted_value
                
                # Check if it's a relationship
                elif prop_name in entity_schema.get('relationships', {}):
                    converted_value = self.convert_relationship_value(prop_value)
                    jsonld_entity[f"{self.ontology_base}{prop_name}"] = converted_value
                
                else:
                    # Unknown property, include as-is with ontology prefix
                    logger.debug(f"Unknown property '{prop_name}' in {filename}")
                    jsonld_entity[f"{self.ontology_base}{prop_name}"] = prop_value
            
            # Add metadata properties
            if 'created' in frontmatter:
                jsonld_entity["http://purl.org/dc/terms/created"] = frontmatter['created']
            
            if 'extraction_date' in frontmatter:
                jsonld_entity[f"{self.ontology_base}extractionDate"] = frontmatter['extraction_date']
            
            if 'extraction_confidence' in frontmatter:
                jsonld_entity[f"{self.ontology_base}extractionConfidence"] = frontmatter['extraction_confidence']
            
            if 'source' in frontmatter:
                jsonld_entity[f"{self.ontology_base}sourceFile"] = frontmatter['source']
            
            return jsonld_entity
            
        except Exception as e:
            logger.error(f"Error converting frontmatter from {filename}: {e}")
            return None
    
    def process_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Process a single Markdown file.
        
        Args:
            filepath: Path to the Markdown file
            
        Returns:
            JSON-LD entity or None if processing fails
        """
        filename = os.path.basename(filepath)
        logger.info(f"Processing {filename}")
        
        frontmatter = self.extract_frontmatter(filepath)
        if not frontmatter:
            logger.warning(f"No frontmatter found in {filename}")
            return None
        
        return self.convert_frontmatter_to_jsonld(frontmatter, filename)
    
    def process_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Process all Markdown files in a directory.
        
        Args:
            directory: Path to directory containing Markdown files
            
        Returns:
            List of JSON-LD entities
        """
        entities = []
        md_files = list(Path(directory).glob("**/*.md"))
        
        logger.info(f"Found {len(md_files)} Markdown files in {directory}")
        
        for filepath in md_files:
            entity = self.process_file(str(filepath))
            if entity:
                entities.append(entity)
        
        logger.info(f"Successfully converted {len(entities)} entities")
        return entities
    
    def create_jsonld_context(self) -> Dict[str, Any]:
        """
        Create JSON-LD context based on the schema.
        
        Returns:
            JSON-LD context
        """
        context = {
            "@vocab": self.ontology_base,
            "@base": self.resource_base,
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "schema": "http://schema.org/",
            "dcterms": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
        
        # Add schema-specific mappings
        for entity_type, entity_def in self.schema_def.entities.items():
            # Add property mappings
            properties = entity_def.properties if hasattr(entity_def, 'properties') else {}
            for prop_name, prop_def in properties.items():
                prop_type = prop_def.get('type', 'string')
                
                if prop_type == 'integer':
                    context[prop_name] = {
                        "@id": f"{self.ontology_base}{prop_name}",
                        "@type": "xsd:integer"
                    }
                elif prop_type == 'number':
                    context[prop_name] = {
                        "@id": f"{self.ontology_base}{prop_name}",
                        "@type": "xsd:decimal"
                    }
                elif prop_type == 'boolean':
                    context[prop_name] = {
                        "@id": f"{self.ontology_base}{prop_name}",
                        "@type": "xsd:boolean"
                    }
                elif prop_def.get('format') == 'date':
                    context[prop_name] = {
                        "@id": f"{self.ontology_base}{prop_name}",
                        "@type": "xsd:date"
                    }
                elif prop_def.get('format') == 'datetime':
                    context[prop_name] = {
                        "@id": f"{self.ontology_base}{prop_name}",
                        "@type": "xsd:dateTime"
                    }
        
        return context
    
    def export_jsonld(self, entities: List[Dict[str, Any]], output_path: str, web_app: bool = False) -> bool:
        """
        Export entities to JSON-LD file.
        
        Args:
            entities: List of JSON-LD entities
            output_path: Output file path
            web_app: If True, also copy the output to the web app directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there is one
                os.makedirs(output_dir, exist_ok=True)
            
            # Create JSON-LD document
            jsonld_doc = {
                "@context": self.create_jsonld_context(),
                "@graph": entities
            }
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(jsonld_doc, f, indent=2, ensure_ascii=False)
            
            logger.info(f"JSON-LD exported to {output_path}")
            logger.info(f"Total entities: {len(entities)}")
            
            # If web_app is True, also copy the file to the web app directory
            if web_app:
                web_app_path = os.path.join('docs', 'web', 'mycomind_knowledge_graph.jsonld')
                
                # Create web app directory if needed
                web_app_dir = os.path.dirname(web_app_path)
                os.makedirs(web_app_dir, exist_ok=True)
                
                # Copy the file
                shutil.copy2(output_path, web_app_path)
                logger.info(f"JSON-LD also copied to web app: {web_app_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting JSON-LD: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Convert YAML frontmatter to JSON-LD')
    parser.add_argument('--schema', '-s', required=True, help='Path to schema definition file')
    parser.add_argument('--input', '-i', help='Input directory containing Markdown files')
    parser.add_argument('--file', '-f', help='Single Markdown file to process')
    parser.add_argument('--output', '-o', required=True, help='Output JSON-LD file path')
    parser.add_argument('--base-iri', default='http://mycomind.org/kg/', help='Base IRI for resources')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--web-app', '-w', action='store_true',
                        help='Also save the output to the web app directory (docs/web/mycomind_knowledge_graph.jsonld)')

    args = parser.parse_args()

    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Validate arguments
    # if not args.input and not args.file:
    #     logger.error("Either --input or --file must be specified")
    #     return 1

    if args.input and args.file:
        logger.error("Cannot specify both --input and --file")
        return 1

    try:
        # Initialize converter
        converter = YAMLToJSONLDConverter(args.schema, args.base_iri)

        # Process files
        if args.file:
            entity = converter.process_file(args.file)
            entities = [entity] if entity else []
        else:
            # Use the output from main_etl.py if no input is specified
            if not args.input:
                # Use the demo_vault as the default input directory
                args.input = os.path.join("demo_vault", "extracted_knowledge", "project")
                logger.info(f"Using default input directory: {args.input}")
            entities = converter.process_directory(args.input)

        if not entities:
            logger.warning("No entities were converted")
            return 1

        # Export to JSON-LD
        success = converter.export_jsonld(entities, args.output, args.web_app)

        if success:
            logger.info("Conversion completed successfully!")
            return 0
        else:
            logger.error("Export failed")
            return 1

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
