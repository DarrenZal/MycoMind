#!/usr/bin/env python3
"""
YAML to Neo4j Cypher Converter for MycoMind

This script converts YAML frontmatter from Markdown files to Neo4j Cypher statements
using the original schema definitions. It's an alternative to the JSON-LD converter
that allows direct loading into Neo4j for graph visualization and querying.

Usage:
    python yaml_to_neo4j_converter.py --schema schemas/example_schemas/personal_knowledge.json --input /path/to/markdown/files --output output.cypher
    python yaml_to_neo4j_converter.py --schema schemas/example_schemas/personal_knowledge.json --file single_file.md --output output.cypher
    python yaml_to_neo4j_converter.py --schema schemas/example_schemas/personal_knowledge.json --input /path/to/markdown/files --output output.cypher --browser
"""

import os
import re
import yaml
import json
import argparse
import logging
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime
from urllib.parse import quote

# Import MycoMind modules
from schema_parser import SchemaParser, SchemaDefinition
from config_manager import load_config

logger = logging.getLogger(__name__)


class YAMLToNeo4jConverter:
    """
    Converts YAML frontmatter from Markdown files to Neo4j Cypher statements
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
        
        # Track processed entities and relationships
        self.entities = []
        self.relationships = []
        self.entity_names_to_iris = {}
        self.processed_entity_iris = set()
        
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
                return self.resolve_wikilink(value)
            
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
        Convert a relationship value to proper IRI format.
        
        Args:
            value: The relationship value
            
        Returns:
            Converted value with IRI references
        """
        if isinstance(value, list):
            return [self.convert_relationship_value(v) for v in value]
        
        if isinstance(value, str):
            if value.startswith('[[') and value.endswith(']]'):
                return self.resolve_wikilink(value)
            else:
                # Assume it's an entity name that should be converted to IRI
                iri = self.generate_iri(value)
                self.entity_names_to_iris[value] = iri
                return iri
        
        return value
    
    def convert_frontmatter_to_cypher(self, frontmatter: Dict[str, Any], filename: str) -> Optional[Dict[str, Any]]:
        """
        Convert YAML frontmatter to Neo4j entity and relationships.
        
        Args:
            frontmatter: Parsed YAML frontmatter
            filename: Source filename for generating IRI
            
        Returns:
            Dictionary with entity and relationships or None if conversion fails
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
            
            # Skip if already processed
            if entity_iri in self.processed_entity_iris:
                logger.info(f"Skipping already processed entity: {entity_iri}")
                return None
            
            self.processed_entity_iris.add(entity_iri)
            
            # Start building Neo4j entity
            entity_props = {
                'iri': entity_iri,
                'name': entity_name,
                'type': entity_type
            }
            
            # Relationships to create
            relationships = []
            
            # Convert properties
            for prop_name, prop_value in frontmatter.items():
                if prop_name in ['type', 'created', 'source', 'extraction_date', 
                               'extraction_confidence', 'schema_version', 'tags']:
                    # Handle metadata properties
                    if prop_name == 'created':
                        entity_props['created'] = prop_value
                    elif prop_name == 'source':
                        entity_props['source_file'] = prop_value
                    elif prop_name == 'extraction_date':
                        entity_props['extraction_date'] = prop_value
                    elif prop_name == 'extraction_confidence':
                        entity_props['extraction_confidence'] = float(prop_value)
                    continue
                
                # Check if it's a defined property in the schema
                if prop_name in entity_schema.get('properties', {}):
                    prop_def = entity_schema['properties'][prop_name]
                    converted_value = self.convert_property_value(prop_value, prop_def)
                    entity_props[prop_name] = converted_value
                
                # Check if it's a relationship
                elif prop_name in entity_schema.get('relationships', {}):
                    target_iris = self.convert_relationship_value(prop_value)
                    if isinstance(target_iris, list):
                        for target_iri in target_iris:
                            relationships.append({
                                'source': entity_iri,
                                'type': prop_name,
                                'target': target_iri
                            })
                    else:
                        relationships.append({
                            'source': entity_iri,
                            'type': prop_name,
                            'target': target_iris
                        })
                
                else:
                    # Unknown property, include as-is
                    logger.debug(f"Unknown property '{prop_name}' in {filename}")
                    entity_props[prop_name] = prop_value
            
            return {
                'entity': entity_props,
                'relationships': relationships
            }
            
        except Exception as e:
            logger.error(f"Error converting frontmatter from {filename}: {e}")
            return None
    
    def process_file(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        Process a single Markdown file.
        
        Args:
            filepath: Path to the Markdown file
            
        Returns:
            Dictionary with entity and relationships or None if processing fails
        """
        filename = os.path.basename(filepath)
        logger.info(f"Processing {filename}")
        
        frontmatter = self.extract_frontmatter(filepath)
        if not frontmatter:
            logger.warning(f"No frontmatter found in {filename}")
            return None
        
        return self.convert_frontmatter_to_cypher(frontmatter, filename)
    
    def process_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Process all Markdown files in a directory.
        
        Args:
            directory: Path to directory containing Markdown files
            
        Returns:
            List of dictionaries with entities and relationships
        """
        results = []
        md_files = list(Path(directory).glob("**/*.md"))
        
        logger.info(f"Found {len(md_files)} Markdown files in {directory}")
        
        for filepath in md_files:
            result = self.process_file(str(filepath))
            if result:
                results.append(result)
                self.entities.append(result['entity'])
                self.relationships.extend(result['relationships'])
        
        logger.info(f"Successfully converted {len(results)} entities")
        return results
    
    def generate_cypher_statements(self) -> str:
        """
        Generate Cypher statements for creating entities and relationships.
        
        Returns:
            String containing Cypher statements
        """
        cypher_statements = []
        
        # Add header comment
        cypher_statements.append("// MycoMind Knowledge Graph - Generated Cypher Statements")
        cypher_statements.append(f"// Generated on: {datetime.now().isoformat()}")
        cypher_statements.append(f"// Schema: {self.schema_def.name}")
        cypher_statements.append("")
        
        # Optional: Add statement to clear existing data
        cypher_statements.append("// Uncomment to clear existing data (use with caution)")
        cypher_statements.append("// MATCH (n) DETACH DELETE n;")
        cypher_statements.append("")
        
        # Create entity type indexes
        entity_types = set()
        for entity in self.entities:
            entity_types.add(entity['type'])
        
        for entity_type in sorted(entity_types):
            cypher_statements.append(f"// Create index for {entity_type} entities")
            cypher_statements.append(f"CREATE INDEX ON :{entity_type}(iri);")
        
        cypher_statements.append("")
        
        # Create entities
        cypher_statements.append("// Create entities")
        for entity in self.entities:
            # Create a copy of the entity properties without the IRI (used separately)
            props = {k: v for k, v in entity.items() if k != 'iri'}
            
            # Format property values for Cypher
            formatted_props = {}
            for key, value in props.items():
                if isinstance(value, str):
                    formatted_props[key] = f'"{value}"'
                elif isinstance(value, bool):
                    formatted_props[key] = str(value).lower()
                elif value is None:
                    formatted_props[key] = "null"
                else:
                    formatted_props[key] = str(value)
            
            # Build property string
            props_str = ", ".join([f"{k}: {v}" for k, v in formatted_props.items()])
            
            # Create Cypher statement
            cypher_statements.append(f"CREATE (:{entity['type']} {{iri: \"{entity['iri']}\", {props_str}}});")
        
        cypher_statements.append("")
        
        # Find referenced entities that don't exist yet
        referenced_iris = set()
        for rel in self.relationships:
            referenced_iris.add(rel['target'])
        
        existing_iris = {entity['iri'] for entity in self.entities}
        
        # Extract entity names from IRIs for better comparison
        existing_entity_names = set()
        for iri in existing_iris:
            # Extract the entity name from the IRI
            parts = iri.split('/')
            if len(parts) > 0:
                entity_name = parts[-1].replace('_', ' ').lower()
                existing_entity_names.add(entity_name)
        
        # Find truly missing IRIs (not in existing entities)
        missing_iris = set()
        for iri in referenced_iris:
            if iri in existing_iris:
                continue  # Skip if exact IRI match
                
            # Extract the entity name from the IRI for comparison
            parts = iri.split('/')
            if len(parts) > 0:
                entity_name = parts[-1].replace('_', ' ').lower()
                if entity_name not in existing_entity_names:
                    missing_iris.add(iri)
            else:
                missing_iris.add(iri)  # Add if can't extract name
        
        # Create placeholder nodes for missing entities
        if missing_iris:
            cypher_statements.append("// Create placeholder nodes for referenced entities that don't exist yet")
            for iri in missing_iris:
                # Extract entity name from IRI
                name = iri.split('/')[-1].replace('_', ' ')
                
                # Try to determine entity type from IRI
                entity_type = "Entity"  # Default type
                for known_type in self.schema_def.entities.keys():
                    if f"/{known_type}/" in iri:
                        entity_type = known_type
                        break
                
                # Create placeholder node
                cypher_statements.append(f"CREATE (:{entity_type} {{iri: \"{iri}\", name: \"{name}\", type: \"{entity_type}\"}});")
            
            cypher_statements.append("")
        
        # Create relationships
        if self.relationships:
            cypher_statements.append("// Create relationships")
            for rel in self.relationships:
                cypher_statements.append(
                    f"MATCH (a), (b) "
                    f"WHERE a.iri = \"{rel['source']}\" AND b.iri = \"{rel['target']}\" "
                    f"CREATE (a)-[:{rel['type'].upper()}]->(b);"
                )
        
        return "\n".join(cypher_statements)
    
    def export_cypher(self, output_path: str, browser: bool = False) -> bool:
        """
        Export Cypher statements to file.
        
        Args:
            output_path: Output file path
            browser: If True, also copy the output to the Neo4j browser import directory
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create output directory if needed
            output_dir = os.path.dirname(output_path)
            if output_dir:  # Only create directory if there is one
                os.makedirs(output_dir, exist_ok=True)
            
            # Generate Cypher statements
            cypher_statements = self.generate_cypher_statements()
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cypher_statements)
            
            logger.info(f"Cypher statements exported to {output_path}")
            logger.info(f"Total entities: {len(self.entities)}")
            logger.info(f"Total relationships: {len(self.relationships)}")
            
            # If browser is True, also copy the file to the Neo4j browser import directory
            if browser:
                # Try to find Neo4j import directory
                neo4j_import_dir = None
                
                # First check if Neo4j was installed by setup_neo4j.py
                local_neo4j_dir = os.path.join(os.getcwd(), "neo4j")
                if os.path.isdir(local_neo4j_dir):
                    # Find the Neo4j installation directory
                    for item in os.listdir(local_neo4j_dir):
                        if item.startswith("neo4j-community-"):
                            neo4j_install_dir = os.path.join(local_neo4j_dir, item)
                            possible_import_dir = os.path.join(neo4j_install_dir, "import")
                            if os.path.isdir(possible_import_dir):
                                neo4j_import_dir = possible_import_dir
                                logger.info(f"Found Neo4j import directory at: {neo4j_import_dir}")
                                break
                
                # If not found, check common locations
                if not neo4j_import_dir:
                    # Common locations for Neo4j import directory
                    possible_locations = [
                        os.path.expanduser("~/neo4j/import"),
                        "/var/lib/neo4j/import",
                        "C:\\Program Files\\Neo4j\\import",
                        "C:\\Users\\Public\\Documents\\Neo4j Desktop\\neo4jDatabases\\database-*\\installation-*\\import"
                    ]
                    
                    for location in possible_locations:
                        if "*" in location:
                            # Handle wildcard paths
                            import glob
                            for path in glob.glob(location):
                                if os.path.isdir(path):
                                    neo4j_import_dir = path
                                    break
                        elif os.path.isdir(location):
                            neo4j_import_dir = location
                            break
                
                if neo4j_import_dir:
                    browser_path = os.path.join(neo4j_import_dir, os.path.basename(output_path))
                    shutil.copy2(output_path, browser_path)
                    logger.info(f"Cypher statements also copied to Neo4j import directory: {browser_path}")
                else:
                    logger.warning("Could not find Neo4j import directory. Please copy the file manually.")
                    logger.info("Common Neo4j import directories:")
                    for location in possible_locations:
                        logger.info(f"  - {location}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting Cypher statements: {e}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Convert YAML frontmatter to Neo4j Cypher statements')
    parser.add_argument('--schema', '-s', help='Path to schema definition file')
    parser.add_argument('--input', '-i', help='Input directory containing Markdown files')
    parser.add_argument('--file', '-f', help='Single Markdown file to process')
    parser.add_argument('--output', '-o', help='Output Cypher file path')
    parser.add_argument('--base-iri', default='http://mycomind.org/kg/', help='Base IRI for resources')
    parser.add_argument('--browser', '-b', action='store_true', 
                        help='Also copy the output to the Neo4j browser import directory')
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config_manager = load_config(args.config)
    
    # Get schema path from arguments or use default
    schema_path = args.schema
    if not schema_path:
        schema_path = "schemas/hyphaltips_mycomind_schema.json"
        logger.info(f"Using default schema: {schema_path}")
    
    # Get input directory from arguments or configuration
    input_dir = args.input
    if not input_dir and not args.file:
        # Get vault path and notes folder from configuration
        obsidian_config = config_manager.get_obsidian_config()
        vault_path = obsidian_config.get("vault_path", "./demo_vault")
        notes_folder = obsidian_config.get("notes_folder", "extracted_knowledge")
        input_dir = os.path.join(vault_path, notes_folder)
        logger.info(f"Using input directory from config: {input_dir}")
    
    # Get output path from arguments or use default
    output_path = args.output
    if not output_path:
        output_path = "knowledge_graph.cypher"
        logger.info(f"Using default output path: {output_path}")
    
    # Validate arguments
    if not input_dir and not args.file:
        logger.error("No input directory or file specified and couldn't find in config")
        return 1
    
    if args.input and args.file:
        logger.error("Cannot specify both --input and --file")
        return 1
    
    try:
        # Initialize converter
        converter = YAMLToNeo4jConverter(schema_path, args.base_iri)
        
        # Process files
        if args.file:
            result = converter.process_file(args.file)
            if result:
                converter.entities.append(result['entity'])
                converter.relationships.extend(result['relationships'])
        else:
            converter.process_directory(input_dir)
        
        if not converter.entities:
            logger.warning("No entities were converted")
            return 1
        
        # Export to Cypher
        success = converter.export_cypher(output_path, args.browser)
        
        if success:
            logger.info("Conversion completed successfully!")
            logger.info(f"To load into Neo4j, run:")
            logger.info(f"  1. Start Neo4j")
            logger.info(f"  2. Open Neo4j Browser")
            logger.info(f"  3. Run: :source {os.path.basename(output_path)}")
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
