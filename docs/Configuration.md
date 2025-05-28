# Configuration Guide

## Overview

MycoMind uses a flexible configuration system that allows you to customize every aspect of the knowledge extraction pipeline. Configuration is managed through JSON files with support for environment variables and multiple configuration profiles.

## Configuration File Structure

### Main Configuration File (`config.json`)

```json
{
  "version": "1.0.0",
  "profile": "default",
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "base_url": null,
    "temperature": 0.1,
    "max_tokens": 4000,
    "timeout": 60,
    "retry_attempts": 3,
    "retry_delay": 1.0
  },
  "obsidian": {
    "vault_path": "/path/to/your/obsidian/vault",
    "notes_folder": "extracted_knowledge",
    "create_folders": true,
    "folder_structure": "by_type",
    "filename_template": "{name}",
    "overwrite_existing": false,
    "backup_existing": true
  },
  "processing": {
    "batch_size": 5,
    "max_concurrent": 3,
    "chunk_size": 4000,
    "chunk_overlap": 200,
    "enable_caching": true,
    "cache_ttl": 3600,
    "quality_threshold": 0.7
  },
  "logging": {
    "level": "INFO",
    "file": "logs/mycomind.log",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "max_size": "10MB",
    "backup_count": 5
  },
  "data_sources": {
    "default_encoding": "utf-8",
    "supported_formats": ["txt", "md", "pdf", "docx", "html"],
    "web_scraping": {
      "user_agent": "MycoMind/1.0",
      "timeout": 30,
      "max_redirects": 5
    }
  }
}
```

## Configuration Sections

### LLM Configuration

#### OpenAI Configuration
```json
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4",
    "api_key_env": "OPENAI_API_KEY",
    "organization": null,
    "temperature": 0.1,
    "max_tokens": 4000,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
  }
}
```

#### Anthropic Configuration
```json
{
  "llm": {
    "provider": "anthropic",
    "model": "claude-3-sonnet-20240229",
    "api_key_env": "ANTHROPIC_API_KEY",
    "temperature": 0.1,
    "max_tokens": 4000
  }
}
```

#### Local/Custom LLM Configuration
```json
{
  "llm": {
    "provider": "custom",
    "base_url": "http://localhost:8000/v1",
    "model": "local-model",
    "api_key_env": "LOCAL_API_KEY",
    "headers": {
      "Custom-Header": "value"
    }
  }
}
```

### Obsidian Configuration

#### Vault Settings
```json
{
  "obsidian": {
    "vault_path": "/Users/username/Documents/MyVault",
    "notes_folder": "extracted_knowledge",
    "create_folders": true,
    "folder_structure": "by_type"
  }
}
```

**Folder Structure Options:**
- `"flat"`: All notes in the same folder
- `"by_type"`: Separate folders for each entity type
- `"by_date"`: Organize by extraction date
- `"by_source"`: Organize by source document
- `"custom"`: Use custom folder mapping

#### Custom Folder Structure
```json
{
  "obsidian": {
    "folder_structure": "custom",
    "folder_mapping": {
      "Person": "people",
      "Organization": "organizations",
      "Concept": "concepts",
      "Project": "projects"
    }
  }
}
```

#### File Naming
```json
{
  "obsidian": {
    "filename_template": "{name}",
    "filename_sanitization": {
      "replace_spaces": "_",
      "remove_special_chars": true,
      "max_length": 100,
      "case": "lower"
    }
  }
}
```

**Template Variables:**
- `{name}`: Entity name
- `{type}`: Entity type
- `{date}`: Current date (YYYY-MM-DD)
- `{timestamp}`: Unix timestamp
- `{source}`: Source document name

### Processing Configuration

#### Batch Processing
```json
{
  "processing": {
    "batch_size": 5,
    "max_concurrent": 3,
    "processing_mode": "parallel"
  }
}
```

#### Text Chunking
```json
{
  "processing": {
    "chunk_size": 4000,
    "chunk_overlap": 200,
    "chunking_strategy": "semantic",
    "preserve_structure": true
  }
}
```

**Chunking Strategies:**
- `"fixed"`: Fixed character count
- `"semantic"`: Respect paragraph boundaries
- `"sentence"`: Split on sentence boundaries
- `"custom"`: Use custom splitting logic

#### Caching
```json
{
  "processing": {
    "enable_caching": true,
    "cache_backend": "file",
    "cache_directory": ".cache/mycomind",
    "cache_ttl": 3600,
    "cache_compression": true
  }
}
```

### Data Source Configuration

#### File Processing
```json
{
  "data_sources": {
    "file_processing": {
      "default_encoding": "utf-8",
      "encoding_detection": true,
      "supported_formats": ["txt", "md", "pdf", "docx", "html"],
      "pdf_extraction": {
        "method": "pdfplumber",
        "preserve_layout": false,
        "extract_images": false
      },
      "docx_extraction": {
        "include_headers": true,
        "include_footers": false,
        "extract_tables": true
      }
    }
  }
}
```

#### Web Scraping
```json
{
  "data_sources": {
    "web_scraping": {
      "user_agent": "MycoMind/1.0",
      "timeout": 30,
      "max_redirects": 5,
      "respect_robots_txt": true,
      "rate_limit": 1.0,
      "headers": {
        "Accept": "text/html,application/xhtml+xml"
      }
    }
  }
}
```

## Environment Variables

### Required Environment Variables

```bash
# LLM API Keys
export OPENAI_API_KEY="your-openai-api-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optional: Custom LLM endpoints
export LOCAL_API_KEY="your-local-api-key"
export CUSTOM_LLM_ENDPOINT="http://localhost:8000"

# Optional: Obsidian vault path (if not in config)
export OBSIDIAN_VAULT_PATH="/path/to/vault"
```

### Environment Variable Naming Convention

MycoMind follows these conventions for environment variables:
- Prefix with `MYCOMIND_` for application-specific variables
- Use `_ENV` suffix in config to reference environment variables
- Support both direct values and environment variable references

```json
{
  "llm": {
    "api_key_env": "OPENAI_API_KEY",
    "organization_env": "OPENAI_ORG_ID"
  },
  "obsidian": {
    "vault_path_env": "OBSIDIAN_VAULT_PATH"
  }
}
```

## Configuration Profiles

### Multiple Profiles

Create different configurations for different use cases:

#### `config.development.json`
```json
{
  "extends": "config.json",
  "llm": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.2
  },
  "processing": {
    "batch_size": 2,
    "enable_caching": false
  },
  "logging": {
    "level": "DEBUG"
  }
}
```

#### `config.production.json`
```json
{
  "extends": "config.json",
  "llm": {
    "model": "gpt-4",
    "temperature": 0.1
  },
  "processing": {
    "batch_size": 10,
    "max_concurrent": 5
  },
  "logging": {
    "level": "INFO",
    "file": "/var/log/mycomind/production.log"
  }
}
```

### Profile Selection

```bash
# Use specific profile
python scripts/main_etl.py --config config.production.json

# Use environment variable
export MYCOMIND_PROFILE=production
python scripts/main_etl.py
```

## Schema Configuration

### Schema Selection
```json
{
  "schemas": {
    "default": "schemas/general_knowledge.json",
    "research": "schemas/academic_research.json",
    "business": "schemas/business_intelligence.json"
  },
  "schema_validation": {
    "strict_mode": true,
    "allow_unknown_entities": false,
    "require_all_properties": false
  }
}
```

### Schema Overrides
```json
{
  "schema_overrides": {
    "Person": {
      "properties": {
        "additional_field": {
          "type": "string",
          "description": "Custom field for this configuration"
        }
      }
    }
  }
}
```

## Advanced Configuration

### Custom Prompt Templates
```json
{
  "prompts": {
    "extraction_template": "custom_templates/extraction.txt",
    "validation_template": "custom_templates/validation.txt",
    "variables": {
      "system_name": "MycoMind",
      "extraction_style": "detailed"
    }
  }
}
```

### Plugin Configuration
```json
{
  "plugins": {
    "enabled": ["custom_processor", "quality_checker"],
    "custom_processor": {
      "module": "plugins.custom_processor",
      "config": {
        "parameter1": "value1"
      }
    }
  }
}
```

### Quality Control
```json
{
  "quality_control": {
    "confidence_threshold": 0.7,
    "require_relationships": true,
    "max_entities_per_document": 50,
    "validation_rules": [
      "require_name_property",
      "validate_relationship_targets",
      "check_duplicate_entities"
    ]
  }
}
```

## Configuration Validation

### Schema Validation
MycoMind validates configuration files against a JSON schema:

```bash
# Validate configuration
python scripts/validate_config.py --config config.json

# Validate with specific schema
python scripts/validate_config.py --config config.json --schema config_schema.json
```

### Configuration Testing
```bash
# Test configuration with dry run
python scripts/main_etl.py --config config.json --dry-run

# Test specific components
python scripts/test_config.py --config config.json --test llm,obsidian
```

## Configuration Best Practices

### Security
1. **Never commit API keys** to version control
2. **Use environment variables** for sensitive data
3. **Restrict file permissions** on configuration files
4. **Use separate configs** for different environments

### Performance
1. **Tune batch sizes** based on your hardware
2. **Enable caching** for repeated processing
3. **Adjust chunk sizes** for your content type
4. **Monitor resource usage** and adjust accordingly

### Maintainability
1. **Use configuration inheritance** to reduce duplication
2. **Document custom settings** with comments
3. **Version your configurations** alongside your schemas
4. **Test configurations** before deploying

## Troubleshooting

### Common Configuration Issues

#### API Key Problems
```bash
# Check if environment variable is set
echo $OPENAI_API_KEY

# Test API connectivity
python scripts/test_llm.py --config config.json
```

#### Path Issues
```bash
# Verify vault path exists
ls -la "/path/to/your/obsidian/vault"

# Check permissions
python scripts/test_paths.py --config config.json
```

#### Schema Validation Errors
```bash
# Validate schema file
python scripts/validate_schema.py --schema schemas/your_schema.json

# Check schema compatibility
python scripts/test_schema.py --config config.json --schema schemas/your_schema.json
```

### Debug Mode
Enable debug mode for detailed logging:

```json
{
  "logging": {
    "level": "DEBUG"
  },
  "debug": {
    "save_llm_requests": true,
    "save_llm_responses": true,
    "verbose_validation": true
  }
}
```

This comprehensive configuration system ensures that MycoMind can be adapted to a wide variety of use cases while maintaining ease of use and robust error handling.
