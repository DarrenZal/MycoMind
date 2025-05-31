#!/usr/bin/env python3
"""
MycoMind Knowledge Graph Demo

This script demonstrates the complete MycoMind workflow using a realistic
example of a personal knowledge management project. It processes an unstructured
text document about the MycoMind project, extracts entities including a HyphalTip
and a RegenerativePerson, converts to JSON-LD, loads into a graph database,
and demonstrates SPARQL querying.

Usage:
    python mycomind_demo.py
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from yaml_to_jsonld_converter import YAMLToJSONLDConverter
from graph_db_client import MycoMindGraphClient
from setup_fuseki import FusekiSetup


def run_mycomind_demo():
    """
    Run the complete MycoMind workflow demonstration using the realistic project example.
    """
    print("🧠 MycoMind Knowledge Graph Demo")
    print("=" * 50)
    print("This demo shows the complete workflow from unstructured text to queryable knowledge graph")
    print("using a realistic example of a personal knowledge management project.\n")
    
    # Step 1: Check Fuseki setup
    print("📋 Step 1: Checking Fuseki Setup")
    print("-" * 30)
    
    fuseki_setup = FusekiSetup()
    
    if not fuseki_setup.fuseki_jar.exists():
        print("❌ Fuseki not found. Please run:")
        print("   cd scripts && python setup_fuseki.py --download")
        return False
    
    # Start Fuseki if not running
    if not fuseki_setup.is_running():
        print("🔄 Starting Fuseki server...")
        if not fuseki_setup.start_server():
            print("❌ Failed to start Fuseki server")
            return False
    else:
        print("✅ Fuseki server is already running")
    
    # Step 2: Process the sample document
    print("\n📄 Step 2: Processing Sample Document")
    print("-" * 30)
    
    # Path to our sample document
    sample_doc = Path(__file__).parent / "sample_data" / "mycomind_project.txt"
    schema_path = Path(__file__).parent.parent / "schemas" / "hyphaltips_mycomind_schema.json"
    
    if not sample_doc.exists():
        print(f"❌ Sample document not found: {sample_doc}")
        return False
    
    if not schema_path.exists():
        print(f"❌ Schema not found: {schema_path}")
        return False
    
    print(f"✅ Found sample document: {sample_doc.name}")
    print(f"✅ Found schema: {schema_path.name}")
    
    # Show a preview of the document
    with open(sample_doc, 'r') as f:
        content = f.read()
        preview = content[:300] + "..." if len(content) > 300 else content
        print(f"\n📖 Document preview:")
        print(f"   {preview}")
    
    # Step 3: Extract entities using ETL pipeline
    print(f"\n🔄 Step 3: Extracting Entities from Document")
    print("-" * 30)
    
    # Import ETL modules
    try:
        from main_etl import MycoMindETL
        
        # Initialize ETL pipeline
        etl = MycoMindETL()
        
        # Process the document
        print("🤖 Running AI extraction on the document...")
        result = etl.process_data_source(
            source=str(sample_doc),
            schema_path=str(schema_path),
            output_index=False
        )
        
        if result.success and result.entities:
            print(f"✅ Extracted {len(result.entities)} entities:")
            for entity in result.entities:
                entity_type = entity.get('type', 'Unknown')
                entity_name = entity.get('properties', {}).get('name', 'Unnamed')
                confidence = entity.get('confidence', 0)
                print(f"   • {entity_name} ({entity_type}) - confidence: {confidence:.2f}")
        else:
            print("❌ No entities extracted or extraction failed")
            if result.errors:
                for error in result.errors[:3]:
                    print(f"   Error: {error}")
            return False
            
    except Exception as e:
        print(f"❌ Error during entity extraction: {e}")
        print("This might be due to missing LLM configuration or API keys.")
        print("For demo purposes, we'll create sample extracted entities...")
        
        # Create sample entities that would be extracted
        result = type('Result', (), {
            'success': True,
            'entities': [
                {
                    'type': 'HyphalTip',
                    'properties': {
                        'name': 'MycoMind',
                        'description': 'Personal knowledge management system using AI and knowledge graphs',
                        'activityStatus': 'alive'
                    },
                    'relationships': {
                        'collaborator': ['[[Shawn]]']
                    },
                    'confidence': 0.95,
                    'source_context': 'MycoMind - personal knowledge management system'
                },
                {
                    'type': 'RegenerativePerson',
                    'properties': {
                        'name': 'Shawn',
                        'bio': 'Brilliant developer with background in semantic web technologies',
                        'location': 'Portland',
                        'expertise': ['semantic web technologies', 'bioregional mapping', 'community resilience'],
                        'interests': ['Transition Towns movement', 'knowledge commons', 'open source tools'],
                        'domainTags': ['regenerative systems', 'community resilience'],
                        'methodTags': ['semantic web', 'open source'],
                        'currentRole': 'Consultant'
                    },
                    'relationships': {
                        'collaboratesWith': ['[[MycoMind Author]]']
                    },
                    'confidence': 0.88,
                    'source_context': 'Shawn is this brilliant developer I met at a conference'
                }
            ],
            'errors': []
        })()
        
        print(f"✅ Created {len(result.entities)} sample entities:")
        for entity in result.entities:
            entity_type = entity.get('type', 'Unknown')
            entity_name = entity.get('properties', {}).get('name', 'Unnamed')
            confidence = entity.get('confidence', 0)
            print(f"   • {entity_name} ({entity_type}) - confidence: {confidence:.2f}")
    
    # Step 4: Convert to JSON-LD (simulating the YAML frontmatter step)
    print(f"\n🔄 Step 4: Converting to JSON-LD")
    print("-" * 30)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create markdown files with YAML frontmatter (simulating obsidian_utils output)
        markdown_files = []
        
        for entity in result.entities:
            entity_name = entity.get('properties', {}).get('name', 'unnamed')
            safe_name = "".join(c for c in entity_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            filename = f"{safe_name.lower().replace(' ', '_')}.md"
            filepath = temp_path / filename
            
            # Create YAML frontmatter
            frontmatter = {
                'type': entity.get('type'),
                'extraction_confidence': entity.get('confidence', 0),
                'source': str(sample_doc),
                'created': '2025-05-30T17:00:00'
            }
            
            # Add properties
            for prop, value in entity.get('properties', {}).items():
                frontmatter[prop] = value
            
            # Add relationships
            for rel, targets in entity.get('relationships', {}).items():
                frontmatter[rel] = targets
            
            # Create markdown content
            content = f"""---
{chr(10).join(f"{k}: {repr(v) if isinstance(v, (list, dict)) else v}" for k, v in frontmatter.items())}
---

# {entity_name}

{entity.get('source_context', 'Extracted entity from MycoMind project document.')}

This entity was automatically extracted from the source document using AI-powered knowledge extraction.
"""
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            markdown_files.append(filepath)
            print(f"   📝 Created: {filename}")
        
        # Convert YAML frontmatter to JSON-LD
        try:
            converter = YAMLToJSONLDConverter(str(schema_path))
            entities = converter.process_directory(str(temp_path))
            
            if entities:
                output_path = temp_path / "mycomind_knowledge_graph.jsonld"
                success = converter.export_jsonld(entities, str(output_path))
                
                if success:
                    print(f"✅ Converted {len(entities)} entities to JSON-LD")
                    
                    # Show JSON-LD preview
                    with open(output_path, 'r') as f:
                        jsonld_content = f.read()
                        preview = jsonld_content[:400] + "..." if len(jsonld_content) > 400 else jsonld_content
                        print(f"\n📄 JSON-LD preview:")
                        print(f"   {preview}")
                else:
                    print("❌ Failed to export JSON-LD")
                    return False
            else:
                print("❌ No entities converted to JSON-LD")
                return False
                
        except Exception as e:
            print(f"❌ Error during JSON-LD conversion: {e}")
            return False
        
        # Step 5: Load into graph database
        print(f"\n📊 Step 5: Loading into Graph Database")
        print("-" * 30)
        
        try:
            client = MycoMindGraphClient()
            
            # Test connection
            if not client.test_connection():
                print("❌ Cannot connect to Fuseki server")
                return False
            
            # Create dataset
            client.create_dataset()
            
            # Load data
            if client.load_jsonld(str(output_path)):
                print("✅ Data loaded successfully into graph database")
            else:
                print("❌ Failed to load data")
                return False
                
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
        
        # Step 6: Query the knowledge graph
        print(f"\n🔍 Step 6: Querying the Knowledge Graph")
        print("-" * 30)
        
        try:
            # Get statistics
            stats = client.get_stats()
            if stats:
                print(f"📊 Knowledge Graph Statistics:")
                print(f"   • Total Entities: {stats['total_entities']}")
                print(f"   • Unique Types: {stats['unique_types']}")
                print(f"   • Total Relationships: {stats['total_relationships']}")
            
            # Custom queries for our demo
            print(f"\n🔍 Demo Queries:")
            
            # Query 1: Find the HyphalTip
            print(f"\n1️⃣ Finding HyphalTips:")
            hyphal_query = """
            SELECT ?tip ?name ?description ?status WHERE {
                ?tip a myco:HyphalTip ;
                     myco:name ?name .
                OPTIONAL { ?tip myco:description ?description }
                OPTIONAL { ?tip myco:activityStatus ?status }
            }
            """
            result = client.query(hyphal_query)
            if result:
                client.print_query_results(result)
            
            # Query 2: Find RegenerativePerson entities
            print(f"\n2️⃣ Finding RegenerativePerson entities:")
            person_query = """
            SELECT ?person ?name ?bio ?location ?role WHERE {
                ?person a myco:RegenerativePerson ;
                        myco:name ?name .
                OPTIONAL { ?person myco:bio ?bio }
                OPTIONAL { ?person myco:location ?location }
                OPTIONAL { ?person myco:currentRole ?role }
            }
            """
            result = client.query(person_query)
            if result:
                client.print_query_results(result)
            
            # Query 3: Find collaboration relationships
            print(f"\n3️⃣ Finding collaboration relationships:")
            collab_query = """
            SELECT ?entity1 ?name1 ?relationship ?entity2 ?name2 WHERE {
                ?entity1 myco:name ?name1 ;
                         ?predicate ?entity2 .
                ?entity2 myco:name ?name2 .
                FILTER(STRSTARTS(STR(?predicate), STR(myco:)))
                BIND(STRAFTER(STR(?predicate), STR(myco:)) as ?relationship)
                FILTER(?relationship IN ("collaborator", "collaboratesWith"))
            }
            """
            result = client.query(collab_query)
            if result:
                client.print_query_results(result)
            
            # Query 4: Find entities by expertise/domain
            print(f"\n4️⃣ Finding entities with semantic web expertise:")
            expertise_query = """
            SELECT ?person ?name ?expertise WHERE {
                ?person a myco:RegenerativePerson ;
                        myco:name ?name ;
                        myco:expertise ?expertise .
                FILTER(CONTAINS(LCASE(?expertise), "semantic"))
            }
            """
            result = client.query(expertise_query)
            if result:
                client.print_query_results(result)
            
        except Exception as e:
            print(f"❌ Error querying data: {e}")
            return False
    
    # Step 7: Summary and next steps
    print(f"\n🎉 Demo Complete!")
    print("-" * 30)
    
    print("✅ Successfully demonstrated the MycoMind workflow:")
    print("   1. ✅ Processed unstructured text about MycoMind project")
    print("   2. ✅ Extracted HyphalTip and RegenerativePerson entities")
    print("   3. ✅ Converted to JSON-LD using combined schema")
    print("   4. ✅ Loaded into Fuseki graph database")
    print("   5. ✅ Queried using SPARQL to find entities and relationships")
    
    print(f"\n🌐 Access Points:")
    print(f"   • Web Interface: http://localhost:3030")
    print(f"   • SPARQL Endpoint: http://localhost:3030/mycomind/sparql")
    print(f"   • Interactive Client: python scripts/graph_db_client.py --interactive")
    
    print(f"\n📚 Try These Queries in the Web Interface:")
    print(f"   • List all entities: SELECT ?s ?p ?o WHERE {{ ?s ?p ?o }} LIMIT 20")
    print(f"   • Find people in Portland: SELECT ?person ?name WHERE {{ ?person myco:location \"Portland\" ; myco:name ?name }}")
    print(f"   • Find active projects: SELECT ?project ?name WHERE {{ ?project myco:activityStatus \"alive\" ; myco:name ?name }}")
    
    return True


def main():
    """Main entry point."""
    try:
        success = run_mycomind_demo()
        if success:
            print(f"\n🎊 MycoMind demo completed successfully!")
            print(f"You now have a working knowledge graph with HyphalTips and RegenerativePerson entities!")
            return 0
        else:
            print(f"\n❌ Demo failed. Check the error messages above.")
            return 1
    except KeyboardInterrupt:
        print(f"\n⏹️  Demo interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
