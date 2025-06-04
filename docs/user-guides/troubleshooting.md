# Troubleshooting Guide

## Common Issues and Solutions

### API and Authentication Issues

#### OpenAI API Key Not Found
```bash
# Check if environment variable is set
echo $OPENAI_API_KEY

# Set it temporarily
export OPENAI_API_KEY="your-key-here"

# Add to shell profile for persistence
echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.bashrc
source ~/.bashrc
```

#### API Rate Limits
**Symptoms**: HTTP 429 errors, slow processing
**Solutions**:
- Reduce batch size in configuration
- Add delays between requests
- Upgrade your OpenAI plan

```json
{
  "processing": {
    "batch_size": 2,
    "max_concurrent": 1
  },
  "llm": {
    "retry_attempts": 5,
    "retry_delay": 2.0
  }
}
```

#### Invalid API Key
**Symptoms**: HTTP 401 errors
**Solutions**:
- Verify key is correct and active
- Check for extra spaces or characters
- Regenerate key if necessary

### Configuration Issues

#### Obsidian Vault Path Not Found
```bash
# Verify the path exists
ls -la "/path/to/your/obsidian/vault"

# Check permissions
ls -ld "/path/to/your/obsidian/vault"

# Create directory if it doesn't exist
mkdir -p "/path/to/your/obsidian/vault"
```

#### Configuration File Syntax Errors
```bash
# Validate JSON syntax
python -m json.tool config.json

# Check for common issues:
# - Missing commas
# - Trailing commas
# - Unmatched brackets
# - Incorrect quotes
```

#### Schema Validation Errors
```bash
# Validate your schema
python scripts/schema_parser.py validate schemas/your_schema.json

# Common schema issues:
# - Missing required fields
# - Invalid JSON-LD syntax
# - Incorrect @context references
```

### Processing Issues

#### No Entities Extracted
**Possible Causes**:
- Schema doesn't match content
- Content doesn't contain recognizable entities
- Quality threshold too high
- LLM temperature too low

**Solutions**:
```bash
# Test with verbose output
python scripts/main_etl.py --source document.md --schema schema.json --verbose

# Lower quality threshold
# Edit config.json:
{
  "processing": {
    "quality_threshold": 0.5
  }
}

# Increase LLM temperature slightly
{
  "llm": {
    "temperature": 0.3
  }
}
```

#### Partial Extraction Results
**Symptoms**: Some entities missing, incomplete relationships
**Solutions**:
- Check document chunking settings
- Verify entity definitions in schema
- Review extraction prompts

```json
{
  "processing": {
    "chunk_size": 6000,
    "chunk_overlap": 400
  }
}
```

#### Memory or Performance Issues
```bash
# Reduce batch size
{
  "processing": {
    "batch_size": 1,
    "max_concurrent": 1
  }
}

# Enable caching to avoid reprocessing
{
  "processing": {
    "enable_caching": true
  }
}

# Process files individually
python scripts/main_etl.py --source single_file.md --schema schema.json
```

### Graph Database Issues

#### Neo4j Won't Start
```bash
# Check Java version (requires Java 17 or 21)
java -version

# Check if port 7474 is already in use
lsof -i :7474

# View Neo4j logs
python scripts/setup_neo4j.py --logs

# Kill existing Neo4j processes
pkill -f neo4j
```

#### Neo4j Connection Refused
**Solutions**:
- Verify Neo4j is running: `python scripts/setup_neo4j.py --status`
- Check firewall settings
- Ensure localhost resolution works
- Try accessing via IP: http://127.0.0.1:7474

#### Cypher Loading Errors
```bash
# Check for syntax errors in generated Cypher
head -20 mycomind_knowledge_graph.cypher

# Load data in smaller batches
grep "^CREATE (" mycomind_knowledge_graph.cypher | head -10 | scripts/neo4j/neo4j-community-5.15.0/bin/cypher-shell -u neo4j -p ''

# Clear and restart database if needed
python scripts/setup_neo4j.py --stop
rm -rf scripts/neo4j/neo4j-community-5.15.0/data/
python scripts/setup_neo4j.py --start
```

#### Fuseki Server Issues
```bash
# Check if Fuseki is running
python scripts/setup_fuseki.py --status

# View Fuseki logs
python scripts/setup_fuseki.py --logs

# Restart Fuseki
python scripts/setup_fuseki.py --stop
python scripts/setup_fuseki.py --start --port 3030
```

### File System Issues

#### Permission Denied Errors
```bash
# Fix ownership
sudo chown -R $USER:$USER /path/to/vault

# Fix permissions
chmod -R 755 /path/to/vault

# Check disk space
df -h
```

#### File Encoding Issues
**Symptoms**: Unicode errors, garbled text
**Solutions**:
```json
{
  "data_sources": {
    "default_encoding": "utf-8",
    "encoding_detection": true
  }
}
```

#### Large File Processing
```bash
# Split large files before processing
split -l 1000 large_file.txt chunk_

# Adjust chunk size for large documents
{
  "processing": {
    "chunk_size": 8000,
    "chunk_overlap": 200
  }
}
```

### Quality and Accuracy Issues

#### Low Extraction Quality
**Strategies**:
- Improve schema definitions with better descriptions
- Add examples to entity types
- Adjust extraction prompts
- Use higher-quality source documents

#### Inconsistent Entity Names
**Solutions**:
- Add entity normalization rules
- Use consistent naming in source documents
- Post-process extracted data for cleanup

#### Missing Relationships
**Common Causes**:
- Relationships not explicitly stated in text
- Schema doesn't define expected relationship types
- Context window too small for relationship detection

**Solutions**:
```json
{
  "processing": {
    "chunk_overlap": 500,
    "relationship_extraction": {
      "context_window": 2000,
      "minimum_confidence": 0.6
    }
  }
}
```

## Debug Mode

Enable comprehensive debugging:

```json
{
  "logging": {
    "level": "DEBUG"
  },
  "debug": {
    "save_llm_requests": true,
    "save_llm_responses": true,
    "save_intermediate_results": true,
    "verbose_validation": true
  }
}
```

## Getting Additional Help

### Log Analysis
Check detailed logs for error context:
```bash
# View recent errors
tail -50 logs/mycomind.log | grep ERROR

# Search for specific issues
grep -i "api\|auth\|connection" logs/mycomind.log
```

### Component Testing
Test individual components:
```bash
# Test LLM connectivity
python scripts/test_llm.py --config config.json

# Test schema validation
python scripts/schema_parser.py validate schemas/your_schema.json

# Test file processing
python scripts/main_etl.py --dry-run --verbose
```

### Performance Monitoring
```bash
# Monitor resource usage during processing
top -p $(pgrep -f main_etl.py)

# Check disk usage
du -sh vault/extracted_knowledge/
```

If issues persist, check the logs directory for detailed error messages and consider running with the `--verbose` flag for additional debugging information.