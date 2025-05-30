import json
import logging
import argparse # Added this line
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, XSD, OWL, SKOS, DC, DCTERMS, FOAF, PROV, SDO
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Define common namespaces (these are standard, not specific to hyphal)
SCHEMA = Namespace("http://schema.org/")

class OntologyConverterError(Exception):
    """Custom exception for ontology conversion errors."""
    pass

class OntologyConverter:
    """
    Converts an RDF/JSON-LD ontology into a MycoMind-compatible JSON schema.
    """
    def __init__(self):
        self.graph = Graph()
        self.mycomind_schema: Dict[str, Any] = {
            "@context": {
                "@vocab": "https://schema.org/",
                "myco": "https://mycomind.org/schema/"
            },
            "@type": "Schema",
            "name": "Converted MycoMind Schema",
            "description": "Schema converted from RDF/JSON-LD ontology",
            "version": "1.0.0",
            "entities": {}
        }
        self.entity_uris = set()
        self.property_uris = set()

    def load_ontology(self, input_path: str):
        """Loads an RDF/JSON-LD ontology file."""
        try:
            self.graph.parse(input_path, format="json-ld")
            logger.info(f"Successfully loaded ontology from {input_path}")
        except Exception as e:
            raise OntologyConverterError(f"Failed to load ontology: {e}")

    def convert(self) -> Dict[str, Any]:
        """Performs the conversion from RDF graph to MycoMind schema."""
        self._extract_entities()
        self._extract_properties_and_relationships()
        self._add_schema_metadata()
        return self.mycomind_schema

    def _extract_entities(self):
        """Extracts rdfs:Class definitions as MycoMind entities."""
        for s, p, o in self.graph.triples((None, RDF.type, RDFS.Class)):
            # Exclude common RDF/OWL classes that are not user-defined entities
            if s in [RDFS.Class, RDF.Property, OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty]:
                continue
            
            # Get local name for the entity type
            entity_name = self._get_local_name(s)
            if not entity_name:
                logger.warning(f"Could not determine local name for entity URI: {s}")
                continue

            self.entity_uris.add(s)

            entity_def = {
                "@type": "Class",
                "description": self._get_literal_value(s, RDFS.comment),
                "properties": {},
                "relationships": {}
            }
            
            # Add rdfs:label as a default 'name' property if not explicitly defined later
            label = self._get_literal_value(s, RDFS.label)
            if label:
                entity_def['properties']['name'] = {
                    "type": "string",
                    "required": True,
                    "description": f"Name of the {entity_name.lower()}",
                    "default_value_from_label": True # Custom flag for converter
                }

            self.mycomind_schema['entities'][entity_name] = entity_def
            logger.debug(f"Extracted entity: {entity_name}")

    def _extract_properties_and_relationships(self):
        """Extracts rdf:Property definitions and maps them to entities."""
        for s, p, o in self.graph.triples((None, RDF.type, RDF.Property)):
            # Exclude properties that are part of RDF/RDFS/OWL itself
            if s.startswith(str(RDF)) or s.startswith(str(RDFS)) or s.startswith(str(OWL)):
                continue
            
            prop_name = self._get_local_name(s)
            if not prop_name:
                logger.warning(f"Could not determine local name for property URI: {s}")
                continue
            
            self.property_uris.add(s)

            # Get domain and range
            domains = list(self.graph.objects(s, SCHEMA.domainIncludes))
            ranges = list(self.graph.objects(s, SCHEMA.rangeIncludes))

            prop_comment = self._get_literal_value(s, RDFS.comment)
            prop_label = self._get_literal_value(s, RDFS.label) or prop_name

            # Determine if it's a data property or object property (relationship)
            is_relationship = False
            target_entity_name = None
            prop_type = "string" # Default to string

            if ranges:
                for r in ranges:
                    if r in self.entity_uris: # Range is one of our defined entities
                        is_relationship = True
                        target_entity_name = self._get_local_name(r)
                        break
                    elif r == XSD.string:
                        prop_type = "string"
                    elif r == XSD.integer:
                        prop_type = "integer"
                    elif r == XSD.decimal or r == XSD.float or r == XSD.double:
                        prop_type = "number"
                    elif r == XSD.boolean:
                        prop_type = "boolean"
                    elif r == XSD.date:
                        prop_type = "string" # MycoMind uses string for date, with 'format'
                        prop_format = "date"
                    elif r == XSD.dateTime:
                        prop_type = "string"
                        prop_format = "datetime"
                    elif r == XSD.anyURI:
                        prop_type = "string"
                        prop_format = "uri"
                    # Add more XSD types as needed

            # Assign to relevant entities based on domainIncludes
            for domain_uri in domains:
                domain_entity_name = self._get_local_name(domain_uri)
                if domain_entity_name in self.mycomind_schema['entities']:
                    entity_def = self.mycomind_schema['entities'][domain_entity_name]

                    if is_relationship and target_entity_name:
                        # Add to relationships
                        entity_def['relationships'][prop_name] = {
                            "target": target_entity_name,
                            "description": prop_comment or f"Related {target_entity_name.lower()}",
                            # "bidirectional": False # RDF doesn't explicitly state this, assume unidirectional unless inverseOf is used
                        }
                        logger.debug(f"  Added relationship '{prop_name}' to {domain_entity_name} targeting {target_entity_name}")
                    else:
                        # Add to properties
                        prop_def = {
                            "type": prop_type,
                            "description": prop_comment or f"The {prop_label.lower()}",
                            "required": False # RDF doesn't explicitly state required, assume optional
                        }
                        if 'prop_format' in locals(): # Add format if determined
                            prop_def['format'] = prop_format
                        
                        # Check if this property is already defined as 'name' from rdfs:label
                        if prop_name == 'name' and 'name' in entity_def['properties'] and \
                           entity_def['properties']['name'].get('default_value_from_label'):
                            # If 'name' was added from rdfs:label, and we now have an explicit hyphal:name property,
                            # use the explicit one and remove the default_value_from_label flag.
                            # This assumes hyphal:name is the canonical name property.
                            entity_def['properties']['name'].update(prop_def)
                            entity_def['properties']['name'].pop('default_value_from_label', None)
                        else:
                            entity_def['properties'][prop_name] = prop_def
                        logger.debug(f"  Added property '{prop_name}' to {domain_entity_name}")
                else:
                    logger.warning(f"Domain entity '{domain_entity_name}' not found for property '{prop_name}'")

    def _add_schema_metadata(self):
        """Adds overall schema metadata like name and version."""
        # Attempt to find a schema name/description from common ontology properties
        # This is a heuristic and might need refinement for very diverse ontologies.
        
        # Try to find a main ontology URI and its label/comment
        ontology_uri = None
        for s, p, o in self.graph.triples((None, RDF.type, OWL.Ontology)):
            ontology_uri = s
            break
        
        if ontology_uri:
            schema_name = self._get_literal_value(ontology_uri, RDFS.label)
            if schema_name:
                self.mycomind_schema['name'] = schema_name
            
            schema_comment = self._get_literal_value(ontology_uri, RDFS.comment)
            if schema_comment:
                self.mycomind_schema['description'] = schema_comment
        
        # If no specific ontology URI found, try to infer from the graph itself
        if self.mycomind_schema['name'] == "Converted MycoMind Schema":
            # Try to use the input file name as a default
            # This would require passing the input_path to this method, or inferring it.
            # For now, keep the generic default if no explicit ontology URI is found.
            pass

        # Versioning is not standard in RDF/RDFS, might need to be manual or inferred
        # For now, keep default 1.0.0

    def _get_local_name(self, uri: URIRef) -> str:
        """Extracts the local name from a URI, handling common prefixes."""
        # Use graph's namespace manager first for registered prefixes
        for prefix, ns_uri in self.graph.namespace_manager.namespaces():
            if str(uri).startswith(str(ns_uri)):
                return str(uri).replace(str(ns_uri), "")
        
        # Fallback for common well-known namespaces if not explicitly bound in graph
        # This list can be expanded as needed
        common_namespaces = {
            "http://example.org/hyphaltips-ontology#": "hyphal", # Keep this for user's specific case, but make it a fallback
            "http://schema.org/": "schema",
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://www.w3.org/2002/07/owl#": "owl",
            "http://purl.org/dc/elements/1.1/": "dc",
            "http://purl.org/dc/terms/": "dcterms",
            "http://xmlns.com/foaf/0.1/": "foaf",
            "http://www.w3.org/ns/prov#": "prov",
            "http://www.w3.org/2004/02/skos/core#": "skos"
        }
        
        for ns_uri_str, prefix in common_namespaces.items():
            if str(uri).startswith(ns_uri_str):
                return str(uri).replace(ns_uri_str, "")

        # Last resort: get fragment or last path segment
        if "#" in str(uri):
            return str(uri).split("#")[-1]
        if "/" in str(uri):
            return str(uri).split("/")[-1]
        return ""

    def _get_literal_value(self, subject: URIRef, predicate: URIRef) -> Optional[str]:
        """Helper to get a single literal value for a predicate."""
        for o in self.graph.objects(subject, predicate):
            if isinstance(o, Literal):
                return str(o)
        return None

def main():
    parser = argparse.ArgumentParser(description="Convert RDF/JSON-LD ontology to MycoMind JSON schema.")
    parser.add_argument("input_ontology", help="Path to the input RDF/JSON-LD ontology file.")
    parser.add_argument("output_schema", help="Path for the output MycoMind JSON schema file.")
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging.')
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')

    converter = OntologyConverter()
    try:
        converter.load_ontology(args.input_ontology)
        mycomind_schema = converter.convert()
        
        with open(args.output_schema, 'w', encoding='utf-8') as f:
            json.dump(mycomind_schema, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Successfully converted ontology and saved to {args.output_schema}")
        print(f"Conversion successful! MycoMind schema saved to: {args.output_schema}")
        print("\n--- Generated MycoMind Schema ---")
        print(json.dumps(mycomind_schema, indent=2, ensure_ascii=False))

    except OntologyConverterError as e:
        logger.error(f"Conversion failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"Input ontology file not found: {args.input_ontology}")
        print(f"Error: Input ontology file not found at {args.input_ontology}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
