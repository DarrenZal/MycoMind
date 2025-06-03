# Changelog

All notable changes to MycoMind will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Neo4j Integration**: 
  - New `yaml_to_neo4j_converter.py` script to convert YAML frontmatter to Cypher statements
  - `setup_neo4j.py` utility for automated Neo4j installation and configuration
  - Comprehensive documentation in `docs/Neo4j_Database_Setup.md`
- **Browser-based SPARQL Interface**:
  - Full SPARQL 1.1 support using SPARQL.js
  - In-browser querying without requiring external SPARQL endpoints
  - Interactive entity exploration with clickable links
  - Documentation in `docs/Web_SPARQL_Interface.md`
- **File-as-Entity Mode**: New processing mode that updates original files with rich YAML frontmatter while preserving content
- **Dual Output System**: 
  - Standard mode creates new notes in `mycomind_extracted/`
  - File-as-entity mode creates enhanced files in `mycomind_processed/`
- **Enhanced LLM Extraction**: Improved prompts with explicit examples and step-by-step guidance
- **Retry Logic**: Automatic retry mechanism for file-as-entity mode when expected entities aren't extracted
- **Robust Schema Validation**: Proper handling of empty relationship arrays and None values
- **Ontology Converter**: New utility to convert RDF/JSON-LD ontologies to MycoMind schemas
- **Debug Tools**: Added comprehensive debugging scripts for troubleshooting extraction issues

### Improved
- **Knowledge Graph Visualization**: Added Neo4j support for interactive graph visualization
- **Query Capabilities**: Multiple query interfaces (Browser SPARQL, Neo4j Cypher, Fuseki SPARQL)
- **SPARQL.js Integration**: Enhanced web interface with full SPARQL 1.1 support, including UNION, FILTER, and OPTIONAL patterns
- **Neo4j Java Compatibility Check**: Added automatic Java version validation to ensure Neo4j 5.x compatibility (requires Java 17 or 21)
- **LLM Consistency**: Enhanced extraction prompts with concrete examples for more reliable entity extraction
- **Validation Logic**: Fixed schema validation to properly handle empty relationships without false rejections
- **Error Handling**: Better error messages and logging throughout the pipeline
- **Documentation**: Comprehensive documentation for all query interfaces and database options

### Fixed
- **Schema Validation Bug**: Empty relationship arrays no longer cause validation failures
- **Entity Extraction Consistency**: LLM now consistently extracts main document subjects as primary entities
- **File-as-Entity Processing**: Proper detection and processing of primary entities for in-place file updates

### Technical Changes
- Added `scripts/yaml_to_neo4j_converter.py` for Neo4j Cypher generation
- Added `scripts/setup_neo4j.py` for Neo4j installation and management
- Updated `docs/web/mycomind-query.js` to use SPARQL.js for full SPARQL 1.1 support
- Modified `scripts/schema_parser.py` to skip validation for empty arrays and None values in relationships
- Enhanced `scripts/main_etl.py` with retry logic and improved extraction prompts
- Updated `scripts/obsidian_utils.py` to support dual output modes
- Added `scripts/ontology_converter.py` for schema conversion workflows
- Set LLM temperature to 0.0 for deterministic results
- Updated dependencies in `scripts/requirements.txt` to include Neo4j and graph database libraries

## [Previous Versions]

### Initial Release
- Basic ETL pipeline for knowledge extraction
- Obsidian integration with YAML frontmatter
- JSON-LD schema support
- OpenAI and Anthropic LLM integration
- Configurable processing workflows
