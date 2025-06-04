# MycoMind Step-by-Step Example

This guide walks you through the complete MycoMind workflow using the included sample data. You'll start with unstructured text and end up with a queryable knowledge graph.

## Prerequisites

1. **Java 17 or 21** installed (for Neo4j 5.x graph database)
2. **OpenAI API key** (or compatible LLM service)
3. **Python dependencies** installed: `pip install -r scripts/requirements.txt`

## Step 0: Choose Your Graph Database

MycoMind supports two graph database backends:

- **🔥 Neo4j** (Recommended) - Visual graph exploration with Cypher queries
- **Apache Jena Fuseki** - Standard SPARQL endpoint for semantic web applications

This guide covers **Neo4j** as the primary option. For Fuseki setup, see the bottom of this document.

## Step 1: Setup Configuration

```bash
# Copy the example configuration
cp examples/config_example.json config.json

# Edit config.json and make these changes:
# 1. Change "your_openai_api_key_here" to your actual OpenAI API key
# 2. Update "vault_path": "./demo_vault" to your desired output path
#    For this demo, you can use: "./demo_vault" (creates a demo_vault folder)
#    Or use your existing Obsidian vault: "/Users/yourname/Documents/MyObsidianVault"
```

## Step 2: Process Unstructured Text with AI Extraction

We'll use the sample document `examples/sample_data/mycomind_project.txt` which contains unstructured text about the MycoMind project and mentions collaboration with "Shawn".

```bash
# Run the ETL pipeline to extract entities from unstructured text
python scripts/main_etl.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --source examples/sample_data/mycomind_project.txt \
  --no-index
```

This will:
- Use AI to identify entities (HyphalTip, RegenerativePerson, etc.)
- Create markdown files with YAML frontmatter in your configured output directory
- Extract relationships between entities (e.g., collaboration between MycoMind and Shawn)

**Expected Output:**
- `MycoMind.md` - A HyphalTip entity with project details
- `Shawn.md` - A RegenerativePerson entity with location, expertise, etc.
- Each file will have YAML frontmatter with structured data

## Step 3: Set Up Neo4j Database

```bash
# Download and install Neo4j
python scripts/setup_neo4j.py --download

# Start the Neo4j server
python scripts/setup_neo4j.py --start
```

This will:
- Download Neo4j Community Edition 5.15.0
- Configure it for MycoMind (disable auth, set memory limits)
- Start the server on http://localhost:7474 (Bolt: bolt://localhost:7687)

## Step 4: Convert YAML Frontmatter to Neo4j Cypher

```bash
# Convert the generated markdown files to Cypher statements
python scripts/yaml_to_neo4j_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output mycomind_knowledge_graph.cypher
```

This will:
- Process all markdown files with YAML frontmatter in the `demo_vault/extracted_knowledge/` directory
- Resolve WikiLinks (`[[Shawn]]` → proper IRI references)
- Generate Cypher CREATE statements for Neo4j

## Step 5: Load Data into Neo4j

```bash
# Load the Cypher statements into Neo4j
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p '' < mycomind_knowledge_graph.cypher
```

**If the above command completes but you don't see data loaded**, try importing just the entity creation statements:

```bash
# Alternative: Import only the CREATE statements for entities
grep "^CREATE (" mycomind_knowledge_graph.cypher | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

**Verify data was loaded:**

```bash
# Check that entities were created
echo "MATCH (n) RETURN labels(n) as entity_types, count(n) as count ORDER BY count DESC;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

Alternatively, you can use the Neo4j Browser:
1. Open http://localhost:7474
2. Run `:source mycomind_knowledge_graph.cypher` (if the file is in the import directory)

This will:
- Create indexes for efficient querying
- Create nodes for all extracted entities (HyphalTip, RegenerativePerson, Organization)
- Create relationships between entities (collaborations, memberships, etc.)

## Step 6: Query Your Neo4j Knowledge Graph

### 🌐 Neo4j Browser (Recommended)

Open http://localhost:7474 in your browser for visual graph exploration and querying.

### 💻 Command Line Interface

```bash
# Quick queries via command line
echo "MATCH (n) RETURN count(n) as total_nodes;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''

# Interactive shell
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

### Sample Cypher Queries to Try

**Note:** Since the ETL pipeline uses AI, the exact entities extracted may vary between runs. These queries are designed to work with common entity types and relationships.

#### 1. **Overview Queries**

```cypher
// Count all nodes by type
MATCH (n) 
RETURN labels(n) as entity_types, count(n) as count
ORDER BY count DESC;

// Count all relationships by type
MATCH ()-[r]->() 
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;

// Show all entities with their names
MATCH (n) 
WHERE exists(n.name)
RETURN labels(n)[0] as type, n.name as name, n.description as description
ORDER BY type, name;
```

#### 2. **Find People (RegenerativePerson entities)**

```cypher
// Find all people with their details
MATCH (person:RegenerativePerson) 
RETURN person.name as name, 
       person.location as location, 
       person.currentRole as role,
       person.bio as bio
ORDER BY name;

// Find people in specific locations (adapt as needed)
MATCH (person:RegenerativePerson) 
WHERE person.location CONTAINS "Portland" OR person.location CONTAINS "Seattle"
RETURN person.name as name, person.location as location, person.currentRole as role;
```

#### 3. **Find Projects (HyphalTip entities)**

```cypher
// Find all projects/tips with their status
MATCH (tip:HyphalTip) 
RETURN tip.name as name, 
       tip.description as description, 
       tip.activityStatus as status
ORDER BY name;

// Find active projects
MATCH (tip:HyphalTip) 
WHERE tip.activityStatus = "alive" OR tip.activityStatus = "active"
RETURN tip.name as name, tip.description as description;
```

#### 4. **Find Organizations**

```cypher
// Find all organizations
MATCH (org:Organization) 
RETURN org.name as name, org.description as description
ORDER BY name;

// Find organizations and their members
MATCH (org:Organization)-[:HASMEMBER]->(member)
RETURN org.name as organization, member.name as member_name
ORDER BY organization, member_name;
```

#### 5. **Relationship Queries**

```cypher
// Find all collaboration relationships
MATCH (entity1)-[:COLLABORATOR|:COLLABORATESWITH]-(entity2)
RETURN entity1.name as collaborator1, entity2.name as collaborator2
ORDER BY collaborator1, collaborator2;

// Find all relationships in the graph
MATCH (n1)-[r]-(n2) 
RETURN n1.name as entity1, type(r) as relationship, n2.name as entity2
ORDER BY entity1, relationship, entity2;

// Find entities with the most connections
MATCH (n)-[r]-() 
RETURN n.name as entity, labels(n)[0] as type, count(r) as connections
ORDER BY connections DESC
LIMIT 10;
```

#### 6. **Advanced Queries**

```cypher
// Find paths between entities (adapt names as needed)
MATCH path = (start)-[*1..3]-(end)
WHERE start.name CONTAINS "MycoMind" AND end.name CONTAINS "Transition"
RETURN path
LIMIT 5;

// Find entities that are both members and collaborators
MATCH (person)-[:MEMBEROF]->(org), (person)-[:COLLABORATESWITH]->(project)
RETURN person.name as person, org.name as organization, project.name as project;

// Geographic analysis (find entities by location)
MATCH (n) 
WHERE exists(n.location)
RETURN n.location as location, count(n) as entity_count, collect(n.name) as entities
ORDER BY entity_count DESC;
```

## Expected Results

After completing this Neo4j workflow, you should have:

### 📊 **Data Loaded**
- **3+ entities** (exact number depends on AI extraction)
- **HyphalTip projects** like "MycoMind: Personal Knowledge Management System"
- **RegenerativePerson entities** like "Shawn" with location and role information
- **Organization entities** like "Transition Towns"
- **5+ relationships** connecting these entities

### 🔗 **Relationships Discovered**
- **Collaboration** relationships between people and projects
- **Membership** relationships between people and organizations
- **Geographic connections** based on location data
- **Project ownership** and contribution patterns

### 🌐 **Visualization**
- **Interactive graph** in Neo4j Browser showing node-link networks
- **Expandable nodes** with detailed properties
- **Relationship paths** showing how entities connect
- **Query results** in both table and graph formats

## Step 7: Explore Advanced Neo4j Features

### 🔧 **Neo4j Management Commands**

```bash
# Check server status
python scripts/setup_neo4j.py --install-dir scripts/neo4j --status

# Stop the server
python scripts/setup_neo4j.py --install-dir scripts/neo4j --stop

# Restart the server
python scripts/setup_neo4j.py --install-dir scripts/neo4j --restart

# View recent logs
python scripts/setup_neo4j.py --install-dir scripts/neo4j --logs
```

### 🗑️ **Completely Wipe Neo4j Database**

If you need to completely reset your Neo4j database (useful when re-running the demo or fixing index conflicts):

#### **Method 1: Database Reset via Cypher (Recommended)**

```bash
# Connect to Neo4j shell
scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''

# Then run these commands in order:
# 1. Drop all indexes and constraints first
DROP INDEX index_32dd8477 IF EXISTS;
CALL db.indexes() YIELD name CALL db.index.drop(name);
CALL db.constraints() YIELD name CALL db.constraint.drop(name);

# 2. Delete all data
MATCH (n) DETACH DELETE n;

# 3. Verify everything is clean
MATCH (n) RETURN count(n) as remaining_nodes;
CALL db.indexes() YIELD name RETURN name;
```

#### **Method 2: Complete Database Directory Removal**

```bash
# Stop Neo4j first
python scripts/setup_neo4j.py --install-dir scripts/neo4j --stop

# Remove the entire data directory
rm -rf scripts/neo4j/neo4j-community-5.15.0/data/

# Restart Neo4j (this will recreate a fresh database)
python scripts/setup_neo4j.py --install-dir scripts/neo4j --start
```

#### **Method 3: Command Line Reset (One-liner)**

```bash
# Stop, wipe, and restart in one command sequence
python scripts/setup_neo4j.py --install-dir scripts/neo4j --stop && \
rm -rf scripts/neo4j/neo4j-community-5.15.0/data/ && \
python scripts/setup_neo4j.py --install-dir scripts/neo4j --start
```

#### **Verify Clean Database**

After wiping, verify the database is clean before reloading:

```bash
# Should return 0 nodes
echo "MATCH (n) RETURN count(n) as node_count;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''

# Should return no indexes
echo "CALL db.indexes() YIELD name RETURN name;" | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''
```

#### **Common Issues When Wiping**

- **"An equivalent index already exists"** - This happens when you try to reload data without dropping indexes first. Use Method 1 above.
- **"Could not stop Neo4j server"** - The restart command may fail to stop. Use `pkill java` or manually kill Neo4j processes, then start fresh.
- **Database still shows old data** - Ensure you're connected to the correct database. Neo4j may have multiple databases.

### 📈 **Graph Analytics**

```cypher
// Analyze graph structure
CALL db.stats.retrieve('GRAPH') YIELD data RETURN data;

// Find shortest paths between entities
MATCH (start:RegenerativePerson {name: "Shawn"}), 
      (end:HyphalTip)
MATCH path = shortestPath((start)-[*..5]-(end))
RETURN path;

// Degree centrality (most connected entities)
MATCH (n)-[r]-()
RETURN n.name as entity, labels(n)[0] as type, count(r) as degree
ORDER BY degree DESC
LIMIT 10;
```

### 🎯 **Custom Schema Queries**

```cypher
// Explore the schema
CALL db.schema.visualization();

// Find all relationship types
CALL db.relationshipTypes();

// Find all node labels
CALL db.labels();

// Property key statistics
CALL db.propertyKeys();
```

## Troubleshooting

### Neo4j Issues

#### **Neo4j Won't Start**
```bash
# Check Java version (requires Java 17 or 21)
java -version

# Check if port 7474 is already in use
lsof -i :7474

# View Neo4j logs
python scripts/setup_neo4j.py --install-dir scripts/neo4j --logs

# Try starting with verbose logging
python scripts/setup_neo4j.py --install-dir scripts/neo4j --start --verbose
```

#### **Can't Connect to Neo4j Browser**
1. Verify Neo4j is running: `python scripts/setup_neo4j.py --install-dir scripts/neo4j --status`
2. Check the web interface at http://localhost:7474
3. Ensure no firewall is blocking port 7474
4. Try connecting with different browser or incognito mode

#### **Cypher Loading Errors**
- **Syntax errors**: Neo4j 5.x uses newer syntax. Check index creation format.
- **Authentication**: Default setup disables auth. If enabled, use username: `neo4j`, password: `neo4j`
- **File location**: Ensure `.cypher` file is accessible or in Neo4j import directory

### Common Issues

#### **No Entities Extracted**
If the ETL pipeline doesn't extract entities:
- Verify your OpenAI API key is correct in `config.json`
- Check that the schema file exists and is valid
- Ensure the source document contains recognizable entities
- Try increasing the LLM temperature slightly (0.1 → 0.3) for more creative extraction

#### **Queries Return No Results**
- Verify data was loaded: `MATCH (n) RETURN count(n);`
- Check node labels: `CALL db.labels();`
- Check relationship types: `CALL db.relationshipTypes();`
- Use the Neo4j Browser to visually explore the graph

---

## Alternative Setup: Apache Jena Fuseki + SPARQL

If you prefer semantic web standards and SPARQL querying:

### **Setup Fuseki**

```bash
# Download and install Apache Jena Fuseki
python scripts/setup_fuseki.py --download

# Start the Fuseki server
python scripts/setup_fuseki.py --start --port 3030

# Check status
python scripts/setup_fuseki.py --status
```

### **Convert Data to JSON-LD**

```bash
# Convert YAML frontmatter to JSON-LD instead of Cypher
python scripts/yaml_to_jsonld_converter.py \
  --schema schemas/hyphaltips_mycomind_schema.json \
  --input demo_vault/extracted_knowledge \
  --output mycomind_knowledge_graph.jsonld
```

### **Load Data into Fuseki**

```bash
# Create dataset and load data
python scripts/graph_db_client.py --create-dataset
python scripts/graph_db_client.py --load mycomind_knowledge_graph.jsonld
```

### **Query with SPARQL**

- **Web interface:** http://localhost:3030 (built-in Fuseki interface)
- **Command line:** `python scripts/graph_db_client.py --interactive`

For detailed Fuseki setup and SPARQL query examples, see the original documentation.

## Next Steps

Once you have your Neo4j knowledge graph running:

### 🚀 **Scale Up Your Knowledge Base**
1. **Process your own documents:** Point the ETL pipeline at your personal files, notes, or documents
2. **Create custom schemas:** Define your own entity types and relationships for specific domains
3. **Batch processing:** Use the `--input` directory option to process multiple files at once

### 🔧 **Customize and Extend**
4. **Build applications** that query your knowledge graph via Neo4j's drivers (Python, JavaScript, etc.)
5. **Set up automated pipelines** to continuously process new documents and update your graph
6. **Integrate with Obsidian:** Use the generated markdown files as your personal knowledge vault

### 📊 **Advanced Analytics**
7. **Network analysis:** Use Neo4j's graph algorithms to find communities, influential nodes, etc.
8. **Knowledge discovery:** Run queries to uncover hidden connections and patterns
9. **Export and share:** Generate reports or visualizations from your knowledge graph

### 🌟 **Production Deployment**
10. **Neo4j Desktop:** For larger datasets, consider Neo4j Desktop or cloud deployment
11. **Authentication:** Enable proper authentication for production use
12. **Backup strategies:** Implement regular database backups

---

**🎉 Congratulations!** You've successfully built an AI-powered knowledge graph system that transforms unstructured text into queryable, visual knowledge networks using cutting-edge LLM and graph database technologies!
