// MycoMind Project Knowledge Graph
// This Cypher script creates a knowledge graph representation of the MycoMind project
// including its code structure, documentation, and architectural relationships

// Clear existing data (use with caution)
// MATCH (n) DETACH DELETE n;

// Create Python Modules
CREATE (config_manager:PythonModule {
  name: "config_manager.py",
  path: "scripts/config_manager.py",
  docstring: "Configuration Manager for MycoMind - handles loading, validating, and managing configuration settings",
  line_count: 400,
  imports: ["json", "os", "logging", "yaml", "jsonschema", "dotenv"]
});

CREATE (schema_parser:PythonModule {
  name: "schema_parser.py", 
  path: "scripts/schema_parser.py",
  docstring: "Schema Parser for MycoMind - handles parsing and validation of JSON-LD schemas",
  line_count: 600,
  imports: ["json", "logging", "pathlib", "dataclasses", "jsonschema", "re"]
});

CREATE (obsidian_utils:PythonModule {
  name: "obsidian_utils.py",
  path: "scripts/obsidian_utils.py", 
  docstring: "Obsidian Utilities for MycoMind - handles generation of Obsidian-compatible Markdown files",
  line_count: 500,
  imports: ["os", "re", "yaml", "logging", "pathlib", "datetime", "unicodedata", "shutil"]
});

CREATE (main_etl:PythonModule {
  name: "main_etl.py",
  path: "scripts/main_etl.py",
  docstring: "Main ETL Pipeline for MycoMind - orchestrates the complete Extract, Transform, Load process",
  line_count: 800,
  imports: ["os", "sys", "json", "logging", "argparse", "time", "datetime", "pathlib", "hashlib", "pickle"]
});

// Create Python Classes
CREATE (config_manager_class:PythonClass {
  name: "ConfigManager",
  docstring: "Centralized configuration management for MycoMind",
  line_number: 25,
  is_abstract: false,
  methods: ["__init__", "load_config", "_validate_config", "get", "set", "save_config"]
});

CREATE (schema_parser_class:PythonClass {
  name: "SchemaParser", 
  docstring: "Parser for JSON-LD schemas used in MycoMind knowledge extraction",
  line_number: 80,
  is_abstract: false,
  methods: ["__init__", "load_schema", "validate_extracted_entity", "build_extraction_prompt"]
});

CREATE (obsidian_generator_class:PythonClass {
  name: "ObsidianNoteGenerator",
  docstring: "Generator for Obsidian-compatible Markdown notes with YAML frontmatter", 
  line_number: 30,
  is_abstract: false,
  methods: ["__init__", "generate_note", "save_note", "process_entities"]
});

CREATE (llm_client_class:PythonClass {
  name: "LLMClient",
  docstring: "Unified client for different LLM providers",
  line_number: 50,
  is_abstract: false,
  methods: ["__init__", "generate_completion", "_openai_completion", "_anthropic_completion"]
});

CREATE (etl_class:PythonClass {
  name: "MycoMindETL",
  docstring: "Main ETL pipeline for MycoMind knowledge extraction",
  line_number: 300,
  is_abstract: false,
  methods: ["__init__", "process_data_source", "_extract_entities_from_chunk", "_validate_entities"]
});

// Create Key Functions
CREATE (load_config_func:PythonFunction {
  name: "load_config",
  signature: "load_config(config_path: Optional[str] = None) -> ConfigManager",
  docstring: "Convenience function to load configuration",
  complexity: "low",
  line_number: 380,
  parameters: ["config_path"],
  return_type: "ConfigManager"
});

CREATE (extract_entities_func:PythonFunction {
  name: "_extract_entities_from_chunk",
  signature: "_extract_entities_from_chunk(self, text_chunk: str, schema_def: SchemaDefinition) -> ProcessingResult",
  docstring: "Extract entities from a single text chunk",
  complexity: "high", 
  line_number: 450,
  parameters: ["self", "text_chunk", "schema_def"],
  return_type: "ProcessingResult"
});

CREATE (generate_note_func:PythonFunction {
  name: "generate_note",
  signature: "generate_note(self, entity: Dict[str, Any], metadata: Dict[str, Any]) -> Tuple[str, str]",
  docstring: "Generate a complete Obsidian note from an entity",
  complexity: "medium",
  line_number: 80,
  parameters: ["self", "entity", "metadata"],
  return_type: "Tuple[str, str]"
});

CREATE (validate_schema_func:PythonFunction {
  name: "validate_extracted_entity",
  signature: "validate_extracted_entity(self, entity_data: Dict[str, Any], schema_def: SchemaDefinition) -> Tuple[bool, List[str]]",
  docstring: "Validate an extracted entity against the schema",
  complexity: "medium",
  line_number: 280,
  parameters: ["self", "entity_data", "schema_def"],
  return_type: "Tuple[bool, List[str]]"
});

// Create System Components
CREATE (config_component:Component {
  name: "Configuration Management",
  description: "Handles loading, validation, and access to system configuration",
  type: "core",
  responsibility: "Centralized configuration handling with validation and environment management"
});

CREATE (schema_component:Component {
  name: "Schema Processing",
  description: "Parses and validates JSON-LD schemas for knowledge extraction",
  type: "core", 
  responsibility: "Schema definition parsing and entity validation"
});

CREATE (extraction_component:Component {
  name: "Knowledge Extraction",
  description: "LLM-driven entity extraction and relationship identification",
  type: "core",
  responsibility: "Transform unstructured text into structured knowledge"
});

CREATE (output_component:Component {
  name: "Output Generation", 
  description: "Generates Obsidian-compatible notes with YAML frontmatter",
  type: "interface",
  responsibility: "Create structured Markdown files with YAML frontmatter and WikiLinks"
});

// Create Features
CREATE (ontology_feature:Feature {
  name: "Ontology-Driven Extraction",
  description: "Uses JSON-LD schemas to define knowledge structures",
  status: "implemented",
  priority: "critical",
  complexity: "complex"
});

CREATE (semantic_linking_feature:Feature {
  name: "Semantic Linking",
  description: "Automatically creates WikiLinks for entity relationships",
  status: "implemented", 
  priority: "high",
  complexity: "moderate"
});

CREATE (llm_integration_feature:Feature {
  name: "LLM Integration",
  description: "Leverages language models for intelligent information extraction",
  status: "implemented",
  priority: "critical", 
  complexity: "complex"
});

CREATE (obsidian_integration_feature:Feature {
  name: "Obsidian Integration",
  description: "Creates structured Markdown notes with YAML frontmatter",
  status: "implemented",
  priority: "high",
  complexity: "moderate"
});

// Create Documentation Files
CREATE (readme_doc:DocFile {
  name: "README.md",
  path: "README.md",
  format: "markdown",
  word_count: 800,
  last_modified: "2024-01-15"
});

CREATE (architecture_doc:DocFile {
  name: "Architecture.md",
  path: "docs/Architecture.md", 
  format: "markdown",
  word_count: 2500,
  last_modified: "2024-01-15"
});

CREATE (config_doc:DocFile {
  name: "Configuration.md",
  path: "docs/Configuration.md",
  format: "markdown", 
  word_count: 3000,
  last_modified: "2024-01-15"
});

CREATE (etl_doc:DocFile {
  name: "ETL_Process.md",
  path: "docs/ETL_Process.md",
  format: "markdown",
  word_count: 2800,
  last_modified: "2024-01-15"
});

// Create Documentation Sections
CREATE (overview_section:DocSection {
  name: "Overview",
  heading_level: 2,
  content: "MycoMind is designed as a modular, extensible system for ontology-driven knowledge extraction",
  word_count: 150,
  section_type: "overview",
  topics: ["architecture", "modularity", "extensibility"]
});

CREATE (config_section:DocSection {
  name: "Configuration Management",
  heading_level: 3,
  content: "Centralized configuration handling with validation and environment management",
  word_count: 400,
  section_type: "guide",
  topics: ["configuration", "validation", "environment"]
});

CREATE (etl_overview_section:DocSection {
  name: "ETL Process Overview", 
  heading_level: 2,
  content: "The ETL process is the core of MycoMind's knowledge extraction pipeline",
  word_count: 200,
  section_type: "overview",
  topics: ["etl", "pipeline", "extraction"]
});

// Create Key Concepts
CREATE (ontology_concept:Concept {
  name: "Ontology-Driven Knowledge Extraction",
  definition: "Using formal schema definitions to guide the extraction of structured information from unstructured text",
  domain: "knowledge management",
  importance: "fundamental",
  keywords: ["ontology", "schema", "extraction", "structured data"]
});

CREATE (semantic_linking_concept:Concept {
  name: "Semantic Linking",
  definition: "Creating meaningful connections between entities using WikiLink formatting and relationship definitions",
  domain: "knowledge graphs",
  importance: "important", 
  keywords: ["linking", "relationships", "wikilinks", "connections"]
});

CREATE (etl_concept:Concept {
  name: "ETL Pipeline",
  definition: "Extract, Transform, Load process for converting unstructured data into structured knowledge",
  domain: "data processing",
  importance: "fundamental",
  keywords: ["etl", "pipeline", "data processing", "transformation"]
});

// Create Configuration Options
CREATE (llm_provider_config:Configuration {
  name: "llm.provider",
  type: "string",
  default_value: "openai",
  description: "LLM provider to use (openai, anthropic, custom)",
  required: true
});

CREATE (vault_path_config:Configuration {
  name: "obsidian.vault_path", 
  type: "string",
  default_value: "/path/to/vault",
  description: "Path to Obsidian vault directory",
  required: true
});

CREATE (batch_size_config:Configuration {
  name: "processing.batch_size",
  type: "integer", 
  default_value: "5",
  description: "Number of items to process in each batch",
  required: false
});

// Create Relationships

// Module relationships
MATCH (config_manager:PythonModule {name: "config_manager.py"})
MATCH (main_etl:PythonModule {name: "main_etl.py"})
CREATE (main_etl)-[:IMPORTS]->(config_manager);

MATCH (schema_parser:PythonModule {name: "schema_parser.py"})
MATCH (main_etl:PythonModule {name: "main_etl.py"})
CREATE (main_etl)-[:IMPORTS]->(schema_parser);

MATCH (obsidian_utils:PythonModule {name: "obsidian_utils.py"})
MATCH (main_etl:PythonModule {name: "main_etl.py"})
CREATE (main_etl)-[:IMPORTS]->(obsidian_utils);

// Class-Module relationships
MATCH (config_manager:PythonModule {name: "config_manager.py"})
MATCH (config_manager_class:PythonClass {name: "ConfigManager"})
CREATE (config_manager)-[:CONTAINS]->(config_manager_class);

MATCH (schema_parser:PythonModule {name: "schema_parser.py"})
MATCH (schema_parser_class:PythonClass {name: "SchemaParser"})
CREATE (schema_parser)-[:CONTAINS]->(schema_parser_class);

MATCH (obsidian_utils:PythonModule {name: "obsidian_utils.py"})
MATCH (obsidian_generator_class:PythonClass {name: "ObsidianNoteGenerator"})
CREATE (obsidian_utils)-[:CONTAINS]->(obsidian_generator_class);

MATCH (main_etl:PythonModule {name: "main_etl.py"})
MATCH (etl_class:PythonClass {name: "MycoMindETL"})
CREATE (main_etl)-[:CONTAINS]->(etl_class);

// Function-Class relationships
MATCH (etl_class:PythonClass {name: "MycoMindETL"})
MATCH (extract_entities_func:PythonFunction {name: "_extract_entities_from_chunk"})
CREATE (etl_class)-[:HAS_METHOD]->(extract_entities_func);

MATCH (obsidian_generator_class:PythonClass {name: "ObsidianNoteGenerator"})
MATCH (generate_note_func:PythonFunction {name: "generate_note"})
CREATE (obsidian_generator_class)-[:HAS_METHOD]->(generate_note_func);

MATCH (schema_parser_class:PythonClass {name: "SchemaParser"})
MATCH (validate_schema_func:PythonFunction {name: "validate_extracted_entity"})
CREATE (schema_parser_class)-[:HAS_METHOD]->(validate_schema_func);

// Component-Module relationships
MATCH (config_component:Component {name: "Configuration Management"})
MATCH (config_manager:PythonModule {name: "config_manager.py"})
CREATE (config_component)-[:IMPLEMENTED_BY]->(config_manager);

MATCH (schema_component:Component {name: "Schema Processing"})
MATCH (schema_parser:PythonModule {name: "schema_parser.py"})
CREATE (schema_component)-[:IMPLEMENTED_BY]->(schema_parser);

MATCH (extraction_component:Component {name: "Knowledge Extraction"})
MATCH (main_etl:PythonModule {name: "main_etl.py"})
CREATE (extraction_component)-[:IMPLEMENTED_BY]->(main_etl);

MATCH (output_component:Component {name: "Output Generation"})
MATCH (obsidian_utils:PythonModule {name: "obsidian_utils.py"})
CREATE (output_component)-[:IMPLEMENTED_BY]->(obsidian_utils);

// Feature-Function relationships
MATCH (ontology_feature:Feature {name: "Ontology-Driven Extraction"})
MATCH (extract_entities_func:PythonFunction {name: "_extract_entities_from_chunk"})
CREATE (ontology_feature)-[:IMPLEMENTED_BY]->(extract_entities_func);

MATCH (semantic_linking_feature:Feature {name: "Semantic Linking"})
MATCH (generate_note_func:PythonFunction {name: "generate_note"})
CREATE (semantic_linking_feature)-[:IMPLEMENTED_BY]->(generate_note_func);

MATCH (obsidian_integration_feature:Feature {name: "Obsidian Integration"})
MATCH (generate_note_func:PythonFunction {name: "generate_note"})
CREATE (obsidian_integration_feature)-[:IMPLEMENTED_BY]->(generate_note_func);

// Documentation relationships
MATCH (architecture_doc:DocFile {name: "Architecture.md"})
MATCH (overview_section:DocSection {name: "Overview"})
CREATE (architecture_doc)-[:CONTAINS]->(overview_section);

MATCH (architecture_doc:DocFile {name: "Architecture.md"})
MATCH (config_section:DocSection {name: "Configuration Management"})
CREATE (architecture_doc)-[:CONTAINS]->(config_section);

MATCH (etl_doc:DocFile {name: "ETL_Process.md"})
MATCH (etl_overview_section:DocSection {name: "ETL Process Overview"})
CREATE (etl_doc)-[:CONTAINS]->(etl_overview_section);

// Documentation-Feature relationships
MATCH (config_section:DocSection {name: "Configuration Management"})
MATCH (config_component:Component {name: "Configuration Management"})
CREATE (config_section)-[:DESCRIBES]->(config_component);

MATCH (etl_overview_section:DocSection {name: "ETL Process Overview"})
MATCH (extraction_component:Component {name: "Knowledge Extraction"})
CREATE (etl_overview_section)-[:DESCRIBES]->(extraction_component);

// Concept-Feature relationships
MATCH (ontology_concept:Concept {name: "Ontology-Driven Knowledge Extraction"})
MATCH (ontology_feature:Feature {name: "Ontology-Driven Extraction"})
CREATE (ontology_concept)-[:IMPLEMENTED_BY]->(ontology_feature);

MATCH (semantic_linking_concept:Concept {name: "Semantic Linking"})
MATCH (semantic_linking_feature:Feature {name: "Semantic Linking"})
CREATE (semantic_linking_concept)-[:IMPLEMENTED_BY]->(semantic_linking_feature);

MATCH (etl_concept:Concept {name: "ETL Pipeline"})
MATCH (extraction_component:Component {name: "Knowledge Extraction"})
CREATE (etl_concept)-[:IMPLEMENTED_BY]->(extraction_component);

// Configuration-Component relationships
MATCH (llm_provider_config:Configuration {name: "llm.provider"})
MATCH (extraction_component:Component {name: "Knowledge Extraction"})
CREATE (llm_provider_config)-[:AFFECTS]->(extraction_component);

MATCH (vault_path_config:Configuration {name: "obsidian.vault_path"})
MATCH (output_component:Component {name: "Output Generation"})
CREATE (vault_path_config)-[:AFFECTS]->(output_component);

MATCH (batch_size_config:Configuration {name: "processing.batch_size"})
MATCH (extraction_component:Component {name: "Knowledge Extraction"})
CREATE (batch_size_config)-[:AFFECTS]->(extraction_component);

// Component dependencies
MATCH (extraction_component:Component {name: "Knowledge Extraction"})
MATCH (config_component:Component {name: "Configuration Management"})
CREATE (extraction_component)-[:DEPENDS_ON]->(config_component);

MATCH (extraction_component:Component {name: "Knowledge Extraction"})
MATCH (schema_component:Component {name: "Schema Processing"})
CREATE (extraction_component)-[:DEPENDS_ON]->(schema_component);

MATCH (output_component:Component {name: "Output Generation"})
MATCH (extraction_component:Component {name: "Knowledge Extraction"})
CREATE (output_component)-[:DEPENDS_ON]->(extraction_component);

// Feature dependencies
MATCH (semantic_linking_feature:Feature {name: "Semantic Linking"})
MATCH (ontology_feature:Feature {name: "Ontology-Driven Extraction"})
CREATE (semantic_linking_feature)-[:DEPENDS_ON]->(ontology_feature);

MATCH (obsidian_integration_feature:Feature {name: "Obsidian Integration"})
MATCH (semantic_linking_feature:Feature {name: "Semantic Linking"})
CREATE (obsidian_integration_feature)-[:DEPENDS_ON]->(semantic_linking_feature);

// Concept relationships
MATCH (semantic_linking_concept:Concept {name: "Semantic Linking"})
MATCH (ontology_concept:Concept {name: "Ontology-Driven Knowledge Extraction"})
CREATE (semantic_linking_concept)-[:RELATED_TO]->(ontology_concept);

MATCH (etl_concept:Concept {name: "ETL Pipeline"})
MATCH (ontology_concept:Concept {name: "Ontology-Driven Knowledge Extraction"})
CREATE (etl_concept)-[:RELATED_TO]->(ontology_concept);

// Create indexes for better query performance
CREATE INDEX FOR (n:PythonFunction) ON (n.name);
CREATE INDEX FOR (n:PythonClass) ON (n.name);
CREATE INDEX FOR (n:PythonModule) ON (n.name);
CREATE INDEX FOR (n:Component) ON (n.name);
CREATE INDEX FOR (n:Feature) ON (n.name);
CREATE INDEX FOR (n:DocSection) ON (n.name);
CREATE INDEX FOR (n:Concept) ON (n.name);
CREATE INDEX FOR (n:Configuration) ON (n.name);
