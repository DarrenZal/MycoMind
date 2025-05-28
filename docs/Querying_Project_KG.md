# Querying the Project's Knowledge Graph

## Overview

MycoMind practices what it preaches by maintaining its own documentation and codebase as a queryable knowledge graph. This advanced feature demonstrates the power of the system while providing a unique way to explore and understand the project itself.

## What is the Project Knowledge Graph?

The Project Knowledge Graph is a Neo4j-compatible graph database that contains:
- **Code Structure**: Functions, classes, modules, and their relationships
- **Documentation**: Sections, concepts, and cross-references
- **Architecture**: Components, dependencies, and data flows
- **Features**: Capabilities, implementations, and usage patterns

This "dogfooding" approach serves multiple purposes:
1. **Demonstrates MycoMind's capabilities** with real-world complexity
2. **Provides deep queryability** beyond traditional documentation
3. **Enables architectural analysis** and code exploration
4. **Shows practical examples** of knowledge graph applications

## Prerequisites

To use the Project Knowledge Graph, you'll need:

### Required Software
- **Neo4j Desktop** (recommended) or **Neo4j Community Server**
- **Docker** (alternative installation method)
- **Web browser** for Neo4j Browser interface

### Installation Options

#### Option 1: Neo4j Desktop (Recommended)
1. Download Neo4j Desktop from [neo4j.com/download](https://neo4j.com/download/)
2. Install and create a new project
3. Create a new database (Graph DBMS)
4. Start the database

#### Option 2: Docker
```bash
# Pull and run Neo4j container
docker run \
    --name mycomind-neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/mycomind123 \
    neo4j:latest
```

#### Option 3: Cloud Instance
- Use Neo4j Aura (cloud service)
- Follow setup instructions at [neo4j.com/aura](https://neo4j.com/aura/)

## Setup Instructions

### Step 1: Prepare the Database

1. **Start your Neo4j instance**
2. **Open Neo4j Browser** (usually at http://localhost:7474)
3. **Connect** using your credentials
4. **Clear any existing data** (if needed):
   ```cypher
   MATCH (n) DETACH DELETE n
   ```

### Step 2: Load the Project Knowledge Graph

1. **Copy the data files** to your Neo4j import directory:
   ```bash
   # If using Docker
   cp project_knowledge_graph/mycomind_kg.cypher $HOME/neo4j/import/
   
   # If using Neo4j Desktop
   # Copy to the import folder shown in Neo4j Desktop
   ```

2. **Load the data** using the provided Cypher script:
   ```cypher
   // In Neo4j Browser, run:
   :auto USING PERIODIC COMMIT 500
   LOAD CSV WITH HEADERS FROM 'file:///mycomind_kg.cypher' AS row
   // The actual import commands are in the .cypher file
   ```

   Or execute the script directly:
   ```bash
   # If you have cypher-shell installed
   cat project_knowledge_graph/mycomind_kg.cypher | cypher-shell -u neo4j -p your-password
   ```

### Step 3: Verify the Import

Run this query to check that data was loaded successfully:
```cypher
MATCH (n) 
RETURN labels(n) as NodeTypes, count(n) as Count
ORDER BY Count DESC
```

You should see output similar to:
```
NodeTypes          Count
["PythonFunction"] 45
["DocSection"]     28
["PythonClass"]    12
["Feature"]        8
["Schema"]         5
```

## Meta-Schema: Understanding the Knowledge Graph Structure

### Node Labels (Entity Types)

#### Code-Related Nodes
- **`PythonFunction`**: Individual functions in the codebase
- **`PythonClass`**: Classes and their methods
- **`PythonModule`**: Python files and modules
- **`PythonVariable`**: Important variables and constants

#### Documentation Nodes
- **`DocSection`**: Sections within documentation files
- **`DocFile`**: Documentation files
- **`Concept`**: Key concepts and ideas
- **`Example`**: Code examples and usage patterns

#### Architecture Nodes
- **`Component`**: System components and modules
- **`Feature`**: Functional capabilities
- **`Schema`**: JSON-LD schema definitions
- **`Configuration`**: Configuration options and settings

### Relationship Types

#### Code Relationships
- **`CALLS`**: Function A calls Function B
- **`IMPORTS`**: Module A imports Module B
- **`INHERITS`**: Class A inherits from Class B
- **`DEFINES`**: Module defines Function/Class
- **`USES`**: Function uses Variable/Constant

#### Documentation Relationships
- **`DESCRIBES`**: Documentation describes Code/Feature
- **`REFERENCES`**: Document references another Document/Concept
- **`CONTAINS`**: File contains Section
- **`EXPLAINS`**: Section explains Concept
- **`EXEMPLIFIES`**: Example demonstrates Concept

#### Architecture Relationships
- **`IMPLEMENTS`**: Code implements Feature
- **`DEPENDS_ON`**: Component depends on Component
- **`CONFIGURES`**: Configuration affects Component
- **`VALIDATES`**: Schema validates Data

### Node Properties

#### Common Properties
```cypher
// All nodes have these base properties
{
  name: "Entity Name",
  type: "EntityType", 
  created: "2024-01-15T10:30:00Z",
  source_file: "path/to/source.py",
  line_number: 42
}
```

#### Function-Specific Properties
```cypher
// PythonFunction nodes
{
  name: "extract_entities",
  signature: "extract_entities(text: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]",
  docstring: "Extract entities from text using the provided schema",
  complexity: "medium",
  parameters: ["text", "schema"],
  return_type: "List[Dict[str, Any]]"
}
```

#### Documentation Properties
```cypher
// DocSection nodes
{
  name: "Configuration Guide",
  heading_level: 1,
  word_count: 1250,
  section_type: "guide",
  topics: ["configuration", "setup", "environment"]
}
```

## Example Queries

### Basic Exploration

#### 1. Overview of the Project Structure
```cypher
// Get a high-level view of the project
MATCH (n)
RETURN labels(n)[0] as NodeType, count(n) as Count
ORDER BY Count DESC
```

#### 2. Find All Python Functions
```cypher
// List all functions with their modules
MATCH (f:PythonFunction)-[:DEFINED_IN]->(m:PythonModule)
RETURN f.name as Function, m.name as Module, f.signature as Signature
ORDER BY Module, Function
```

#### 3. Explore Documentation Structure
```cypher
// Show documentation hierarchy
MATCH (file:DocFile)-[:CONTAINS]->(section:DocSection)
RETURN file.name as Document, 
       collect(section.name) as Sections
ORDER BY Document
```

### Code Analysis Queries

#### 4. Find Functions in a Specific Module
```cypher
// Find all functions in schema_parser.py
MATCH (m:PythonModule {name: "schema_parser.py"})-[:DEFINES]->(f:PythonFunction)
RETURN f.name as Function, 
       f.signature as Signature,
       f.docstring as Description
ORDER BY f.name
```

#### 5. Analyze Function Dependencies
```cypher
// Show what functions a specific function calls
MATCH (f:PythonFunction {name: "main_etl"})-[:CALLS]->(called:PythonFunction)
RETURN f.name as Caller, 
       called.name as Called,
       called.signature as CalledSignature
```

#### 6. Find Most Connected Functions
```cypher
// Functions that are called by many others (high fan-in)
MATCH (f:PythonFunction)<-[:CALLS]-(caller:PythonFunction)
WITH f, count(caller) as callers
WHERE callers > 2
RETURN f.name as Function, 
       f.signature as Signature,
       callers as CalledBy
ORDER BY callers DESC
```

### Documentation Queries

#### 7. Find Documentation for a Feature
```cypher
// Show documentation sections that describe the 'Semantic Linking' feature
MATCH (feature:Feature {name: "Semantic Linking"})<-[:DESCRIBES]-(doc:DocSection)
RETURN doc.name as Section,
       doc.source_file as Document,
       doc.word_count as WordCount
```

#### 8. Cross-Reference Analysis
```cypher
// Find concepts mentioned across multiple documents
MATCH (concept:Concept)<-[:EXPLAINS]-(section:DocSection)-[:CONTAINED_IN]->(doc:DocFile)
WITH concept, collect(DISTINCT doc.name) as Documents
WHERE size(Documents) > 1
RETURN concept.name as Concept,
       Documents,
       size(Documents) as DocumentCount
ORDER BY DocumentCount DESC
```

#### 9. Find Examples for a Concept
```cypher
// Find code examples that demonstrate a specific concept
MATCH (concept:Concept {name: "Entity Extraction"})<-[:EXEMPLIFIES]-(example:Example)
RETURN example.name as Example,
       example.code_snippet as Code,
       example.description as Description
```

### Architecture Analysis

#### 10. Component Dependencies
```cypher
// Show how components depend on each other
MATCH (c1:Component)-[:DEPENDS_ON]->(c2:Component)
RETURN c1.name as Component,
       c2.name as DependsOn
ORDER BY Component
```

#### 11. Feature Implementation Mapping
```cypher
// Which code implements which features
MATCH (feature:Feature)<-[:IMPLEMENTS]-(code:PythonFunction)
RETURN feature.name as Feature,
       collect(code.name) as ImplementedBy
ORDER BY Feature
```

#### 12. Configuration Impact Analysis
```cypher
// Show what components are affected by configuration changes
MATCH (config:Configuration)-[:CONFIGURES]->(component:Component)
RETURN config.name as ConfigOption,
       component.name as AffectedComponent,
       config.description as Description
```

### Advanced Queries

#### 13. Find Potential Refactoring Opportunities
```cypher
// Functions with high complexity that are called frequently
MATCH (f:PythonFunction)<-[:CALLS]-(caller)
WITH f, count(caller) as usage, f.complexity as complexity
WHERE usage > 3 AND complexity IN ['high', 'very_high']
RETURN f.name as Function,
       f.signature as Signature,
       usage as UsageCount,
       complexity as Complexity
ORDER BY usage DESC, complexity DESC
```

#### 14. Documentation Coverage Analysis
```cypher
// Find code that lacks documentation
MATCH (f:PythonFunction)
WHERE NOT EXISTS((f)<-[:DESCRIBES]-(:DocSection))
RETURN f.name as UndocumentedFunction,
       f.signature as Signature,
       f.source_file as File
ORDER BY File, f.name
```

#### 15. Schema Usage Tracking
```cypher
// Show which schemas are used by which functions
MATCH (schema:Schema)<-[:USES]-(func:PythonFunction)
RETURN schema.name as Schema,
       collect(func.name) as UsedByFunctions
ORDER BY Schema
```

### Knowledge Discovery Queries

#### 16. Find Related Concepts
```cypher
// Discover concepts related to a specific topic
MATCH (concept1:Concept)-[:RELATED_TO]-(concept2:Concept)
WHERE concept1.name CONTAINS "LLM"
RETURN concept1.name as MainConcept,
       concept2.name as RelatedConcept,
       concept2.description as Description
```

#### 17. Trace Feature to Implementation
```cypher
// Complete path from feature to implementation
MATCH path = (feature:Feature)-[:IMPLEMENTS*1..3]-(code:PythonFunction)
WHERE feature.name = "Entity Extraction"
RETURN feature.name as Feature,
       [node in nodes(path) | node.name] as ImplementationPath
```

#### 18. Find Learning Paths
```cypher
// Suggested reading order for understanding a topic
MATCH (concept:Concept {name: "Ontology Design"})-[:PREREQUISITE_FOR*1..3]->(advanced:Concept)
RETURN concept.name as StartingPoint,
       advanced.name as AdvancedTopic,
       length(path) as Steps
ORDER BY Steps, AdvancedTopic
```

## Visualization and Analysis

### Neo4j Browser Visualizations

#### Network Graph View
```cypher
// Visualize component relationships
MATCH (c:Component)-[r:DEPENDS_ON]->(dep:Component)
RETURN c, r, dep
LIMIT 50
```

#### Documentation Map
```cypher
// Visualize documentation structure
MATCH (doc:DocFile)-[:CONTAINS]->(section:DocSection)-[:EXPLAINS]->(concept:Concept)
RETURN doc, section, concept
LIMIT 30
```

### Export for External Analysis

#### Export to CSV
```cypher
// Export function relationships for analysis
MATCH (f1:PythonFunction)-[:CALLS]->(f2:PythonFunction)
RETURN f1.name as Caller, 
       f2.name as Called,
       f1.source_file as CallerFile,
       f2.source_file as CalledFile
```

#### Generate GraphML
```cypher
// Export for Gephi or other graph analysis tools
CALL apoc.export.graphml.all("mycomind_graph.graphml", {})
```

## Maintenance and Updates

### Keeping the Knowledge Graph Current

The project knowledge graph should be regenerated when:
- New code is added or existing code is modified
- Documentation is updated or restructured
- New features are implemented
- Architecture changes occur

### Future Automation

A planned `build_project_kg.py` script will automate the knowledge graph generation:

```python
# Future automation script
def build_project_kg():
    """
    Automatically generate the project knowledge graph by:
    1. Parsing Python AST for code structure
    2. Analyzing Markdown documentation
    3. Extracting schema definitions
    4. Mapping relationships between components
    5. Generating Cypher import script
    """
    pass
```

## Benefits and Use Cases

### For Developers
- **Code Navigation**: Understand function dependencies and call graphs
- **Impact Analysis**: See what code is affected by changes
- **Architecture Understanding**: Visualize system components and relationships
- **Refactoring Support**: Identify tightly coupled code and potential improvements

### For Documentation
- **Content Discovery**: Find related documentation across files
- **Gap Analysis**: Identify undocumented features or concepts
- **Cross-Reference Validation**: Ensure documentation links are accurate
- **Learning Path Creation**: Build guided tours through complex topics

### For Project Management
- **Feature Tracking**: Map features to their implementations
- **Complexity Assessment**: Understand system complexity and technical debt
- **Dependency Management**: Visualize and manage component dependencies
- **Knowledge Transfer**: Help new team members understand the codebase

This advanced documentation feature showcases MycoMind's power while providing practical value for understanding and maintaining the project itself.
