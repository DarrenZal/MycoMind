#!/usr/bin/env python3
"""
Graph Database Client for MycoMind

This script provides utilities for loading JSON-LD data into Apache Jena Fuseki
and querying the knowledge graph. It's designed to work with the MycoMind
schema system and provides both programmatic and interactive interfaces.

Usage:
    python graph_db_client.py --load data.jsonld
    python graph_db_client.py --query
    python graph_db_client.py --interactive
"""

import os
import sys
import json
import requests
import argparse
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime
import yaml

# Import MycoMind modules
from schema_parser import SchemaParser, SchemaDefinition

logger = logging.getLogger(__name__)


class MycoMindGraphClient:
    """
    Client for interacting with Apache Jena Fuseki SPARQL endpoint
    specifically designed for MycoMind knowledge graphs.
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:3030", 
                 dataset: str = "mycomind",
                 base_iri: str = "http://mycomind.org/kg/"):
        """
        Initialize the graph database client.
        
        Args:
            base_url: Fuseki server base URL
            dataset: Dataset name in Fuseki
            base_iri: Base IRI for the knowledge graph
        """
        self.base_url = base_url.rstrip('/')
        self.dataset = dataset
        self.base_iri = base_iri
        self.resource_base = f"{base_iri}resource/"
        self.ontology_base = f"{base_iri}ontology/"
        
        # Fuseki endpoints
        self.query_endpoint = f"{self.base_url}/{dataset}/sparql"
        self.update_endpoint = f"{self.base_url}/{dataset}/update"
        self.data_endpoint = f"{self.base_url}/{dataset}/data"
        
        # Common prefixes for SPARQL queries
        self.prefixes = {
            "myco": self.ontology_base,
            "resource": self.resource_base,
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "schema": "http://schema.org/",
            "dcterms": "http://purl.org/dc/terms/",
            "xsd": "http://www.w3.org/2001/XMLSchema#"
        }
        
        logger.info(f"Initialized MycoMind Graph Client for {self.base_url}/{dataset}")
    
    def test_connection(self) -> bool:
        """
        Test connection to Fuseki server.
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/$/ping", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Fuseki server is reachable")
                return True
            else:
                logger.error(f"✗ Fuseki server responded with: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ Cannot reach Fuseki server: {e}")
            return False
    
    def create_dataset(self) -> bool:
        """
        Create the dataset if it doesn't exist.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if dataset exists
            response = requests.get(f"{self.base_url}/$/datasets")
            if response.status_code == 200:
                datasets = response.json()
                if f"/{self.dataset}" in [ds["ds.name"] for ds in datasets.get("datasets", [])]:
                    logger.info(f"✓ Dataset '{self.dataset}' already exists")
                    return True
            
            # Create dataset
            data = {
                "dbName": self.dataset,
                "dbType": "mem"  # In-memory for now, can be changed to "tdb2" for persistence
            }
            
            response = requests.post(
                f"{self.base_url}/$/datasets",
                data=data
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✓ Created dataset '{self.dataset}'")
                return True
            else:
                logger.error(f"✗ Failed to create dataset: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error creating dataset: {e}")
            return False
    
    def load_jsonld(self, file_path: str, graph_uri: Optional[str] = None) -> bool:
        """
        Load JSON-LD file into the graph database.
        
        Args:
            file_path: Path to JSON-LD file
            graph_uri: Optional named graph URI
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            
            headers = {'Content-Type': 'application/ld+json'}
            
            url = self.data_endpoint
            if graph_uri:
                url += f"?graph={graph_uri}"
            
            response = requests.post(url, data=data, headers=headers)
            
            if response.status_code in [200, 201, 204]:
                logger.info(f"✓ Successfully loaded {file_path}")
                return True
            else:
                logger.error(f"✗ Load failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error loading file: {e}")
            return False
    
    def query(self, sparql_query: str, format: str = "json") -> Optional[Union[Dict, str]]:
        """
        Execute SPARQL SELECT query.
        
        Args:
            sparql_query: SPARQL query string
            format: Response format ('json', 'xml', 'csv', 'tsv')
            
        Returns:
            Query results or None if failed
        """
        try:
            # Add prefixes if not already present
            if not sparql_query.strip().upper().startswith('PREFIX'):
                prefix_lines = []
                for prefix, uri in self.prefixes.items():
                    prefix_lines.append(f"PREFIX {prefix}: <{uri}>")
                sparql_query = "\n".join(prefix_lines) + "\n\n" + sparql_query
            
            headers = {
                'json': 'application/sparql-results+json',
                'xml': 'application/sparql-results+xml',
                'csv': 'text/csv',
                'tsv': 'text/tab-separated-values'
            }
            
            accept_header = headers.get(format, headers['json'])
            request_headers = {'Accept': accept_header}
            data = {'query': sparql_query}
            
            response = requests.post(self.query_endpoint, data=data, headers=request_headers)
            
            if response.status_code == 200:
                if format == 'json':
                    return response.json()
                else:
                    return response.text
            else:
                logger.error(f"✗ Query failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Error executing query: {e}")
            return None
    
    def update(self, sparql_update: str) -> bool:
        """
        Execute SPARQL UPDATE query.
        
        Args:
            sparql_update: SPARQL UPDATE query string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Add prefixes if not already present
            if not sparql_update.strip().upper().startswith('PREFIX'):
                prefix_lines = []
                for prefix, uri in self.prefixes.items():
                    prefix_lines.append(f"PREFIX {prefix}: <{uri}>")
                sparql_update = "\n".join(prefix_lines) + "\n\n" + sparql_update
            
            headers = {'Content-Type': 'application/sparql-update'}
            
            response = requests.post(self.update_endpoint, data=sparql_update, headers=headers)
            
            if response.status_code in [200, 204]:
                logger.info("✓ Update executed successfully")
                return True
            else:
                logger.error(f"✗ Update failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"✗ Error executing update: {e}")
            return False
    
    def get_stats(self) -> Optional[Dict]:
        """
        Get knowledge graph statistics.
        
        Returns:
            Statistics dictionary or None if failed
        """
        stats_query = """
        SELECT 
            (COUNT(DISTINCT ?entity) as ?totalEntities)
            (COUNT(DISTINCT ?type) as ?uniqueTypes) 
            (COUNT(?relationship) as ?totalRelationships)
        WHERE {
            ?entity a ?type .
            OPTIONAL { 
                ?entity ?predicate ?target . 
                FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
                BIND(?predicate as ?relationship)
            }
        }
        """
        
        result = self.query(stats_query)
        if result and 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            if bindings:
                stats = bindings[0]
                return {
                    'total_entities': int(stats.get('totalEntities', {}).get('value', 0)),
                    'unique_types': int(stats.get('uniqueTypes', {}).get('value', 0)),
                    'total_relationships': int(stats.get('totalRelationships', {}).get('value', 0))
                }
        return None
    
    def find_entities_by_type(self, entity_type: str, limit: int = 10) -> List[Dict]:
        """
        Find entities by type.
        
        Args:
            entity_type: Entity type to search for
            limit: Maximum number of results
            
        Returns:
            List of entities
        """
        query = f"""
        SELECT ?entity ?name ?description WHERE {{
            ?entity a myco:{entity_type} ;
                    myco:name ?name .
            OPTIONAL {{ ?entity myco:description ?description }}
        }}
        LIMIT {limit}
        """
        
        result = self.query(query)
        entities = []
        
        if result and 'results' in result and 'bindings' in result['results']:
            for binding in result['results']['bindings']:
                entity = {
                    'iri': binding.get('entity', {}).get('value', ''),
                    'name': binding.get('name', {}).get('value', ''),
                    'description': binding.get('description', {}).get('value', '')
                }
                entities.append(entity)
        
        return entities
    
    def find_relationships(self, entity_iri: str) -> List[Dict]:
        """
        Find all relationships for an entity.
        
        Args:
            entity_iri: IRI of the entity
            
        Returns:
            List of relationships
        """
        query = f"""
        SELECT ?predicate ?object ?objectName WHERE {{
            <{entity_iri}> ?predicate ?object .
            FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
            OPTIONAL {{ ?object myco:name ?objectName }}
        }}
        """
        
        result = self.query(query)
        relationships = []
        
        if result and 'results' in result and 'bindings' in result['results']:
            for binding in result['results']['bindings']:
                rel = {
                    'predicate': binding.get('predicate', {}).get('value', ''),
                    'object': binding.get('object', {}).get('value', ''),
                    'object_name': binding.get('objectName', {}).get('value', '')
                }
                relationships.append(rel)
        
        return relationships
    
    def search_entities(self, search_term: str, limit: int = 10) -> List[Dict]:
        """
        Search entities by name or description.
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results
            
        Returns:
            List of matching entities
        """
        query = f"""
        SELECT ?entity ?name ?description ?type WHERE {{
            ?entity a ?type ;
                    myco:name ?name .
            OPTIONAL {{ ?entity myco:description ?description }}
            FILTER(
                CONTAINS(LCASE(?name), LCASE("{search_term}")) ||
                CONTAINS(LCASE(?description), LCASE("{search_term}"))
            )
        }}
        LIMIT {limit}
        """
        
        result = self.query(query)
        entities = []
        
        if result and 'results' in result and 'bindings' in result['results']:
            for binding in result['results']['bindings']:
                entity = {
                    'iri': binding.get('entity', {}).get('value', ''),
                    'name': binding.get('name', {}).get('value', ''),
                    'description': binding.get('description', {}).get('value', ''),
                    'type': binding.get('type', {}).get('value', '')
                }
                entities.append(entity)
        
        return entities
    
    def get_sample_queries(self) -> Dict[str, str]:
        """
        Get sample SPARQL queries for MycoMind knowledge graphs.
        
        Returns:
            Dictionary of query names and SPARQL strings
        """
        return {
            "1. Count entities by type": """
                SELECT ?type (COUNT(?entity) as ?count) WHERE {
                    ?entity a ?type .
                    FILTER(STRSTARTS(STR(?type), STR(myco:)))
                }
                GROUP BY ?type
                ORDER BY DESC(?count)
            """,
            
            "2. List all HyphalTips": """
                SELECT ?tip ?name ?description ?status WHERE {
                    ?tip a myco:HyphalTip ;
                         myco:name ?name .
                    OPTIONAL { ?tip myco:description ?description }
                    OPTIONAL { ?tip myco:activityStatus ?status }
                }
                ORDER BY ?name
            """,
            
            "3. Find collaborations": """
                SELECT ?tip ?tipName ?collaborator ?collabName WHERE {
                    ?tip a myco:HyphalTip ;
                         myco:name ?tipName ;
                         myco:collaborator ?collaborator .
                    ?collaborator myco:name ?collabName .
                }
            """,
            
            "4. Find projects and their status": """
                SELECT ?project ?name ?status ?startDate ?endDate WHERE {
                    ?project a myco:Project ;
                             myco:name ?name .
                    OPTIONAL { ?project myco:status ?status }
                    OPTIONAL { ?project myco:startDate ?startDate }
                    OPTIONAL { ?project myco:endDate ?endDate }
                }
                ORDER BY ?startDate
            """,
            
            "5. Find entity relationships": """
                SELECT ?entity1 ?name1 ?relationship ?entity2 ?name2 WHERE {
                    ?entity1 myco:name ?name1 ;
                             ?predicate ?entity2 .
                    ?entity2 myco:name ?name2 .
                    FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
                    BIND(STRAFTER(STR(?predicate), STR(myco:)) as ?relationship)
                }
                LIMIT 20
            """,
            
            "6. Find most connected entities": """
                SELECT ?entity ?name (COUNT(?connection) as ?connectionCount) WHERE {
                    ?entity myco:name ?name .
                    {
                        ?entity ?predicate ?connection .
                        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
                    } UNION {
                        ?connection ?predicate ?entity .
                        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
                    }
                }
                GROUP BY ?entity ?name
                ORDER BY DESC(?connectionCount)
                LIMIT 10
            """,
            
            "7. Find orphaned entities": """
                SELECT ?entity ?name WHERE {
                    ?entity myco:name ?name .
                    FILTER NOT EXISTS {
                        { ?entity ?predicate ?other . FILTER(STRSTARTS(STR(?predicate), STR(myco:))) }
                        UNION
                        { ?other ?predicate ?entity . FILTER(STRSTARTS(STR(?predicate), STR(myco:))) }
                    }
                }
            """,
            
            "8. Knowledge graph statistics": """
                SELECT 
                    (COUNT(DISTINCT ?entity) as ?totalEntities)
                    (COUNT(DISTINCT ?type) as ?uniqueTypes) 
                    (COUNT(?relationship) as ?totalRelationships)
                WHERE {
                    ?entity a ?type .
                    OPTIONAL { 
                        ?entity ?predicate ?target . 
                        FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
                        BIND(?predicate as ?relationship)
                    }
                }
            """
        }
    
    def print_query_results(self, result: Dict, max_rows: int = 20) -> None:
        """
        Pretty print SPARQL query results.
        
        Args:
            result: Query result dictionary
            max_rows: Maximum number of rows to display
        """
        if 'results' in result and 'bindings' in result['results']:
            bindings = result['results']['bindings']
            
            if not bindings:
                print("No results found.")
                return
            
            # Get column headers
            headers = list(bindings[0].keys()) if bindings else []
            
            # Calculate column widths
            col_widths = {}
            for header in headers:
                col_widths[header] = max(
                    len(header),
                    max(len(str(binding.get(header, {}).get('value', ''))) for binding in bindings[:max_rows])
                )
                col_widths[header] = min(col_widths[header], 50)  # Max width of 50
            
            # Print headers
            header_row = " | ".join(f"{h:<{col_widths[h]}}" for h in headers)
            print(header_row)
            print("-" * len(header_row))
            
            # Print rows
            for i, binding in enumerate(bindings[:max_rows]):
                row = []
                for header in headers:
                    value = binding.get(header, {}).get('value', '')
                    # Truncate long values
                    if len(value) > col_widths[header]:
                        value = value[:col_widths[header]-3] + "..."
                    row.append(f"{value:<{col_widths[header]}}")
                print(" | ".join(row))
            
            total_results = len(bindings)
            if total_results > max_rows:
                print(f"\nShowing {max_rows} of {total_results} results.")
            else:
                print(f"\nFound {total_results} results.")
        else:
            print("Unexpected result format:")
            print(json.dumps(result, indent=2))


def interactive_mode(client: MycoMindGraphClient):
    """
    Interactive mode for querying the knowledge graph.
    
    Args:
        client: Graph database client
    """
    print("\n" + "="*60)
    print("MycoMind Knowledge Graph - Interactive Mode")
    print("="*60)
    
    # Test connection
    if not client.test_connection():
        print("\n❌ Cannot connect to Fuseki server.")
        print("Make sure Fuseki is running on http://localhost:3030")
        return
    
    # Get stats
    stats = client.get_stats()
    if stats:
        print(f"\n📊 Knowledge Graph Statistics:")
        print(f"   • Total Entities: {stats['total_entities']}")
        print(f"   • Unique Types: {stats['unique_types']}")
        print(f"   • Total Relationships: {stats['total_relationships']}")
    
    sample_queries = client.get_sample_queries()
    
    while True:
        print("\n" + "-"*60)
        print("Options:")
        print("  load    - Load JSON-LD file")
        print("  query   - Run a sample query")
        print("  custom  - Enter custom SPARQL query")
        print("  search  - Search entities")
        print("  stats   - Show knowledge graph statistics")
        print("  quit    - Exit")
        
        choice = input("\nEnter your choice: ").strip().lower()
        
        if choice == "quit":
            break
            
        elif choice == "load":
            file_path = input("Enter JSON-LD file path: ").strip()
            if file_path and os.path.exists(file_path):
                graph_uri = input("Enter graph URI (optional): ").strip() or None
                client.load_jsonld(file_path, graph_uri)
            else:
                print("❌ File not found or invalid path")
                
        elif choice == "query":
            print("\nSample queries:")
            for key in sample_queries.keys():
                print(f"  {key}")
            
            query_choice = input("\nEnter query number: ").strip()
            query_key = next((k for k in sample_queries.keys() if k.startswith(query_choice)), None)
            
            if query_key:
                print(f"\nExecuting: {query_key}")
                print("-" * 50)
                result = client.query(sample_queries[query_key])
                if result:
                    client.print_query_results(result)
            else:
                print("❌ Invalid query number")
                
        elif choice == "custom":
            print("\nEnter your SPARQL query (end with empty line):")
            query_lines = []
            while True:
                line = input()
                if not line:
                    break
                query_lines.append(line)
            
            custom_query = "\n".join(query_lines)
            if custom_query.strip():
                result = client.query(custom_query)
                if result:
                    client.print_query_results(result)
                    
        elif choice == "search":
            search_term = input("Enter search term: ").strip()
            if search_term:
                entities = client.search_entities(search_term)
                if entities:
                    print(f"\nFound {len(entities)} entities:")
                    for entity in entities:
                        print(f"  • {entity['name']} ({entity['type']})")
                        if entity['description']:
                            print(f"    {entity['description'][:100]}...")
                else:
                    print("No entities found.")
                    
        elif choice == "stats":
            stats = client.get_stats()
            if stats:
                print(f"\n📊 Knowledge Graph Statistics:")
                print(f"   • Total Entities: {stats['total_entities']}")
                print(f"   • Unique Types: {stats['unique_types']}")
                print(f"   • Total Relationships: {stats['total_relationships']}")
            else:
                print("❌ Could not retrieve statistics")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='MycoMind Graph Database Client')
    parser.add_argument('--load', '-l', help='Load JSON-LD file into graph database')
    parser.add_argument('--query', '-q', help='Execute SPARQL query from file')
    parser.add_argument('--interactive', '-i', action='store_true', help='Start interactive mode')
    parser.add_argument('--server', default='http://localhost:3030', help='Fuseki server URL')
    parser.add_argument('--dataset', default='mycomind', help='Dataset name')
    parser.add_argument('--base-iri', default='http://mycomind.org/kg/', help='Base IRI for knowledge graph')
    parser.add_argument('--graph-uri', help='Named graph URI for loading data')
    parser.add_argument('--create-dataset', action='store_true', help='Create dataset if it doesn\'t exist')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Initialize client
        client = MycoMindGraphClient(args.server, args.dataset, args.base_iri)
        
        # Test connection
        if not client.test_connection():
            logger.error("Cannot connect to Fuseki server. Make sure it's running.")
            return 1
        
        # Create dataset if requested
        if args.create_dataset:
            if not client.create_dataset():
                logger.error("Failed to create dataset")
                return 1
        
        # Load data if specified
        if args.load:
            if not client.load_jsonld(args.load, args.graph_uri):
                logger.error("Failed to load data")
                return 1
        
        # Execute query if specified
        if args.query:
            if os.path.exists(args.query):
                with open(args.query, 'r') as f:
                    query = f.read()
            else:
                query = args.query
            
            result = client.query(query)
            if result:
                client.print_query_results(result)
            else:
                logger.error("Query failed")
                return 1
        
        # Start interactive mode if requested
        if args.interactive:
            interactive_mode(client)
        
        # If no specific action, show help
        if not any([args.load, args.query, args.interactive, args.create_dataset]):
            parser.print_help()
        
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
